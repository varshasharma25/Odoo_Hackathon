from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app import db
from app.models import Users

@bp.route('/forgot-password')
def forgot_password():
    return render_template('auth/forgot_password.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and current_user.is_authenticated:
        logout_user()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Users.query.filter_by(username=username).first()
        
        if not user:
            flash('Please create your new user account first.', 'warning')
            return redirect(url_for('auth.create_user'))
            
        if user and user.check_password(password):
            login_user(user)
            # Role-based redirection
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('portal.home'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    return redirect(url_for('auth.create_user'))

@bp.route('/create-user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form.get('login_id')
        email = request.form.get('email_id')
        name = request.form.get('name')
        password = request.form.get('password')
        re_password = request.form.get('re_password')
        role = request.form.get('role', 'portal')

        if password != re_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/create_user.html')

        if Users.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('auth/create_user.html')

        user = Users(username=username, email=email, name=name, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Auto-login after successful creation
        login_user(user)
        flash(f'Account created for {name}! Welcome to Shiv Furniture.', 'success')
        
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('portal.home'))
        
    return render_template('auth/create_user.html')
