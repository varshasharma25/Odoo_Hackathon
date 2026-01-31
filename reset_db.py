"""
Reset database - drop all tables and recreate them
"""
from app import create_app, db
from sqlalchemy import text

def reset_database():
    app = create_app()
    
    with app.app_context():
        print("Dropping all tables...")
        # Use raw SQL to drop all tables with CASCADE
        db.session.execute(text("DROP SCHEMA public CASCADE"))
        db.session.execute(text("CREATE SCHEMA public"))
        db.session.commit()
        print("✓ All tables dropped")
        
        print("\nCreating tables with correct schema...")
        db.create_all()
        print("✓ Tables created successfully!")
        
        print("\nDatabase reset complete!")
        print("Now run: python init_db.py to add sample data")

if __name__ == '__main__':
    reset_database()
