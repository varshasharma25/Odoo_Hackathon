from app import create_app, db
from app.models import AutoAnalyticalModel  # Verify import works

app = create_app()

with app.app_context():
    print("Updating database schema...")
    # This creates any tables that don't exist, leaving existing ones valid
    db.create_all()
    print("Database schema updated successfully!")
    print("Created 'auto_analytical_models' table if it was missing.")
