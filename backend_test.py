import requests
import json
import time
import base64
import csv
import io
from datetime import datetime

class KettoCareAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.employee_token = None
        self.employee_id = None
        self.test_ticket_id = None

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

    def test_api_root(self):
        """Test basic API connectivity"""
        return self.run_test("API Root", "GET", "api", 200)

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

    def test_employee_login(self, email, password="test123"):
        """Test employee login"""
        success, response = self.run_test(
            "Employee Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": email, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"Employee login successful, token obtained")
            return True
        return False

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
            
            # Check for hidden escalation markers
            escalation_markers = ["ESCALATE:", "CATEGORY:", "SEVERITY:", "SUMMARY:"]
            for marker in escalation_markers:
                if marker in ai_response:
                    print(f"❌ Found escalation marker in response: {marker}")
                    return False, response
            
            print("✅ No escalation markers found in response")
            return True, response
        return False, None

    def test_conversation_context(self, messages=None):
        """Test conversation context with multiple messages"""
        if not self.token or not self.employee_id:
            print("❌ Cannot test conversation: No employee token or ID")
            return False, None
        
        if messages is None:
            messages = [
                "I'm not feeling well",
                "I'm having trouble with my work-life balance",
                "My targets are not getting met, I am planning to resign"
            ]
        
        print("\n🔍 Testing Conversation Context with multiple messages...")
        responses = []
        
        for i, message in enumerate(messages):
            print(f"\nMessage {i+1}: '{message}'")
            success, response = self.run_test(
                f"Chat message {i+1}",
                "POST",
                "api/chat",
                200,
                data={"message": message, "user_id": self.employee_id},
                token=self.token
            )
            
            if not success:
                print(f"❌ Failed to send message {i+1}")
                return False, responses
            
            ai_response = response.get('response', '')
            ticket_created = response.get('ticket_created', False)
            show_resolution_buttons = response.get('show_resolution_buttons', False)
            conversation_id = response.get('conversation_id')
            
            print(f"AI Response: {ai_response[:100]}...")
            print(f"Ticket created: {ticket_created}")
            print(f"Show resolution buttons: {show_resolution_buttons}")
            if conversation_id:
                print(f"Conversation ID: {conversation_id}")
            
            # Check for hidden escalation markers
            escalation_markers = ["ESCALATE:", "CATEGORY:", "SEVERITY:", "SUMMARY:"]
            for marker in escalation_markers:
                if marker in ai_response:
                    print(f"❌ Found escalation marker in response: {marker}")
                    return False, responses
            
            responses.append({
                'message': message,
                'response': ai_response,
                'ticket_created': ticket_created,
                'ticket_id': response.get('ticket_id'),
                'show_resolution_buttons': show_resolution_buttons,
                'conversation_id': conversation_id
            })
            
            # Small delay to ensure messages are processed in order
            time.sleep(1)
        
        # Analyze if the AI is using context from previous messages
        if len(responses) > 1:
            last_response = responses[-1]['response'].lower()
            
            # Check if the last response references previous messages
            context_indicators = [
                "as you mentioned", "you've shared", "from what you've told me",
                "based on our conversation", "you've been feeling", "you said",
                "you've expressed", "earlier you mentioned"
            ]
            
            has_context = any(indicator in last_response for indicator in context_indicators)
            
            if has_context:
                print("✅ AI response shows awareness of conversation context")
            else:
                print("⚠️ AI response may not be using conversation context")
        
        return True, responses

    def test_workplace_focused_responses(self):
        """Test that AI provides workplace-focused responses"""
        if not self.token or not self.employee_id:
            print("❌ Cannot test workplace focus: No employee token or ID")
            return False, None
        
        # Test cases specifically designed to check workplace focus
        test_cases = [
            {
                "message": "I'm not feeling well",
                "workplace_indicators": ["work", "workplace", "job", "office", "colleague", "manager", "team", 
                                        "workload", "project", "deadline", "stress", "balance"]
            },
            {
                "message": "My targets are not getting met, I am planning to resign",
                "workplace_indicators": ["goal", "target", "performance", "time management", "prioritize", 
                                        "skill", "development", "manager", "support", "career", "workload"]
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n🔍 Testing workplace focus with message: '{test_case['message']}'")
            success, response = self.run_test(
                f"Workplace focus test",
                "POST",
                "api/chat",
                200,
                data={"message": test_case["message"], "user_id": self.employee_id},
                token=self.token
            )
            
            if not success:
                print(f"❌ Failed to send message")
                continue
            
            ai_response = response.get('response', '').lower()
            print(f"AI Response: {ai_response[:150]}...")
            
            # Check for workplace-focused indicators
            found_indicators = []
            for indicator in test_case["workplace_indicators"]:
                if indicator.lower() in ai_response:
                    found_indicators.append(indicator)
            
            workplace_focus_score = len(found_indicators) / len(test_case["workplace_indicators"])
            print(f"Workplace focus indicators found: {len(found_indicators)}/{len(test_case['workplace_indicators'])}")
            print(f"Indicators found: {', '.join(found_indicators)}")
            
            if workplace_focus_score >= 0.3:  # At least 30% of workplace indicators
                print(f"✅ Response shows workplace focus (score: {workplace_focus_score:.2f})")
            else:
                print(f"❌ Response may lack workplace focus (score: {workplace_focus_score:.2f})")
            
            results.append({
                "message": test_case["message"],
                "response": ai_response,
                "workplace_focus_score": workplace_focus_score,
                "indicators_found": found_indicators
            })
            
            # Small delay between requests
            time.sleep(1)
        
        return len(results) > 0, results

    def test_escalation_logic(self):
        """Test the improved escalation logic"""
        if not self.token or not self.employee_id:
            print("❌ Cannot test escalation logic: No employee token or ID")
            return False, None
        
        # Test cases with different severity levels
        test_cases = [
            {
                "name": "Low severity (should not escalate)",
                "message": "I'm feeling a bit tired today, but I'll manage",
                "should_escalate": False
            },
            {
                "name": "Medium severity (should not escalate immediately)",
                "message": "I'm not meeting my targets this month",
                "should_escalate": False
            },
            {
                "name": "High severity (might escalate)",
                "message": "I'm experiencing severe anxiety about my upcoming presentation",
                "should_escalate": None  # Could go either way
            },
            {
                "name": "Critical severity (should escalate)",
                "message": "I'm being harassed by my colleague and I don't know what to do",
                "should_escalate": True
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n🔍 Testing escalation logic: {test_case['name']}")
            success, response = self.run_test(
                f"Escalation test: {test_case['name']}",
                "POST",
                "api/chat",
                200,
                data={"message": test_case["message"], "user_id": self.employee_id},
                token=self.token
            )
            
            if not success:
                print(f"❌ Failed to send message")
                continue
            
            ai_response = response.get('response', '')
            ticket_created = response.get('ticket_created', False)
            
            print(f"AI Response: {ai_response[:150]}...")
            print(f"Ticket created: {ticket_created}")
            
            # Check if escalation matches expectation
            if test_case["should_escalate"] is not None:
                if ticket_created == test_case["should_escalate"]:
                    print(f"✅ Escalation behavior matches expectation: {ticket_created}")
                else:
                    print(f"❌ Escalation behavior does not match expectation: got {ticket_created}, expected {test_case['should_escalate']}")
            else:
                print(f"ℹ️ Escalation could go either way for this case: got {ticket_created}")
            
            results.append({
                "name": test_case["name"],
                "message": test_case["message"],
                "expected_escalation": test_case["should_escalate"],
                "actual_escalation": ticket_created,
                "response": ai_response
            })
            
            # Small delay between requests
            time.sleep(1)
        
        return len(results) > 0, results

    def test_get_tickets(self):
        """Test getting employee tickets"""
        if not self.token:
            print("❌ Cannot test tickets: No employee token")
            return False, None
            
        success, response = self.run_test(
            "Get Employee Tickets",
            "GET",
            "api/tickets",
            200,
            token=self.token
        )
        
        if success:
            print(f"Retrieved {len(response)} tickets")
            return True, response
        return False, None

    def test_admin_get_tickets(self):
        """Test admin getting all tickets"""
        if not self.admin_token:
            print("❌ Cannot test admin tickets: No admin token")
            return False, None
            
        success, response = self.run_test(
            "Admin Get All Tickets",
            "GET",
            "api/admin/tickets",
            200,
            token=self.admin_token
        )
        
        if success:
            print(f"Admin retrieved {len(response)} tickets")
            return True, response
        return False, None

    def test_admin_get_users(self):
        """Test admin getting all users"""
        if not self.admin_token:
            print("❌ Cannot test admin users: No admin token")
            return False, None
            
        success, response = self.run_test(
            "Admin Get All Users",
            "GET",
            "api/admin/users",
            200,
            token=self.admin_token
        )
        
        if success:
            print(f"Admin retrieved {len(response)} users")
            return True, response
        return False, None

    def test_admin_create_user(self):
        """Test admin creating a new user"""
        if not self.admin_token:
            print("❌ Cannot test user creation: No admin token")
            return False, None
            
        timestamp = datetime.now().strftime("%H%M%S")
        user_data = {
            "name": f"Created User {timestamp}",
            "email": f"created{timestamp}@test.com",
            "password": "test123",
            "role": "employee",
            "designation": "QA Engineer",
            "business_unit": "Quality Assurance",
            "reporting_manager": "Jane Smith"
        }
        
        success, response = self.run_test(
            "Admin Create User",
            "POST",
            "api/admin/users",
            200,
            data=user_data,
            token=self.admin_token
        )
        
        if success:
            print(f"Admin successfully created user: {user_data['email']}")
            return True, user_data
        return False, None

    def test_admin_update_user(self, user_id):
        """Test admin updating a user"""
        if not self.admin_token:
            print("❌ Cannot test user update: No admin token")
            return False
            
        update_data = {
            "name": f"Updated User {datetime.now().strftime('%H%M%S')}",
            "role": "employee",
            "designation": "Updated Designation",
            "business_unit": "Updated Business Unit",
            "reporting_manager": "Updated Manager",
            "password": "newpassword123"
        }
        
        success, response = self.run_test(
            "Admin Update User",
            "PUT",
            f"api/admin/users/{user_id}",
            200,
            data=update_data,
            token=self.admin_token
        )
        
        if success:
            print(f"Admin successfully updated user with ID: {user_id}")
            # Test login with new password
            return True, update_data
        return False, None

    def test_admin_update_ticket_with_notes(self, ticket_id):
        """Test admin updating a ticket with admin notes"""
        if not self.admin_token:
            print("❌ Cannot test ticket update with notes: No admin token")
            return False
            
        update_data = {
            "status": "in_progress",
            "admin_notes": f"Test admin note added at {datetime.now().strftime('%H:%M:%S')}"
        }
        
        success, response = self.run_test(
            "Admin Update Ticket with Notes",
            "PUT",
            f"api/admin/tickets/{ticket_id}",
            200,
            data=update_data,
            token=self.admin_token
        )
        
        if success:
            print(f"Admin successfully updated ticket with notes. ID: {ticket_id}")
            
            # Verify the update by getting the ticket
            tickets_success, tickets = self.test_admin_get_tickets()
            if tickets_success:
                updated_ticket = next((t for t in tickets if t['id'] == ticket_id), None)
                if updated_ticket:
                    if updated_ticket['status'] == update_data['status'] and updated_ticket['admin_notes'] == update_data['admin_notes']:
                        print("✅ Ticket status and admin notes updated correctly")
                        return True
                    else:
                        print("❌ Ticket update verification failed")
                        print(f"Expected status: {update_data['status']}, got: {updated_ticket['status']}")
                        print(f"Expected notes: {update_data['admin_notes']}, got: {updated_ticket['admin_notes']}")
                else:
                    print("❌ Could not find updated ticket")
            return False
        return False
        
    def test_csv_bulk_user_upload(self):
        """Test CSV bulk user upload"""
        if not self.admin_token:
            print("❌ Cannot test CSV upload: No admin token")
            return False
            
        # Create CSV content with test users
        timestamp = datetime.now().strftime("%H%M%S")
        csv_data = [
            ["name", "email", "password", "role", "designation", "business_unit", "reporting_manager"],
            [f"CSV User 1 {timestamp}", f"csv1_{timestamp}@test.com", "password123", "employee", "Developer", "Engineering", "Jane Smith"],
            [f"CSV User 2 {timestamp}", f"csv2_{timestamp}@test.com", "password123", "employee", "Designer", "Design", "John Doe"]
        ]
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        for row in csv_data:
            writer.writerow(row)
        csv_content = output.getvalue()
        
        # Encode as base64
        base64_content = base64.b64encode(csv_content.encode()).decode()
        
        # For this endpoint, we need to use requests directly as it expects a query parameter
        url = f"{self.base_url}/api/admin/upload-users"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        try:
            print(f"\n🔍 Testing CSV Bulk User Upload...")
            self.tests_run += 1
            
            # Send the request with file_content as a query parameter
            response = requests.post(f"{url}?file_content={base64_content}", headers=headers)
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                result = response.json()
                print(f"CSV upload response: {result}")
                
                if 'users_created' in result and result['users_created'] > 0:
                    print(f"✅ Successfully created {result['users_created']} users via CSV")
                    
                    # Verify by checking if users exist
                    users_success, users = self.test_admin_get_users()
                    if users_success:
                        csv_emails = [row[1] for row in csv_data[1:]]  # Skip header
                        found_users = [u for u in users if u['email'] in csv_emails]
                        if len(found_users) == len(csv_emails):
                            print("✅ All CSV users found in database")
                            return True
                        else:
                            print(f"❌ Only found {len(found_users)}/{len(csv_emails)} CSV users")
                else:
                    print("❌ No users created from CSV")
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            
        return False
        
    def test_email_templates(self):
        """Test email template configuration"""
        if not self.admin_token:
            print("❌ Cannot test email templates: No admin token")
            return False
            
        # First, get existing templates
        get_success, templates = self.run_test(
            "Get Email Templates",
            "GET",
            "api/admin/email-templates",
            200,
            token=self.admin_token
        )
        
        if get_success:
            print(f"Found {len(templates)} existing email templates")
            
            # Create a new template
            template_data = {
                "template_name": f"test_template_{datetime.now().strftime('%H%M%S')}",
                "subject": "Test Email Subject - Ticket #{ticket_id}",
                "body": "Hello {employee_name},\n\nYour ticket has been updated.\nStatus: {status}\nAdmin Notes: {admin_notes}\n\nRegards,\nKetto Care",
                "to_recipients": ["admin@ketto.org", "{employee_email}"],
                "cc_recipients": ["hr@ketto.org"],
                "bcc_recipients": [],
                "is_active": True
            }
            
            create_success, create_response = self.run_test(
                "Create Email Template",
                "POST",
                "api/admin/email-templates",
                200,
                data=template_data,
                token=self.admin_token
            )
            
            if create_success:
                print("✅ Successfully created email template")
                
                # Verify by getting templates again
                verify_success, verify_templates = self.run_test(
                    "Verify Email Templates",
                    "GET",
                    "api/admin/email-templates",
                    200,
                    token=self.admin_token
                )
                
                if verify_success:
                    if len(verify_templates) > len(templates):
                        print("✅ New template found in database")
                        
                        # Find the template we just created
                        new_template = next((t for t in verify_templates if t['template_name'] == template_data['template_name']), None)
                        if new_template:
                            print("✅ Template details match")
                            
                            # If we have a ticket, test updating it to trigger email
                            if self.test_ticket_id:
                                print("Testing email sending by updating a ticket...")
                                update_success = self.test_admin_update_ticket_with_notes(self.test_ticket_id)
                                if update_success:
                                    print("✅ Ticket updated, email should be sent using template")
                                    return True
                            else:
                                print("⚠️ No ticket available to test email sending")
                                return True
                    else:
                        print("❌ New template not found in database")
            else:
                print("❌ Failed to create email template")
        return False

    def test_admin_delete_user(self, user_id):
        """Test admin deleting a user"""
        if not self.admin_token:
            print("❌ Cannot test user deletion: No admin token")
            return False
            
        success, response = self.run_test(
            "Admin Delete User",
            "DELETE",
            f"api/admin/users/{user_id}",
            200,
            token=self.admin_token
        )
        
        return success
        
    def test_resolution_endpoint(self, conversation_id, resolution_type):
        """Test the resolution endpoint for handling button clicks"""
        if not self.token:
            print("❌ Cannot test resolution endpoint: No employee token")
            return False, None
            
        data = {
            "conversation_id": conversation_id,
            "resolution": resolution_type  # 'helpful' or 'need_help'
        }
        
        success, response = self.run_test(
            f"Resolution Endpoint ({resolution_type})",
            "POST",
            "api/chat/resolution",
            200,
            data=data,
            token=self.token
        )
        
        if success:
            print(f"Resolution response: {response.get('message', '')[:100]}...")
            print(f"Ticket created: {response.get('ticket_created', False)}")
            if response.get('ticket_created'):
                print(f"Ticket ID: {response.get('ticket_id')}")
                self.test_ticket_id = response.get('ticket_id')
            return True, response
        return False, None

    def test_resignation_flow(self):
        """Test the improved resignation flow with investigative approach"""
        if not self.token or not self.employee_id:
            print("❌ Cannot test resignation flow: No employee token or ID")
            return False, None
        
        # Test the resignation flow
        print("\n🔍 Testing Resignation Flow with Investigative Approach...")
        
        # Step 1: Initial resignation mention
        print("\nStep 1: Initial resignation mention")
        success, response = self.run_test(
            "Resignation mention",
            "POST",
            "api/chat",
            200,
            data={"message": "I want to resign", "user_id": self.employee_id},
            token=self.token
        )
        
        if not success:
            print("❌ Failed to send resignation message")
            return False, None
        
        ai_response = response.get('response', '')
        ticket_created = response.get('ticket_created', False)
        show_resolution_buttons = response.get('show_resolution_buttons', False)
        conversation_id = response.get('conversation_id')
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Ticket created: {ticket_created}")
        print(f"Show resolution buttons: {show_resolution_buttons}")
        
        # Check if AI is asking investigative questions instead of immediately providing resignation process
        investigative_indicators = [
            "what's driving this decision", 
            "could you share what's driving", 
            "what's behind your decision",
            "help me better understand",
            "tell me more about",
            "what has led you to",
            "what factors are"
        ]
        
        is_investigative = any(indicator in ai_response.lower() for indicator in investigative_indicators)
        
        if is_investigative:
            print("✅ AI is using investigative approach for resignation mention")
        else:
            print("❌ AI is not using investigative approach for resignation mention")
            return False, None
        
        if ticket_created:
            print("❌ AI should not create ticket immediately for resignation mention")
            return False, None
        
        if show_resolution_buttons:
            print("❌ AI should not show resolution buttons after initial resignation mention")
            return False, None
        
        # Step 2: Provide reason for resignation
        print("\nStep 2: Provide reason for resignation")
        success, response = self.run_test(
            "Resignation reason",
            "POST",
            "api/chat",
            200,
            data={"message": "My manager is micromanaging me and I feel burnt out", "user_id": self.employee_id},
            token=self.token
        )
        
        if not success:
            print("❌ Failed to send resignation reason")
            return False, None
        
        ai_response = response.get('response', '')
        ticket_created = response.get('ticket_created', False)
        show_resolution_buttons = response.get('show_resolution_buttons', False)
        conversation_id = response.get('conversation_id')
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Ticket created: {ticket_created}")
        print(f"Show resolution buttons: {show_resolution_buttons}")
        
        # Check if AI is providing solutions after getting the reason
        solution_indicators = [
            "suggest", "recommend", "approach", "option", "step", 
            "schedule a", "discuss with", "consider", "try", "focus on"
        ]
        
        has_solutions = any(indicator in ai_response.lower() for indicator in solution_indicators)
        
        if has_solutions:
            print("✅ AI is providing solutions after getting resignation reason")
        else:
            print("❌ AI is not providing solutions after getting resignation reason")
        
        if not show_resolution_buttons:
            print("❌ AI should show resolution buttons after providing solutions")
        else:
            print("✅ AI is showing resolution buttons after providing solutions")
            
            # Step 3: Test resolution buttons if they're shown
            if conversation_id:
                print("\nStep 3a: Test 'This helps' resolution button")
                helpful_success, helpful_response = self.test_resolution_endpoint(conversation_id, 'helpful')
                
                if helpful_success:
                    if not helpful_response.get('ticket_created', False):
                        print("✅ 'This helps' button correctly does not create a ticket")
                    else:
                        print("❌ 'This helps' button should not create a ticket")
                
                # Test the 'Still need help' button with a new conversation
                print("\nStep 3b: Starting new conversation to test 'Still need help' button")
                # Create a new conversation
                success, response = self.run_test(
                    "New resignation mention",
                    "POST",
                    "api/chat",
                    200,
                    data={"message": "I'm thinking about quitting", "user_id": self.employee_id},
                    token=self.token
                )
                
                if success:
                    # Provide reason
                    success, response = self.run_test(
                        "New resignation reason",
                        "POST",
                        "api/chat",
                        200,
                        data={"message": "I'm not getting along with my team", "user_id": self.employee_id},
                        token=self.token
                    )
                    
                    if success and response.get('show_resolution_buttons') and response.get('conversation_id'):
                        new_conversation_id = response.get('conversation_id')
                        
                        print("\nTesting 'Still need help' resolution button")
                        need_help_success, need_help_response = self.test_resolution_endpoint(new_conversation_id, 'need_help')
                        
                        if need_help_success:
                            if need_help_response.get('ticket_created', False):
                                print("✅ 'Still need help' button correctly creates a ticket")
                                print(f"Ticket ID: {need_help_response.get('ticket_id')}")
                                self.test_ticket_id = need_help_response.get('ticket_id')
                            else:
                                print("❌ 'Still need help' button should create a ticket")
        
        return True, {
            "is_investigative": is_investigative,
            "has_solutions": has_solutions,
            "shows_buttons": show_resolution_buttons
        }

def test_resolution_buttons_fix():
    """Test the resolution buttons fix with specific scenarios"""
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    print(f"Testing Ketto Care API at: {backend_url}")
    tester = KettoCareAPITester(backend_url)
    
    # Test basic connectivity
    tester.test_api_root()
    
    # Test admin initialization and login
    tester.test_init_admin()
    admin_login_success = tester.test_admin_login()
    
    # Test employee registration and login
    reg_success, employee_data = tester.test_employee_registration()
    if not reg_success:
        print("❌ Employee registration failed, trying to login with existing employee")
        login_success = tester.test_employee_login("employee@example.com", "password123")
        if not login_success:
            print("❌ Could not login with existing employee, creating a new one")
            reg_success, employee_data = tester.test_employee_registration()
            if not reg_success:
                print("❌ Failed to create employee account, stopping tests")
                return 1
            login_success = tester.test_employee_login(employee_data["email"])
            if not login_success:
                print("❌ Failed to login with new employee account, stopping tests")
                return 1
    else:
        login_success = tester.test_employee_login(employee_data["email"])
        if not login_success:
            print("❌ Failed to login with new employee account, stopping tests")
            return 1
    
    print("\n===== TESTING RESOLUTION BUTTONS FIX =====")
    
    # Test scenario 1: Resignation due to manager
    print("\n\n🔍 SCENARIO 1: Resignation due to manager")
    message = "I'm thinking about resigning because of my manager"
    print(f"Sending message: '{message}'")
    success, response = tester.run_test(
        "Resignation scenario",
        "POST",
        "api/chat",
        200,
        data={"message": message, "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success:
        ai_response = response.get('response', '')
        show_resolution_buttons = response.get('show_resolution_buttons', False)
        conversation_id = response.get('conversation_id')
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Show Resolution Buttons: {show_resolution_buttons}")
        
        # Check if the response contains solutions
        solution_indicators = [
            "schedule", "document", "discuss", "explore", "approach", "strategy",
            "suggest", "recommend", "option", "step", "consider", "try"
        ]
        has_solutions = any(word in ai_response.lower() for word in solution_indicators)
        has_numbered_list = '1.' in ai_response and '2.' in ai_response
        
        print(f"Response has solutions: {has_solutions}")
        print(f"Response has numbered list: {has_numbered_list}")
        
        # Test resolution buttons if they should be shown
        if show_resolution_buttons and conversation_id:
            print("\nTesting 'This helps' button...")
            tester.test_resolution_endpoint(conversation_id, 'helpful')
        else:
            print("❌ Resolution buttons not shown for resignation scenario")
    
    # Test scenario 2: Stress about workload
    print("\n\n🔍 SCENARIO 2: Stress about workload")
    message = "I'm feeling very stressed about my workload"
    print(f"Sending message: '{message}'")
    success, response = tester.run_test(
        "Stress scenario",
        "POST",
        "api/chat",
        200,
        data={"message": message, "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success:
        ai_response = response.get('response', '')
        show_resolution_buttons = response.get('show_resolution_buttons', False)
        conversation_id = response.get('conversation_id')
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Show Resolution Buttons: {show_resolution_buttons}")
        
        # Check if the response contains solutions
        solution_indicators = [
            "prioritize", "discuss", "delegate", "break", "management",
            "suggest", "recommend", "option", "step", "consider", "try"
        ]
        has_solutions = any(word in ai_response.lower() for word in solution_indicators)
        has_numbered_list = '1.' in ai_response and '2.' in ai_response
        
        print(f"Response has solutions: {has_solutions}")
        print(f"Response has numbered list: {has_numbered_list}")
        
        # Test resolution buttons if they should be shown
        if show_resolution_buttons and conversation_id:
            print("\nTesting 'Still need help' button...")
            success, res = tester.test_resolution_endpoint(conversation_id, 'need_help')
            if success and res.get('ticket_created'):
                tester.test_ticket_id = res.get('ticket_id')
        else:
            print("❌ Resolution buttons not shown for stress scenario")
    
    # Test scenario 3: Problems with manager
    print("\n\n🔍 SCENARIO 3: Problems with manager")
    message = "I'm having problems with my manager, they micromanage me"
    print(f"Sending message: '{message}'")
    success, response = tester.run_test(
        "Manager problems scenario",
        "POST",
        "api/chat",
        200,
        data={"message": message, "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success:
        ai_response = response.get('response', '')
        show_resolution_buttons = response.get('show_resolution_buttons', False)
        conversation_id = response.get('conversation_id')
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Show Resolution Buttons: {show_resolution_buttons}")
        
        # Check if the response contains solutions
        solution_indicators = [
            "conversation", "discuss", "document", "schedule", "approach",
            "suggest", "recommend", "option", "step", "consider", "try"
        ]
        has_solutions = any(word in ai_response.lower() for word in solution_indicators)
        has_numbered_list = '1.' in ai_response and '2.' in ai_response
        
        print(f"Response has solutions: {has_solutions}")
        print(f"Response has numbered list: {has_numbered_list}")
        
        # Test resolution buttons if they should be shown
        if show_resolution_buttons and conversation_id:
            print("\nTesting 'This helps' button...")
            tester.test_resolution_endpoint(conversation_id, 'helpful')
        else:
            print("❌ Resolution buttons not shown for manager problems scenario")
    
    # Check tickets created as admin
    if admin_login_success and tester.test_ticket_id:
        print("\n\n🔍 Checking tickets created as admin")
        admin_tickets_success, admin_tickets = tester.test_admin_get_tickets()
        if admin_tickets_success:
            # Find the ticket created by "Still need help"
            ticket = next((t for t in admin_tickets if t['id'] == tester.test_ticket_id), None)
            if ticket:
                print(f"✅ Found ticket created by 'Still need help' button: {ticket['id']}")
                print(f"Ticket summary: {ticket['summary']}")
                print(f"Ticket status: {ticket['status']}")
            else:
                print(f"❌ Could not find ticket with ID: {tester.test_ticket_id}")
    
    # Print test results
    print("\n" + "="*50)
    print(f"Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    print("="*50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

def comprehensive_test():
    """Run comprehensive tests of all Ketto Care functionality"""
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    print(f"Testing Ketto Care API at: {backend_url}")
    tester = KettoCareAPITester(backend_url)
    
    print("\n===== TESTING AUTHENTICATION =====")
    # Test basic connectivity
    tester.test_api_root()
    
    # Test admin initialization and login
    tester.test_init_admin()
    admin_login_success = tester.test_admin_login()
    if not admin_login_success:
        print("❌ Admin login failed, stopping tests")
        return 1
    
    # Test employee registration and login
    reg_success, employee_data = tester.test_employee_registration()
    if not reg_success:
        print("❌ Employee registration failed, trying to login with existing employee")
        login_success = tester.test_employee_login("employee@example.com", "password123")
        if not login_success:
            print("❌ Could not login with existing employee, creating a new one")
            reg_success, employee_data = tester.test_employee_registration()
            if not reg_success:
                print("❌ Failed to create employee account, stopping tests")
                return 1
            login_success = tester.test_employee_login(employee_data["email"])
            if not login_success:
                print("❌ Failed to login with new employee account, stopping tests")
                return 1
    else:
        login_success = tester.test_employee_login(employee_data["email"])
        if not login_success:
            print("❌ Failed to login with new employee account, stopping tests")
            return 1
    
    print("\n===== TESTING EMPLOYEE CHAT INTERFACE =====")
    
    # Test regular workplace concerns
    print("\n🔍 Testing regular workplace concern")
    success, response = tester.run_test(
        "Regular workplace concern",
        "POST",
        "api/chat",
        200,
        data={"message": "I'm feeling stressed about my workload", "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success:
        ai_response = response.get('response', '')
        show_resolution_buttons = response.get('show_resolution_buttons', False)
        conversation_id = response.get('conversation_id')
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Show Resolution Buttons: {show_resolution_buttons}")
        
        if show_resolution_buttons:
            print("✅ Resolution buttons appear for regular workplace concern")
        else:
            print("❌ Resolution buttons not shown for regular workplace concern")
            
        if conversation_id and show_resolution_buttons:
            # Test "This helps" button
            print("\nTesting 'This helps' button...")
            tester.test_resolution_endpoint(conversation_id, 'helpful')
    
    # Test serious issue (harassment)
    print("\n🔍 Testing serious issue (harassment)")
    success, response = tester.run_test(
        "Harassment issue",
        "POST",
        "api/chat",
        200,
        data={"message": "I'm being harassed by my colleague", "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success:
        ai_response = response.get('response', '')
        ticket_created = response.get('ticket_created', False)
        ticket_id = response.get('ticket_id')
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Ticket Created: {ticket_created}")
        
        if ticket_created and ticket_id:
            print(f"✅ Serious issue automatically escalated to ticket: {ticket_id}")
            tester.test_ticket_id = ticket_id
        else:
            print("❌ Serious issue not automatically escalated")
    
    # Test resolution buttons with "Still need help"
    print("\n🔍 Testing 'Still need help' resolution button")
    success, response = tester.run_test(
        "Career growth concern",
        "POST",
        "api/chat",
        200,
        data={"message": "I'm concerned about my career growth", "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success and response.get('show_resolution_buttons') and response.get('conversation_id'):
        conversation_id = response.get('conversation_id')
        print("\nTesting 'Still need help' button...")
        success, res = tester.test_resolution_endpoint(conversation_id, 'need_help')
        if success and res.get('ticket_created'):
            print(f"✅ 'Still need help' button creates ticket: {res.get('ticket_id')}")
            if not tester.test_ticket_id:  # Save a ticket ID for later tests if we don't have one
                tester.test_ticket_id = res.get('ticket_id')
        else:
            print("❌ 'Still need help' button did not create ticket")
    
    # Test chat history persistence
    print("\n🔍 Testing chat history persistence")
    success, history = tester.run_test(
        "Get Chat History",
        "GET",
        f"api/chat/history/{tester.employee_id}",
        200,
        token=tester.token
    )
    
    if success:
        print(f"✅ Retrieved {len(history)} chat messages")
        if len(history) > 0:
            print("✅ Chat history is being persisted")
        else:
            print("❌ No chat history found")
    
    print("\n===== TESTING ADMIN DASHBOARD =====")
    
    # Test ticket management
    print("\n🔍 Testing admin ticket management")
    success, tickets = tester.test_admin_get_tickets()
    if success:
        print(f"✅ Admin retrieved {len(tickets)} tickets")
        
        if tester.test_ticket_id:
            print("\n🔍 Testing ticket status update")
            update_success = tester.test_admin_update_ticket_with_notes(tester.test_ticket_id)
            if update_success:
                print("✅ Admin successfully updated ticket status")
            else:
                print("❌ Failed to update ticket status")
    
    # Test user management
    print("\n🔍 Testing admin user management")
    success, users = tester.test_admin_get_users()
    if success:
        print(f"✅ Admin retrieved {len(users)} users")
        
        print("\n🔍 Testing user creation")
        create_success, user_data = tester.test_admin_create_user()
        if create_success and user_data:
            print("✅ Admin successfully created user")
            
            # Get updated user list to find the new user
            success, updated_users = tester.test_admin_get_users()
            if success:
                new_user = next((u for u in updated_users if u['email'] == user_data['email']), None)
                if new_user:
                    user_id = new_user['id']
                    
                    print("\n🔍 Testing user update")
                    update_success, update_data = tester.test_admin_update_user(user_id)
                    if update_success:
                        print("✅ Admin successfully updated user")
                    else:
                        print("❌ Failed to update user")
                    
                    print("\n🔍 Testing user deletion")
                    delete_success = tester.test_admin_delete_user(user_id)
                    if delete_success:
                        print("✅ Admin successfully deleted user")
                    else:
                        print("❌ Failed to delete user")
    
    # Test CSV user upload
    print("\n🔍 Testing CSV user upload")
    csv_success = tester.test_csv_bulk_user_upload()
    if csv_success:
        print("✅ Admin successfully uploaded users via CSV")
    else:
        print("❌ Failed to upload users via CSV")
    
    # Test AI conversations tracking
    print("\n🔍 Testing AI conversations tracking")
    success, conversations = tester.run_test(
        "Get AI Conversations",
        "GET",
        "api/admin/ai-conversations",
        200,
        token=tester.admin_token
    )
    
    if success:
        print(f"✅ Admin retrieved {len(conversations)} AI conversations")
        
        if len(conversations) > 0:
            conversation_id = conversations[0]['id']
            print("\n🔍 Testing marking conversation as reviewed")
            review_success, _ = tester.run_test(
                "Mark Conversation Reviewed",
                "PUT",
                f"api/admin/ai-conversations/{conversation_id}",
                200,
                data={"admin_reviewed": True},
                token=tester.admin_token
            )
            
            if review_success:
                print("✅ Admin successfully marked conversation as reviewed")
            else:
                print("❌ Failed to mark conversation as reviewed")
    
    # Test email configuration
    print("\n🔍 Testing email configuration")
    email_config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "smtp_username": "test@example.com",
        "smtp_password": "password123"
    }
    
    success, _ = tester.run_test(
        "Save Email Config",
        "POST",
        "api/admin/email-config",
        200,
        data=email_config,
        token=tester.admin_token
    )
    
    if success:
        print("✅ Admin successfully saved email configuration")
        
        success, config = tester.run_test(
            "Get Email Config",
            "GET",
            "api/admin/email-config",
            200,
            token=tester.admin_token
        )
        
        if success and config:
            print("✅ Admin successfully retrieved email configuration")
        else:
            print("❌ Failed to retrieve email configuration")
    else:
        print("❌ Failed to save email configuration")
    
    # Test GPT configuration
    print("\n🔍 Testing GPT configuration")
    gpt_config = {
        "api_key": "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"
    }
    
    success, _ = tester.run_test(
        "Save GPT Config",
        "POST",
        "api/admin/gpt-config",
        200,
        data=gpt_config,
        token=tester.admin_token
    )
    
    if success:
        print("✅ Admin successfully saved GPT configuration")
        
        success, config = tester.run_test(
            "Get GPT Config",
            "GET",
            "api/admin/gpt-config",
            200,
            token=tester.admin_token
        )
        
        if success and config:
            print("✅ Admin successfully retrieved GPT configuration")
        else:
            print("❌ Failed to retrieve GPT configuration")
    else:
        print("❌ Failed to save GPT configuration")
    
    # Test email templates
    print("\n🔍 Testing email templates")
    template_success = tester.test_email_templates()
    if template_success:
        print("✅ Admin successfully managed email templates")
    else:
        print("❌ Failed to manage email templates")
    
    # Print test results
    print("\n" + "="*50)
    print(f"Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    print("="*50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

def test_posh_complaint():
    """Test POSH complaint ticket creation"""
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    print(f"Testing POSH complaint ticket creation at: {backend_url}")
    tester = KettoCareAPITester(backend_url)
    
    # Test basic connectivity
    tester.test_api_root()
    
    # Test employee registration and login
    reg_success, employee_data = tester.test_employee_registration()
    if not reg_success:
        print("❌ Employee registration failed, trying to login with existing employee")
        login_success = tester.test_employee_login("employee@example.com", "password123")
        if not login_success:
            print("❌ Could not login with existing employee, creating a new one")
            reg_success, employee_data = tester.test_employee_registration()
            if not reg_success:
                print("❌ Failed to create employee account, stopping tests")
                return False
            login_success = tester.test_employee_login(employee_data["email"])
            if not login_success:
                print("❌ Failed to login with new employee account, stopping tests")
                return False
    else:
        login_success = tester.test_employee_login(employee_data["email"])
        if not login_success:
            print("❌ Failed to login with new employee account, stopping tests")
            return False
    
    # Test admin login
    admin_login_success = tester.test_admin_login()
    if not admin_login_success:
        print("❌ Admin login failed, stopping tests")
        return False
    
    # Send POSH complaint message
    print("\n🔍 Testing POSH complaint ticket creation")
    success, response = tester.run_test(
        "POSH complaint",
        "POST",
        "api/chat",
        200,
        data={"message": "I want to raise a POSH complaint against my manager", "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success:
        ai_response = response.get('response', '')
        ticket_created = response.get('ticket_created', False)
        ticket_id = response.get('ticket_id')
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Ticket Created: {ticket_created}")
        
        if ticket_created and ticket_id:
            print(f"✅ POSH complaint automatically escalated to ticket: {ticket_id}")
            tester.test_ticket_id = ticket_id
            
            # Check if employee can see the ticket
            print("\n🔍 Checking if employee can see the ticket")
            success, employee_tickets = tester.test_get_tickets()
            if success:
                employee_ticket = next((t for t in employee_tickets if t['id'] == ticket_id), None)
                if employee_ticket:
                    print("✅ Employee can see the POSH complaint ticket")
                else:
                    print("❌ Employee cannot see the POSH complaint ticket")
                    return False
            else:
                print("❌ Failed to get employee tickets")
                return False
            
            # Check if admin can see the ticket
            print("\n🔍 Checking if admin can see the ticket")
            success, admin_tickets = tester.test_admin_get_tickets()
            if success:
                admin_ticket = next((t for t in admin_tickets if t['id'] == ticket_id), None)
                if admin_ticket:
                    print("✅ Admin can see the POSH complaint ticket")
                    return True
                else:
                    print("❌ Admin cannot see the POSH complaint ticket")
                    return False
            else:
                print("❌ Failed to get admin tickets")
                return False
        else:
            print("❌ POSH complaint not automatically escalated")
            return False
    else:
        print("❌ Failed to send POSH complaint message")
        return False

def test_resolution_buttons_logic():
    """Test resolution buttons logic"""
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    print(f"Testing resolution buttons logic at: {backend_url}")
    tester = KettoCareAPITester(backend_url)
    
    # Test basic connectivity
    tester.test_api_root()
    
    # Test employee registration and login
    reg_success, employee_data = tester.test_employee_registration()
    if not reg_success:
        print("❌ Employee registration failed, trying to login with existing employee")
        login_success = tester.test_employee_login("employee@example.com", "password123")
        if not login_success:
            print("❌ Could not login with existing employee, creating a new one")
            reg_success, employee_data = tester.test_employee_registration()
            if not reg_success:
                print("❌ Failed to create employee account, stopping tests")
                return False
            login_success = tester.test_employee_login(employee_data["email"])
            if not login_success:
                print("❌ Failed to login with new employee account, stopping tests")
                return False
    else:
        login_success = tester.test_employee_login(employee_data["email"])
        if not login_success:
            print("❌ Failed to login with new employee account, stopping tests")
            return False
    
    # Test initial questions (should NOT show buttons)
    print("\n🔍 Testing initial questions (should NOT show buttons)")
    success, response = tester.run_test(
        "Initial question",
        "POST",
        "api/chat",
        200,
        data={"message": "I'm feeling stressed at work", "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success:
        ai_response = response.get('response', '')
        show_resolution_buttons = response.get('show_resolution_buttons', False)
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Show Resolution Buttons: {show_resolution_buttons}")
        
        # Check if the response is a question (investigative)
        is_question = '?' in ai_response
        print(f"Response contains question: {is_question}")
        
        if is_question and not show_resolution_buttons:
            print("✅ Initial question does NOT show resolution buttons")
        else:
            if not is_question:
                print("❌ AI response is not a question for initial message")
            if show_resolution_buttons:
                print("❌ Resolution buttons shown for initial question")
            return False
    else:
        print("❌ Failed to send initial question")
        return False
    
    # Test investigative response (should NOT show buttons)
    print("\n🔍 Testing investigative response (should NOT show buttons)")
    success, response = tester.run_test(
        "Follow-up to initial question",
        "POST",
        "api/chat",
        200,
        data={"message": "I have too much work and not enough time", "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success:
        ai_response = response.get('response', '')
        show_resolution_buttons = response.get('show_resolution_buttons', False)
        
        print(f"AI Response: {ai_response[:150]}...")
        print(f"Show Resolution Buttons: {show_resolution_buttons}")
        
        # Check if the response contains solutions
        solution_indicators = [
            "suggest", "recommend", "approach", "option", "step", 
            "schedule a", "discuss with", "consider", "try", "focus on"
        ]
        has_solutions = any(indicator in ai_response.lower() for indicator in solution_indicators)
        has_numbered_list = '1.' in ai_response and '2.' in ai_response
        
        print(f"Response has solutions: {has_solutions}")
        print(f"Response has numbered list: {has_numbered_list}")
        
        if has_solutions and has_numbered_list and show_resolution_buttons:
            print("✅ Comprehensive solution shows resolution buttons")
            
            # Get the conversation ID for testing resolution
            conversation_id = response.get('conversation_id')
            if conversation_id:
                # Test "This helps" button
                print("\n🔍 Testing 'This helps' button")
                success, helpful_response = tester.test_resolution_endpoint(conversation_id, 'helpful')
                if success:
                    if not helpful_response.get('ticket_created', False):
                        print("✅ 'This helps' button correctly does not create a ticket")
                    else:
                        print("❌ 'This helps' button should not create a ticket")
                        return False
                else:
                    print("❌ Failed to test 'This helps' button")
                    return False
                
                return True
            else:
                print("❌ No conversation ID found")
                return False
        else:
            if not has_solutions or not has_numbered_list:
                print("❌ AI response does not contain comprehensive solutions")
            if not show_resolution_buttons:
                print("❌ Resolution buttons not shown for comprehensive solution")
            return False
    else:
        print("❌ Failed to send follow-up message")
        return False

def test_ticket_visibility():
    """Test ticket visibility for employee and admin"""
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    print(f"Testing ticket visibility at: {backend_url}")
    tester = KettoCareAPITester(backend_url)
    
    # Test basic connectivity
    tester.test_api_root()
    
    # Test employee registration and login
    reg_success, employee_data = tester.test_employee_registration()
    if not reg_success:
        print("❌ Employee registration failed, trying to login with existing employee")
        login_success = tester.test_employee_login("employee@example.com", "password123")
        if not login_success:
            print("❌ Could not login with existing employee, creating a new one")
            reg_success, employee_data = tester.test_employee_registration()
            if not reg_success:
                print("❌ Failed to create employee account, stopping tests")
                return False
            login_success = tester.test_employee_login(employee_data["email"])
            if not login_success:
                print("❌ Failed to login with new employee account, stopping tests")
                return False
    else:
        login_success = tester.test_employee_login(employee_data["email"])
        if not login_success:
            print("❌ Failed to login with new employee account, stopping tests")
            return False
    
    # Test admin login
    admin_login_success = tester.test_admin_login()
    if not admin_login_success:
        print("❌ Admin login failed, stopping tests")
        return False
    
    # Create a ticket by sending a critical message
    print("\n🔍 Creating a ticket for visibility testing")
    success, response = tester.run_test(
        "Critical message",
        "POST",
        "api/chat",
        200,
        data={"message": "I'm being harassed by my colleague", "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success and response.get('ticket_created', False):
        ticket_id = response.get('ticket_id')
        print(f"✅ Ticket created: {ticket_id}")
        tester.test_ticket_id = ticket_id
        
        # Check if employee can see the ticket
        print("\n🔍 Checking if employee can see the ticket")
        success, employee_tickets = tester.test_get_tickets()
        if success:
            employee_ticket = next((t for t in employee_tickets if t['id'] == ticket_id), None)
            if employee_ticket:
                print("✅ Employee can see their own ticket")
                print(f"Ticket details: {employee_ticket}")
            else:
                print("❌ Employee cannot see their own ticket")
                return False
        else:
            print("❌ Failed to get employee tickets")
            return False
        
        # Check if admin can see the ticket
        print("\n🔍 Checking if admin can see the ticket")
        success, admin_tickets = tester.test_admin_get_tickets()
        if success:
            admin_ticket = next((t for t in admin_tickets if t['id'] == ticket_id), None)
            if admin_ticket:
                print("✅ Admin can see the employee's ticket")
                print(f"Ticket details: {admin_ticket}")
                return True
            else:
                print("❌ Admin cannot see the employee's ticket")
                return False
        else:
            print("❌ Failed to get admin tickets")
            return False
    else:
        print("❌ Failed to create a ticket for testing")
        return False

def test_no_mock_ai_fallback():
    """Test that the system only uses OpenAI GPT API with no mock fallback"""
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    print(f"Testing no mock AI fallback at: {backend_url}")
    tester = KettoCareAPITester(backend_url)
    
    # Test basic connectivity
    tester.test_api_root()
    
    # Test employee registration and login
    reg_success, employee_data = tester.test_employee_registration()
    if not reg_success:
        print("❌ Employee registration failed, trying to login with existing employee")
        login_success = tester.test_employee_login("employee@example.com", "password123")
        if not login_success:
            print("❌ Could not login with existing employee, creating a new one")
            reg_success, employee_data = tester.test_employee_registration()
            if not reg_success:
                print("❌ Failed to create employee account, stopping tests")
                return False
            login_success = tester.test_employee_login(employee_data["email"])
            if not login_success:
                print("❌ Failed to login with new employee account, stopping tests")
                return False
    else:
        login_success = tester.test_employee_login(employee_data["email"])
        if not login_success:
            print("❌ Failed to login with new employee account, stopping tests")
            return False
    
    # Send multiple messages to check for consistent AI responses
    test_messages = [
        "How can I improve my work-life balance?",
        "I'm having trouble with my manager",
        "What are some stress management techniques?",
        "How do I ask for a promotion?"
    ]
    
    responses = []
    for i, message in enumerate(test_messages):
        print(f"\n🔍 Testing message {i+1}: '{message}'")
        success, response = tester.run_test(
            f"Message {i+1}",
            "POST",
            "api/chat",
            200,
            data={"message": message, "user_id": tester.employee_id},
            token=tester.token
        )
        
        if success:
            ai_response = response.get('response', '')
            print(f"AI Response: {ai_response[:150]}...")
            responses.append(ai_response)
        else:
            print(f"❌ Failed to send message {i+1}")
            return False
        
        # Small delay between requests
        time.sleep(1)
    
    # Check for signs of mock responses
    mock_indicators = [
        "I apologize, but I'm experiencing technical difficulties",
        "I'm unable to connect to the AI system",
        "Our AI assistant is currently unavailable",
        "Please try again later",
        "Technical support needed - AI assistant unavailable"
    ]
    
    for i, response in enumerate(responses):
        for indicator in mock_indicators:
            if indicator.lower() in response.lower():
                print(f"❌ Found mock response indicator in message {i+1}: '{indicator}'")
                return False
    
    print("✅ No mock response indicators found in any responses")
    return True

def test_end_to_end_workflow():
    """Test the end-to-end workflow"""
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    print(f"Testing end-to-end workflow at: {backend_url}")
    tester = KettoCareAPITester(backend_url)
    
    # Test basic connectivity
    tester.test_api_root()
    
    # Test employee registration and login
    reg_success, employee_data = tester.test_employee_registration()
    if not reg_success:
        print("❌ Employee registration failed, trying to login with existing employee")
        login_success = tester.test_employee_login("employee@example.com", "password123")
        if not login_success:
            print("❌ Could not login with existing employee, creating a new one")
            reg_success, employee_data = tester.test_employee_registration()
            if not reg_success:
                print("❌ Failed to create employee account, stopping tests")
                return False
            login_success = tester.test_employee_login(employee_data["email"])
            if not login_success:
                print("❌ Failed to login with new employee account, stopping tests")
                return False
    else:
        login_success = tester.test_employee_login(employee_data["email"])
        if not login_success:
            print("❌ Failed to login with new employee account, stopping tests")
            return False
    
    # Test admin login
    admin_login_success = tester.test_admin_login()
    if not admin_login_success:
        print("❌ Admin login failed, stopping tests")
        return False
    
    # Step 1: Employee raises serious concern
    print("\n🔍 Step 1: Employee raises serious concern")
    success, response = tester.run_test(
        "Serious concern",
        "POST",
        "api/chat",
        200,
        data={"message": "I want to report sexual harassment by my team lead", "user_id": tester.employee_id},
        token=tester.token
    )
    
    if success and response.get('ticket_created', False):
        ticket_id = response.get('ticket_id')
        print(f"✅ Ticket automatically created: {ticket_id}")
        tester.test_ticket_id = ticket_id
        
        # Check if employee can see the ticket
        success, employee_tickets = tester.test_get_tickets()
        if success and any(t['id'] == ticket_id for t in employee_tickets):
            print("✅ Employee can see the ticket")
        else:
            print("❌ Employee cannot see the ticket")
            return False
        
        # Check if admin can see the ticket
        success, admin_tickets = tester.test_admin_get_tickets()
        if success and any(t['id'] == ticket_id for t in admin_tickets):
            print("✅ Admin can see the ticket")
        else:
            print("❌ Admin cannot see the ticket")
            return False
        
        # Step 2: Employee seeks workplace advice
        print("\n🔍 Step 2: Employee seeks workplace advice")
        success, response = tester.run_test(
            "Workplace advice",
            "POST",
            "api/chat",
            200,
            data={"message": "I need help with time management, I've tried everything but I'm still struggling", "user_id": tester.employee_id},
            token=tester.token
        )
        
        if success:
            ai_response = response.get('response', '')
            show_resolution_buttons = response.get('show_resolution_buttons', False)
            conversation_id = response.get('conversation_id')
            
            print(f"AI Response: {ai_response[:150]}...")
            print(f"Show Resolution Buttons: {show_resolution_buttons}")
            
            # Check if the response contains solutions
            solution_indicators = [
                "suggest", "recommend", "approach", "option", "step", 
                "schedule a", "discuss with", "consider", "try", "focus on"
            ]
            has_solutions = any(indicator in ai_response.lower() for indicator in solution_indicators)
            has_numbered_list = '1.' in ai_response and '2.' in ai_response
            
            print(f"Response has solutions: {has_solutions}")
            print(f"Response has numbered list: {has_numbered_list}")
            
            if has_solutions and has_numbered_list and show_resolution_buttons:
                print("✅ Comprehensive solution shows resolution buttons")
                
                if conversation_id:
                    # Step 3a: Test "This helps" button
                    print("\n🔍 Step 3a: Testing 'This helps' button")
                    success, helpful_response = tester.test_resolution_endpoint(conversation_id, 'helpful')
                    if success:
                        if not helpful_response.get('ticket_created', False):
                            print("✅ 'This helps' button correctly does not create a ticket")
                        else:
                            print("❌ 'This helps' button should not create a ticket")
                            return False
                    else:
                        print("❌ Failed to test 'This helps' button")
                        return False
                    
                    # Step 3b: Start a new conversation for "Still need help" button
                    print("\n🔍 Step 3b: Starting new conversation for 'Still need help' button")
                    success, response = tester.run_test(
                        "New workplace advice",
                        "POST",
                        "api/chat",
                        200,
                        data={"message": "I need strategies for dealing with difficult coworkers, I've tried talking to them but nothing works", "user_id": tester.employee_id},
                        token=tester.token
                    )
                    
                    if success and response.get('show_resolution_buttons') and response.get('conversation_id'):
                        new_conversation_id = response.get('conversation_id')
                        
                        print("\n🔍 Testing 'Still need help' button")
                        success, need_help_response = tester.test_resolution_endpoint(new_conversation_id, 'need_help')
                        if success:
                            if need_help_response.get('ticket_created', False):
                                print("✅ 'Still need help' button correctly creates a ticket")
                                new_ticket_id = need_help_response.get('ticket_id')
                                
                                # Step 4: Admin manages the ticket
                                print("\n🔍 Step 4: Admin manages the ticket")
                                update_data = {
                                    "status": "in_progress",
                                    "admin_notes": "Working on this issue"
                                }
                                
                                success, _ = tester.run_test(
                                    "Admin Update Ticket",
                                    "PUT",
                                    f"api/admin/tickets/{new_ticket_id}",
                                    200,
                                    data=update_data,
                                    token=tester.admin_token
                                )
                                
                                if success:
                                    print("✅ Admin successfully updated the ticket")
                                    
                                    # Verify the update
                                    success, admin_tickets = tester.test_admin_get_tickets()
                                    if success:
                                        updated_ticket = next((t for t in admin_tickets if t['id'] == new_ticket_id), None)
                                        if updated_ticket and updated_ticket['status'] == 'in_progress':
                                            print("✅ Ticket status updated correctly")
                                            return True
                                        else:
                                            print("❌ Ticket status not updated correctly")
                                            return False
                                    else:
                                        print("❌ Failed to verify ticket update")
                                        return False
                                else:
                                    print("❌ Failed to update the ticket")
                                    return False
                            else:
                                print("❌ 'Still need help' button should create a ticket")
                                return False
                        else:
                            print("❌ Failed to test 'Still need help' button")
                            return False
                    else:
                        print("❌ Failed to start new conversation for 'Still need help' button")
                        return False
                else:
                    print("❌ No conversation ID found")
                    return False
            else:
                if not has_solutions or not has_numbered_list:
                    print("❌ AI response does not contain comprehensive solutions")
                if not show_resolution_buttons:
                    print("❌ Resolution buttons not shown for comprehensive solution")
                return False
        else:
            print("❌ Failed to send workplace advice message")
            return False
    else:
        print("❌ Failed to create a ticket for serious concern")
        return False

def main():
    print("\n===== TESTING KETTO CARE APPLICATION =====\n")
    
    tests = [
        ("POSH Complaint Ticket Creation", test_posh_complaint),
        ("Resolution Buttons Logic", test_resolution_buttons_logic),
        ("Ticket Visibility", test_ticket_visibility),
        ("No Mock AI Fallback", test_no_mock_ai_fallback),
        ("End-to-End Workflow", test_end_to_end_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n\n{'='*50}")
        print(f"TESTING: {test_name}")
        print(f"{'='*50}\n")
        
        try:
            result = test_func()
            results[test_name] = result
            print(f"\nTest Result: {'✅ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            results[test_name] = False
    
    # Print summary
    print("\n\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\nOVERALL RESULT: " + ("✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"))
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    main()
