import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 Testing specific user case: sumitroy1221@gmail.com")

# Test if this user exists and can login
login_data = {"email": "sumitroy1221@gmail.com", "password": "password123"}
response = requests.post(f"{base_url}/api/auth/login", json=login_data)

if response.status_code == 200:
    user_data = response.json()
    token = user_data["access_token"]
    user_id = user_data["user"]["id"]
    
    print(f"✅ User login successful. User ID: {user_id}")
    
    # Test POSH complaint
    print("\n🔍 Testing POSH complaint...")
    chat_data = {
        "message": "I want to raise a POSH complaint against my manager",
        "user_id": user_id
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat successful")
        print(f"AI Response: {data.get('response', '')}")
        print(f"Ticket Created: {data.get('ticket_created', False)}")
        print(f"Ticket ID: {data.get('ticket_id', 'None')}")
        print(f"Show Resolution Buttons: {data.get('show_resolution_buttons', False)}")
        
        if data.get('ticket_created'):
            ticket_id = data.get('ticket_id')
            print(f"\n✅ Ticket created successfully: {ticket_id}")
            
            # Check if user can see their tickets
            print("\n🔍 Checking user's tickets...")
            response = requests.get(f"{base_url}/api/tickets", headers=headers)
            if response.status_code == 200:
                tickets = response.json()
                print(f"✅ User can see {len(tickets)} tickets")
                
                # Find the POSH ticket
                posh_ticket = next((t for t in tickets if t['id'] == ticket_id), None)
                if posh_ticket:
                    print(f"✅ POSH ticket found in user's ticket list!")
                    print(f"   - Category: {posh_ticket['category']}")
                    print(f"   - Severity: {posh_ticket['severity']}")
                    print(f"   - Status: {posh_ticket['status']}")
                    print(f"   - Summary: {posh_ticket['summary']}")
                else:
                    print(f"❌ POSH ticket NOT found in user's ticket list!")
            else:
                print(f"❌ Failed to get user tickets: {response.text}")
        else:
            print(f"❌ No ticket was created for POSH complaint!")
    else:
        print(f"❌ Chat failed: {response.text}")
        
else:
    print(f"❌ User login failed: {response.text}")
    print("User might not exist. Let me try to create the user...")
    
    # Create the user
    register_data = {
        "name": "Sumit Roy",
        "email": "sumitroy1221@gmail.com", 
        "password": "password123",
        "role": "employee"
    }
    
    response = requests.post(f"{base_url}/api/auth/register", json=register_data)
    if response.status_code == 200:
        print("✅ User created successfully")
        # Retry the test
        print("Retrying the test with the new user...")
    else:
        print(f"❌ User creation failed: {response.text}")

# Test admin dashboard
print("\n" + "="*50)
print("TESTING ADMIN DASHBOARD TICKET VISIBILITY")
print("="*50)

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
        print(f"✅ Admin can see {len(tickets)} total tickets")
        
        # Look for recent POSH-related tickets
        posh_tickets = [t for t in tickets if 'posh' in t['description'].lower() or 'posh' in t['summary'].lower()]
        harassment_tickets = [t for t in tickets if 'harass' in t['description'].lower()]
        
        print(f"📊 POSH tickets: {len(posh_tickets)}")
        print(f"📊 Harassment tickets: {len(harassment_tickets)}")
        
        # Show recent tickets
        recent_tickets = tickets[-5:] if len(tickets) >= 5 else tickets
        print(f"\n📋 Last {len(recent_tickets)} tickets:")
        for ticket in recent_tickets:
            print(f"  - ID: {ticket['id'][:8]}... | Category: {ticket['category']} | Severity: {ticket['severity']}")
            print(f"    Summary: {ticket['summary'][:60]}...")
            print(f"    Created: {ticket['created_at'][:19]}")
    else:
        print(f"❌ Failed to get admin tickets: {response.text}")
else:
    print(f"❌ Admin login failed: {response.text}")
