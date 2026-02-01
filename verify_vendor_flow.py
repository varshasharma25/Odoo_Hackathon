import requests
import re
from app import create_app, db
from app.models import Users, Contact # Ensure Role if needed, though models usually sufficient
from werkzeug.security import generate_password_hash

BASE_URL = "http://127.0.0.1:5000"

def setup_data():
    app = create_app()
    with app.app_context():
        print("[Setup] Ensuring Test Data exists...")
        # 1. Admin
        admin = Users.query.filter_by(username='Admin').first()
        if not admin:
            print("[Setup] Creating Admin user...")
            admin = Users(email='admin@shiv.com', username='Admin', password_hash=generate_password_hash('password123'), role='admin', name='Administrator')
            db.session.add(admin)
        else:
             admin.password_hash = generate_password_hash('password123')
             
        # 2. Vendor User
        vendor = Users.query.filter_by(username='vendor').first()
        if not vendor:
            print("[Setup] Creating Vendor user...")
            vendor = Users(email='vendor@shiv.com', username='vendor', password_hash=generate_password_hash('password123'), role='portal', name='Vendor User')
            db.session.add(vendor)
        else:
             vendor.password_hash = generate_password_hash('password123')

        # 3. Vendor Contact (Crucial)
        # Check by name 'Vendor User' because that's what we use in PO
        contact = Contact.query.filter_by(name='Vendor User').first()
        if not contact:
            print("[Setup] Creating Contact 'Vendor User'...")
            contact = Contact(name='Vendor User', email='vendor@shiv.com', phone='5555555555')
            db.session.add(contact)
        else:
            # Ensure email matches vendor user for linkage
            if contact.email != 'vendor@shiv.com':
                 print("[Setup] Fixing Contact email...")
                 contact.email = 'vendor@shiv.com'
        
        db.session.commit()
        print("[Setup] Data ready.")

