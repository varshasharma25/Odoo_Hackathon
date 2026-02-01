from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.portal import bp
from app import db
from app.models import PurchaseOrder, PurchaseOrderLine, Contact, Product, AnalyticalAccount, Invoice, Users, SaleOrder, VendorBill, SaleOrderLine
from datetime import datetime

@bp.route('/')
def index():
    return render_template('admin/layout.html')

@bp.route('/home')
@login_required
def home():
    # Get invoice statistics for the user
    total_invoices = Invoice.query.filter_by(customer_id=current_user.id, is_archived=False).count()
    paid_invoices = Invoice.query.filter_by(customer_id=current_user.id, status='paid', is_archived=False).count()
    unpaid_invoices = Invoice.query.filter_by(customer_id=current_user.id, is_archived=False).filter(Invoice.status.in_(['sent', 'partial', 'overdue'])).count()
    
    total_amount_due = db.session.query(db.func.sum(Invoice.balance_due)).filter_by(customer_id=current_user.id, is_archived=False).scalar() or 0
    total_payments_made = db.session.query(db.func.sum(Invoice.paid_amount)).filter_by(customer_id=current_user.id, is_archived=False).scalar() or 0
    
    # Financials for Vendor Perspective
    # Pending Payments: Amount Admin owes to this vendor (Unpaid Bills)
    pending_vendor_payments = db.session.query(db.func.sum(VendorBill.total_amount - VendorBill.amount_paid)).filter_by(vendor_id=current_user.id, is_archived=False).filter(VendorBill.payment_status != 'paid').scalar() or 0
    # Total Sales: Total amount of bills sent by this vendor
    total_vendor_sales = db.session.query(db.func.sum(VendorBill.total_amount)).filter_by(vendor_id=current_user.id, is_archived=False).scalar() or 0
    
    # Active orders from SaleOrder model (Customer perspective)
    active_sale_orders = SaleOrder.query.filter_by(customer_id=current_user.id, status='sent', is_archived=False).count()
    # Received POs (Vendor perspective) - Only 'sent' or 'received' status
    new_purchase_orders = PurchaseOrder.query.filter_by(vendor_id=current_user.id, is_archived=False).filter(PurchaseOrder.status.in_(['sent'])).count()
    
    return render_template('portal/user.html', 
                         total_invoices=total_invoices,
                         paid_invoices=paid_invoices,
                         unpaid_invoices=unpaid_invoices,
                         total_amount_due=total_amount_due,
                         total_payments_made=total_payments_made,
                         active_orders=active_sale_orders,
                         pending_vendor_payments=pending_vendor_payments,
                         total_vendor_sales=total_vendor_sales,
                         new_purchase_orders=new_purchase_orders)

@bp.route('/invoices')
@login_required
def invoices_list():
    # Get all invoices for the current user (lifetime)
    invoices = Invoice.query.filter_by(customer_id=current_user.id, is_archived=False).order_by(Invoice.invoice_date.desc()).all()
    
    # Calculate summary statistics
    total_invoices = len(invoices)
    paid_count = sum(1 for inv in invoices if inv.status == 'paid')
    unpaid_count = sum(1 for inv in invoices if inv.status in ['sent', 'partial', 'overdue'])
    total_amount = sum(inv.total_amount for inv in invoices)
    total_paid = sum(inv.paid_amount for inv in invoices)
    total_due = sum(inv.balance_due for inv in invoices)
    
    return render_template('portal/invoice_list.html', 
                         invoices=invoices,
                         total_invoices=total_invoices,
                         paid_count=paid_count,
                         unpaid_count=unpaid_count,
                         total_amount=total_amount,
                         total_paid=total_paid,
                         total_due=total_due)

@bp.route('/invoice/<int:invoice_id>')
@login_required
def invoice_detail(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, customer_id=current_user.id).first_or_404()
    return render_template('portal/invoice_detail.html', invoice=invoice)

@bp.route('/orders')
@login_required
def so_list():
    # Get all sale orders for the current user (Purchases from their perspective)
    orders = SaleOrder.query.filter_by(customer_id=current_user.id, is_archived=False).order_by(SaleOrder.order_date.desc()).all()
    return render_template('portal/so_list.html', orders=orders)

@bp.route('/invoice/<int:invoice_id>/pay')
@login_required
def invoice_pay(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, customer_id=current_user.id).first_or_404()
    return render_template('portal/invoice_pay.html', invoice=invoice)

@bp.route('/payments')
@login_required
def payment_history():
    # Get all paid invoices as payment history
    paid_invoices = Invoice.query.filter_by(customer_id=current_user.id, is_archived=False).filter(Invoice.paid_amount > 0).order_by(Invoice.updated_at.desc()).all()
    return render_template('portal/payment.html', payments=paid_invoices)

# --- Purchase Draft Routes ---

@bp.route('/purchase-orders')
@login_required
def po_list():
    # Show POs where this user is either the creator (Portal Drafts) -> Only Drafts
    draft_pos = PurchaseOrder.query.filter_by(user_id=current_user.id, is_archived=False, status='draft').all()
    # Vendor sees orders only when they are SENT by Admin
    received_pos = PurchaseOrder.query.filter_by(vendor_id=current_user.id, is_archived=False).filter(PurchaseOrder.status.in_(['sent', 'received'])).all()
    return render_template('portal/po_list.html', draft_pos=draft_pos, received_pos=received_pos)

