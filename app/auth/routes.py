from flask import render_template, request, redirect, url_for
from app.auth import bp

@bp.route('/forgot-password')
def forgot_password():
    return "Forgot Password Page"

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('portal.home'))
    return render_template('auth/login.html')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect(url_for('portal.home'))
    return render_template('auth/signup.html')

@bp.route('/auth/create-user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        return redirect(url_for('portal.home'))
    return render_template('auth/create_user.html')
