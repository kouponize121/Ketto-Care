from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import openai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import pandas as pd
import io
import base64
import json
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
# SQLite doesn't have a native UUID type, so we'll use String instead
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./ketto_care.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="employee")  # employee or admin
    designation = Column(String, nullable=True)
    business_unit = Column(String, nullable=True)
    reporting_manager = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    category = Column(String)  # grievance, request, wellness
    summary = Column(String)
    description = Column(Text)
    status = Column(String, default="open")  # open, in_progress, resolved
    severity = Column(String, default="medium")  # low, medium, high, critical
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admin_notes = Column(Text, nullable=True)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String, nullable=True)
    user_id = Column(String, index=True)
    sender = Column(String)  # user or ai
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class EmailConfig(Base):
    __tablename__ = "email_config"
    
    id = Column(Integer, primary_key=True)
    smtp_server = Column(String)
    smtp_port = Column(Integer)
    smtp_username = Column(String)
    smtp_password = Column(String)

class GPTConfig(Base):
    __tablename__ = "gpt_config"
    
    id = Column(Integer, primary_key=True)
    api_key = Column(String)
    is_active = Column(Boolean, default=True)
    last_tested_at = Column(DateTime, nullable=True)

class EmailTemplate(Base):
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True)
    template_name = Column(String, unique=True)  # ticket_created, ticket_updated
    subject = Column(String)
    body = Column(Text)
    to_recipients = Column(String)  # JSON string: ["admin@company.com"]
    cc_recipients = Column(String, nullable=True)  # JSON string: ["hr@company.com"]
    bcc_recipients = Column(String, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    conversation_summary = Column(Text)
    initial_concern = Column(Text)
    ai_solution_provided = Column(Text)
    resolution_status = Column(String, default="pending")  # pending, resolved, escalated
    ticket_id = Column(String, nullable=True)  # If escalated to ticket
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    follow_up_needed = Column(Boolean, default=False)
    admin_reviewed = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

# OpenAI setup
openai_api_key = os.environ.get('OPENAI_API_KEY')
if openai_api_key:
    openai.api_key = openai_api_key

# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for API
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "employee"
    designation: Optional[str] = None
    business_unit: Optional[str] = None
    reporting_manager: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TicketCreate(BaseModel):
    category: str
    summary: str
    description: str
    severity: str = "medium"

class ChatRequest(BaseModel):
    message: str
    user_id: str

class EmailConfigModel(BaseModel):
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str

class GPTConfigModel(BaseModel):
    api_key: str

class EmailTemplateModel(BaseModel):
    template_name: str
    subject: str
    body: str
    to_recipients: List[str]
    cc_recipients: Optional[List[str]] = None
    bcc_recipients: Optional[List[str]] = None
    is_active: bool = True

class TicketUpdateModel(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None

class AIConversationModel(BaseModel):
    conversation_summary: str
    initial_concern: str
    ai_solution_provided: str
    resolution_status: str = "pending"

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def chat_with_ai(message: str, user_id: str, db: Session) -> dict:
    """Process chat with CareAI and determine if ticket creation is needed"""
    try:
        # Get user info for context
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.name if user else "User"
        
        # Get recent chat history for context (last 10 messages)
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        
        # Check if this is a follow-up to an unresolved conversation
        conversation_context = ""
        pending_conversation = db.query(AIConversation).filter(
            AIConversation.user_id == user_id,
            AIConversation.resolution_status == "pending"
        ).order_by(AIConversation.created_at.desc()).first()
        
        is_follow_up = False
        if pending_conversation and recent_messages:
            # Check if user is responding to AI's resolution question
            last_ai_message = next((msg for msg in recent_messages if msg.sender == "ai"), None)
            if last_ai_message and ("does this help" in last_ai_message.message.lower() or "resolve your concern" in last_ai_message.message.lower()):
                is_follow_up = True
                conversation_context = f"\nPrevious concern: {pending_conversation.initial_concern}\nPrevious solution: {pending_conversation.ai_solution_provided}\n"
        
        # Build conversation history
        conversation_history = ""
        if recent_messages:
            conversation_history = "\n\nRecent conversation context:\n"
            for msg in reversed(recent_messages):  # Show in chronological order
                role = "Employee" if msg.sender == "user" else "CareAI"
                conversation_history += f"{role}: {msg.message}\n"
        
        # Enhanced system prompt with decisive approach
        system_prompt = f"""You are CareAI, an INTERNAL employee support assistant for Ketto Care. You help employees resolve workplace concerns with a decisive, solution-focused approach.

IMPORTANT INSTRUCTIONS:
1. You are an internal workplace assistant, not an external counselor
2. COLLECT INFORMATION EFFICIENTLY: Ask only 1-2 targeted questions to understand the issue
3. PROVIDE SOLUTIONS QUICKLY: After gathering basic information, offer concrete workplace solutions
4. RESOLUTION BUTTONS: The system will automatically show "This helps" / "Still need help" buttons after you provide solutions
5. DO NOT ask "does this help" in your text - the UI handles this with buttons

CONVERSATION PHASES:
- PHASE 1 (First interaction): Ask 1 focused question to understand the root cause
- PHASE 2 (Second interaction): Provide 3-4 concrete solutions and actionable steps
- PHASE 3 (Buttons): System shows resolution buttons automatically

IMMEDIATE ESCALATION (create ticket right away without investigation):
- Harassment, discrimination, bullying, or serious workplace violations
- Safety concerns or threats
- Employee explicitly requests HR/management intervention
- POSH (Prevention of Sexual Harassment) complaints - NEVER ask for details

CRITICAL POSH COMPLAINT HANDLING:
If user mentions "POSH", "POSH complaint", "sexual harassment complaint", or wants to "raise a POSH complaint":
- IMMEDIATELY respond with: "I understand you want to raise a POSH complaint. This is a serious matter that requires immediate attention through proper channels. I have escalated this to our HR team who will contact you within 24 hours to guide you through the formal POSH complaint process. Your safety and confidentiality are our top priorities."
- DO NOT ask for any details about the incident
- DO NOT investigate further
- The system will automatically create a ticket

SOLUTION-FOCUSED APPROACH:
- Resignation concerns: Understand basic reason → Provide retention solutions
- Workload issues: Quick assessment → Practical time management and delegation solutions  
- Manager conflicts: Brief context → Communication strategies and escalation paths
- Career concerns: Simple needs assessment → Internal growth opportunities

EXAMPLE FLOW:
User: "I want to resign"
AI: "What's the main factor driving this decision - workload, management, career growth, or work environment?"

User: "My manager micromanages me"
AI: "I understand how frustrating micromanagement can be. Here are proven strategies to improve this situation:

1. **Schedule a direct conversation**: Request a one-on-one to discuss working styles and expectations
2. **Demonstrate independence**: Proactively update your manager with progress reports to build trust
3. **Set boundaries**: Propose check-in schedules that work for both of you
4. **Document successes**: Track your autonomous achievements to showcase your reliability
5. **Internal transfer option**: Explore other teams if the relationship doesn't improve

These approaches have helped many employees improve their manager relationships."

[Buttons automatically appear: "This helps" | "Still need help"]

CRITICAL: After providing solutions, STOP talking and let the resolution buttons handle the next step.

{conversation_context}

Current conversation with {user_name}:{conversation_history}

Current message: {message}

Be decisive: investigate briefly, then provide solutions. Let the buttons handle resolution confirmation."""

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            
            
        except Exception as openai_error:
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
            }
        
        # Enhanced escalation logic
        escalate = False
        category = "request"
        severity = "medium" 
        summary = message[:100] + "..." if len(message) > 100 else message
        
        # Log for debugging
        logging.info(f"User message: {message}")
        logging.info(f"Is follow-up: {is_follow_up}")
        logging.info(f"Escalate: {escalate}")
        logging.info(f"Raw AI response: {ai_response[:200]}...")
        
        # Enhanced escalation logic
        # Check for escalation markers from AI
        response_upper = ai_response.upper()
        if "ESCALATE: TRUE" in response_upper or "ESCALATE:TRUE" in response_upper:
            escalate = True
            logging.info("Escalation detected from AI response markers")
        
        # Force escalation for critical keywords
        critical_keywords = ["harassment", "harass", "discriminat", "abuse", "threat", "unsafe", "sexual", "posh"]
        if any(keyword in message.lower() for keyword in critical_keywords):
            escalate = True
            category = "grievance"
            severity = "critical"
            summary = f"Serious workplace concern: {message[:80]}..."
            logging.info(f"Force escalating due to critical keywords in message: {message}")
        
        # Auto-escalate follow-ups indicating unresolved issues
        unresolved_indicators = ["no", "not really", "still having", "doesn't help", "not resolved", "still struggling", "not working"]
        if is_follow_up and any(indicator in message.lower() for indicator in unresolved_indicators):
            escalate = True
            category = "request"
            severity = "medium"
            summary = f"Unresolved workplace concern: {pending_conversation.initial_concern[:60]}..." if pending_conversation else summary
            logging.info("Auto-escalating follow-up with unresolved issue")
        
        # Extract escalation details from AI response
        if escalate:
            if "CATEGORY:" in response_upper:
                category_line = [line for line in ai_response.split('\n') if 'CATEGORY:' in line.upper()]
                if category_line:
                    extracted_category = category_line[0].split(':')[-1].strip().lower()
                    if extracted_category in ['grievance', 'request', 'wellness']:
                        category = extracted_category
            
            if "SEVERITY:" in response_upper:
                severity_line = [line for line in ai_response.split('\n') if 'SEVERITY:' in line.upper()]
                if severity_line:
                    extracted_severity = severity_line[0].split(':')[-1].strip().lower()
                    if extracted_severity in ['low', 'medium', 'high', 'critical']:
                        severity = extracted_severity
            
            if "SUMMARY:" in response_upper:
                summary_line = [line for line in ai_response.split('\n') if 'SUMMARY:' in line.upper()]
                if summary_line:
                    summary = summary_line[0].split(':', 1)[-1].strip()
        
        # Create or update AI conversation record
        conversation_id = None
        if not is_follow_up:
            # New conversation
            ai_conversation = AIConversation(
                user_id=user_id,
                conversation_summary=f"Employee concern: {message[:200]}...",
                initial_concern=message,
                ai_solution_provided=ai_response,
                resolution_status="escalated" if escalate else "pending",
                follow_up_needed=not escalate
            )
            db.add(ai_conversation)
            db.commit()
            db.refresh(ai_conversation)
            conversation_id = ai_conversation.id
        else:
            # Update existing conversation
            if pending_conversation:
                pending_conversation.resolution_status = "escalated" if escalate else "resolved"
                pending_conversation.updated_at = datetime.utcnow()
                pending_conversation.follow_up_needed = False
                db.commit()
                conversation_id = pending_conversation.id
        
        logging.info(f"Final escalation decision: escalate={escalate}, category={category}, severity={severity}")
        
        # Clean AI response from escalation markers
        clean_response = ai_response
        for marker in ["ESCALATE:", "CATEGORY:", "SEVERITY:", "SUMMARY:"]:
            lines = clean_response.split('\n')
            clean_response = '\n'.join([line for line in lines 
                                      if not line.upper().strip().startswith(marker)])
        
        # Determine if we should show resolution buttons
        # Enhanced logic to detect solution-providing responses
        solution_indicators = [
            "here are", "strategies", "approaches", "suggestions", "try", "consider", 
            "recommend", "solution", "steps", "ways to", "you can", "you might",
            "i suggest", "approach", "option", "would help", "could help",
            "proven strategies", "effective way", "helpful", "improve", 
            "schedule a", "document", "discuss", "explore", "look into"
        ]
        
        # More comprehensive question detection
        question_indicators = ["what", "how", "when", "why", "could you", "can you", "would you"]
        
        # Count numbered lists as solutions (AI often provides numbered advice)
        has_numbered_list = bool(len([line for line in clean_response.split('\n') if line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))]) >= 2)
        
        # Check for solution content
        has_solutions = any(indicator in clean_response.lower() for indicator in solution_indicators) or has_numbered_list
        
        # Check if it's primarily asking questions
        question_count = clean_response.count("?")
        starts_with_question = any(clean_response.lower().strip().startswith(q) for q in question_indicators)
        is_mostly_questions = question_count > 1 or (question_count == 1 and starts_with_question and len(clean_response) < 200)
        
        # Show buttons ONLY for final solutions (not initial questions or investigations)
        # Must have multiple solutions AND minimal questions AND be comprehensive
        is_final_solution = has_numbered_list and has_solutions and question_count == 0 and len(clean_response) > 400
        is_comprehensive_advice = has_solutions and len(clean_response) > 500 and question_count == 0 and has_numbered_list
        
        # Additional check: the user message should indicate they've already tried something or need specific help
        user_seeking_final_help = any(phrase in message.lower() for phrase in [
            "i've tried", "i have tried", "nothing changes", "need specific", "need help with", 
            "what should i do", "how do i handle", "need strategies", "need advice"
        ])
        
        should_show_buttons = not escalate and not is_follow_up and (is_final_solution or is_comprehensive_advice) and not is_mostly_questions and user_seeking_final_help
        
        logging.info(f"Resolution buttons logic: escalate={escalate}, is_follow_up={is_follow_up}, has_solutions={has_solutions}, is_mostly_questions={is_mostly_questions}, has_numbered_list={has_numbered_list}, should_show_buttons={should_show_buttons}")
        logging.info(f"Response snippet for analysis: {clean_response[:200]}...")
        logging.info(f"Solution indicators found: {[ind for ind in solution_indicators if ind in clean_response.lower()]}")
        
        return {
            "response": clean_response.strip(),
            "escalate": escalate,
            "category": category,
            "severity": severity,
            "summary": summary,
            "show_resolution_buttons": should_show_buttons,
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        logging.error(f"Error in AI chat: {str(e)}")
        return {
            "response": "I apologize, but I'm experiencing technical difficulties. I'm creating a support ticket to ensure your concern is addressed by our team.",
            "escalate": True,
            "category": "request",
            "severity": "medium",
            "summary": "Technical support needed - AI assistant unavailable"
        }

async def send_email_notification(ticket: Ticket, user: User, db: Session, notification_type: str = "ticket_created"):
    """Send email notification for ticket events using templates"""
    try:
        email_config = db.query(EmailConfig).first()
        if not email_config:
            logging.warning("Email configuration not found")
            return
        
        # Get email template
        template = db.query(EmailTemplate).filter(
            EmailTemplate.template_name == notification_type,
            EmailTemplate.is_active == True
        ).first()
        
        if not template:
            # Default template if none configured
            template_data = get_default_email_template(notification_type)
        else:
            template_data = {
                "subject": template.subject,
                "body": template.body,
                "to_recipients": json.loads(template.to_recipients) if template.to_recipients else [],
                "cc_recipients": json.loads(template.cc_recipients) if template.cc_recipients else [],
                "bcc_recipients": json.loads(template.bcc_recipients) if template.bcc_recipients else []
            }
        
        # Replace placeholders in template
        subject = template_data["subject"].format(
            ticket_id=ticket.id,
            employee_name=user.name,
            employee_email=user.email,
            category=ticket.category,
            severity=ticket.severity,
            summary=ticket.summary,
            status=ticket.status,
            created_at=ticket.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=ticket.updated_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.updated_at else ""
        )
        
        body = template_data["body"].format(
            ticket_id=ticket.id,
            employee_name=user.name,
            employee_email=user.email,
            category=ticket.category,
            severity=ticket.severity,
            summary=ticket.summary,
            description=ticket.description,
            status=ticket.status,
            admin_notes=ticket.admin_notes or "None",
            created_at=ticket.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=ticket.updated_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.updated_at else ""
        )
        
        msg = MIMEMultipart()
        msg['From'] = email_config.smtp_username
        
        # Set recipients from template
        to_recipients = template_data["to_recipients"].copy()
        if user.email not in to_recipients:
            to_recipients.append(user.email)
        
        msg['To'] = ", ".join(to_recipients)
        
        if template_data["cc_recipients"]:
            msg['Cc'] = ", ".join(template_data["cc_recipients"])
        
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(email_config.smtp_server, email_config.smtp_port)
        server.starttls()
        server.login(email_config.smtp_username, email_config.smtp_password)
        
        all_recipients = to_recipients + template_data["cc_recipients"] + template_data["bcc_recipients"]
        server.sendmail(email_config.smtp_username, all_recipients, msg.as_string())
        server.quit()
        
        logging.info(f"Email sent successfully for {notification_type}: {ticket.id}")
        
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

def get_default_email_template(notification_type: str):
    """Get default email templates if none configured"""
    templates = {
        "ticket_created": {
            "subject": "New Support Ticket Created - {ticket_id}",
            "body": """Dear Team,

A new support ticket has been created in Ketto Care:

Ticket Details:
- Ticket ID: {ticket_id}
- Employee: {employee_name} ({employee_email})
- Category: {category}
- Severity: {severity}
- Summary: {summary}
- Description: {description}
- Status: {status}
- Created: {created_at}

Please log in to the admin dashboard to review and respond to this ticket.

Best regards,
Ketto Care System""",
            "to_recipients": ["admin@ketto.org"],
            "cc_recipients": [],
            "bcc_recipients": []
        },
        "ticket_updated": {
            "subject": "Ticket Status Updated - {ticket_id}",
            "body": """Dear {employee_name},

Your support ticket has been updated:

Ticket Details:
- Ticket ID: {ticket_id}
- Category: {category}
- Severity: {severity}
- Summary: {summary}
- Status: {status}
- Admin Notes: {admin_notes}
- Updated: {updated_at}

If you have any questions, please contact your HR team.

Best regards,
Ketto Care System""",
            "to_recipients": [],
            "cc_recipients": [],
            "bcc_recipients": []
        }
    }
    return templates.get(notification_type, templates["ticket_created"])

# Authentication routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    db_user = User(
        id=str(uuid.uuid4()),
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        designation=user_data.designation,
        business_unit=user_data.business_unit,
        reporting_manager=user_data.reporting_manager
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create token
    token = create_access_token({"user_id": db_user.id, "email": db_user.email})
    
    return Token(
        access_token=token,
        token_type="bearer",
        user={
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "role": db_user.role
        }
    )

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": user.id, "email": user.email})
    
    return Token(
        access_token=token,
        token_type="bearer",
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    )

# Chat routes
@api_router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Ensure user can only access their own chat history or admin can access any
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get chat messages for this user, excluding ticket_id is None for cleaner history
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return [
        {
            "id": msg.id,
            "sender": msg.sender,
            "message": msg.message,
            "timestamp": msg.timestamp.isoformat(),
            "ticket_id": msg.ticket_id
        }
        for msg in messages
    ]

@api_router.post("/chat/resolution")
async def handle_resolution_response(
    resolution_data: dict, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Handle resolution button clicks from frontend"""
    conversation_id = resolution_data.get('conversation_id')
    resolution = resolution_data.get('resolution')  # 'helpful' or 'need_help'
    
    if not conversation_id or not resolution:
        raise HTTPException(status_code=400, detail="Missing conversation_id or resolution")
    
    # Find the conversation
    conversation = db.query(AIConversation).filter(AIConversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if resolution == 'helpful':
        # Mark as resolved
        conversation.resolution_status = 'resolved'
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": "Great! I'm glad I could help resolve your concern. Feel free to reach out anytime if you need further assistance.",
            "ticket_created": False
        }
    
    elif resolution == 'need_help':
        # Create ticket and mark as escalated
        ticket = Ticket(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            category="request",
            summary=f"Unresolved concern: {conversation.initial_concern[:80]}...",
            description=conversation.initial_concern,
            severity="medium"
        )
        db.add(ticket)
        
        # Update conversation
        conversation.resolution_status = 'escalated'
        conversation.ticket_id = ticket.id
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ticket)
        
        # Send email notification
        await send_email_notification(ticket, current_user, db, "ticket_created")
        
        return {
            "message": "I understand you need additional support. I've created a support ticket for you and notified our admin team. You should receive follow-up within 24 hours. Your ticket ID is: " + ticket.id,
            "ticket_created": True,
            "ticket_id": ticket.id
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid resolution value")

@api_router.post("/chat")
async def chat_with_careai(chat_request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Save user message
    user_message = ChatMessage(
        id=str(uuid.uuid4()),
        user_id=chat_request.user_id,
        sender="user",
        message=chat_request.message
    )
    db.add(user_message)
    db.commit()
    
    # Get AI response
    ai_result = await chat_with_ai(chat_request.message, chat_request.user_id, db)
    
    # Create ticket if escalation is needed
    ticket_id = None
    if ai_result['escalate']:
        ticket = Ticket(
            id=str(uuid.uuid4()),
            user_id=chat_request.user_id,
            category=ai_result['category'],
            summary=ai_result['summary'],
            description=chat_request.message,
            severity=ai_result['severity']
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        ticket_id = ticket.id
        
        # Send email notification
        await send_email_notification(ticket, current_user, db)
    
    # Save AI response
    ai_message = ChatMessage(
        id=str(uuid.uuid4()),
        ticket_id=ticket_id,
        user_id=chat_request.user_id,
        sender="ai",
        message=ai_result['response']
    )
    db.add(ai_message)
    db.commit()
    
    # Log the AI result for debugging
    logging.info(f"Chat endpoint - AI result keys: {list(ai_result.keys())}")
    logging.info(f"Chat endpoint - show_resolution_buttons: {ai_result.get('show_resolution_buttons', 'NOT_FOUND')}")
    
    return {
        "response": ai_result['response'],
        "ticket_created": ai_result['escalate'],
        "ticket_id": ticket_id,
        "show_resolution_buttons": ai_result.get('show_resolution_buttons', False),
        "conversation_id": ai_result.get('conversation_id')
    }

# Ticket routes
@api_router.get("/tickets")
async def get_user_tickets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tickets = db.query(Ticket).filter(Ticket.user_id == current_user.id).all()
    return [
        {
            "id": ticket.id,
            "category": ticket.category,
            "summary": ticket.summary,
            "description": ticket.description,
            "status": ticket.status,
            "severity": ticket.severity,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
            "admin_notes": ticket.admin_notes
        }
        for ticket in tickets
    ]

@api_router.get("/admin/tickets")
async def get_all_tickets(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    result = []
    for ticket in tickets:
        user = db.query(User).filter(User.id == ticket.user_id).first()
        result.append({
            "id": ticket.id,
            "user_id": ticket.user_id,
            "user_name": user.name if user else "Unknown",
            "user_email": user.email if user else "Unknown",
            "category": ticket.category,
            "summary": ticket.summary,
            "description": ticket.description,
            "status": ticket.status,
            "severity": ticket.severity,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
            "admin_notes": ticket.admin_notes
        })
    return result

@api_router.put("/admin/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, update_data: TicketUpdateModel, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Track if status changed to send notification
    old_status = ticket.status
    
    # Update ticket fields
    if update_data.status:
        ticket.status = update_data.status
    if update_data.admin_notes:
        ticket.admin_notes = update_data.admin_notes
    
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    
    # Send email notification if status changed
    if update_data.status and old_status != update_data.status:
        user = db.query(User).filter(User.id == ticket.user_id).first()
        if user:
            await send_email_notification(ticket, user, db, "ticket_updated")
    
    return {"message": "Ticket updated successfully"}

# Admin routes
# Admin routes for AI conversation tracking
@api_router.get("/admin/ai-conversations")
async def get_ai_conversations(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    conversations = db.query(AIConversation).order_by(AIConversation.created_at.desc()).all()
    result = []
    for conv in conversations:
        user = db.query(User).filter(User.id == conv.user_id).first()
        result.append({
            "id": conv.id,
            "user_id": conv.user_id,
            "user_name": user.name if user else "Unknown",
            "user_email": user.email if user else "Unknown",
            "conversation_summary": conv.conversation_summary,
            "initial_concern": conv.initial_concern,
            "ai_solution_provided": conv.ai_solution_provided,
            "resolution_status": conv.resolution_status,
            "ticket_id": conv.ticket_id,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "follow_up_needed": conv.follow_up_needed,
            "admin_reviewed": conv.admin_reviewed
        })
    return result

@api_router.put("/admin/ai-conversations/{conversation_id}")
async def update_ai_conversation(conversation_id: str, update_data: dict, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    conversation = db.query(AIConversation).filter(AIConversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Update admin_reviewed flag
    if 'admin_reviewed' in update_data:
        conversation.admin_reviewed = update_data['admin_reviewed']
    
    conversation.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Conversation updated successfully"}

@api_router.get("/admin/users")
async def get_all_users(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "designation": user.designation,
            "business_unit": user.business_unit,
            "reporting_manager": user.reporting_manager,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]

@api_router.post("/admin/users")
async def create_user(user_data: UserCreate, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_user = User(
        id=str(uuid.uuid4()),
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        designation=user_data.designation,
        business_unit=user_data.business_unit,
        reporting_manager=user_data.reporting_manager
    )
    
    db.add(db_user)
    db.commit()
    return {"message": "User created successfully"}

@api_router.put("/admin/users/{user_id}")
async def update_user(user_id: str, update_data: dict, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields (except email and id)
    for key, value in update_data.items():
        if key in ['name', 'role', 'designation', 'business_unit', 'reporting_manager'] and hasattr(user, key):
            setattr(user, key, value)
        elif key == 'password' and value:  # Only update password if provided
            user.password_hash = hash_password(value)
    
    db.commit()
    return {"message": "User updated successfully"}

@api_router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@api_router.post("/admin/upload-users")
async def upload_users_csv(file_content: str, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    try:
        # Decode base64 content
        csv_content = base64.b64decode(file_content).decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Validate required columns
        required_columns = ['name', 'email']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}")
        
        users_created = 0
        users_updated = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                user_data = {
                    'name': str(row.get('name', '')).strip(),
                    'email': str(row.get('email', '')).strip().lower(),
                    'password_hash': hash_password(str(row.get('password', 'default123'))),
                    'role': str(row.get('role', 'employee')).strip().lower(),
                    'designation': str(row.get('designation', '')).strip(),
                    'business_unit': str(row.get('business_unit', '')).strip(),
                    'reporting_manager': str(row.get('reporting_manager', '')).strip(),
                    'id': str(uuid.uuid4()),
                    'created_at': datetime.utcnow()
                }
                
                # Validate email format
                if not user_data['email'] or '@' not in user_data['email']:
                    errors.append(f"Row {index + 1}: Invalid email format")
                    continue
                
                # Check if user exists
                existing_user = db.query(User).filter(User.email == user_data['email']).first()
                if existing_user:
                    # Update existing user
                    existing_user.name = user_data['name']
                    existing_user.role = user_data['role']
                    existing_user.designation = user_data['designation']
                    existing_user.business_unit = user_data['business_unit']
                    existing_user.reporting_manager = user_data['reporting_manager']
                    # Only update password if provided in CSV
                    if 'password' in row and str(row['password']).strip():
                        existing_user.password_hash = user_data['password_hash']
                    users_updated += 1
                else:
                    # Create new user
                    new_user = User(**user_data)
                    db.add(new_user)
                    users_created += 1
                    
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        db.commit()
        
        result = {
            "message": f"CSV processed successfully",
            "users_created": users_created,
            "users_updated": users_updated,
            "total_processed": users_created + users_updated,
            "errors": errors
        }
        
        if errors:
            result["message"] += f" with {len(errors)} errors"
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

# Email Template Management
@api_router.get("/admin/email-templates")
async def get_email_templates(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    templates = db.query(EmailTemplate).all()
    return [
        {
            "id": template.id,
            "template_name": template.template_name,
            "subject": template.subject,
            "body": template.body,
            "to_recipients": json.loads(template.to_recipients) if template.to_recipients else [],
            "cc_recipients": json.loads(template.cc_recipients) if template.cc_recipients else [],
            "bcc_recipients": json.loads(template.bcc_recipients) if template.bcc_recipients else [],
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat()
        }
        for template in templates
    ]

@api_router.post("/admin/email-templates")
async def create_or_update_email_template(template_data: EmailTemplateModel, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    # Check if template exists
    existing_template = db.query(EmailTemplate).filter(EmailTemplate.template_name == template_data.template_name).first()
    
    if existing_template:
        # Update existing template
        existing_template.subject = template_data.subject
        existing_template.body = template_data.body
        existing_template.to_recipients = json.dumps(template_data.to_recipients)
        existing_template.cc_recipients = json.dumps(template_data.cc_recipients) if template_data.cc_recipients else None
        existing_template.bcc_recipients = json.dumps(template_data.bcc_recipients) if template_data.bcc_recipients else None
        existing_template.is_active = template_data.is_active
        existing_template.updated_at = datetime.utcnow()
        message = "Email template updated successfully"
    else:
        # Create new template
        new_template = EmailTemplate(
            template_name=template_data.template_name,
            subject=template_data.subject,
            body=template_data.body,
            to_recipients=json.dumps(template_data.to_recipients),
            cc_recipients=json.dumps(template_data.cc_recipients) if template_data.cc_recipients else None,
            bcc_recipients=json.dumps(template_data.bcc_recipients) if template_data.bcc_recipients else None,
            is_active=template_data.is_active
        )
        db.add(new_template)
        message = "Email template created successfully"
    
    db.commit()
    return {"message": message}

@api_router.delete("/admin/email-templates/{template_id}")
async def delete_email_template(template_id: int, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")
    
    db.delete(template)
    db.commit()
    return {"message": "Email template deleted successfully"}

# Configuration routes
@api_router.post("/admin/email-config")
async def save_email_config(config: EmailConfigModel, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    # Delete existing config
    db.query(EmailConfig).delete()
    
    # Create new config
    email_config = EmailConfig(
        smtp_server=config.smtp_server,
        smtp_port=config.smtp_port,
        smtp_username=config.smtp_username,
        smtp_password=config.smtp_password
    )
    db.add(email_config)
    db.commit()
    return {"message": "Email configuration saved"}

@api_router.get("/admin/email-config")
async def get_email_config(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    config = db.query(EmailConfig).first()
    if config:
        return {
            "smtp_server": config.smtp_server,
            "smtp_port": config.smtp_port,
            "smtp_username": config.smtp_username,
            "smtp_password": config.smtp_password
        }
    return {}

@api_router.post("/admin/gpt-config")
async def save_gpt_config(config: GPTConfigModel, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    openai.api_key = config.api_key
    
    # Test the API key
    try:
        test_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        
        # Delete existing config
        db.query(GPTConfig).delete()
        
        # Create new config
        gpt_config = GPTConfig(
            api_key=config.api_key,
            is_active=True,
            last_tested_at=datetime.utcnow()
        )
        db.add(gpt_config)
        db.commit()
        
        return {"message": "GPT configuration saved and tested successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid API key: {str(e)}")

@api_router.get("/admin/gpt-config")
async def get_gpt_config(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    config = db.query(GPTConfig).first()
    if config:
        return {
            "api_key": config.api_key[:10] + "..." if len(config.api_key) > 10 else config.api_key,
            "is_active": config.is_active,
            "last_tested_at": config.last_tested_at.isoformat() if config.last_tested_at else None
        }
    return {}

# Initialize admin user
@api_router.post("/init-admin")
async def initialize_admin(db: Session = Depends(get_db)):
    admin_exists = db.query(User).filter(User.role == "admin").first()
    if admin_exists:
        return {
            "message": "Admin already exists", 
            "email": "admin@ketto.org", 
            "password": "admin123",
            "admin_name": admin_exists.name
        }
    
    admin_user = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@ketto.org",
        password_hash=hash_password("admin123"),
        role="admin"
    )
    
    db.add(admin_user)
    db.commit()
    return {"message": "Admin user created successfully", "email": "admin@ketto.org", "password": "admin123"}

# API root endpoint
@api_router.get("/")
async def root():
    return {"message": "Ketto Care API is running", "version": "1.0.0", "status": "healthy"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)