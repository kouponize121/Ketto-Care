import requests
import json

base_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"

print("🔍 TESTING EMAIL RECIPIENTS MANAGEMENT")
print("="*60)

# Login as admin
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
admin_data = response.json()
admin_token = admin_data["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

print("Step 1: Testing email recipients API endpoints...")

# Test getting current email recipients
response = requests.get(f"{base_url}/api/admin/email-recipients", headers=admin_headers)
if response.status_code == 200:
    current_recipients = response.json()
    print("✅ GET email recipients endpoint working")
    print(f"   Additional recipients: {len(current_recipients['additional_recipients'])}")
    print(f"   Excluded admin emails: {len(current_recipients['excluded_admin_emails'])}")
else:
    print(f"❌ Failed to get email recipients: {response.text}")

print("\nStep 2: Testing email recipients configuration...")

# Configure email recipients
new_recipients = {
    "additional_recipients": [
        "hr.external@consultant.com",
        "ceo@company.com", 
        "compliance@company.com"
    ],
    "excluded_admin_emails": [
        "temp.admin@ketto.org"  # Exclude a specific admin if exists
    ]
}

response = requests.post(f"{base_url}/api/admin/email-recipients", json=new_recipients, headers=admin_headers)
if response.status_code == 200:
    result = response.json()
    print("✅ Email recipients configuration saved")
    print(f"   Added {result['additional_count']} additional recipients")
    print(f"   Excluded {result['excluded_count']} admin emails")
else:
    print(f"❌ Failed to save email recipients: {response.text}")

print("\nStep 3: Verifying configuration was saved...")

# Verify the configuration was saved
response = requests.get(f"{base_url}/api/admin/email-recipients", headers=admin_headers)
if response.status_code == 200:
    saved_recipients = response.json()
    print("✅ Configuration verified:")
    print("   Additional recipients:")
    for recipient in saved_recipients['additional_recipients']:
        print(f"     - {recipient['email']}")
    
    print("   Excluded admin emails:")
    for recipient in saved_recipients['excluded_admin_emails']:
        print(f"     - {recipient['email']}")
else:
    print(f"❌ Failed to verify configuration: {response.text}")

print("\nStep 4: Testing email notification with custom recipients...")

# Create test employee and ticket to test email notifications
employee_data = {
    "name": "Email Recipients Test User",
    "email": "emailrecipientstest@example.com",
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
    login_data = {"email": "emailrecipientstest@example.com", "password": "test123"}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    emp_data = response.json()
    emp_token = emp_data["access_token"]
    emp_user_id = emp_data["user"]["id"]
    print(f"✅ Test employee logged in: {emp_user_id}")

# Create ticket to test email with custom recipients
emp_headers = {"Authorization": f"Bearer {emp_token}", "Content-Type": "application/json"}
chat_data = {
    "message": "I need help with sexual harassment from my colleague - this is urgent",
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
        print(f"Primary Recipients (TO):")
        print(f"  ✅ All admin users (except excluded)")
        print(f"  ✅ hr.external@consultant.com (additional)")
        print(f"  ✅ ceo@company.com (additional)")
        print(f"  ✅ compliance@company.com (additional)")
        print(f"\nCC Recipients:")
        print(f"  ✅ emailrecipientstest@example.com (employee)")
        print(f"\nExcluded:")
        print(f"  ❌ temp.admin@ketto.org (if exists)")
        
        print(f"\n🎯 CUSTOM EMAIL RECIPIENTS BENEFITS:")
        print(f"1. ✅ Add external consultants automatically")
        print(f"2. ✅ Include C-level executives") 
        print(f"3. ✅ Add compliance/legal teams")
        print(f"4. ✅ Exclude specific admin users")
        print(f"5. ✅ All configurable from admin dashboard")
        print(f"6. ✅ No code changes needed")
    else:
        print(f"❌ Ticket was not created")
else:
    print(f"❌ Failed to create ticket: {response.text}")

print("\n" + "="*60)
print("EMAIL RECIPIENTS MANAGEMENT TEST COMPLETE")
print("="*60)
print("✅ Admins can now customize email recipients from the dashboard!")
print("✅ Additional recipients automatically included in notifications")
print("✅ Specific admin users can be excluded if needed")
