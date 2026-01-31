"""
Create PostgreSQL database if it doesn't exist
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connection parameters
DB_USER = "postgres"
DB_PASSWORD = "Kalpana@2"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "odoo_db"

try:
    # Connect to PostgreSQL server (default postgres database)
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cursor.fetchone()
    
    if exists:
        print(f"✓ Database '{DB_NAME}' already exists")
    else:
        # Create database
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"✓ Database '{DB_NAME}' created successfully!")
    
    cursor.close()
    conn.close()
    print("\nNow run: python init_db.py")
    
except psycopg2.Error as e:
    print(f"Error: {e}")
    print("\nPlease check:")
    print("1. PostgreSQL is running")
    print("2. Username and password are correct")
    print("3. PostgreSQL is listening on localhost:5432")
