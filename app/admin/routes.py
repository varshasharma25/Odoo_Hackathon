from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.admin import bp
from app import db
from app.models import Contact, Product, Budget, AnalyticalAccount, PurchaseOrder, PurchaseOrderLine, VendorBill, VendorBillLine, Invoice, InvoiceLine, SaleOrder, SaleOrderLine, Users, AutoAnalyticalModel
from sqlalchemy.exc import IntegrityError

def save_image(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Ensure unique filename to prevent overwrites
        import uuid
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        return f"uploads/{filename}"
    return None

@bp.route('/dashboard')
@login_required
def dashboard():
    portal_drafts_count = PurchaseOrder.query.filter(PurchaseOrder.user_id.isnot(None), PurchaseOrder.status == 'draft').count()
    sales_drafts_count = SaleOrder.query.filter(SaleOrder.customer_id.isnot(None), SaleOrder.status == 'draft').count()
    total_po_count = PurchaseOrder.query.count()
    
    # Financial Analytics for Admin Dashboard
    balance_outstanding = db.session.query(db.func.sum(VendorBill.total_amount - VendorBill.amount_paid)).filter(VendorBill.payment_status != 'paid').scalar() or 0
    total_purchases = db.session.query(db.func.sum(VendorBill.total_amount)).scalar() or 0
    
    return render_template('admin/dashboard.html', 
                           portal_drafts_count=portal_drafts_count,
                           sales_drafts_count=sales_drafts_count,
                           total_po_count=total_po_count,
                           balance_outstanding=balance_outstanding,
                           total_purchases=total_purchases)

@bp.route('/contacts')
@login_required
def contacts_list():
    contacts = Contact.query.filter_by(is_archived=False).all()
    return render_template('admin/contacts_list.html', contacts=contacts)

@bp.route('/contact/new', methods=['GET', 'POST'])
@login_required
def contact_new():
    if request.method == 'POST':
        try:
            image_url = None
            if 'image' in request.files:
                file = request.files['image']
                saved_path = save_image(file)
                if saved_path:
                    image_url = saved_path

            contact = Contact(
                name=request.form.get('name'),
                email=request.form.get('email') or None,  # Store empty email as None
                phone=request.form.get('phone'),
                company=request.form.get('company'),
                address=request.form.get('address'),
                image_url=image_url
            )
            db.session.add(contact)
            db.session.commit()
            flash('Contact created successfully!', 'success')
            return redirect(url_for('admin.contacts_list'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: A contact with this email already exists.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred: {str(e)}', 'danger')
    return render_template('admin/contact_form.html', contact=None)

@bp.route('/contact/<int:id>', methods=['GET', 'POST'])
@login_required
def contact_detail(id):
    contact = Contact.query.get_or_404(id)
    if request.method == 'POST':
        try:
            contact.name = request.form.get('name')
            contact.email = request.form.get('email') or None
            contact.phone = request.form.get('phone')
            contact.company = request.form.get('company')
            contact.address = request.form.get('address')
            
            if 'image' in request.files:
                file = request.files['image']
                saved_path = save_image(file)
                if saved_path:
                    contact.image_url = saved_path
                    
            db.session.commit()
            flash('Contact updated successfully!', 'success')
            return redirect(url_for('admin.contacts_list'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: A contact with this email already exists.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred: {str(e)}', 'danger')
    return render_template('admin/contact_form.html', contact=contact)

@bp.route('/products')
@login_required
def products_list():
    products = Product.query.filter_by(is_archived=False).all()
    return render_template('admin/products_list.html', products=products)

@bp.route('/product/new', methods=['GET', 'POST'])
@login_required
def product_new():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            category=request.form.get('category', ''),
            sales_price=request.form.get('sales_price', ''),
            purchase_price=request.form.get('purchase_price', '')
        )
        db.session.add(product) 
        db.session.commit()
        flash('Product created successfully!', 'success')
        return redirect(url_for('admin.products_list'))
    return render_template('admin/product_form.html', product=None)

@bp.route('/product/<int:id>', methods=['GET', 'POST'])
@login_required
def product_detail(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST': 
        product.name = request.form.get('name')
        product.category = request.form.get('category')
        product.sales_price = request.form.get('sales_price')
        product.purchase_price = request.form.get('purchase_price')
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.products_list'))
    return render_template('admin/product_form.html', product=product)

@bp.route('/analytical-accounts')
@login_required
def analytical_accounts_list():
    accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()
    return render_template('admin/analytical_accounts_list.html', accounts=accounts)

@bp.route('/analytical-account/new', methods=['GET', 'POST'])
@login_required
def analytical_account_new():
    if request.method == 'POST':
        account = AnalyticalAccount(
            name=request.form.get('name'),
            code=request.form.get('code'),
            description=request.form.get('description'),
            account_type=request.form.get('account_type', 'income')
        )
        db.session.add(account)
        db.session.commit()
        flash('Analytical Account created successfully!', 'success')
        return redirect(url_for('admin.analytical_accounts_list'))
    return render_template('admin/analytical_account_form.html', account=None)

@bp.route('/analytical-account/<int:id>', methods=['GET', 'POST'])
@login_required
def analytical_account_detail(id):
    account = AnalyticalAccount.query.get_or_404(id)
    if request.method == 'POST':
        account.name = request.form.get('name')
        account.code = request.form.get('code')
        account.description = request.form.get('description')
        account.account_type = request.form.get('account_type', 'income')
        db.session.commit()
        flash('Analytical Account updated successfully!', 'success')
        return redirect(url_for('admin.analytical_accounts_list'))
    return render_template('admin/analytical_account_form.html', account=account)

@bp.route('/auto-analytical-models')
@login_required
def auto_analytical_models_list():
    models = AutoAnalyticalModel.query.all()
    return render_template('admin/auto_analytical_models_list.html', models=models)

@bp.route('/auto-analytical-model/new', methods=['GET', 'POST'])
@login_required
def auto_analytical_model_new():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        vendor_name = request.form.get('vendor_name')
        analytical_account_name = request.form.get('analytical_account_name')
        
        model = AutoAnalyticalModel(
            product_name=product_name,
            vendor_name=vendor_name,
            analytical_account_name=analytical_account_name
        )
        db.session.add(model)
        db.session.commit()
        flash('Auto Analytical Model created successfully!', 'success')
        return redirect(url_for('admin.auto_analytical_models_list'))
    
    products = Product.query.all()
    vendors = Contact.query.all()
    analytical_accounts = AnalyticalAccount.query.all()
    return render_template('admin/auto_analytical_model_form.html', 
                           products=products, 
                           vendors=vendors, 
                           analytical_accounts=analytical_accounts)

@bp.route('/auto-analytical-model/delete/<int:id>')
@login_required
def auto_analytical_model_delete(id):
    model = AutoAnalyticalModel.query.get_or_404(id)
    db.session.delete(model)
    db.session.commit()
    flash('Model deleted successfully!', 'success')
    return redirect(url_for('admin.auto_analytical_models_list'))

@bp.route('/budgets')
@login_required
def budgets_list():
    budgets = Budget.query.filter_by(is_archived=False).all()
    return render_template('admin/budgets_list.html', budgets=budgets)

@bp.route('/budget/revised')
@login_required
def budget_revised():
    return render_template('admin/budget_vs_actual.html')

@bp.route('/budget/explanation')
@login_required
def budget_explanation():
    return render_template('admin/budget_achievement_lines.html')

@bp.route('/budget/new', methods=['GET', 'POST'])
@login_required
def budget_new():
    analytical_accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()
    if request.method == 'POST':
        budget = Budget(
            name=request.form.get('name'),
            period_start=request.form.get('period_start') or None,
            period_end=request.form.get('period_end') or None,
            analytical_account=request.form.get('analytical_account'),
            total_amount=request.form.get('total_amount'),
            description=request.form.get('description')
        )
        db.session.add(budget)
        db.session.commit()
        flash('Budget created successfully!', 'success')
        return redirect(url_for('admin.budgets_list'))
    return render_template('admin/budget_detail.html', budget=None, analytical_accounts=analytical_accounts)

@bp.route('/budget/<int:id>', methods=['GET', 'POST'])
@login_required
def budget_detail(id):
    budget = Budget.query.get_or_404(id)
    analytical_accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()
    if request.method == 'POST':
        budget.name = request.form.get('name')
        budget.period_start = request.form.get('period_start') or None
        budget.period_end = request.form.get('period_end') or None
        budget.analytical_account = request.form.get('analytical_account')
        budget.total_amount = request.form.get('total_amount')
        budget.description = request.form.get('description')
        db.session.commit()
        flash('Budget updated successfully!', 'success')
        return redirect(url_for('admin.budgets_list'))
    return render_template('admin/budget_detail.html', budget=budget, analytical_accounts=analytical_accounts)

@bp.route('/budget/revised')
@login_required
def budget_vs_actual():
    return render_template('admin/budget_vs_actual.html')

@bp.route('/budget/explanation')
@login_required
def budget_achievement_lines():
    return render_template('admin/budget_achievement_lines.html')

@bp.route('/purchase-orders')
@login_required
def po_list():
    purchase_orders = PurchaseOrder.query.filter_by(is_archived=False).all()
    return render_template('admin/po_list.html', purchase_orders=purchase_orders)

@bp.route('/purchase-order/new', methods=['GET', 'POST'])
@login_required
def po_new():
    vendors = Contact.query.filter_by(is_archived=False).all()
    analytical_accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()
    products = Product.query.filter_by(is_archived=False).all()
    
    # Generate next serial PO Number
    last_po = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).first()
    if last_po and last_po.order_number and last_po.order_number.startswith('PO'):
        try:
            last_num = int(last_po.order_number[2:])
            order_number = f"PO{last_num + 1:04d}"
        except ValueError:
            order_number = "PO0001"
    else:
        order_number = "PO0001"
        
    if request.method == 'POST':
        po = PurchaseOrder(
            order_number=request.form.get('order_number'),
            reference=request.form.get('reference'),
            vendor_name=request.form.get('vendor_name'),
            order_date=datetime.strptime(request.form.get('order_date'), '%Y-%m-%d').date() if request.form.get('order_date') else None,
            expected_delivery=datetime.strptime(request.form.get('expected_delivery'), '%Y-%m-%d').date() if request.form.get('expected_delivery') else None,
            status='draft',
            notes=request.form.get('notes'),
            total_amount=0.0
        )
        
        # Link Vendor User if email matches
        vendor_contact = Contact.query.filter_by(name=po.vendor_name).first()
        if vendor_contact and vendor_contact.email:
            vendor_user = Users.query.filter_by(email=vendor_contact.email, role='portal').first()
            if vendor_user:
                po.vendor_id = vendor_user.id

        db.session.add(po)
        db.session.flush() # Get PO ID
        
        # Handle Line Items
        line_products = request.form.getlist('product_name[]')
        line_analytics = request.form.getlist('budget_analytics[]')
        line_qtys = request.form.getlist('quantity[]')
        line_prices = request.form.getlist('unit_price[]')
        
        total_amount = 0.0
        for i in range(len(line_products)):
            if not line_products[i]: continue
            qty = float(line_qtys[i] or 0)
            price = float(line_prices[i] or 0)
            line_total = qty * price
            total_amount += line_total
            
            line = PurchaseOrderLine(
                po_id=po.id,
                product_name=line_products[i],
                budget_analytics=line_analytics[i],
                quantity=qty,
                unit_price=price,
                total=line_total
            )
            db.session.add(line)
            
        po.total_amount = total_amount
        db.session.commit()
        flash('Purchase Order created successfully!', 'success')
        return redirect(url_for('admin.po_list'))
        
    auto_models = AutoAnalyticalModel.query.filter_by(is_active=True).all()
    return render_template('admin/po_form.html', po=None, order_number=order_number, 
                           vendors=vendors, analytical_accounts=analytical_accounts, products=products,
                           auto_models=auto_models)

@bp.route('/purchase-order/<int:id>', methods=['GET', 'POST'])
@login_required
def po_detail(id):
    po = PurchaseOrder.query.get_or_404(id)
    vendors = Contact.query.filter_by(is_archived=False).all()
    analytical_accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()
    products = Product.query.filter_by(is_archived=False).all()

    if request.method == 'POST':
        # Update header
        po.reference = request.form.get('reference')
        po.vendor_name = request.form.get('vendor_name')
        po.order_date = datetime.strptime(request.form.get('order_date'), '%Y-%m-%d').date() if request.form.get('order_date') else None
        po.expected_delivery = datetime.strptime(request.form.get('expected_delivery'), '%Y-%m-%d').date() if request.form.get('expected_delivery') else None
        po.notes = request.form.get('notes')
        
        # Link/Relink Vendor User
        vendor_contact = Contact.query.filter_by(name=po.vendor_name).first()
        if vendor_contact and vendor_contact.email:
            vendor_user = Users.query.filter_by(email=vendor_contact.email, role='portal').first()
            if vendor_user:
                po.vendor_id = vendor_user.id
            else:
                po.vendor_id = None
        else:
            po.vendor_id = None
        
        # Clear existing lines and re-add
        PurchaseOrderLine.query.filter_by(po_id=po.id).delete()
        
        line_products = request.form.getlist('product_name[]')
        line_analytics = request.form.getlist('budget_analytics[]')
        line_qtys = request.form.getlist('quantity[]')
        line_prices = request.form.getlist('unit_price[]')
        
        total_amount = 0.0
        for i in range(len(line_products)):
            if not line_products[i]: continue
            qty = float(line_qtys[i] or 0)
            price = float(line_prices[i] or 0)
            line_total = qty * price
            total_amount += line_total
            
            line = PurchaseOrderLine(
                po_id=po.id,
                product_name=line_products[i],
                budget_analytics=line_analytics[i],
                quantity=qty,
                unit_price=price,
                total=line_total
            )
            db.session.add(line)
            
        po.total_amount = total_amount
        db.session.commit()
        flash('Purchase Order updated successfully!', 'success')
        return redirect(url_for('admin.po_list'))
        
    auto_models = AutoAnalyticalModel.query.filter_by(is_active=True).all()
    return render_template('admin/po_form.html', po=po, order_number=po.order_number, 
                           vendors=vendors, analytical_accounts=analytical_accounts, products=products,
                           auto_models=auto_models)

@bp.route('/purchase-order/<int:id>/status/<status>')
@login_required
def po_update_status(id, status):
    po = PurchaseOrder.query.get_or_404(id)
    if status in ['confirmed', 'cancelled', 'received', 'sent']:
        po.status = status
        db.session.commit()
        flash(f'Purchase Order {status} successfully!', 'success')
    return redirect(url_for('admin.po_detail', id=po.id))

@bp.route('/purchase-order/<int:id>/create-bill')
@login_required
def po_create_bill(id):
    po = PurchaseOrder.query.get_or_404(id)
    
    # Generate Bill Number
    last_bill = VendorBill.query.order_by(VendorBill.id.desc()).first()
    if last_bill and last_bill.bill_number and last_bill.bill_number.startswith('Bill'):
        try:
            last_num = int(last_bill.bill_number.split('/')[-1])
            bill_number = f"Bill/{datetime.now().year}/{last_num + 1:04d}"
        except (ValueError, IndexError):
            bill_number = f"Bill/{datetime.now().year}/0001"
    else:
        bill_number = f"Bill/{datetime.now().year}/0001"
        
    bill = VendorBill(
        bill_number=bill_number,
        vendor_name=po.vendor_name,
        bill_date=datetime.now().date(),
        reference=po.order_number,
        total_amount=po.total_amount,
        po_id=po.id,
        status='draft'
    )
    db.session.add(bill)
    db.session.flush()
    
    for line in po.lines:
        bill_line = VendorBillLine(
            bill_id=bill.id,
            product_name=line.product_name,
            budget_analytics=line.budget_analytics,
            quantity=line.quantity,
            unit_price=line.unit_price,
            total=line.total
        )
        db.session.add(bill_line)
        
    db.session.commit()
    flash('Vendor Bill created from Purchase Order!', 'success')
    return redirect(url_for('admin.vendor_bill_detail', id=bill.id))

@bp.route('/vendor-bills')
@login_required
def vendor_bills_list():
    bills = VendorBill.query.filter_by(is_archived=False).all()
    return render_template('admin/vendor_bills_list.html', bills=bills)

@bp.route('/vendor-bill/new', methods=['GET', 'POST'])
@login_required
def vendor_bill_new():
    # Similar to po_new but for bills
    return render_template('admin/vendor_bill_form.html', bill=None)

@bp.route('/vendor-bill/<int:id>', methods=['GET', 'POST'])
@login_required
def vendor_bill_detail(id):
    bill = VendorBill.query.get_or_404(id)
    if request.method == 'POST':
        # Logic to update bill if needed
        pass
    return render_template('admin/vendor_bill_form.html', bill=bill)

@bp.route('/vendor-bill/payment/<int:id>', methods=['GET', 'POST'])
@login_required
def payment_detail(id):
    return render_template('admin/vendor_bill_detail.html')

@bp.route('/payments')
@login_required
def payments_list():
    return render_template('admin/payments_list.html')

@bp.route('/invoices')
@login_required
def invoices_list():
    return render_template('admin/invoices_list.html')

@bp.route('/invoice/new', methods=['GET', 'POST'])
@login_required
def invoice_new():
    return render_template('admin/invoice_detail.html')

@bp.route('/invoice/<int:id>', methods=['GET', 'POST'])
@login_required
def invoice_detail(id):
    return render_template('admin/invoice_detail.html')

@bp.route('/invoice/pay/<int:id>', methods=['GET', 'POST'])
@login_required
def invoice_pay(id):
    return render_template('admin/invoice_pay.html')

@bp.route('/sale-orders')
@login_required
def so_list():
    sale_orders = SaleOrder.query.filter_by(is_archived=False).all()
    return render_template('admin/so_list.html', sale_orders=sale_orders)

@bp.route('/sale-order/new', methods=['GET', 'POST'])
@login_required
def so_new():
    customers = Users.query.filter_by(role='portal').all()
    products = Product.query.filter_by(is_archived=False).all()
    analytical_accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()
    
    # Generate next serial SO Number
    last_so = SaleOrder.query.order_by(SaleOrder.id.desc()).first()
    if last_so and last_so.order_number and last_so.order_number.startswith('SO'):
        try:
            last_num = int(last_so.order_number[2:])
            order_number = f"SO{last_num + 1:04d}"
        except ValueError:
            order_number = "SO0001"
    else:
        order_number = "SO0001"
        
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        customer = Users.query.get(customer_id)
        
        so = SaleOrder(
            order_number=request.form.get('order_number'),
            customer_id=customer_id,
            customer_name=customer.name or customer.username,
            order_date=datetime.strptime(request.form.get('order_date'), '%Y-%m-%d').date() if request.form.get('order_date') else None,
            status='draft',
            notes=request.form.get('notes'),
            total_amount=0.0
        )
        db.session.add(so)
        db.session.flush()
        
        # Handle Line Items
        line_products = request.form.getlist('product_name[]')
        line_analytics = request.form.getlist('budget_analytics[]')
        line_qtys = request.form.getlist('quantity[]')
        line_prices = request.form.getlist('unit_price[]')
        
        total_amount = 0.0
        for i in range(len(line_products)):
            if not line_products[i]: continue
            qty = float(line_qtys[i] or 0)
            price = float(line_prices[i] or 0)
            line_total = qty * price
            total_amount += line_total
            
            line = SaleOrderLine(
                so_id=so.id,
                product_name=line_products[i],
                budget_analytics=line_analytics[i] if i < len(line_analytics) else None,
                quantity=qty,
                unit_price=price,
                total=line_total
            )
            db.session.add(line)
            
        so.total_amount = total_amount
        db.session.commit()
        flash('Sale Order created successfully!', 'success')
        return redirect(url_for('admin.so_list'))
        
    return render_template('admin/so_form.html', so=None, order_number=order_number, 
                           customers=customers, products=products, analytical_accounts=analytical_accounts)

@bp.route('/sale-order/<int:id>', methods=['GET', 'POST'])
@login_required
def so_detail(id):
    so = SaleOrder.query.get_or_404(id)
    customers = Users.query.filter_by(role='portal').all()
    products = Product.query.filter_by(is_archived=False).all()
    analytical_accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()

    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        customer = Users.query.get(customer_id)
        
        so.customer_id = customer_id
        so.customer_name = customer.name or customer.username
        so.order_date = datetime.strptime(request.form.get('order_date'), '%Y-%m-%d').date() if request.form.get('order_date') else None
        so.notes = request.form.get('notes')
        
        # Clear existing lines and re-add
        SaleOrderLine.query.filter_by(so_id=so.id).delete()
        
        line_products = request.form.getlist('product_name[]')
        line_analytics = request.form.getlist('budget_analytics[]')
        line_qtys = request.form.getlist('quantity[]')
        line_prices = request.form.getlist('unit_price[]')
        
        total_amount = 0.0
        for i in range(len(line_products)):
            if not line_products[i]: continue
            qty = float(line_qtys[i] or 0)
            price = float(line_prices[i] or 0)
            line_total = qty * price
            total_amount += line_total
            
            line = SaleOrderLine(
                so_id=so.id,
                product_name=line_products[i],
                budget_analytics=line_analytics[i] if i < len(line_analytics) else None,
                quantity=qty,
                unit_price=price,
                total=line_total
            )
            db.session.add(line)
            
        so.total_amount = total_amount
        db.session.commit()
        flash('Sale Order updated successfully!', 'success')
        return redirect(url_for('admin.so_list'))
        
    return render_template('admin/so_form.html', so=so, order_number=so.order_number, 
                           customers=customers, products=products, analytical_accounts=analytical_accounts)

@bp.route('/sale-order/<int:id>/send')
@login_required
def so_send(id):
    so = SaleOrder.query.get_or_404(id)
    
    # Check if already sent to avoid duplicate invoices
    if so.status == 'sent':
        flash('Sale Order already sent!', 'warning')
        return redirect(url_for('admin.so_detail', id=so.id))
        
    # Generate Invoice from SO
    # Generate next serial Invoice Number
    last_inv = Invoice.query.order_by(Invoice.id.desc()).first()
    if last_inv and last_inv.invoice_number and last_inv.invoice_number.startswith('INV'):
        try:
            last_num = int(last_inv.invoice_number[4:])
            invoice_number = f"INV-{last_num + 1:04d}"
        except ValueError:
            invoice_number = f"INV-{len(Invoice.query.all()) + 1:04d}"
    else:
        invoice_number = "INV-0001"

    invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=so.customer_id,
        customer_name=so.customer_name,
        invoice_date=datetime.utcnow().date(),
        due_date=datetime.utcnow().date(), # Default to today, can be changed
        subtotal=so.total_amount,
        tax_amount=0.0,
        total_amount=so.total_amount,
        paid_amount=0.0,
        balance_due=so.total_amount,
        status='sent',
        notes=f"Generated from Sale Order {so.order_number}"
    )
    db.session.add(invoice)
    db.session.flush()
    
    # Add Invoice Lines
    for so_line in so.lines:
        inv_line = InvoiceLine(
            invoice_id=invoice.id,
            product_name=so_line.product_name,
            quantity=so_line.quantity,
            unit_price=so_line.unit_price,
            total=so_line.total
        )
        db.session.add(inv_line)
        
    so.status = 'sent'
    db.session.commit()
    
    flash(f'Sale Order sent successfully! Invoice {invoice_number} generated.', 'success')
    return redirect(url_for('admin.so_detail', id=so.id))
