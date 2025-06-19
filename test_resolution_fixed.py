import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 TESTING FIXED RESOLUTION BUTTONS")
print("="*50)

# Login with existing user
login_data = {"email": "finaltest@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=login_data)
data = response.json()
token = data["access_token"]
user_id = data["user"]["id"]

# Test different scenarios
test_scenarios = [
    {
        "name": "Simple workplace concern",
        "message": "I'm feeling stressed about my workload",
        "should_show_buttons": "Maybe (depends on AI response)"
    },
    {
        "name": "Manager relationship issue", 
        "message": "My manager and I don't communicate well",
        "should_show_buttons": "Maybe (depends on AI response)"
    },
    {
        "name": "Career growth question",
        "message": "How can I grow in my career here?",
        "should_show_buttons": "Maybe (depends on AI response)"
    },
    {
        "name": "Specific problem seeking solutions",
        "message": "My colleagues don't include me in meetings and I feel left out",
        "should_show_buttons": "Likely YES"
    }
]

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n--- SCENARIO {i}: {scenario['name']} ---")
    print(f"Message: {scenario['message']}")
    print(f"Expected: {scenario['should_show_buttons']}")
    
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
        conversation_id = data.get('conversation_id')
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Show Resolution Buttons: {show_buttons}")
        print(f"Ticket Created: {ticket_created}")
        print(f"Conversation ID: {conversation_id}")
        
        # Analyze response characteristics
        has_questions = ai_response.count('?') > 0
        has_numbered_list = '1.' in ai_response and '2.' in ai_response
        has_investigation = any(phrase in ai_response.lower() for phrase in ['could you', 'can you tell me', 'please share', 'more details'])
        response_length = len(ai_response)
        
        print(f"Response analysis:")
        print(f"  - Has questions: {has_questions}")
        print(f"  - Has numbered list: {has_numbered_list}")
        print(f"  - Is investigation: {has_investigation}")
        print(f"  - Length: {response_length}")
        
        if show_buttons:
            print("✅ RESOLUTION BUTTONS SHOWN")
            
            # Test one of the buttons
            if conversation_id:
                print("Testing 'This helps' button...")
                resolution_data = {"conversation_id": conversation_id, "resolution": "helpful"}
                response = requests.post(f"{base_url}/api/chat/resolution", json=resolution_data, headers=headers)
                if response.status_code == 200:
                    res_data = response.json()
                    print(f"✅ Button works: {res_data.get('message', '')[:100]}...")
                else:
                    print(f"❌ Button failed: {response.text}")
        else:
            print("❌ NO RESOLUTION BUTTONS")
            
        # Determine if this is appropriate
        if has_investigation:
            if not show_buttons:
                print("✅ CORRECT: No buttons for investigation questions")
            else:
                print("⚠️  QUESTIONABLE: Buttons shown for investigation")
        elif has_numbered_list or (response_length > 200 and not has_investigation):
            if show_buttons:
                print("✅ CORRECT: Buttons shown for solution response")
            else:
                print("❌ ISSUE: Should show buttons for solutions")
        
    else:
        print(f"❌ Chat failed: {response.text}")

print("\n" + "="*50)
print("RESOLUTION BUTTONS TEST COMPLETE")
print("="*50)
