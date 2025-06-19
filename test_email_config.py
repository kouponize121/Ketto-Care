import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 TESTING EMAIL CONFIGURATION")
print("="*50)

# Login as admin to check email config
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
if response.status_code == 200:
    admin_data = response.json()
    admin_token = admin_data["access_token"]
    
    print("✅ Admin login successful")
    
    # Check current email configuration
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{base_url}/api/admin/email-config", headers=headers)
    
    if response.status_code == 200:
        email_config = response.json()
        print(f"\n📧 Current Email Configuration:")
        print(f"SMTP Server: {email_config.get('smtp_server', 'Not configured')}")
        print(f"SMTP Port: {email_config.get('smtp_port', 'Not configured')}")
        print(f"SMTP Username: {email_config.get('smtp_username', 'Not configured')}")
        print(f"SMTP Password: {'***configured***' if email_config.get('smtp_password') else 'Not configured'}")
        
        if not email_config.get('smtp_server'):
            print("\n⚠️  EMAIL NOT CONFIGURED - Setting up test configuration...")
            
            # Configure test email settings (using Gmail SMTP as example)
            test_config = {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "kettocare.notifications@gmail.com", 
                "smtp_password": "test_password_replace_with_real"
            }
            
            response = requests.post(f"{base_url}/api/admin/email-config", json=test_config, headers=headers)
            if response.status_code == 200:
                print("✅ Email configuration saved (test setup)")
                print("⚠️  NOTE: Replace with real SMTP credentials for production")
            else:
                print(f"❌ Failed to save email config: {response.text}")
        else:
            print("✅ Email configuration exists")
    else:
        print(f"❌ Failed to get email config: {response.text}")
    
    # Check email templates
    print(f"\n📧 Checking Email Templates:")
    response = requests.get(f"{base_url}/api/admin/email-templates", headers=headers)
    if response.status_code == 200:
        templates = response.json()
        print(f"Found {len(templates)} email templates")
        for template in templates:
            print(f"  - {template['template_name']}: {template['subject']}")
    else:
        print(f"❌ Failed to get email templates: {response.text}")
        
else:
    print(f"❌ Admin login failed: {response.text}")

print("\n" + "="*50)
print("EMAIL CONFIGURATION CHECK COMPLETE")
print("="*50)
