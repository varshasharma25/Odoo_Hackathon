import os
import sys
from sqlalchemy import create_engine, inspect, text

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app import create_app, db

app = create_app()
with app.app_context():
    engine = db.engine
    inspector = inspect(engine)
    
    print('DATABASE_URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    
    with engine.connect() as conn:
        try:
            res = conn.execute(text("SELECT current_user, current_database(), current_schema()")).fetchone()
            print('DB INFO:', res)
        except Exception as e:
            print('Error getting DB info:', e)
        
        print('\nTABLES IN PUBLIC SCHEMA:')
        try:
            res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).fetchall()
            for r in res:
                print('-', r[0])
        except Exception as e:
            print('Error listing tables:', e)
            
        print('\nCOLUMNS IN purchase_orders:')
        try:
            res = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'purchase_orders' AND table_schema = 'public'")).fetchall()
            for r in res:
                print(f'- {r[0]} ({r[1]})')
        except Exception as e:
            print('Error listing columns:', e)
            
        print('\nALEMBIC VERSION:')
        try:
            res = conn.execute(text("SELECT version_num FROM alembic_version")).fetchall()
            for r in res:
                print('-', r[0])
        except Exception as e:
            print('Error reading alembic_version:', e)
