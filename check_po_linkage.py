from app import create_app, db
from app.models import PurchaseOrder, Contact, Users

app = create_app()

with app.app_context():
    print("--- PO Linkage Check (Last 5) ---")
    pos = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).limit(5).all()
    if not pos:
        print("No Purchase Orders found.")
    
    for po in pos:
        print(f"PO: {po.order_number} | ID: {po.id} | Status: {po.status}")
        print(f"    Vendor: {po.vendor_name}")
        
        if po.vendor_id:
            user = Users.query.get(po.vendor_id)
            print(f"    -> LINKED to User ID: {po.vendor_id} ({user.username})")
        else:
            print(f"    -> NOT LINKED (Vendor ID is None)")
        print("-" * 30)
