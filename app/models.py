from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(128))
    address = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'address': self.address,
            'image_url': self.image_url,
            'is_archived': self.is_archived
        }


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(128))
    description = db.Column(db.Text)
    sales_price = db.Column(db.Float)
    purchase_price = db.Column(db.Float)
    price = db.Column(db.Float)  # Keep for backward compatibility
    cost = db.Column(db.Float)   # Keep for backward compatibility
    quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'sales_price': self.sales_price,
            'purchase_price': self.purchase_price,
            'price': self.price,
            'cost': self.cost,
            'quantity': self.quantity,
            'image_url': self.image_url,
            'is_archived': self.is_archived
        }


class AnalyticalAccount(db.Model):
    __tablename__ = 'analytical_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(32), unique=True)
    description = db.Column(db.Text)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnalyticalAccount {self.name}>'


class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    analytical_account = db.Column(db.String(128))
    total_amount = db.Column(db.Float)
    description = db.Column(db.Text)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Budget {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'analytical_account': self.analytical_account,
            'total_amount': self.total_amount,
            'description': self.description,
            'is_archived': self.is_archived
        }


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    name = db.Column(db.String(128))
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='portal')  # admin, portal
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
