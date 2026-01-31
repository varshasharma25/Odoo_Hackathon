from app.admin import bp

@bp.route('/dashboard')
def dashboard():
    return "Admin Dashboard"
