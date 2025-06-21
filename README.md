# 🏥 Ketto Care - Employee Mental Wellness Platform

A comprehensive employee mental wellness and grievance management platform with integrated AI assistant CareAI.

## ✨ Features

- 🤖 **CareAI Assistant**: AI-powered workplace support and guidance
- 🎫 **Ticket Management**: Structured grievance and request handling
- 👥 **User Management**: Complete employee administration system
- 📧 **Email Notifications**: Automated alert system
- 📊 **Admin Dashboard**: Comprehensive oversight and analytics
- 🔐 **Secure Authentication**: JWT-based role management
- 📱 **Responsive Design**: Works on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone [your-repo-url]
cd ketto-care
```

2. **Set up environment variables**
```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
# Edit .env files with your API keys
```

3. **Install dependencies**
```bash
npm run install-deps
```

4. **Run the application**
```bash
npm run dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## 🌐 Deployment

This project is configured for easy deployment on multiple platforms:

- **Railway** (Recommended): `railway up`
- **Render**: Connect GitHub repo
- **Vercel**: `vercel`
- **Netlify + Railway**: Separate frontend/backend
- **Docker**: `docker-compose up`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11
- **Database**: SQLite (production-ready with PostgreSQL)
- **Authentication**: JWT tokens with bcrypt hashing
- **AI Integration**: OpenAI GPT-3.5-turbo
- **Email**: SMTP with configurable templates

### Frontend (React)
- **Framework**: React 19 with modern hooks
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **HTTP Client**: Axios

### Database Schema
- **Users**: Employee profiles and authentication
- **Tickets**: Support requests and grievances
- **ChatMessages**: Conversation history
- **AIConversations**: AI interaction tracking
- **EmailConfig**: SMTP configuration

## 👥 User Roles

### Employee Interface
- Chat with CareAI for workplace support
- View personal ticket history
- Track resolution status
- Access mental wellness resources

### Admin Dashboard
- Manage all employee tickets
- Monitor AI conversations
- User account management
- Email configuration
- Bulk CSV user import

## 🤖 CareAI Features

### Intelligent Conversations
- Context-aware responses
- Solution-focused approach
- Automatic escalation detection
- Follow-up management

### Escalation Logic
- **Immediate**: Harassment, discrimination, safety
- **Gradual**: Performance issues after solutions
- **User-triggered**: "Still need help" button

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_jwt_secret_key
DATABASE_URL=sqlite:///./ketto_care.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
```

**Frontend (frontend/.env)**
```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_NAME=Ketto Care
```

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Chat & AI
- `POST /api/chat` - Chat with CareAI
- `POST /api/chat/resolution` - Handle resolution buttons
- `GET /api/chat/history` - Get chat history

### Tickets
- `GET /api/tickets` - Get user tickets
- `POST /api/admin/tickets` - Create ticket
- `PUT /api/admin/tickets/{id}` - Update ticket

### Admin
- `GET /api/admin/users` - List users
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Manual Testing
1. Create admin user
2. Test employee chat functionality
3. Verify ticket creation and management
4. Test email notifications
5. Validate user management

## 🐳 Docker Support

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker build -t ketto-care .
docker run -p 8000:8000 ketto-care
```

## 📈 Monitoring

### Health Checks
- `GET /health` - Application health status
- `GET /api/health` - API health check

### Logging
- Structured logging with timestamp
- Error tracking and debugging
- Performance monitoring

## 🔒 Security

### Authentication
- JWT tokens with 7-day expiry
- Bcrypt password hashing
- Role-based access control

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration

## 🛠️ Development

### Project Structure
```
ketto-care/
├── backend/
│   ├── server.py          # Main FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   └── App.js        # Main React component
│   └── package.json      # Node dependencies
├── deploy.sh             # Deployment helper
├── docker-compose.yml    # Docker configuration
└── README.md
```

### Adding Features
1. Backend: Add endpoints in `server.py`
2. Frontend: Update components in `src/`
3. Database: Add models and migrations
4. Testing: Create test cases

## 📋 Troubleshooting

### Common Issues

**Port conflicts**
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

**Database issues**
```bash
# Reset database
rm ketto_care.db
# Restart backend to recreate
```

**API key errors**
- Verify OpenAI API key validity
- Check API usage limits
- Ensure proper environment variable setup

## 📞 Support

For technical support:
1. Check logs for error details
2. Verify environment configuration
3. Test with minimal setup
4. Review deployment documentation

## 🏆 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request with description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Roadmap

- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Multi-language support
- [ ] Advanced AI capabilities
- [ ] Integration with HR systems

---

**Built with ❤️ for employee wellbeing**