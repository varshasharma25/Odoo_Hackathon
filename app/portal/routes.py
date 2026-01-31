from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.portal import bp
from app import db
from app.models import PurchaseOrder, PurchaseOrderLine, Contact, Product, AnalyticalAccount
from datetime import datetime

@bp.route('/')
def index():
    return render_template('admin/layout.html')

@bp.route('/home')
@login_required
def home():
    return render_template('portal/user.html')

@bp.route('/invoices')
@login_required
def invoices_list():
    return render_template('portal/invoice_list.html')

@bp.route('/orders')
@login_required
def so_list():
    return render_template('portal/so_list.html')

@bp.route('/invoice/<int:invoice_id>')
@login_required
def invoice_detail(invoice_id):
    return render_template('portal/invoice_detail.html', invoice_id=invoice_id)

@bp.route('/invoice/<int:invoice_id>/pay')
@login_required
def invoice_pay(invoice_id):
    return render_template('portal/invoice_pay.html', invoice_id=invoice_id)

@bp.route('/payments')
@login_required
def payment_history():
    return render_template('portal/payment.html')

# --- Purchase Draft Routes ---

@bp.route('/purchase-orders')
@login_required
def po_list():
    # Only show POs created by the current user
    purchase_orders = PurchaseOrder.query.filter_by(user_id=current_user.id, is_archived=False).all()
    return render_template('portal/po_list.html', purchase_orders=purchase_orders)

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
    po = PurchaseOrder.query.filter_by(id=id, user_id=current_user.id).get_or_404(id)
    return render_template('portal/po_form.html', po=po)
