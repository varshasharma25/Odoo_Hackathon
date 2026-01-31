from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from app.admin import bp
from app import db
from app.models import Contact, Product, Budget, AnalyticalAccount, PurchaseOrder, PurchaseOrderLine

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
    return render_template('admin/dashboard.html')

@bp.route('/contacts')
@login_required
def contacts_list():
    contacts = Contact.query.filter_by(is_archived=False).all()
    return render_template('admin/contacts_list.html', contacts=contacts)

@bp.route('/contact/new', methods=['GET', 'POST'])
@login_required
def contact_new():
    if request.method == 'POST':
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            saved_path = save_image(file)
            if saved_path:
                image_url = saved_path

        contact = Contact(
            name=request.form.get('name'),
            email=request.form.get('email'), 
            phone=request.form.get('phone'),
            company=request.form.get('company'),
            address=request.form.get('address'),
            image_url=image_url
        )
        db.session.add(contact)
        db.session.commit()
        flash('Contact created successfully!', 'success')
        return redirect(url_for('admin.contacts_list'))
    return render_template('admin/contact_form.html', contact=None)

@bp.route('/contact/<int:id>', methods=['GET', 'POST'])
@login_required
def contact_detail(id):
    contact = Contact.query.get_or_404(id)
    if request.method == 'POST':
        contact.name = request.form.get('name')
        contact.email = request.form.get('email')
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
    return render_template('admin/contact_form.html', contact=contact)



@bp.route('/products')
@login_required
def products_list():
    products = Product.query.filter_by(is_archived=False).all()
    return render_template('admin/products_list.html', products=products)

@bp.route('/product/new', methods=['GET', 'POST'])
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
def analytical_accounts_list():
    accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()
    return render_template('admin/analytical_accounts_list.html', accounts=accounts)

@bp.route('/analytical-account/new', methods=['GET', 'POST'])
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

@bp.route('/budgets')
def budgets_list():
    budgets = Budget.query.filter_by(is_archived=False).all()
    return render_template('admin/budgets_list.html', budgets=budgets)

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
def budget_vs_actual():
    return render_template('admin/budget_vs_actual.html')

@bp.route('/budget/explanation')
def budget_achievement_lines():
    return render_template('admin/budget_achievement_lines.html')

@bp.route('/purchase-orders')
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
        
    return render_template('admin/po_form.html', po=None, order_number=order_number, 
                           vendors=vendors, analytical_accounts=analytical_accounts, products=products)

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
        
    return render_template('admin/po_form.html', po=po, order_number=po.order_number, 
                           vendors=vendors, analytical_accounts=analytical_accounts, products=products)

@bp.route('/purchase-order/<int:id>/status/<status>')
@login_required
def po_update_status(id, status):
    po = PurchaseOrder.query.get_or_404(id)
    if status in ['confirmed', 'cancelled', 'received']:
        po.status = status
        db.session.commit()
        flash(f'Purchase Order {status} successfully!', 'success')
    return redirect(url_for('admin.po_detail', id=po.id))

@bp.route('/vendor-bills')
def vendor_bills_list():
    return render_template('admin/vendor_bills_list.html')

@bp.route('/vendor-bill/new', methods=['GET', 'POST'])
def vendor_bill_new():
    return render_template('admin/vendor_bill_form.html')

@bp.route('/vendor-bill/<int:id>', methods=['GET', 'POST'])
def vendor_bill_detail(id):
    return render_template('admin/vendor_bill_form.html')

@bp.route('/vendor-bill/payment/<int:id>', methods=['GET', 'POST'])
def payment_detail(id):
    return render_template('admin/vendor_bill_detail.html')

@bp.route('/payments')
def payments_list():
    return render_template('admin/payments_list.html')

@bp.route('/invoices')
def invoices_list():
    return render_template('admin/invoices_list.html')

@bp.route('/invoice/new', methods=['GET', 'POST'])
def invoice_new():
    return render_template('admin/invoice_detail.html')

@bp.route('/invoice/<int:id>', methods=['GET', 'POST'])
def invoice_detail(id):
    return render_template('admin/invoice_detail.html')

@bp.route('/invoice/pay/<int:id>', methods=['GET', 'POST'])
def invoice_pay(id):
    return render_template('admin/invoice_pay.html')

@bp.route('/sale-orders')
def so_list():
    return render_template('admin/so_list.html')

@bp.route('/sale-order/new', methods=['GET', 'POST'])
def so_new():
    return render_template('admin/so_form.html')

@bp.route('/sale-order/<int:id>', methods=['GET', 'POST'])
def so_detail(id):
    return render_template('admin/so_form.html')
