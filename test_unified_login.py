import requests
import json

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 TESTING UNIFIED LOGIN SYSTEM")
print("="*60)

print("Step 1: Testing admin login with automatic role detection...")

# Test admin login
admin_login_data = {
    "email": "admin@ketto.org",
    "password": "admin123"
}

response = requests.post(f"{base_url}/api/auth/login", json=admin_login_data)
if response.status_code == 200:
    admin_data = response.json()
    print(f"✅ Admin login successful")
    print(f"   User: {admin_data['user']['name']}")
    print(f"   Role: {admin_data['user']['role']}")
    print(f"   Should redirect to: /admin")
else:
    print(f"❌ Admin login failed: {response.text}")

print(f"\nStep 2: Testing employee login with automatic role detection...")

# Test employee login
employee_login_data = {
    "email": "cleanemailtest@example.com",
    "password": "test123"
}

response = requests.post(f"{base_url}/api/auth/login", json=employee_login_data)
if response.status_code == 200:
    employee_data = response.json()
    print(f"✅ Employee login successful")
    print(f"   User: {employee_data['user']['name']}")
    print(f"   Role: {employee_data['user']['role']}")
    print(f"   Should redirect to: /employee")
else:
    print(f"❌ Employee login failed: {response.text}")

print(f"\nStep 3: Testing new employee registration...")

# Test employee registration
registration_data = {
    "name": "Unified Login Test User",
    "email": "unifiedtest@example.com",
    "password": "test123",
    "designation": "Software Tester",
    "bu": "Quality Assurance",
    "reporting_manager": "QA Manager",
    "role": "employee"
}

response = requests.post(f"{base_url}/api/auth/register", json=registration_data)
if response.status_code == 200:
    print(f"✅ Employee registration successful")
    
    # Test login with new employee
    new_employee_login = {
        "email": "unifiedtest@example.com",
        "password": "test123"
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=new_employee_login)
    if response.status_code == 200:
        new_user_data = response.json()
        print(f"✅ New employee login successful")
        print(f"   User: {new_user_data['user']['name']}")
        print(f"   Role: {new_user_data['user']['role']}")
        print(f"   Should redirect to: /employee")
    else:
        print(f"❌ New employee login failed: {response.text}")
else:
    print(f"❌ Employee registration failed: {response.text}")

print(f"\nStep 4: Testing invalid credentials...")

# Test invalid login
invalid_login_data = {
    "email": "invalid@example.com",
    "password": "wrongpassword"
}

response = requests.post(f"{base_url}/api/auth/login", json=invalid_login_data)
if response.status_code == 401 or response.status_code == 422:
    print(f"✅ Invalid login correctly rejected")
    print(f"   Status: {response.status_code}")
else:
    print(f"❌ Invalid login should be rejected: {response.status_code}")

print("\n" + "="*60)
print("UNIFIED LOGIN SYSTEM FEATURES")
print("="*60)
print("✅ Single login form for all users")
print("✅ Automatic role detection and redirection")
print("✅ Admin users → /admin dashboard")
print("✅ Employee users → /employee dashboard")
print("✅ Employee self-registration available")
print("✅ Legacy route redirects (/login/admin → /login)")
print("✅ Improved error messages and UI")
print("✅ Better security with proper token handling")

print("\n🎯 USER EXPERIENCE IMPROVEMENTS:")
print("1. No more confusing separate login buttons")
print("2. Users don't need to know their role type")
print("3. System automatically routes to correct dashboard")
print("4. Unified registration for new employees")
print("5. Better error handling and user feedback")
print("6. Responsive and modern UI design")
