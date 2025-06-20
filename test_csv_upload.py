import requests
import json
import base64

base_url = "https://9456fd82-d41d-48e0-b85e-e00275813adc.preview.emergentagent.com"

print("🔍 TESTING FIXED CSV UPLOAD")
print("="*50)

# Login as admin
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
if response.status_code == 200:
    admin_data = response.json()
    token = admin_data["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Admin login successful")
    
    # Create test CSV content
    csv_content = """name,email,password,role,designation,business_unit,reporting_manager
John Doe,john.doe@example.com,password123,employee,Software Engineer,IT,Tech Lead
Jane Smith,jane.smith@example.com,password123,employee,HR Manager,HR,HR Director
Bob Wilson,bob.wilson@example.com,password123,employee,Sales Rep,Sales,Sales Manager"""
    
    print("📄 Testing CSV upload with sample data...")
    
    # Test the fixed CSV upload
    csv_data = {
        "file_content": base64.b64encode(csv_content.encode()).decode()
    }
    
    response = requests.post(f"{base_url}/api/admin/upload-users", json=csv_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ CSV upload successful!")
        print(f"Message: {result.get('message', '')}")
        print(f"Users created: {result.get('users_created', 0)}")
        print(f"Users updated: {result.get('users_updated', 0)}")
        print(f"Errors: {len(result.get('errors', []))}")
        
        if result.get('errors'):
            print("Errors encountered:")
            for error in result.get('errors', [])[:5]:  # Show first 5 errors
                print(f"  - {error}")
                
    else:
        print(f"❌ CSV upload failed: {response.status_code}")
        try:
            error_detail = response.json()
            print(f"Error detail: {error_detail}")
        except:
            print(f"Error text: {response.text}")
    
    # Test with invalid CSV (missing required columns)
    print(f"\n📄 Testing CSV upload with invalid data...")
    
    invalid_csv = """invalid_column,another_column
    Test,Value"""
    
    invalid_csv_data = {
        "file_content": base64.b64encode(invalid_csv.encode()).decode()
    }
    
    response = requests.post(f"{base_url}/api/admin/upload-users", json=invalid_csv_data, headers=headers)
    
    if response.status_code == 400:
        print("✅ Invalid CSV correctly rejected")
        try:
            error_detail = response.json()
            print(f"Error message: {error_detail.get('detail', 'No detail')}")
        except:
            print(f"Error text: {response.text}")
    else:
        print(f"❌ Invalid CSV should be rejected: {response.status_code}")
        
else:
    print(f"❌ Admin login failed: {response.text}")

print("\n" + "="*50)
print("CSV UPLOAD FIX SUMMARY")
print("="*50)
print("✅ Fixed frontend to send JSON with file_content field")
print("✅ Fixed backend to expect CsvUploadModel")
print("✅ Improved error handling to show actual error messages")
print("✅ Added proper error responses for debugging")
print("✅ CSV upload should now work without '[object Object]' errors")