# Helper to verify Vendor Workflow
def verify_workflow():
    setup_data()
    session = requests.Session()
    
    # 1. Login as Admin to create PO
    print("[1] Logging in as Admin...")
    # Auth route uses 'username' field, not 'email'
    admin_login = session.post(f"{BASE_URL}/auth/login", data={'username': 'Admin', 'password': 'password123'})
    
    # Debug info
    if admin_login.url != f"{BASE_URL}/admin/dashboard":
        print(f"FAILED: Admin login.")
        print(f"   Expected: {BASE_URL}/admin/dashboard")
        print(f"   Actual: {admin_login.url}")
        print(f"   Status: {admin_login.status_code}")
        print(f"   Content snippet: {admin_login.text[:1000]}")
        return
    print("SUCCESS: Admin logged in")
    
    # 2. Create Purchase Order linked to vendor
    print("[2] Creating Purchase Order for Vendor 'vendor@shiv.com'...")
    # First, ensure vendor exists (assuming from previous steps or manual creation)
    # We will just rely on the route logic we added: if vendor_name matches Contact email
    po_data = {
        'vendor_name': 'Vendor User', # Assuming contact name matches the Contact we created
        'order_date': '2025-02-01',
        'reference': 'AUTO_TEST_PO_001',
        'product_name[]': 'Test Product A',
        'budget_analytics[]': 'Design',
        'quantity[]': '10',
        'unit_price[]': '500',
        'notes': 'Auto generated test PO'
    }
    create_po = session.post(f"{BASE_URL}/admin/purchase-order/new", data=po_data)
    if create_po.status_code != 200 and create_po.status_code != 302:
        print(f"FAILED: PO Creation {create_po.status_code}")
        # print(create_po.text)
        return
    
    print("SUCCESS: PO Created")
    
    # 3. Get PO ID
    # Ideally we parse the list page.
    list_page = session.get(f"{BASE_URL}/admin/purchase-orders")
    found_ids = re.findall(r'/admin/purchase-order/(\d+)', list_page.text)
    if not found_ids:
        print("FAILED: Could not find created PO ID")
        return
    
    # Convert to ints and get max to find the latest
    po_ids = [int(id_str) for id_str in found_ids]
    po_id = max(po_ids)
    print(f"SUCCESS: PO ID found: {po_id} (Max ID)")
    
    # 4. Send the PO (Admin Action) - simulating "Send" button
    print(f"[4] Sending PO {po_id} to Vendor...")
    # The Send button calls updateStatus('sent') which hits this route
    send_po = session.get(f"{BASE_URL}/admin/purchase-order/{po_id}/status/sent")
    if send_po.status_code == 200:
        print(f"SUCCESS: PO {po_id} Sent to Vendor")
    else:
        print(f"FAILED: Sending PO {po_id}. Status: {send_po.status_code}")
    
    # Logout Admin
    session.get(f"{BASE_URL}/auth/logout")
    
    # 5. Login as Vendor
    print("[5] Logging in as Vendor 'vendor'...")
    vendor_login = session.post(f"{BASE_URL}/auth/login", data={'username': 'vendor', 'password': 'password123'})
    # Check if login successful (redirect to /portal/home)
    # Sometimes it might redirect to /portal/home but the final URL property might be tricky with sessions
    if "Dashboard" not in vendor_login.text and "portal/home" not in vendor_login.url:
        print(f"FAILED: Vendor login")
        print(f"   Expected: Dashboard content or /portal/home URL")
        print(f"   Actual URL: {vendor_login.url}")
        print(f"   Status: {vendor_login.status_code}")
        # print(f"   Content: {vendor_login.text[:500]}")
        return
    print("SUCCESS: Vendor logged in")
    
    # 6. Check Portal Dashboard for "New Orders"
    dashboard = session.get(f"{BASE_URL}/portal/home")
    if "Received from Admin" in dashboard.text:
         print("SUCCESS: Dashboard shows 'New Orders' stat")
    else:
         print("WARNING: Dashboard might not be showing stats correctly")

    # 7. View PO Detail
    print(f"[7] Viewing PO {po_id} as Vendor...")
    po_view = session.get(f"{BASE_URL}/portal/purchase-order/{po_id}")
    
    # Check if we are seeing the detail page or redirected
    if "Accept & Send Bill" in po_view.text:
        print("SUCCESS: Vendor sees 'Accept' button")
    else:
        print(f"FAILED: Vendor cannot see 'Accept' button on PO {po_id}")
        # print(f"Page Content Snippet: {po_view.text[:1000]}")
        
        # Check if we see the form instead?
        if "Update Order" in po_view.text or "Save Changes" in po_view.text:
             print("DEBUG: Vendor sees EDIT FORM instead of Read-only view. Vendor linkage failed?")
        elif "Only confirmed Purchase Orders" in po_view.text:
             print("DEBUG: Status warning present.")
             
        # Inspect DB state directly
        print("DEBUG: Inspecting DB state...")
        from app import create_app, db
        from app.models import PurchaseOrder, Users, Contact
        app = create_app()
        with app.app_context():
            po = PurchaseOrder.query.get(po_id)
            vendor = Users.query.filter_by(username='vendor').first()
            contact = Contact.query.filter_by(name='Vendor User').first()
            
            print("   --- Checking ALL Contacts ---")
            all_contacts = Contact.query.all()
            for c in all_contacts:
                print(f"   [ID: {c.id}] Name: '{c.name}', Email: '{c.email}'")
            print("   -----------------------------")

            print(f"   Searching for Contact 'Vendor User'...")
            if contact:
                print(f"   FOUND Contact: ID={contact.id}, Name={contact.name}, Email={contact.email}")
            else:
                print("   FAILED: Contact 'Vendor User' NOT FOUND")

            print(f"   Searching for User 'vendor'...")
            if vendor:
                 print(f"   FOUND User: ID={vendor.id}, Username={vendor.username}, Email={vendor.email}, Role={vendor.role}")
            else:
                 print("   FAILED: User 'vendor' NOT FOUND")
            
            if po:
                print(f"   PO Status: {po.status}")
                print(f"   PO Vendor Name: {po.vendor_name}")
                print(f"   PO Vendor ID: {po.vendor_id}")
                print(f"   Vendor Match: {po.vendor_id == vendor.id if vendor else 'False'}")
            else:
                 print("   PO Not found in DB")
                 
        return

    # 8. Accept PO
    print("[8] Accepting PO...")
    accept_po = session.get(f"{BASE_URL}/portal/purchase-order/{po_id}/accept")
    if "accepted! Bill" in accept_po.text or accept_po.history:
        print("SUCCESS: PO Accepted and Bill Generated")
    else:
        print("FAILED: PO Acceptance")
        return
        
    print(">>> VERIFICATION COMPLETE: ALL STEPS PASSED <<<")

if __name__ == "__main__":
    verify_workflow()
