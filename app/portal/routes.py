from flask import render_template
from app.portal import bp

@bp.route('/')
@bp.route('/home')
def home():
    return render_template('portal/user.html')

@bp.route('/invoices')
def invoices_list():
    return render_template('portal/invoice_list.html')

@bp.route('/orders')
def so_list():
    return render_template('portal/so_list.html')

@bp.route('/invoice/<int:invoice_id>')
def invoice_detail(invoice_id):
    return render_template('portal/invoice_detail.html', invoice_id=invoice_id)

@bp.route('/invoice/<int:invoice_id>/pay')
def invoice_pay(invoice_id):
    return render_template('portal/invoice_pay.html', invoice_id=invoice_id)
@bp.route('/payments')
def payment_history():
    return render_template('portal/payment.html')
