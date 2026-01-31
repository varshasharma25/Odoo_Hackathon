from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True)
    phone = db.Column(db.Numeric(10))
    company = db.Column(db.String(255))
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
    account_type = db.Column(db.String(20), default='income') # income, expense
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


class Users(UserMixin, db.Model):
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


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True)
    reference = db.Column(db.String(128)) # REQ-25-0001
    vendor_name = db.Column(db.String(128), nullable=False)
    order_date = db.Column(db.Date)
    expected_delivery = db.Column(db.Date)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='draft')  # draft, confirmed, received, cancelled
    notes = db.Column(db.Text)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    lines = db.relationship('PurchaseOrderLine', backref='order', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<PurchaseOrder {self.order_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'reference': self.reference,
            'vendor_name': self.vendor_name,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_delivery': self.expected_delivery.isoformat() if self.expected_delivery else None,
            'total_amount': self.total_amount,
            'status': self.status,
            'notes': self.notes,
            'is_archived': self.is_archived,
            'lines': [line.to_dict() for line in self.lines]
        }


class PurchaseOrderLine(db.Model):
    __tablename__ = 'purchase_order_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_name = db.Column(db.String(128))
    budget_analytics = db.Column(db.String(128))
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'budget_analytics': self.budget_analytics,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total': self.total
        }