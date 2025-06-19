import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 CHECKING ADMIN USERS FOR EMAIL NOTIFICATIONS")
print("="*60)

# Login as admin
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
admin_data = response.json()
admin_token = admin_data["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# Get all users and find admins
response = requests.get(f"{base_url}/api/admin/users", headers=admin_headers)
if response.status_code == 200:
    users = response.json()
    
    # Filter admin users
    admin_users = [user for user in users if user['role'] == 'admin']
    employee_users = [user for user in users if user['role'] == 'employee']
    
    print(f"📊 USER SUMMARY:")
    print(f"Total Users: {len(users)}")
    print(f"Admin Users: {len(admin_users)}")
    print(f"Employee Users: {len(employee_users)}")
    
    print(f"\n👥 ADMIN USERS:")
    for admin in admin_users:
        print(f"  - {admin['name']} ({admin['email']})")
    
    print(f"\n📧 CURRENT EMAIL TEMPLATE RECIPIENTS:")
    response = requests.get(f"{base_url}/api/admin/email-templates", headers=admin_headers)
    if response.status_code == 200:
        templates = response.json()
        ticket_created_template = next((t for t in templates if t['template_name'] == 'ticket_created'), None)
        if ticket_created_template:
            to_recipients = json.loads(ticket_created_template.get('to_recipients', '[]'))
            cc_recipients = json.loads(ticket_created_template.get('cc_recipients', '[]'))
            print(f"To Recipients: {to_recipients}")
            print(f"CC Recipients: {cc_recipients}")
            
            # Check if all admin emails are included
            admin_emails = [admin['email'] for admin in admin_users]
            missing_admins = [email for email in admin_emails if email not in to_recipients and email not in cc_recipients]
            
            if missing_admins:
                print(f"\n⚠️  MISSING ADMIN EMAILS: {missing_admins}")
                print(f"These admin users will NOT receive email notifications!")
            else:
                print(f"\n✅ All admin users are included in email notifications")
        else:
            print(f"❌ No 'ticket_created' email template found")
    
    # Show what happens currently
    print(f"\n🔄 CURRENT EMAIL BEHAVIOR:")
    print(f"When a ticket is created:")
    print(f"1. Email is sent to recipients in email template")
    print(f"2. Employee who created ticket is automatically added")
    print(f"3. Static admin list from template is used")
    print(f"4. New admin users are NOT automatically included")
    
else:
    print(f"❌ Failed to get users: {response.text}")

print("\n" + "="*60)
print("ADMIN EMAIL CHECK COMPLETE")
print("="*60)
