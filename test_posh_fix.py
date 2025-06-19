import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 TESTING FIXED POSH COMPLAINT HANDLING")
print("="*60)

# Create a new test user for clean testing
register_data = {
    "name": "POSH Test User",
    "email": "poshtest2@example.com", 
    "password": "test123",
    "role": "employee"
}

response = requests.post(f"{base_url}/api/auth/register", json=register_data)
if response.status_code == 200:
    user_data = response.json()
    token = user_data["access_token"]
    user_id = user_data["user"]["id"]
    
    print(f"✅ User created successfully. User ID: {user_id}")
    
    # Test the exact scenario the user mentioned
    test_messages = [
        "I want to raise a POSH complaint",
        "I want to raise POSH complaint against my manager",
        "I need to file a POSH complaint for sexual harassment",
        "POSH complaint - sexual harassment by colleague"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- TEST {i}: {message} ---")
        
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
            show_buttons = data.get('show_resolution_buttons', False)
            
            print(f"AI Response:")
            print(f"  {ai_response}")
            print(f"Ticket Created: {ticket_created}")
            print(f"Ticket ID: {ticket_id}")
            print(f"Resolution Buttons: {show_buttons}")
            
            # Check if the response is appropriate
            inappropriate_phrases = [
                "could you please share",
                "more details about the incident",
                "what happened",
                "can you provide more information",
                "tell me more about"
            ]
            
            is_appropriate = not any(phrase in ai_response.lower() for phrase in inappropriate_phrases)
            mentions_escalation = "escalated" in ai_response.lower() or "hr team" in ai_response.lower()
            mentions_confidentiality = "confidentiality" in ai_response.lower() or "safety" in ai_response.lower()
            
            print(f"\nResponse Analysis:")
            print(f"  - Does NOT ask for details: {'✅' if is_appropriate else '❌'}")
            print(f"  - Mentions escalation to HR: {'✅' if mentions_escalation else '❌'}")
            print(f"  - Mentions confidentiality/safety: {'✅' if mentions_confidentiality else '❌'}")
            print(f"  - Ticket automatically created: {'✅' if ticket_created else '❌'}")
            print(f"  - No resolution buttons (correct): {'✅' if not show_buttons else '❌'}")
            
            if is_appropriate and mentions_escalation and mentions_confidentiality and ticket_created and not show_buttons:
                print(f"✅ PERFECT POSH RESPONSE!")
            else:
                print(f"❌ RESPONSE NEEDS IMPROVEMENT")
                
        else:
            print(f"❌ Chat failed: {response.text}")

else:
    print(f"❌ User creation failed: {response.text}")

print("\n" + "="*60)
print("POSH COMPLAINT FIX TEST COMPLETE")
print("="*60)
