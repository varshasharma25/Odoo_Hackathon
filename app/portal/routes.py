from flask import render_template
from app.portal import bp

@bp.route('/')
def index():
    return render_template('layout.html')

@bp.route('/home')
def home():
    return render_template('portal/home.html')

@bp.route('/invoices')
def invoices_list():
    return render_template('admin/invoices_list.html')

@bp.route('/orders')
def so_list():
    return render_template('admin/so_list.html')

@bp.route('/invoice/<int:invoice_id>')
def invoice_detail(invoice_id):
    return "Invoice Detail Page"

@bp.route('/invoice/<int:invoice_id>/pay')
def invoice_pay(invoice_id):
    return "Invoice Payment Page"
