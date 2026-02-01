from app import create_app, db
from app.models import Users, Contact, PurchaseOrder

def inspect():
    app = create_app()
    with app.app_context():
        print("--- DEBUG DB ---")
        
        # 1. Check Contact
        contact = Contact.query.filter_by(name='Vendor User').first()
        if contact:
            print(f"Contact Found: ID={contact.id}, Name='{contact.name}', Email='{contact.email}'")
        else:
            print("Contact Found: NONE")
            
        # 2. Check User
        user = Users.query.filter_by(email='vendor@shiv.com').first()
        if user:
            print(f"User Found: ID={user.id}, Username='{user.username}', Email='{user.email}', Role='{user.role}'")
        else:
             print("User Found: NONE")
             
        # 3. Check Last PO
        po = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).first()
        if po:
            print(f"Last PO: {po.order_number}, VendorName='{po.vendor_name}', VendorID={po.vendor_id}")
        else:
            print("Last PO: NONE")
            
        print("----------------")

if __name__ == "__main__":
    inspect()
