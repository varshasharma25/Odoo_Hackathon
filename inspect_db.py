import os
from sqlalchemy import inspect
from app import create_app, db

app = create_app()
with app.app_context():
    engine = db.engine
    inspector = inspect(engine)
    
    print(f"Inspecting table: purchase_orders")
    if 'purchase_orders' in inspector.get_table_names():
        columns = inspector.get_columns('purchase_orders')
        for column in columns:
            print(f"Column: {column['name']}")
    else:
        print("Table purchase_orders not found!")
