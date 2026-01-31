from app import create_app, db
from sqlalchemy import text

def check_schema():
    app = create_app()
    with app.app_context():
        print("Checking tables in database...")
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        for row in result:
            print(f"Table: {row[0]}")
            
        print("\nChecking columns for 'products' table...")
        result = db.session.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'products' AND table_schema = 'public'"))
        for row in result:
            print(f"Column: {row[0]} ({row[1]})")

if __name__ == '__main__':
    check_schema()
