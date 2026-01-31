# Config file
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # PostgreSQL connection
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    
    # Build PostgreSQL URI only if DB_NAME is explicitly set
    # Otherwise use SQLite
    if DB_NAME:
        # URL-encode password to handle special characters like @
        encoded_password = quote_plus(DB_PASSWORD)
        SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max size
