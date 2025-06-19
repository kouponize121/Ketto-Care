import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

# Login with existing user
login_data = {"email": "test.employee@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=login_data)
data = response.json()
token = data["access_token"]
user_id = data["user"]["id"]

# Test various harassment scenarios
test_messages = [
    "I'm facing harassment from my manager",
    "My manager is harassing me",
    "There is harassment happening at work",
    "I am being harassed by my colleague",
    "Sexual harassment is happening in my workplace"
]

for i, message in enumerate(test_messages, 1):
    print(f"\n=== TEST {i}: {message} ===")
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
        
        print(f"AI Response: {ai_response}")
        print(f"Ticket Created: {ticket_created}")
        print(f"Ticket ID: {ticket_id}")
        
        # Check if this matches the message the user mentioned
        if "I will escalate this matter to HR for investigation and support" in ai_response:
            print("⚠️  Found the specific message the user mentioned!")
            if not ticket_created:
                print("❌ BUT NO TICKET WAS CREATED!")
            else:
                print("✅ Ticket was created properly")
    else:
        print(f"❌ Chat failed: {response.text}")
