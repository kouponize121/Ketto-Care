import requests
import json

base_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"

# Login with existing user
login_data = {"email": "test.employee@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=login_data)
data = response.json()
token = data["access_token"]
user_id = data["user"]["id"]

# Test the exact harassment scenario you mentioned
print("Testing specific harassment scenario...")
chat_data = {
    "message": "I'm facing harassment from my manager",
    "user_id": user_id
}
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Chat successful")
    print(f"AI Response:\n{data.get('response', '')}")
    print(f"\nShow Resolution Buttons: {data.get('show_resolution_buttons', False)}")
    print(f"Ticket Created: {data.get('ticket_created', False)}")
    print(f"Ticket ID: {data.get('ticket_id', 'None')}")
    print(f"Conversation ID: {data.get('conversation_id', 'None')}")
else:
    print(f"❌ Chat failed: {response.text}")
