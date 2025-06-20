import requests
import json

base_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"

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
    
    print(f"📊 USER SUMMARY:")
    print(f"Total Users: {len(users)}")
    print(f"Admin Users: {len(admin_users)}")
    
    print(f"\n👥 ADMIN USERS:")
    admin_emails = []
    for admin in admin_users:
        print(f"  - {admin['name']} ({admin['email']})")
        admin_emails.append(admin['email'])
    
    print(f"\n📧 CURRENT EMAIL BEHAVIOR:")
    print(f"Currently, email recipients are configured statically in email templates.")
    print(f"This means:")
    print(f"✅ Predictable - specific emails always get notifications")
    print(f"❌ Not dynamic - new admin users won't automatically get emails")
    
    print(f"\n🔄 IMPROVEMENT NEEDED:")
    print(f"To automatically include ALL admin users in email notifications:")
    print(f"1. Modify email function to dynamically fetch admin emails")
    print(f"2. Add all admin emails to recipient list automatically")
    print(f"3. Keep employee email as CC for transparency")
    
    print(f"\nAdmin emails that should receive notifications:")
    for email in admin_emails:
        print(f"  - {email}")
        
else:
    print(f"❌ Failed to get users: {response.text}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
print("🔧 SHOULD I MODIFY THE EMAIL FUNCTION TO:")
print("1. Automatically fetch all admin users from database")
print("2. Send email notifications to ALL admin users")
print("3. Keep current template system for customization")
print("4. Add employee as CC for transparency")
print("\nThis ensures all admin users get notified regardless of template config!")