@bp.route('/purchase-order/new', methods=['GET', 'POST'])
@login_required
def po_new():
    vendors = Contact.query.filter_by(is_archived=False).all()
    analytical_accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()
    products = Product.query.filter_by(is_archived=False).all()
    
    if request.method == 'POST':
        # Generate next serial PO Number (prefixed with P- for Portal Draft)
        last_po = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).first()
        if last_po and last_po.order_number and last_po.order_number.startswith('PPO'):
            try:
                last_num = int(last_po.order_number[3:])
                order_number = f"PPO{last_num + 1:04d}"
            except ValueError:
                order_number = "PPO0001"
        else:
            order_number = "PPO0001"

        po = PurchaseOrder(
            order_number=order_number,
            reference=request.form.get('reference'),
            vendor_name=request.form.get('vendor_name'),
            order_date=datetime.strptime(request.form.get('order_date'), '%Y-%m-%d').date() if request.form.get('order_date') else None,
            expected_delivery=datetime.strptime(request.form.get('expected_delivery'), '%Y-%m-%d').date() if request.form.get('expected_delivery') else None,
            status='draft',
            notes=request.form.get('notes'),
            total_amount=0.0,
            user_id=current_user.id
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
        flash('Purchase Draft created successfully and sent for review!', 'success')
        return redirect(url_for('portal.po_list'))
        
    return render_template('portal/po_form.html', po=None, 
                           vendors=vendors, analytical_accounts=analytical_accounts, products=products)

@bp.route('/purchase-order/<int:id>', methods=['GET'])
@login_required
def po_detail(id):
    # Check if the user is the creator or the vendor
    po = PurchaseOrder.query.filter(
        (PurchaseOrder.id == id) & 
        ((PurchaseOrder.user_id == current_user.id) | (PurchaseOrder.vendor_id == current_user.id))
    ).first_or_404()
    
    # If the user is the vendor, show the read-only view with "Accept" button
    if po.vendor_id == current_user.id:
        return render_template('portal/po_detail.html', po=po)
    
    # Otherwise show the draft form (existing po_form.html)
    return render_template('portal/po_form.html', po=po)


@bp.route('/purchase-order/<int:id>/accept')
@login_required
def po_accept(id):
    po = PurchaseOrder.query.filter_by(id=id, vendor_id=current_user.id).first_or_404()
    
    if po.status != 'sent':
        flash('Only SENT Purchase Orders can be accepted.', 'warning')
        return redirect(url_for('portal.po_detail', id=po.id))
        
    # Generate Vendor Bill for Admin
    last_bill = VendorBill.query.order_by(VendorBill.id.desc()).first()
    if last_bill and last_bill.bill_number and last_bill.bill_number.startswith('Bill'):
        try:
            last_num = int(last_bill.bill_number.split('/')[-1])
            bill_number = f"Bill/{po.order_number}/{last_num + 1:04d}"
        except (ValueError, IndexError):
            bill_number = f"Bill/{po.order_number}/0001"
    else:
        bill_number = f"Bill/{po.order_number}/0001"
        
    bill = VendorBill(
        bill_number=bill_number,
        vendor_name=current_user.name or current_user.username,
        vendor_id=current_user.id,
        bill_date=datetime.now().date(),
        reference=po.order_number,
        total_amount=po.total_amount,
        po_id=po.id,
        status='confirmed' # Automatically confirmed since it's from an accepted PO
    )
    db.session.add(bill)
    db.session.flush()
    
    from app.models import VendorBillLine
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
        
    po.status = 'received' # Admin marks as received/processed
    db.session.commit()
    
    flash(f'Purchase Order {po.order_number} accepted! Bill {bill_number} has been sent to Admin.', 'success')
    return redirect(url_for('portal.po_list'))

# --- Sales Draft Routes ---

@bp.route('/sales-orders')
@login_required
def sales_orders_list():
    # Show sales orders where the current user is the customer
    sales_orders = SaleOrder.query.filter_by(customer_id=current_user.id, is_archived=False).order_by(SaleOrder.order_date.desc()).all()
    return render_template('portal/so_form_list.html', sales_orders=sales_orders)

@bp.route('/sale-order/new', methods=['GET', 'POST'])
@login_required
def so_new():
    products = Product.query.filter_by(is_archived=False).all()
    analytical_accounts = AnalyticalAccount.query.filter_by(is_archived=False).all()
    
    if request.method == 'POST':
        # Generate next serial SO Number (prefixed with PSO for Portal Sale Order)
        last_so = SaleOrder.query.filter(SaleOrder.order_number.like('PSO%')).order_by(SaleOrder.id.desc()).first()
        if last_so and last_so.order_number and last_so.order_number.startswith('PSO'):
            try:
                last_num = int(last_so.order_number[3:])
                order_number = f"PSO{last_num + 1:04d}"
            except ValueError:
                order_number = "PSO0001"
        else:
            order_number = "PSO0001"

        so = SaleOrder(
            order_number=order_number,
            customer_id=current_user.id,
            customer_name=current_user.name or current_user.username,
            order_date=datetime.strptime(request.form.get('order_date'), '%Y-%m-%d').date() if request.form.get('order_date') else datetime.now().date(),
            status='draft',
            notes=request.form.get('notes'),
            total_amount=0.0
        )
        db.session.add(so)
        db.session.flush() # Get SO ID
        
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
        flash('Sales Draft created successfully and sent for review!', 'success')
        return redirect(url_for('portal.sales_orders_list'))
        
    return render_template('portal/so_form_create.html', so=None, 
                           products=products, analytical_accounts=analytical_accounts)

@bp.route('/sale-order/<int:id>', methods=['GET'])
@login_required
def so_detail(id):
    so = SaleOrder.query.filter_by(id=id, customer_id=current_user.id).first_or_404()
    return render_template('portal/so_form_detail.html', so=so)
