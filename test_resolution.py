import requests
import json

base_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"

# Login with existing user
login_data = {"email": "test.employee@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=login_data)
data = response.json()
token = data["access_token"]
user_id = data["user"]["id"]

# Test "This helps" resolution
print("Testing 'This helps' resolution...")
resolution_data = {
    "conversation_id": "3fabda8d-8de3-46c7-a3ed-cdae8df8c095",
    "resolution": "helpful"
}
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

response = requests.post(f"{base_url}/api/chat/resolution", json=resolution_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Resolution 'helpful' successful")
    print(f"Response: {data.get('message', '')}")
    print(f"Ticket Created: {data.get('ticket_created', False)}")
else:
    print(f"❌ Resolution 'helpful' failed: {response.text}")

# Test "Still need help" with a new conversation
print("\n\nCreating new conversation for 'Still need help' test...")
chat_data = {
    "message": "I'm overwhelmed with my workload and my manager keeps adding more tasks without considering my capacity.",
    "user_id": user_id
}

response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    conversation_id = data.get('conversation_id')
    show_buttons = data.get('show_resolution_buttons', False)
    print(f"✅ New chat successful")
    print(f"Show Resolution Buttons: {show_buttons}")
    print(f"Conversation ID: {conversation_id}")
    
    if show_buttons and conversation_id:
        print("\nTesting 'Still need help' resolution...")
        resolution_data = {
            "conversation_id": conversation_id,
            "resolution": "need_help"
        }
        
        response = requests.post(f"{base_url}/api/chat/resolution", json=resolution_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resolution 'need_help' successful")
            print(f"Response: {data.get('message', '')}")
            print(f"Ticket Created: {data.get('ticket_created', False)}")
            if data.get('ticket_created'):
                print(f"Ticket ID: {data.get('ticket_id')}")
        else:
            print(f"❌ Resolution 'need_help' failed: {response.text}")
    else:
        print("❌ Cannot test 'Still need help' - no buttons shown or conversation ID")
else:
    print(f"❌ New chat failed: {response.text}")
