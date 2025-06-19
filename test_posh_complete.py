import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 COMPLETE POSH COMPLAINT TEST")
print("="*50)

# Create a new test user
register_data = {
    "name": "Test POSH User",
    "email": "poshtest@example.com", 
    "password": "test123",
    "role": "employee"
}

response = requests.post(f"{base_url}/api/auth/register", json=register_data)
if response.status_code == 200:
    user_data = response.json()
    token = user_data["access_token"]
    user_id = user_data["user"]["id"]
    
    print(f"✅ User created successfully. User ID: {user_id}")
    
    # Test POSH complaint scenarios
    posh_messages = [
        "I want to raise a POSH complaint against my manager",
        "I need to file a POSH complaint for sexual harassment",
        "POSH violation by my colleague - need help",
        "Sexual harassment complaint - POSH case"
    ]
    
    created_tickets = []
    
    for i, message in enumerate(posh_messages, 1):
        print(f"\n--- TEST {i}: {message} ---")
        
        chat_data = {
            "message": message,
            "user_id": user_id
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '')
            ticket_created = data.get('ticket_created', False)
            ticket_id = data.get('ticket_id', 'None')
            show_buttons = data.get('show_resolution_buttons', False)
            
            print(f"AI Response: {ai_response[:150]}...")
            print(f"Ticket Created: {ticket_created}")
            print(f"Ticket ID: {ticket_id}")
            print(f"Resolution Buttons: {show_buttons}")
            
            if ticket_created and ticket_id:
                created_tickets.append(ticket_id)
                print(f"✅ TICKET CREATED: {ticket_id}")
            else:
                print(f"❌ NO TICKET CREATED!")
        else:
            print(f"❌ Chat failed: {response.text}")
    
    # Check if user can see their tickets
    print(f"\n🔍 CHECKING USER'S TICKET DASHBOARD...")
    print(f"Expected tickets: {len(created_tickets)}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/api/tickets", headers=headers)
    if response.status_code == 200:
        user_tickets = response.json()
        print(f"✅ User can see {len(user_tickets)} tickets")
        
        for ticket in user_tickets:
            print(f"  - Ticket ID: {ticket['id']}")
            print(f"    Category: {ticket['category']} | Severity: {ticket['severity']}")
            print(f"    Summary: {ticket['summary']}")
            print(f"    Status: {ticket['status']}")
            
        # Check if all created tickets are visible
        visible_ticket_ids = [t['id'] for t in user_tickets]
        missing_tickets = [tid for tid in created_tickets if tid not in visible_ticket_ids]
        
        if len(missing_tickets) == 0:
            print("✅ ALL CREATED TICKETS ARE VISIBLE TO USER")
        else:
            print(f"❌ MISSING TICKETS: {missing_tickets}")
    else:
        print(f"❌ Failed to get user tickets: {response.text}")

else:
    print(f"❌ User creation failed: {response.text}")

# Test admin dashboard visibility
print(f"\n🔍 CHECKING ADMIN DASHBOARD...")

admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
if response.status_code == 200:
    admin_data = response.json()
    admin_token = admin_data["access_token"]
    
    # Get all tickets
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{base_url}/api/admin/tickets", headers=headers)
    
    if response.status_code == 200:
        all_tickets = response.json()
        print(f"✅ Admin can see {len(all_tickets)} total tickets")
        
        # Find POSH-related tickets
        posh_tickets = [t for t in all_tickets if 'posh' in t['description'].lower() or 'posh' in t['summary'].lower()]
        print(f"📊 POSH-specific tickets: {len(posh_tickets)}")
        
        # Find tickets created in this test
        test_tickets = [t for t in all_tickets if t['id'] in created_tickets]
        print(f"📊 Tickets from this test visible to admin: {len(test_tickets)}")
        
        if len(test_tickets) == len(created_tickets):
            print("✅ ALL TEST TICKETS VISIBLE TO ADMIN")
        else:
            print(f"❌ SOME TICKETS MISSING FROM ADMIN VIEW")
            
    else:
        print(f"❌ Failed to get admin tickets: {response.text}")
else:
    print(f"❌ Admin login failed: {response.text}")

print("\n" + "="*50)
print("POSH COMPLAINT TEST COMPLETE")
print("="*50)
