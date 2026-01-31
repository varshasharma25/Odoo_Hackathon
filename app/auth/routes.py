from app.auth import bp

@bp.route('/login')
def login():
    return "Login Page"

@bp.route('/logout')
def logout():
    return "Logout Page"
