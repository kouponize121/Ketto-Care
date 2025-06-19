import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

# Login as admin to check tickets
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
if response.status_code == 200:
    admin_data = response.json()
    admin_token = admin_data["access_token"]
    
    print("✅ Admin login successful")
    
    # Get all tickets
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{base_url}/api/admin/tickets", headers=headers)
    
    if response.status_code == 200:
        tickets = response.json()
        print(f"\n✅ Found {len(tickets)} tickets in the system")
        
        # Show recent tickets
        harassment_tickets = []
        for ticket in tickets[-10:]:  # Show last 10 tickets
            print(f"\nTicket ID: {ticket['id']}")
            print(f"Category: {ticket['category']}")
            print(f"Severity: {ticket['severity']}")
            print(f"Summary: {ticket['summary']}")
            print(f"Description: {ticket['description']}")
            print(f"Status: {ticket['status']}")
            print(f"Created: {ticket['created_at']}")
            
            if 'harass' in ticket['description'].lower():
                harassment_tickets.append(ticket)
        
        print(f"\n📊 Found {len(harassment_tickets)} harassment-related tickets")
        
        if len(harassment_tickets) > 0:
            print("✅ Harassment escalation is working correctly!")
        else:
            print("⚠️  No harassment tickets found - this might indicate an issue")
            
    else:
        print(f"❌ Failed to get tickets: {response.text}")
else:
    print(f"❌ Admin login failed: {response.text}")

# Also login as employee and test harassment scenario one more time
print("\n" + "="*50)
print("TESTING HARASSMENT SCENARIO AS EMPLOYEE")
print("="*50)

employee_login = {"email": "test.employee@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=employee_login)
if response.status_code == 200:
    employee_data = response.json()
    employee_token = employee_data["access_token"]
    user_id = employee_data["user"]["id"]
    
    # Test harassment
    chat_data = {
        "message": "My manager is sexually harassing me and I need help",
        "user_id": user_id
    }
    headers = {"Authorization": f"Bearer {employee_token}", "Content-Type": "application/json"}

    response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat successful")
        print(f"AI Response: {data.get('response', '')}")
        print(f"Ticket Created: {data.get('ticket_created', False)}")
        print(f"Ticket ID: {data.get('ticket_id', 'None')}")
        
        if data.get('ticket_created'):
            print("\n✅ TICKET CREATION IS WORKING FOR HARASSMENT!")
        else:
            print("\n❌ TICKET NOT CREATED FOR HARASSMENT!")
    else:
        print(f"❌ Chat failed: {response.text}")
else:
    print(f"❌ Employee login failed: {response.text}")
