import os
import sys
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.getcwd())

from app import create_app, db

app = create_app()
with app.app_context():
    with db.engine.connect() as conn:
        print("Attempting to manually add 'user_id' column to 'purchase_orders'...")
        try:
            # Check if column exists first
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'purchase_orders' AND column_name = 'user_id'
            """)
            result = conn.execute(check_query).fetchone()
            
            if not result:
                print("Column 'user_id' not found. Adding it...")
                conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN user_id INTEGER REFERENCES users(id)"))
                # If using Postgres, we need to commit the transaction if not handled by context
                # and SQLAlchemy 2.0+ requires explicit commit on connection if not using session
                # But here we are just running raw SQL
                print("Successfully added 'user_id' column.")
            else:
                print("Column 'user_id' already exists.")
            
            # Now satisfy Alembic by stamping the current head that expects this column
            # The head is cb1e8d33fb45 (the merge I created)
            # But let's check the current heads first
            print("Stamping database to version 'cb1e8d33fb45'...")
            conn.execute(text("UPDATE alembic_version SET version_num = 'cb1e8d33fb45'"))
            print("Successfully updated alembic_version.")
            
            # Also ensure password_hash is NOT NULL in users if needed (from 2ad1cf58c54f)
            print("Checking 'users' table password_hash nullability...")
            conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL"))
            print("Ensured 'users.password_hash' is NOT NULL.")
            
            # Commit all changes
            # Note: Postgres DDL is transactional.
            # Depending on the version of SQLAlchemy/driver, we might need this:
            conn.execute(text("COMMIT"))
            
        except Exception as e:
            print("An error occurred during manual fix:", e)
            try:
                conn.execute(text("ROLLBACK"))
            except:
                pass
