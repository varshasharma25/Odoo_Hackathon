"""
Database initialization script
Creates all tables and optionally seeds with sample data
"""
from app import create_app, db
from app.models import Contact, Product, AnalyticalAccount, Budget, User, PurchaseOrder

def init_database():
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("- Database tables created successfully!")
        
        # Check if we should seed data
        try:
            contact_count = db.session.query(Contact).count()
            if contact_count == 0:
                print("\nSeeding sample data...")
                seed_data()
                print("- Sample data added successfully!")
            else:
                print(f"\nDatabase already has {contact_count} contacts. Skipping seed.")
        except Exception as e:
            print(f"\nNote: Could not check existing data: {e}")
            print("You can manually add data through the web interface.")

def seed_data():
    """Add sample contacts and products"""
    
    # Sample contacts
    contacts = [
        Contact(
            name="Azure Interior",
            email="azure.interior24@example.com",
            phone="+91 8080808080",
            company="Azure Interior Design"
        ),
        Contact(
            name="Nimesh Pathak",
            email="nimesh.pathak@example.com",
            phone="+91 9090909090",
            company="Pathak Enterprises"
        ),
        Contact(
            name="Priya Sharma",
            email="priya.sharma@example.com",
            phone="+91 9876543210",
            company="Sharma Furniture"
        )
    ]
    
    for contact in contacts:
        db.session.add(contact)
    
    # Sample products
    products = [
        Product(
            name="Office Chair",
            description="Ergonomic office chair with lumbar support",
            price=5999.00,
            cost=3500.00,
            quantity=50
        ),
        Product(
            name="Wooden Desk",
            description="Solid wood executive desk",
            price=15999.00,
            cost=9000.00,
            quantity=20
        ),
        Product(
            name="Filing Cabinet",
            description="4-drawer steel filing cabinet",
            price=7999.00,
            cost=4500.00,
            quantity=30
        )
    ]
    
    for product in products:
        db.session.add(product)
    
    # Create a default admin user
    admin_user = User(
        username='admin',
        email='admin@example.com',
        name='Administrator',
        role='admin'
    )
    admin_user.set_password('admin123')
    db.session.add(admin_user)
    
    db.session.commit()
    print(f"  - Added {len(contacts)} contacts")
    print(f"  - Added {len(products)} products")
    print(f"  - Added 1 admin user (username: admin, password: admin123)")

if __name__ == '__main__':
    init_database()
