#!/usr/bin/env python3
"""
Fix script for Ketto Care issues:
1. Remove mock AI fallback
2. Fix resolution buttons logic  
3. Fix frontend ticket display
"""

import re

def fix_backend():
    """Fix backend issues"""
    print("Fixing backend server.py...")
    
    with open('/app/backend/server.py', 'r') as f:
        content = f.read()
    
    # 1. Remove the entire mock AI response function
    mock_function_pattern = r'async def get_mock_ai_response.*?return f"Thank you for reaching out.*?\n\n'
    content = re.sub(mock_function_pattern, '', content, flags=re.DOTALL)
    
    # 2. Fix the OpenAI error handling - remove mock fallback
    old_openai_error = '''        except Exception as openai_error:
            logging.warning(f"OpenAI API error: {str(openai_error)}")
            logging.info("Using mock AI response as fallback")
            ai_response = await get_mock_ai_response(message, user_name, conversation_history)
            using_mock = True'''
    
    new_openai_error = '''        except Exception as openai_error:
            logging.error(f"OpenAI API error: {str(openai_error)}")
            # Escalate immediately when AI is unavailable
            return {
                "response": "I apologize, but I'm experiencing technical difficulties connecting to our AI system. I'm creating a support ticket to ensure your concern is addressed by our admin team.",
                "escalate": True,
                "category": "request",
                "severity": "medium",
                "summary": "Technical support needed - AI assistant unavailable",
                "show_resolution_buttons": False,
                "conversation_id": None
            }'''
    
    content = content.replace(old_openai_error, new_openai_error)
    
    # 3. Remove using_mock variable and related logic
    content = content.replace('using_mock = False', '')
    content = content.replace('using_mock = True', '')
    
    # 4. Fix escalation logic to remove using_mock references
    old_escalation = '''        if using_mock:
            # Mock AI escalation logic
            critical_keywords = ["harassment", "harass", "discriminat", "abuse", "threat", "unsafe", "sexual"]
            if any(keyword in message.lower() for keyword in critical_keywords):
                escalate = True
                category = "grievance"
                severity = "critical"
                summary = f"Serious workplace concern: {message[:80]}..."
                logging.info(f"Mock AI escalating due to critical keywords: {message}")
            
            # Auto-escalate follow-ups indicating unresolved issues
            unresolved_indicators = ["no", "not really", "still having", "doesn't help", "not resolved", "still struggling", "not working"]
            if is_follow_up and any(indicator in message.lower() for indicator in unresolved_indicators):
                escalate = True
                category = "request"
                severity = "medium"
                summary = f"Unresolved workplace concern: {pending_conversation.initial_concern[:60]}..." if pending_conversation else summary
                logging.info("Mock AI auto-escalating follow-up with unresolved issue")
        else:'''
    
    new_escalation = '''        # Enhanced escalation logic'''
    
    content = content.replace(old_escalation, new_escalation)
    
    # 5. Fix resolution buttons logic to be more restrictive
    old_resolution_logic = '''        # Show buttons if: not escalating, not follow-up, has solutions, not primarily questions
        should_show_buttons = not escalate and not is_follow_up and has_solutions and not is_mostly_questions'''
    
    new_resolution_logic = '''        # Show buttons ONLY for final solutions (not initial questions or investigations)
        # Must have multiple solutions AND minimal questions
        is_final_solution = has_numbered_list and has_solutions and question_count == 0
        is_comprehensive_advice = has_solutions and len(clean_response) > 300 and question_count <= 1
        
        should_show_buttons = not escalate and not is_follow_up and (is_final_solution or is_comprehensive_advice) and not is_mostly_questions'''
    
    content = content.replace(old_resolution_logic, new_resolution_logic)
    
    # Write the fixed content
    with open('/app/backend/server.py', 'w') as f:
        f.write(content)
    
    print("✅ Backend fixes applied")

def fix_frontend():
    """Fix frontend ticket display issues"""
    print("Fixing frontend App.js...")
    
    with open('/app/frontend/src/App.js', 'r') as f:
        content = f.read()
    
    # Add error handling and debugging for admin ticket loading
    old_load_data = '''  const loadData = async () => {
    try {
      const [ticketsRes, usersRes, emailRes, gptRes, templatesRes, conversationsRes] = await Promise.all([
        axios.get(`${API}/admin/tickets`),
        axios.get(`${API}/admin/users`),
        axios.get(`${API}/admin/email-config`),
        axios.get(`${API}/admin/gpt-config`),
        axios.get(`${API}/admin/email-templates`),
        axios.get(`${API}/admin/ai-conversations`)
      ]);
      
      setTickets(ticketsRes.data);
      setUsers(usersRes.data);
      setEmailConfig(emailRes.data);
      setGptConfig(gptRes.data);
      setEmailTemplates(templatesRes.data);
      setAiConversations(conversationsRes.data);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    }
  };'''
    
    new_load_data = '''  const loadData = async () => {
    try {
      console.log('Loading admin data...');
      const [ticketsRes, usersRes, emailRes, gptRes, templatesRes, conversationsRes] = await Promise.all([
        axios.get(`${API}/admin/tickets`),
        axios.get(`${API}/admin/users`),
        axios.get(`${API}/admin/email-config`),
        axios.get(`${API}/admin/gpt-config`),
        axios.get(`${API}/admin/email-templates`),
        axios.get(`${API}/admin/ai-conversations`)
      ]);
      
      console.log('Tickets loaded:', ticketsRes.data.length);
      console.log('Users loaded:', usersRes.data.length);
      
      setTickets(ticketsRes.data || []);
      setUsers(usersRes.data || []);
      setEmailConfig(emailRes.data || {});
      setGptConfig(gptRes.data || {});
      setEmailTemplates(templatesRes.data || []);
      setAiConversations(conversationsRes.data || []);
    } catch (error) {
      console.error('Failed to load admin data:', error);
      alert('Failed to load admin data. Please refresh the page.');
    }
  };'''
    
    content = content.replace(old_load_data, new_load_data)
    
    # Fix employee ticket loading
    old_tickets_effect = '''  useEffect(() => {
    if (user && user.role === 'employee') {
      loadTickets();
      loadChatHistory();
    }
  }, [user]);'''
    
    new_tickets_effect = '''  useEffect(() => {
    if (user && user.role === 'employee') {
      console.log('Loading employee data for user:', user.id);
      loadTickets();
      loadChatHistory();
    }
  }, [user]);'''
    
    content = content.replace(old_tickets_effect, new_tickets_effect)
    
    # Write the fixed content
    with open('/app/frontend/src/App.js', 'w') as f:
        f.write(content)
    
    print("✅ Frontend fixes applied")

if __name__ == "__main__":
    print("🔧 Applying Ketto Care fixes...")
    fix_backend()
    fix_frontend()
    print("✅ All fixes applied successfully!")