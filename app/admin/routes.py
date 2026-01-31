from flask import render_template, request, redirect, url_for, flash
from app.admin import bp
from app import db
from app.models import Contact, Product

@bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/contacts')
def contacts_list():
    contacts = Contact.query.filter_by(is_archived=False).all()
    return render_template('admin/contacts_list.html', contacts=contacts)

@bp.route('/contact/new', methods=['GET', 'POST'])
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
def products_list():
    return render_template('admin/products_list.html')

@bp.route('/product/new', methods=['GET', 'POST'])
def product_new():
    return render_template('admin/product_form.html')

@bp.route('/product/<int:id>', methods=['GET', 'POST'])
def product_detail(id):
    return render_template('admin/product_form.html')

@bp.route('/analytical-accounts')
def analytical_accounts_list():
    return render_template('admin/analytical_accounts_list.html')

@bp.route('/analytical-account/new', methods=['GET', 'POST'])
def analytical_account_new():
    return render_template('admin/analytical_account_form.html')

@bp.route('/analytical-account/<int:id>', methods=['GET', 'POST'])
def analytical_account_detail(id):
    return render_template('admin/analytical_account_form.html')

@bp.route('/budgets')
def budgets_list():
    return render_template('admin/budgets_list.html')

@bp.route('/budget/new', methods=['GET', 'POST'])
def budget_new():
    return render_template('admin/budget_detail.html')

@bp.route('/budget/<int:id>', methods=['GET', 'POST'])
def budget_detail(id):
    return render_template('admin/budget_detail.html')

@bp.route('/budget/revised')
def budget_revised():
    return render_template('admin/budget_vs_actual.html')

@bp.route('/budget/explanation')
def budget_explanation():
    return render_template('admin/budget_achievement_lines.html')

@bp.route('/purchase-orders')
def po_list():
    return render_template('admin/po_list.html')

@bp.route('/purchase-order/new', methods=['GET', 'POST'])
def po_new():
    return render_template('admin/po_form.html')

@bp.route('/purchase-order/<int:id>', methods=['GET', 'POST'])
def po_detail(id):
    return render_template('admin/po_form.html')

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
