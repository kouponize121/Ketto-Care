import requests
import json
import time
from datetime import datetime

class AIConversationTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.employee_token = None
        self.employee_id = None
        self.test_ticket_id = None
        self.ai_conversation_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, admin=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        elif admin and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
        elif self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
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

    def test_init_admin(self):
        """Test admin initialization"""
        return self.run_test("Initialize Admin", "POST", "api/init-admin", 200)

    def test_admin_login(self, email="admin@ketto.org", password="admin123"):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": email, "password": password}
        )
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"Admin login successful, token obtained")
            return True
        return False

    def test_employee_registration(self):
        """Test employee registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        employee_data = {
            "name": f"Test Employee {timestamp}",
            "email": f"employee{timestamp}@test.com",
            "password": "test123",
            "role": "employee",
            "designation": "Software Engineer",
            "business_unit": "Engineering",
            "reporting_manager": "John Doe"
        }
        
        success, response = self.run_test(
            "Employee Registration",
            "POST",
            "api/auth/register",
            200,
            data=employee_data
        )
        
        if success and 'access_token' in response:
            self.employee_token = response['access_token']
            self.employee_id = response['user']['id']
            print(f"Employee registration successful, token obtained")
            return True, employee_data
        return False, None

    def test_chat_with_careai(self, message="I'm feeling stressed at work"):
        """Test chat with CareAI"""
        if not self.token or not self.employee_id:
            print("❌ Cannot test chat: No employee token or ID")
            return False, None
            
        success, response = self.run_test(
            "Chat with CareAI",
            "POST",
            "api/chat",
            200,
            data={"message": message, "user_id": self.employee_id},
            token=self.token
        )
        
        if success:
            ai_response = response.get('response', '')
            print(f"AI Response: {ai_response[:100]}...")
            print(f"Ticket created: {response.get('ticket_created', False)}")
            if response.get('ticket_created'):
                print(f"Ticket ID: {response.get('ticket_id')}")
                self.test_ticket_id = response.get('ticket_id')
            
            return True, response
        return False, None

    def test_follow_up_chat(self, initial_message="I'm feeling stressed at work", follow_up_message="No, I'm still struggling with my workload"):
        """Test the follow-up chat flow that should create a ticket"""
        if not self.token or not self.employee_id:
            print("❌ Cannot test follow-up chat: No employee token or ID")
            return False, None
        
        # First message to establish context
        print("\n🔍 Testing initial chat message...")
        initial_success, initial_response = self.test_chat_with_careai(initial_message)
        
        if not initial_success:
            print("❌ Failed to send initial message")
            return False, None
        
        # Check if a ticket was created on the first message
        if initial_response.get('ticket_created', False):
            print("⚠️ Ticket was created on initial message, which is not expected for the follow-up flow")
        
        # Get AI conversations to check if one was created
        if self.admin_token:
            print("\n🔍 Checking if AI conversation was created...")
            conv_success, conversations = self.run_test(
                "Get AI Conversations",
                "GET",
                "api/admin/ai-conversations",
                200,
                token=self.admin_token
            )
            
            if conv_success and conversations:
                # Find the conversation for this employee
                employee_conversations = [c for c in conversations if c['user_id'] == self.employee_id]
                if employee_conversations:
                    self.ai_conversation_id = employee_conversations[0]['id']
                    print(f"✅ Found AI conversation: {self.ai_conversation_id}")
                    print(f"Resolution status: {employee_conversations[0]['resolution_status']}")
                    
                    # Verify it's in pending status
                    if employee_conversations[0]['resolution_status'] != 'pending':
                        print(f"❌ Expected 'pending' status, got '{employee_conversations[0]['resolution_status']}'")
                else:
                    print("❌ No AI conversation found for this employee")
        
        # Wait a moment to ensure the conversation is processed
        time.sleep(2)
        
        # Send follow-up message indicating the issue is not resolved
        print("\n🔍 Testing follow-up message indicating issue not resolved...")
        follow_up_success, follow_up_response = self.test_chat_with_careai(follow_up_message)
        
        if not follow_up_success:
            print("❌ Failed to send follow-up message")
            return False, None
        
        # Check if a ticket was created on the follow-up message
        ticket_created = follow_up_response.get('ticket_created', False)
        print(f"Ticket created on follow-up: {ticket_created}")
        
        # Check AI conversation status after follow-up
        if self.admin_token and self.ai_conversation_id:
            print("\n🔍 Checking if AI conversation status was updated...")
            conv_success, conversations = self.run_test(
                "Get AI Conversations",
                "GET",
                "api/admin/ai-conversations",
                200,
                token=self.admin_token
            )
            
            if conv_success and conversations:
                # Find the conversation by ID
                conversation = next((c for c in conversations if c['id'] == self.ai_conversation_id), None)
                if conversation:
                    print(f"✅ Found AI conversation after follow-up")
                    print(f"Resolution status: {conversation['resolution_status']}")
                    
                    # Verify it's now escalated
                    if conversation['resolution_status'] == 'escalated':
                        print("✅ Conversation was correctly escalated after negative follow-up")
                        if conversation['ticket_id']:
                            print(f"✅ Ticket was linked to conversation: {conversation['ticket_id']}")
                            return True, follow_up_response
                        else:
                            print("❌ No ticket linked to escalated conversation")
                    else:
                        print(f"❌ Expected 'escalated' status, got '{conversation['resolution_status']}'")
                else:
                    print("❌ Could not find the AI conversation after follow-up")
        
        return ticket_created, follow_up_response

    def test_positive_follow_up_chat(self, initial_message="I'm feeling stressed at work", follow_up_message="Yes, that helps a lot. Thank you!"):
        """Test the follow-up chat flow with a positive response that should resolve the conversation"""
        if not self.token or not self.employee_id:
            print("❌ Cannot test positive follow-up chat: No employee token or ID")
            return False, None
        
        # First message to establish context
        print("\n🔍 Testing initial chat message...")
        initial_success, initial_response = self.test_chat_with_careai(initial_message)
        
        if not initial_success:
            print("❌ Failed to send initial message")
            return False, None
        
        # Get AI conversations to check if one was created
        if self.admin_token:
            print("\n🔍 Checking if AI conversation was created...")
            conv_success, conversations = self.run_test(
                "Get AI Conversations",
                "GET",
                "api/admin/ai-conversations",
                200,
                token=self.admin_token
            )
            
            if conv_success and conversations:
                # Find the conversation for this employee
                employee_conversations = [c for c in conversations if c['user_id'] == self.employee_id]
                if employee_conversations:
                    self.ai_conversation_id = employee_conversations[0]['id']
                    print(f"✅ Found AI conversation: {self.ai_conversation_id}")
                    print(f"Resolution status: {employee_conversations[0]['resolution_status']}")
                else:
                    print("❌ No AI conversation found for this employee")
        
        # Wait a moment to ensure the conversation is processed
        time.sleep(2)
        
        # Send follow-up message indicating the issue is resolved
        print("\n🔍 Testing positive follow-up message...")
        follow_up_success, follow_up_response = self.test_chat_with_careai(follow_up_message)
        
        if not follow_up_success:
            print("❌ Failed to send follow-up message")
            return False, None
        
        # Check if a ticket was created (should not be)
        ticket_created = follow_up_response.get('ticket_created', False)
        if ticket_created:
            print("❌ Ticket was created on positive follow-up, which is not expected")
        else:
            print("✅ No ticket created on positive follow-up, as expected")
        
        # Check AI conversation status after follow-up
        if self.admin_token and self.ai_conversation_id:
            print("\n🔍 Checking if AI conversation status was updated...")
            conv_success, conversations = self.run_test(
                "Get AI Conversations",
                "GET",
                "api/admin/ai-conversations",
                200,
                token=self.admin_token
            )
            
            if conv_success and conversations:
                # Find the conversation by ID
                conversation = next((c for c in conversations if c['id'] == self.ai_conversation_id), None)
                if conversation:
                    print(f"✅ Found AI conversation after positive follow-up")
                    print(f"Resolution status: {conversation['resolution_status']}")
                    
                    # Verify it's now resolved
                    if conversation['resolution_status'] == 'resolved':
                        print("✅ Conversation was correctly marked as resolved after positive follow-up")
                        return True, follow_up_response
                    else:
                        print(f"❌ Expected 'resolved' status, got '{conversation['resolution_status']}'")
                else:
                    print("❌ Could not find the AI conversation after follow-up")
        
        return not ticket_created, follow_up_response

    def test_admin_mark_conversation_reviewed(self):
        """Test admin marking a conversation as reviewed"""
        if not self.admin_token or not self.ai_conversation_id:
            print("❌ Cannot test marking conversation as reviewed: No admin token or conversation ID")
            return False
        
        print("\n🔍 Testing admin marking conversation as reviewed...")
        success, response = self.run_test(
            "Mark Conversation as Reviewed",
            "PUT",
            f"api/admin/ai-conversations/{self.ai_conversation_id}",
            200,
            data={"admin_reviewed": True},
            token=self.admin_token
        )
        
        if success:
            # Verify the update
            conv_success, conversations = self.run_test(
                "Get AI Conversations",
                "GET",
                "api/admin/ai-conversations",
                200,
                token=self.admin_token
            )
            
            if conv_success and conversations:
                # Find the conversation by ID
                conversation = next((c for c in conversations if c['id'] == self.ai_conversation_id), None)
                if conversation:
                    if conversation['admin_reviewed']:
                        print("✅ Conversation was correctly marked as reviewed")
                        return True
                    else:
                        print("❌ Conversation was not marked as reviewed")
                else:
                    print("❌ Could not find the AI conversation after update")
        
        return False

    def test_get_ai_conversations(self):
        """Test getting AI conversations as admin"""
        if not self.admin_token:
            print("❌ Cannot test getting AI conversations: No admin token")
            return False, None
        
        success, conversations = self.run_test(
            "Get AI Conversations",
            "GET",
            "api/admin/ai-conversations",
            200,
            token=self.admin_token
        )
        
        if success:
            print(f"Retrieved {len(conversations)} AI conversations")
            
            # Check if conversations have the expected fields
            if conversations:
                expected_fields = [
                    'id', 'user_id', 'user_name', 'user_email', 'conversation_summary',
                    'initial_concern', 'ai_solution_provided', 'resolution_status',
                    'ticket_id', 'created_at', 'updated_at', 'follow_up_needed', 'admin_reviewed'
                ]
                
                missing_fields = [field for field in expected_fields if field not in conversations[0]]
                if missing_fields:
                    print(f"❌ Missing expected fields in conversation data: {missing_fields}")
                else:
                    print("✅ All expected fields present in conversation data")
                
                # Check resolution status values
                statuses = set(c['resolution_status'] for c in conversations)
                print(f"Resolution statuses found: {statuses}")
                
                # Check ticket linking
                linked_tickets = [c for c in conversations if c['ticket_id']]
                print(f"Conversations with linked tickets: {len(linked_tickets)}/{len(conversations)}")
            
            return True, conversations
        
        return False, None

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    
    print(f"Testing AI Conversation Tracking at: {backend_url}")
    tester = AIConversationTester(backend_url)
    
    # Test admin initialization and login
    tester.test_init_admin()
    admin_login_success = tester.test_admin_login()
    
    # Test employee registration
    reg_success, employee_data = tester.test_employee_registration()
    if reg_success and employee_data:
        # Use the employee token for subsequent tests
        tester.token = tester.employee_token
        
        print("\n===== TESTING AI CONVERSATION TRACKING =====")
        
        # Test 1: Get AI conversations (should be empty for new employee)
        if admin_login_success:
            print("\n1. Testing AI Conversations Endpoint...")
            ai_conv_success, ai_conversations = tester.test_get_ai_conversations()
            initial_conv_count = len(ai_conversations) if ai_conversations else 0
            print(f"Initial AI conversation count: {initial_conv_count}")
        
        # Test 2: Test follow-up chat flow with negative response (should create ticket)
        print("\n2. Testing Follow-up Chat Flow with Negative Response...")
        follow_up_success, follow_up_response = tester.test_follow_up_chat(
            initial_message="I'm feeling overwhelmed with my workload",
            follow_up_message="No, I'm still struggling with the workload"
        )
        
        # Test 3: Test follow-up chat flow with positive response (should resolve conversation)
        print("\n3. Testing Follow-up Chat Flow with Positive Response...")
        positive_follow_up_success, positive_follow_up_response = tester.test_positive_follow_up_chat(
            initial_message="I need some advice on time management",
            follow_up_message="Yes, that's very helpful. Thank you!"
        )
        
        # Test 4: Admin marking conversation as reviewed
        if admin_login_success and tester.ai_conversation_id:
            print("\n4. Testing Admin Marking Conversation as Reviewed...")
            mark_reviewed_success = tester.test_admin_mark_conversation_reviewed()
        
        # Test 5: Verify AI conversations after tests
        if admin_login_success:
            print("\n5. Verifying AI Conversations After Tests...")
            final_conv_success, final_conversations = tester.test_get_ai_conversations()
            final_conv_count = len(final_conversations) if final_conversations else 0
            
            if final_conv_count > initial_conv_count:
                print(f"✅ AI conversation count increased: {initial_conv_count} -> {final_conv_count}")
            else:
                print(f"❌ AI conversation count did not increase: {initial_conv_count} -> {final_conv_count}")
    
    # Print test results
    print("\n" + "="*50)
    print(f"Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    print("="*50)
    
    # Summary of findings
    if admin_login_success and reg_success:
        print("\nSummary of AI Conversation Tracking Testing:")
        print("1. AI Conversations Endpoint: " + ("✅ Working" if 'ai_conv_success' in locals() and ai_conv_success else "❌ Issue detected"))
        print("2. Follow-up Chat Flow (Negative): " + ("✅ Working" if 'follow_up_success' in locals() and follow_up_success else "❌ Issue detected"))
        print("3. Follow-up Chat Flow (Positive): " + ("✅ Working" if 'positive_follow_up_success' in locals() and positive_follow_up_success else "❌ Issue detected"))
        print("4. Admin Marking Conversation as Reviewed: " + ("✅ Working" if 'mark_reviewed_success' in locals() and mark_reviewed_success else "❌ Issue detected"))
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    main()