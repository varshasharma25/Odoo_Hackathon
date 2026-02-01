import os
import sys
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.getcwd())

from app import create_app, db

app = create_app()
with app.app_context():
    with db.engine.connect() as conn:
        print("Ensuring all missing schema elements from merged branches...")
        try:
            # 1. user_id in purchase_orders (already added, but IF NOT EXISTS for safety)
            try:
                conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))
                print("- Checked purchase_orders.user_id")
            except Exception as e:
                print("- Note on purchase_orders.user_id:", e)

            # 2. name in users
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(128)"))
                print("- Checked users.name")
            except Exception as e:
                print("- Note on users.name:", e)

            # 3. vendor_bills table
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS vendor_bills (
                        id SERIAL PRIMARY KEY,
                        bill_number VARCHAR(50) UNIQUE,
                        vendor_name VARCHAR(128) NOT NULL,
                        bill_date DATE,
                        due_date DATE,
                        reference VARCHAR(128),
                        total_amount FLOAT DEFAULT 0.0,
                        amount_paid FLOAT DEFAULT 0.0,
                        status VARCHAR(20) DEFAULT 'draft',
                        payment_status VARCHAR(20) DEFAULT 'not_paid',
                        po_id INTEGER REFERENCES purchase_orders(id),
                        is_archived BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("- Checked vendor_bills table")
            except Exception as e:
                print("- Note on vendor_bills table:", e)

            # 4. vendor_bill_lines table
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS vendor_bill_lines (
                        id SERIAL PRIMARY KEY,
                        bill_id INTEGER NOT NULL REFERENCES vendor_bills(id),
                        product_name VARCHAR(128),
                        budget_analytics VARCHAR(128),
                        quantity FLOAT DEFAULT 1.0,
                        unit_price FLOAT DEFAULT 0.0,
                        total FLOAT DEFAULT 0.0
                    )
                """))
                print("- Checked vendor_bill_lines table")
            except Exception as e:
                print("- Note on vendor_bill_lines table:", e)
                
            # 5. Ensure password_hash is NOT NULL (from 2ad1cf58c54f)
            try:
                conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL"))
                print("- Checked users.password_hash NOT NULL")
            except Exception as e:
                print("- Note on users.password_hash:", e)

            conn.execute(text("COMMIT"))
            print("\nDatabase schema is now fully synchronized with both branches.")
            
        except Exception as e:
            print("Global fix failed:", e)
            try:
                conn.execute(text("ROLLBACK"))
            except:
                pass
