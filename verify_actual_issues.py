import requests
import json
import base64

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 VERIFYING ACTUAL USER ISSUES")
print("="*60)

# Login as admin
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
admin_data = response.json()
token = admin_data["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("✅ Admin login successful")

# Test 1: Create a user via CSV and verify login
print("\n📝 TEST 1: CSV Upload and Login Verification")
csv_content = """name,email,password,role,designation
Test User New,testnew@example.com,password123,employee,Tester"""

csv_data = {"file_content": base64.b64encode(csv_content.encode()).decode()}
response = requests.post(f"{base_url}/api/admin/upload-users", json=csv_data, headers=headers)

if response.status_code == 200:
    print("✅ CSV upload successful")
    
    # Try to login immediately
    test_login = {"email": "testnew@example.com", "password": "password123"}
    login_response = requests.post(f"{base_url}/api/auth/login", json=test_login)
    
    if login_response.status_code == 200:
        print("✅ CSV user can login immediately after upload")
    else:
        print(f"❌ CSV user CANNOT login: {login_response.status_code}")
        print(f"Error: {login_response.text}")

# Test 2: User update functionality  
print("\n👤 TEST 2: User Update Verification")
response = requests.get(f"{base_url}/api/admin/users", headers=headers)
users = response.json()

# Find the test user we just created
test_user = None
for user in users:
    if user['email'] == 'testnew@example.com':
        test_user = user
        break

if test_user:
    print(f"📝 Found test user: {test_user['name']}")
    
    # Try to update the user
    update_data = {
        "name": "Updated Test User",
        "designation": "Senior Tester",
        "password": "newpassword456"
    }
    
    update_response = requests.put(f"{base_url}/api/admin/users/{test_user['id']}", json=update_data, headers=headers)
    
    if update_response.status_code == 200:
        print("✅ User update successful")
        
        # Test login with new password
        new_login = {"email": "testnew@example.com", "password": "newpassword456"}
        login_response = requests.post(f"{base_url}/api/auth/login", json=new_login)
        
        if login_response.status_code == 200:
            print("✅ User can login with updated password")
        else:
            print(f"❌ User CANNOT login with new password: {login_response.status_code}")
            print(f"Error: {login_response.text}")
    else:
        print(f"❌ User update FAILED: {update_response.status_code}")
        print(f"Error: {update_response.text}")

print("\n" + "="*60)
print("🎯 SUMMARY")
print("="*60)
print("If both tests show ✅, then backend APIs are working")
print("If you still see frontend errors, it's a frontend display issue")
print("If tests show ❌, then there are actual backend problems")
