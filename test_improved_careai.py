import requests
import json

base_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"

print("🔍 TESTING IMPROVED CAREAI BEHAVIOR")
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
    
    # Test the same scenarios with improved CareAI
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
            "name": "Team Conflict",
            "message": "I'm having conflicts with my team members"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- SCENARIO {i}: {scenario['name']} ---")
        print(f"Employee: {scenario['message']}")
        
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
            
            print(f"CareAI: {ai_response}")
            
            # Analyze improvement
            word_count = len(ai_response.split())
            has_directive_language = any(phrase in ai_response.lower() for phrase in [
                'here\'s', 'follow these', 'use this', 'schedule', 'tell your', 'say:', 'this works'
            ])
            has_immediate_solution = any(phrase in ai_response.lower() for phrase in [
                '1)', '2)', '3)', 'immediate', 'plan:', 'steps'
            ])
            question_count = ai_response.count('?')
            
            print(f"\n📊 Analysis:")
            print(f"  - Word count: {word_count} (target: <80 words)")
            print(f"  - Directive language: {'✅' if has_directive_language else '❌'}")
            print(f"  - Immediate solutions: {'✅' if has_immediate_solution else '❌'}")
            print(f"  - Questions asked: {question_count}")
            print(f"  - Resolution buttons: {'✅' if show_buttons else '❌'}")
            print(f"  - Ticket created: {'✅' if ticket_created else '❌'}")
            
            # Overall assessment
            if word_count <= 80 and has_directive_language and question_count <= 1:
                print(f"  🎯 EXCELLENT: Confident, concise, solution-focused!")
            elif word_count <= 120 and has_directive_language:
                print(f"  ✅ GOOD: Directive but could be more concise")
            else:
                print(f"  ⚠️  NEEDS IMPROVEMENT: Still too wordy or not directive enough")
                
        else:
            print(f"❌ Chat failed: {response.text}")

print("\n" + "="*60)
print("🎯 CAREAI IMPROVEMENT RESULTS")
print("="*60)
print("Expected improvements:")
print("✅ More confident and directive language")
print("✅ Immediate solutions with specific steps")
print("✅ Shorter, more concise responses")
print("✅ Less investigation, more problem-solving")
print("✅ Makes employees feel CareAI is THE solution")
