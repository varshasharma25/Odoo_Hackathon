from flask import render_template
from app.admin import bp

@bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/contacts')
def contacts_list():
    return render_template('admin/contacts_list.html')

@bp.route('/contact/new', methods=['GET', 'POST'])
def contact_new():
    return render_template('admin/contact_form.html')

@bp.route('/contact/<int:id>', methods=['GET', 'POST'])
def contact_detail(id):
    return render_template('admin/contact_form.html')

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
