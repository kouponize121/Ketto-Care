import requests
import sys
import json
import time
from datetime import datetime

class ResolutionButtonsTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.conversation_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        
        if not headers:
            headers = {'Content-Type': 'application/json'}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            
            success = response.status_code == expected_status
            if success:
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def init_admin(self):
        """Initialize admin user"""
        return self.run_test("Initialize Admin", "POST", "init-admin", 200)

    def register_employee(self):
        """Register a test employee"""
        timestamp = datetime.now().strftime("%H%M%S")
        employee_data = {
            "name": f"Test Employee {timestamp}",
            "email": f"employee{timestamp}@test.com",
            "password": "test123",
            "role": "employee"
        }
        
        success, response = self.run_test(
            "Employee Registration",
            "POST",
            "auth/register",
            200,
            data=employee_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"Employee registration successful, token obtained")
            return True, employee_data
        return False, None

    def test_chat_with_ai(self, message):
        """Test chat with AI"""
        if not self.token or not self.user_id:
            print("❌ Cannot test chat: No employee token or ID")
            return False, None
            
        success, response = self.run_test(
            "Chat with CareAI",
            "POST",
            "chat",
            200,
            data={"message": message, "user_id": self.user_id}
        )
        
        if success:
            ai_response = response.get('response', '')
            ticket_created = response.get('ticket_created', False)
            show_resolution_buttons = response.get('show_resolution_buttons', False)
            conversation_id = response.get('conversation_id')
            
            print(f"AI Response: {ai_response[:150]}...")
            print(f"Ticket created: {ticket_created}")
            print(f"Show resolution buttons: {show_resolution_buttons}")
            
            if conversation_id:
                print(f"Conversation ID: {conversation_id}")
                self.conversation_id = conversation_id
            
            return True, response
        return False, None

    def test_resolution_response(self, resolution):
        """Test resolution button response"""
        if not self.conversation_id:
            print("❌ No conversation ID available for resolution test")
            return False, None
            
        success, response = self.run_test(
            f"Resolution Response ({resolution})",
            "POST",
            "chat/resolution",
            200,
            data={
                "conversation_id": self.conversation_id,
                "resolution": resolution  # 'helpful' or 'need_help'
            }
        )
        
        if success:
            print(f"Response: {response.get('message', '')[:100]}...")
            print(f"Ticket Created: {response.get('ticket_created', False)}")
            if response.get('ticket_created'):
                print(f"Ticket ID: {response.get('ticket_id')}")
            return True, response
        return False, None

def main():
    base_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    tester = ResolutionButtonsTester(base_url)
    
    # Initialize admin
    tester.init_admin()
    
    # Register employee
    reg_success, employee_data = tester.register_employee()
    if not reg_success:
        print("❌ Employee registration failed, stopping tests")
        return 1
    
    # Test scenarios that should trigger resolution buttons
    test_scenarios = [
        {
            "name": "Resignation concern",
            "message": "I'm thinking about resigning because of my manager"
        },
        {
            "name": "Manager issues",
            "message": "I'm having problems with my manager, they micromanage me"
        },
        {
            "name": "Workplace stress",
            "message": "I'm feeling very stressed about my workload"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n===== TESTING SCENARIO: {scenario['name']} =====")
        
        # Send the message
        chat_success, chat_response = tester.test_chat_with_ai(scenario['message'])
        
        if not chat_success:
            print(f"❌ Failed to send message for {scenario['name']}")
            continue
        
        # Check if show_resolution_buttons is in the response
        if 'show_resolution_buttons' not in chat_response:
            print(f"❌ 'show_resolution_buttons' field missing in chat response for {scenario['name']}")
        else:
            show_buttons = chat_response.get('show_resolution_buttons', False)
            print(f"✅ 'show_resolution_buttons' field present: {show_buttons}")
            
            # If we have a conversation ID and buttons should be shown, test both resolution options
            if tester.conversation_id and show_buttons:
                # Test "This helps" resolution
                print("\nTesting 'This helps' resolution button...")
                helpful_success, helpful_response = tester.test_resolution_response("helpful")
                
                # Create a new conversation for "Still need help"
                print("\nCreating new conversation to test 'Still need help' button...")
                new_chat_success, new_chat_response = tester.test_chat_with_ai(f"I'm having issues with {scenario['name'].lower()}")
                
                if new_chat_success and 'show_resolution_buttons' in new_chat_response and new_chat_response['show_resolution_buttons']:
                    # Test "Still need help" resolution
                    print("\nTesting 'Still need help' resolution button...")
                    need_help_success, need_help_response = tester.test_resolution_response("need_help")
    
    print("\n===== RESOLUTION BUTTONS TESTING COMPLETE =====")
    return 0

if __name__ == "__main__":
    sys.exit(main())