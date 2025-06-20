import requests
import json

base_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"

# Register a new employee
register_data = {
    "name": "Test Employee", 
    "email": "test.employee@example.com",
    "password": "test123",
    "role": "employee"
}

print("Registering employee...")
response = requests.post(f"{base_url}/api/auth/register", json=register_data)
if response.status_code == 200:
    data = response.json()
    token = data["access_token"]
    user_id = data["user"]["id"]
    print(f"✅ Registration successful. User ID: {user_id}")
else:
    print(f"❌ Registration failed: {response.text}")
    # Try to login with existing user
    login_data = {"email": "test.employee@example.com", "password": "test123"}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        user_id = data["user"]["id"]
        print(f"✅ Login successful. User ID: {user_id}")
    else:
        print(f"❌ Login failed: {response.text}")
        exit(1)

# Test resignation scenario
print("\n\nTesting resignation scenario...")
chat_data = {
    "message": "I am thinking about resigning because of my manager",
    "user_id": user_id
}
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Chat successful")
    print(f"AI Response: {data.get('response', '')[:200]}...")
    print(f"Show Resolution Buttons: {data.get('show_resolution_buttons', False)}")
    print(f"Conversation ID: {data.get('conversation_id', 'None')}")
else:
    print(f"❌ Chat failed: {response.text}")
