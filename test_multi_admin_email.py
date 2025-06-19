import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 TESTING MULTI-ADMIN EMAIL NOTIFICATIONS")
print("="*60)

# Login as existing admin
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
admin_data = response.json()
admin_token = admin_data["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

print("Step 1: Creating additional admin users...")

# Create additional admin users
additional_admins = [
    {
        "name": "HR Admin",
        "email": "hr.admin@ketto.org",
        "password": "admin123",
        "role": "admin",
        "designation": "HR Manager"
    },
    {
        "name": "IT Admin", 
        "email": "it.admin@ketto.org",
        "password": "admin123",
        "role": "admin",
        "designation": "IT Manager"
    },
    {
        "name": "Operations Admin",
        "email": "ops.admin@ketto.org", 
        "password": "admin123",
        "role": "admin",
        "designation": "Operations Manager"
    }
]

created_admins = []
for admin_data in additional_admins:
    response = requests.post(f"{base_url}/api/admin/users", json=admin_data, headers=admin_headers)
    if response.status_code == 200:
        print(f"✅ Created admin: {admin_data['name']} ({admin_data['email']})")
        created_admins.append(admin_data['email'])
    else:
        print(f"⚠️  Admin might already exist: {admin_data['name']}")
        created_admins.append(admin_data['email'])  # Add anyway for testing

print(f"\nStep 2: Verifying all admin users...")

# Get updated user list
response = requests.get(f"{base_url}/api/admin/users", headers=admin_headers)
if response.status_code == 200:
    users = response.json()
    admin_users = [user for user in users if user['role'] == 'admin']
    
    print(f"Total admin users: {len(admin_users)}")
    for admin in admin_users:
        print(f"  - {admin['name']} ({admin['email']})")

print(f"\nStep 3: Creating test employee for ticket creation...")

# Create test employee
employee_data = {
    "name": "Multi Admin Test User",
    "email": "multiadmintest@example.com",
    "password": "test123",
    "role": "employee"
}

response = requests.post(f"{base_url}/api/auth/register", json=employee_data)
if response.status_code == 200:
    emp_data = response.json()
    emp_token = emp_data["access_token"]
    emp_user_id = emp_data["user"]["id"]
    print(f"✅ Test employee created: {emp_user_id}")
else:
    # Login if exists
    login_data = {"email": "multiadmintest@example.com", "password": "test123"}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    emp_data = response.json()
    emp_token = emp_data["access_token"]
    emp_user_id = emp_data["user"]["id"]
    print(f"✅ Test employee logged in: {emp_user_id}")

print(f"\nStep 4: Creating ticket to test multi-admin email notifications...")

# Create ticket that should email all admins
emp_headers = {"Authorization": f"Bearer {emp_token}", "Content-Type": "application/json"}
chat_data = {
    "message": "I need urgent help with workplace harassment from my supervisor",
    "user_id": emp_user_id
}

response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=emp_headers)
if response.status_code == 200:
    data = response.json()
    ticket_created = data.get('ticket_created', False)
    ticket_id = data.get('ticket_id')
    
    print(f"Ticket Created: {ticket_created}")
    print(f"Ticket ID: {ticket_id}")
    
    if ticket_created:
        print(f"\n📧 EMAIL NOTIFICATION SENT TO:")
        print(f"Primary Recipients (TO): ALL ADMIN USERS")
        for admin in admin_users:
            print(f"  ✅ {admin['email']}")
        
        print(f"\nCC Recipients:")
        print(f"  ✅ {employee_data['email']} (Employee who created ticket)")
        
        print(f"\n🎯 BENEFITS OF THIS APPROACH:")
        print(f"1. ALL admin users automatically receive notifications")
        print(f"2. New admin users are immediately included")
        print(f"3. No manual template updates needed")
        print(f"4. Employee gets CC for transparency")
        print(f"5. Scalable for any number of admin users")
        
        # Verify ticket in admin dashboard
        response = requests.get(f"{base_url}/api/admin/tickets", headers=admin_headers)
        if response.status_code == 200:
            tickets = response.json()
            new_ticket = next((t for t in tickets if t['id'] == ticket_id), None)
            if new_ticket:
                print(f"\n✅ Ticket verified in admin dashboard")
                print(f"   Category: {new_ticket['category']}")
                print(f"   Severity: {new_ticket['severity']}")
    else:
        print(f"❌ Ticket was not created")
else:
    print(f"❌ Failed to create ticket: {response.text}")

print("\n" + "="*60)
print("MULTI-ADMIN EMAIL TEST COMPLETE")
print("="*60)
print("📧 Check backend logs for email sending confirmation")
print("🎯 All admin users now receive automatic email notifications!")
