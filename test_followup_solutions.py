import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 TESTING FOLLOW-UP SOLUTIONS")
print("="*40)

# Login
login_data = {"email": "finaltest@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=login_data)
data = response.json()
token = data["access_token"]
user_id = data["user"]["id"]

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# First message - investigation
print("STEP 1: Initial message")
chat_data = {"message": "My colleagues don't include me in meetings", "user_id": user_id}
response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
data = response.json()
print(f"AI Response: {data.get('response', '')[:100]}...")
print(f"Show Buttons: {data.get('show_resolution_buttons', False)}")

# Follow-up - should provide solutions
print("\nSTEP 2: Follow-up with more details")
chat_data = {"message": "No, I haven't tried reaching out. They just seem to forget about me.", "user_id": user_id}
response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
data = response.json()
ai_response = data.get('response', '')
show_buttons = data.get('show_resolution_buttons', False)
conversation_id = data.get('conversation_id')

print(f"AI Response: {ai_response}")
print(f"Show Buttons: {show_buttons}")
print(f"Has numbered list: {'1.' in ai_response and '2.' in ai_response}")
print(f"Length: {len(ai_response)}")

if show_buttons and conversation_id:
    print(f"\n✅ SUCCESS: Resolution buttons now appear!")
    print(f"Conversation ID: {conversation_id}")
    
    # Test the "Still need help" button
    print("\nTesting 'Still need help' button...")
    resolution_data = {"conversation_id": conversation_id, "resolution": "need_help"}
    response = requests.post(f"{base_url}/api/chat/resolution", json=resolution_data, headers=headers)
    if response.status_code == 200:
        res_data = response.json()
        print(f"✅ 'Still need help' response: {res_data.get('message', '')[:100]}...")
        print(f"Ticket created: {res_data.get('ticket_created', False)}")
        if res_data.get('ticket_created'):
            print(f"Ticket ID: {res_data.get('ticket_id')}")
    else:
        print(f"❌ Button failed: {response.text}")
else:
    print(f"❌ Still no resolution buttons")

print("\n" + "="*40)
print("FOLLOW-UP TEST COMPLETE")
print("="*40)
