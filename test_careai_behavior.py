import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 TESTING CURRENT CAREAI BEHAVIOR")
print("="*60)

# Login as employee
employee_login = {"email": "cleanemailtest@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=employee_login)
if response.status_code == 200:
    employee_data = response.json()
    token = employee_data["access_token"]
    user_id = employee_data["user"]["id"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Employee login successful")
    
    # Test various workplace scenarios
    test_scenarios = [
        {
            "name": "Workload Stress",
            "message": "I'm feeling overwhelmed with my workload"
        },
        {
            "name": "Manager Issues", 
            "message": "My manager doesn't communicate clearly"
        },
        {
            "name": "Career Growth",
            "message": "I want to grow in my career but don't know how"
        },
        {
            "name": "Resignation Thoughts",
            "message": "I'm thinking about leaving the company"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- SCENARIO {i}: {scenario['name']} ---")
        print(f"Employee message: {scenario['message']}")
        
        chat_data = {
            "message": scenario['message'],
            "user_id": user_id
        }
        
        response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '')
            show_buttons = data.get('show_resolution_buttons', False)
            ticket_created = data.get('ticket_created', False)
            
            print(f"CareAI Response: {ai_response}")
            print(f"Response Length: {len(ai_response)} characters")
            print(f"Show Resolution Buttons: {show_buttons}")
            print(f"Ticket Created: {ticket_created}")
            
            # Analyze response characteristics
            word_count = len(ai_response.split())
            has_questions = ai_response.count('?')
            mentions_departments = any(dept in ai_response.lower() for dept in ['hr', 'manager', 'department', 'team lead'])
            is_directive = any(phrase in ai_response.lower() for phrase in ['here is', 'here are', 'follow these', 'use this'])
            
            print(f"Analysis:")
            print(f"  - Word count: {word_count}")
            print(f"  - Questions asked: {has_questions}")
            print(f"  - Mentions other departments: {mentions_departments}")
            print(f"  - Directive language: {is_directive}")
            
            # Assess if response is too wordy or routing-focused
            if word_count > 100:
                print(f"  ⚠️  Response is wordy (>100 words)")
            if mentions_departments and not is_directive:
                print(f"  ⚠️  Routes to other departments without strong guidance")
            if has_questions > 2:
                print(f"  ⚠️  Asks too many questions")
                
        else:
            print(f"❌ Chat failed: {response.text}")

print("\n" + "="*60)
print("CAREAI BEHAVIOR ANALYSIS COMPLETE")
print("="*60)
print("📊 Review the responses above to identify:")
print("1. Wordiness issues (responses too long)")
print("2. Routing behavior (directing to other departments)")
print("3. Lack of confidence (too many questions, vague language)")
print("4. Missing direct solutions")
