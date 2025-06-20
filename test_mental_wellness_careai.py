import requests
import json

base_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"

print("🧠 TESTING MENTAL WELLNESS CAREAI")
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
    
    # Test mental wellness scenarios
    mental_wellness_scenarios = [
        {
            "name": "Feeling Overwhelmed",
            "message": "I'm feeling overwhelmed with my workload and stressed"
        },
        {
            "name": "Want to Resign",
            "message": "I want to resign because I don't feel valued"
        },
        {
            "name": "Unsupportive Manager", 
            "message": "My manager is not supportive and it's affecting my confidence"
        },
        {
            "name": "Work-Life Balance",
            "message": "I'm struggling with work-life balance and it's affecting my mental health"
        }
    ]
    
    for i, scenario in enumerate(mental_wellness_scenarios, 1):
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
            
            # Analyze mental wellness qualities
            empathy_phrases = [
                'understand', 'sorry', 'tough', 'difficult', 'valid', 'normal', 
                'feel', 'not alone', 'support', 'here for you'
            ]
            
            solution_phrases = [
                'here\'s how', 'steps', 'approach', 'strategy', 'solution', 'help'
            ]
            
            has_empathy = any(phrase in ai_response.lower() for phrase in empathy_phrases)
            has_solutions = any(phrase in ai_response.lower() for phrase in solution_phrases)
            asks_for_understanding = '?' in ai_response
            word_count = len(ai_response.split())
            
            print(f"\n🧠 Mental Wellness Analysis:")
            print(f"  - Shows empathy/validation: {'✅' if has_empathy else '❌'}")
            print(f"  - Provides supportive guidance: {'✅' if has_solutions else '❌'}")
            print(f"  - Seeks understanding: {'✅' if asks_for_understanding else '❌'}")
            print(f"  - Appropriate length: {'✅' if 50 <= word_count <= 150 else '❌'} ({word_count} words)")
            print(f"  - Resolution buttons: {'✅' if show_buttons else '❌'}")
            print(f"  - Escalated if needed: {'✅' if ticket_created else '❌'}")
            
            # Overall mental wellness score
            wellness_score = sum([has_empathy, has_solutions, asks_for_understanding])
            if wellness_score >= 3:
                print(f"  🌟 EXCELLENT: Proper mental wellness support!")
            elif wellness_score >= 2:
                print(f"  ✅ GOOD: Supportive but could be more empathetic")
            else:
                print(f"  ⚠️  NEEDS IMPROVEMENT: Not empathetic enough")
                
        else:
            print(f"❌ Chat failed: {response.text}")

print("\n" + "="*60)
print("🧠 MENTAL WELLNESS ASSESSMENT")
print("="*60)
print("Expected qualities:")
print("✅ Empathetic acknowledgment of feelings")
print("✅ Emotional validation and support")
print("✅ Caring, compassionate tone")
print("✅ Understanding before solutions")
print("✅ Making employees feel heard and supported")
print("✅ Building trust and psychological safety")
