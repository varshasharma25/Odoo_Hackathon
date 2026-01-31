from flask import render_template
from app.auth import bp

@bp.route('/forgot-password')
def forgot_password():
    return "Forgot Password Page"

@bp.route('/login')
def login():
    return render_template('auth/login.html')

@bp.route('/signup')
def signup():
    return render_template('auth/signup.html')

@bp.route('/create-user')
def create_user():
    return render_template('auth/create_user.html')
