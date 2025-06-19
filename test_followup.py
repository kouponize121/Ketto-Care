import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

# Login with existing user
login_data = {"email": "test.employee@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=login_data)
data = response.json()
token = data["access_token"]
user_id = data["user"]["id"]

# Send follow-up message
print("Sending follow-up message...")
chat_data = {
    "message": "My manager micromanages me constantly",
    "user_id": user_id
}
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Chat successful")
    print(f"AI Response:\n{data.get('response', '')}")
    print(f"\nShow Resolution Buttons: {data.get('show_resolution_buttons', False)}")
    print(f"Conversation ID: {data.get('conversation_id', 'None')}")
    print(f"Ticket Created: {data.get('ticket_created', False)}")
else:
    print(f"❌ Chat failed: {response.text}")
