import requests
import json

base_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"

print("🔍 TESTING RESOLUTION BUTTONS LOGIC")
print("="*50)

# Login with existing user
login_data = {"email": "poshtest@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=login_data)
data = response.json()
token = data["access_token"]
user_id = data["user"]["id"]

# Test different scenarios
test_scenarios = [
    {
        "name": "Initial question (should NOT show buttons)",
        "message": "I'm having trouble with my manager"
    },
    {
        "name": "Investigation question (should NOT show buttons)", 
        "message": "My manager is very demanding"
    },
    {
        "name": "Detailed solution request (should show buttons)",
        "message": "My manager micromanages everything I do. I've tried talking to them but nothing changes. I need specific strategies to handle this situation and improve our working relationship."
    }
]

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n--- SCENARIO {i}: {scenario['name']} ---")
    print(f"Message: {scenario['message']}")
    
    chat_data = {
        "message": scenario['message'],
        "user_id": user_id
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        ai_response = data.get('response', '')
        show_buttons = data.get('show_resolution_buttons', False)
        ticket_created = data.get('ticket_created', False)
        
        print(f"AI Response: {ai_response[:200]}...")
        print(f"Show Resolution Buttons: {show_buttons}")
        print(f"Ticket Created: {ticket_created}")
        
        # Check response characteristics
        has_questions = ai_response.count('?') > 0
        has_numbered_list = '1.' in ai_response and '2.' in ai_response
        response_length = len(ai_response)
        
        print(f"Response characteristics:")
        print(f"  - Has questions: {has_questions}")
        print(f"  - Has numbered list: {has_numbered_list}")
        print(f"  - Length: {response_length}")
        
        # Determine if this is correct behavior
        if scenario['name'].startswith("Initial") or scenario['name'].startswith("Investigation"):
            if not show_buttons:
                print("✅ CORRECT: No buttons for investigative/initial responses")
            else:
                print("❌ INCORRECT: Buttons should NOT appear for initial/investigative responses")
        else:
            if show_buttons:
                print("✅ CORRECT: Buttons appear for comprehensive solutions")
            else:
                print("❌ INCORRECT: Buttons should appear for comprehensive solutions")
    else:
        print(f"❌ Chat failed: {response.text}")

print("\n" + "="*50)
print("RESOLUTION BUTTONS LOGIC TEST COMPLETE")
print("="*50)
