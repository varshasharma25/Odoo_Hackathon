from app.portal import bp

@bp.route('/')
def index():
    return "Portal Home"
