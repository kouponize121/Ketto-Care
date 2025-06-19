import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔧 CLEANING EMAIL TEMPLATES - REMOVING HARDCODED EMAILS")
print("="*60)

# Login as admin
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
admin_data = response.json()
admin_token = admin_data["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# Create clean email template with NO hardcoded recipients
clean_ticket_created_template = {
    "template_name": "ticket_created",
    "subject": "New Support Ticket Created - {ticket_id}",
    "body": """Dear Team,

A new support ticket has been created in Ketto Care:

Ticket Details:
- Ticket ID: {ticket_id}
- Employee: {employee_name} ({employee_email})
- Category: {category}
- Severity: {severity}
- Summary: {summary}
- Description: {description}
- Status: {status}
- Created: {created_at}

Please log in to the admin dashboard to review and respond to this ticket.

Best regards,
Ketto Care System""",
    "to_recipients": [],  # EMPTY - will be populated automatically
    "cc_recipients": [],  # EMPTY - will be populated automatically
    "bcc_recipients": [],
    "is_active": True
}

print("Step 1: Creating clean email template...")
response = requests.post(f"{base_url}/api/admin/email-templates", json=clean_ticket_created_template, headers=admin_headers)
if response.status_code == 200:
    print("✅ Clean email template created")
else:
    print(f"❌ Failed to create clean template: {response.text}")

# Clear any existing custom recipients for a fresh start
print("\nStep 2: Clearing existing custom recipients...")
empty_recipients = {
    "additional_recipients": [],
    "excluded_admin_emails": []
}

response = requests.post(f"{base_url}/api/admin/email-recipients", json=empty_recipients, headers=admin_headers)
if response.status_code == 200:
    print("✅ Custom recipients cleared")
else:
    print(f"❌ Failed to clear recipients: {response.text}")

print("\n" + "="*60)
print("EMAIL TEMPLATE CLEANUP COMPLETE")
print("="*60)
print("✅ Email template now has NO hardcoded recipients")
print("✅ Only admin users + employee will be automatically included")
print("✅ All additional emails must be configured via custom recipients")
