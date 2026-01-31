from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.admin import bp
from app import db
from app.models import Contact, Product, Budget, AnalyticalAccount, PurchaseOrder

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
        contact = Contact(
            name=request.form.get('name'),
            email=request.form.get('email'), 
            phone=request.form.get('phone'),
            company=request.form.get('company'),
            address=request.form.get('address')
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
def budget_revised():
    return render_template('admin/budget_vs_actual.html')

@bp.route('/budget/explanation')
def budget_explanation():
    return render_template('admin/budget_achievement_lines.html')

@bp.route('/purchase-orders')
def po_list():
    purchase_orders = PurchaseOrder.query.filter_by(is_archived=False).all()
    return render_template('admin/po_list.html', purchase_orders=purchase_orders)

@bp.route('/purchase-order/new', methods=['GET', 'POST'])
def po_new():
    if request.method == 'POST':
        po = PurchaseOrder(
            order_number=request.form.get('order_number'),
            vendor_name=request.form.get('vendor_name'),
            order_date=request.form.get('order_date'),
            expected_delivery=request.form.get('expected_delivery'),
            total_amount=request.form.get('total_amount'),
            status=request.form.get('status', 'draft'),
            notes=request.form.get('notes')
        )
        db.session.add(po)
        db.session.commit()
        flash('Purchase Order created successfully!', 'success')
        return redirect(url_for('admin.po_list'))
    return render_template('admin/po_form.html', po=None)

@bp.route('/purchase-order/<int:id>', methods=['GET', 'POST'])
def po_detail(id):
    po = PurchaseOrder.query.get_or_404(id)
    if request.method == 'POST':
        po.order_number = request.form.get('order_number')
        po.vendor_name = request.form.get('vendor_name')
        po.order_date = request.form.get('order_date')
        po.expected_delivery = request.form.get('expected_delivery')
        po.total_amount = request.form.get('total_amount')
        po.status = request.form.get('status')
        po.notes = request.form.get('notes')
        db.session.commit()
        flash('Purchase Order updated successfully!', 'success')
        return redirect(url_for('admin.po_list'))
    return render_template('admin/po_form.html', po=po)

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
