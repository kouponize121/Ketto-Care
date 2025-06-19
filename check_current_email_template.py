import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 CHECKING CURRENT EMAIL TEMPLATE CONFIGURATION")
print("="*60)

# Login as admin
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
admin_data = response.json()
admin_token = admin_data["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# Check current email templates
response = requests.get(f"{base_url}/api/admin/email-templates", headers=admin_headers)
if response.status_code == 200:
    templates = response.json()
    
    print(f"📧 CURRENT EMAIL TEMPLATES:")
    for template in templates:
        print(f"\nTemplate: {template['template_name']}")
        print(f"Subject: {template['subject']}")
        
        # Parse recipients
        try:
            to_recipients = json.loads(template.get('to_recipients', '[]')) if template.get('to_recipients') else []
            cc_recipients = json.loads(template.get('cc_recipients', '[]')) if template.get('cc_recipients') else []
            
            print(f"TO Recipients (hardcoded in template): {to_recipients}")
            print(f"CC Recipients (hardcoded in template): {cc_recipients}")
            
            if to_recipients:
                print(f"⚠️  THESE EMAILS ARE AUTO-INCLUDED FROM TEMPLATE:")
                for email in to_recipients:
                    print(f"   - {email}")
                    
        except:
            print(f"TO Recipients (raw): {template.get('to_recipients', 'None')}")
            print(f"CC Recipients (raw): {template.get('cc_recipients', 'None')}")
else:
    print(f"❌ Failed to get email templates: {response.text}")

# Check admin users
response = requests.get(f"{base_url}/api/admin/users", headers=admin_headers)
if response.status_code == 200:
    users = response.json()
    admin_users = [user for user in users if user['role'] == 'admin']
    
    print(f"\n👥 CURRENT ADMIN USERS (should be auto-included):")
    for admin in admin_users:
        print(f"   - {admin['name']} ({admin['email']})")
else:
    print(f"❌ Failed to get admin users: {response.text}")

# Check custom recipients
response = requests.get(f"{base_url}/api/admin/email-recipients", headers=admin_headers)
if response.status_code == 200:
    recipients = response.json()
    
    print(f"\n📝 CUSTOM EMAIL RECIPIENTS:")
    print(f"Additional Recipients: {len(recipients['additional_recipients'])}")
    for recipient in recipients['additional_recipients']:
        print(f"   - {recipient['email']}")
    
    print(f"Excluded Admin Emails: {len(recipients['excluded_admin_emails'])}")
    for recipient in recipients['excluded_admin_emails']:
        print(f"   - {recipient['email']}")
else:
    print(f"❌ Failed to get custom recipients: {response.text}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
print("🔧 CLEAN EMAIL TEMPLATE - Remove hardcoded emails")
print("📧 KEEP AUTO-INCLUSION - Only admin users + employee")
print("🎯 USE CUSTOM RECIPIENTS - For any additional emails")
