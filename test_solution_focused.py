import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🎯 TESTING SOLUTION-FOCUSED CAREAI")
print("="*60)

# Create new employee for clean testing
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
admin_response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
admin_token = admin_response.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# Create employee via admin
register_data = {
    "name": "Solution Test User",
    "email": "solutiontest@example.com",
    "password": "test123",
    "role": "employee"
}
requests.post(f"{base_url}/api/admin/users", json=register_data, headers=admin_headers)

# Login as employee
employee_login = {"email": "solutiontest@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=employee_login)
employee_data = response.json()
token = employee_data["access_token"]
user_id = employee_data["user"]["id"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("✅ Employee login successful")

# Simulate the same problematic conversation flow
conversation_steps = [
    "Not good",
    "My manager is not supportive", 
    "he is not providing guidance on solving my performance issue I tried talking to him but he never provide solution"
]

print("\n🔄 Testing improved conversation flow...")

for i, message in enumerate(conversation_steps, 1):
    print(f"\n--- STEP {i} ---")
    print(f"Employee: {message}")
    
    chat_data = {
        "message": message,
        "user_id": user_id
    }
    
    response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        ai_response = data.get('response', '')
        show_buttons = data.get('show_resolution_buttons', False)
        
        print(f"CareAI: {ai_response}")
        
        # Analyze response quality
        question_count = ai_response.count('?')
        has_solutions = any(word in ai_response.lower() for word in ['here are', 'here\'s', '1.', '2.', '3.', 'you can'])
        word_count = len(ai_response.split())
        asks_for_more_details = any(phrase in ai_response.lower() for phrase in ['tell me more', 'can you share', 'more about'])
        
        print(f"Analysis:")
        print(f"  - Questions asked: {question_count}")
        print(f"  - Provides solutions: {'✅' if has_solutions else '❌'}")
        print(f"  - Word count: {word_count}")
        print(f"  - Asks for more details: {'❌' if asks_for_more_details else '✅'}")
        print(f"  - Resolution buttons: {show_buttons}")
        
        # Assessment for step 3 (should provide solutions)
        if i == 3:
            if has_solutions and not asks_for_more_details:
                print(f"  🌟 EXCELLENT: Provides solutions instead of more questions!")
            elif has_solutions:
                print(f"  ✅ GOOD: Has solutions but still asking questions")
            else:
                print(f"  ❌ POOR: Still asking questions instead of providing solutions")
                
    else:
        print(f"❌ Chat failed: {response.text}")

print("\n" + "="*60)
print("🎯 SOLUTION-FOCUSED ASSESSMENT")
print("="*60)
print("Expected behavior:")
print("✅ Step 1: Quick clarifying question")  
print("✅ Step 2: May ask 1 more question")
print("✅ Step 3: Should provide 3-4 specific solutions")
print("❌ Should NOT keep asking endless questions")
print("❌ Should NOT ask for details already provided")
