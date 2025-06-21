# 🚀 Ketto Care Deployment Guide

## Quick Start

Your Ketto Care application is now deployment-ready for multiple platforms!

## 📋 Prerequisites

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Secret Key**: Generate with `openssl rand -hex 32`

## 🎯 One-Click Deployments

### 1. Railway (Recommended - Full Stack)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

1. Connect your GitHub repository
2. Set environment variables:
   - `OPENAI_API_KEY`
   - `SECRET_KEY`
3. Deploy automatically with `railway.toml`

### 2. Render (Full Stack)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Connect GitHub repository
2. Select "Web Service"
3. Uses `render.yaml` automatically
4. Set `OPENAI_API_KEY` in dashboard

### 3. Vercel (Full Stack)
[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new)

```bash
npm install -g vercel
vercel login
vercel
```

### 4. Netlify (Frontend) + Railway/Render (Backend)

**Frontend on Netlify:**
- Build command: `npm run build`
- Publish directory: `frontend/build`
- Environment: `REACT_APP_BACKEND_URL`

**Backend on Railway/Render**

### 5. Heroku
```bash
heroku create your-app-name
git push heroku main
heroku config:set OPENAI_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret
```

## 🐳 Docker Deployment

### Local Docker
```bash
# Copy environment files
cp .env.example .env
cp frontend/.env.example frontend/.env

# Build and run
docker-compose up --build
```

### Docker Hub
```bash
# Build images
docker build -f Dockerfile -t ketto-care .

# Run container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key ketto-care
```

## 🔧 Platform-Specific Instructions

### Railway
- Configuration: `railway.toml`
- Command: `railway up`
- Environment variables in dashboard

### Render
- Configuration: `render.yaml`
- Auto-deploy from GitHub
- Free tier available

### Vercel
- Configuration: `vercel.json`
- Serverless functions for backend
- Edge deployment

### Netlify
- Configuration: `netlify.toml`
- Best for frontend only
- Combine with backend service

## 📱 Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./ketto_care.db
```

### Frontend (frontend/.env)
```
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

## 🛠️ Local Development

```bash
# Install dependencies
npm run install-deps

# Run both frontend and backend
npm run dev

# Or separately
npm run backend  # Port 8000
npm run frontend # Port 3000
```

## 📊 Database

- **Development**: SQLite (included)
- **Production**: PostgreSQL/MySQL supported
- **Database file**: `ketto_care.db` (auto-created)

## 🔒 Security Notes

1. Always use environment variables for secrets
2. Generate strong SECRET_KEY
3. Keep OPENAI_API_KEY secure
4. Use HTTPS in production

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Change ports in scripts
2. **Missing dependencies**: Run `npm run install-deps`
3. **Database errors**: Delete `ketto_care.db` to reset
4. **API errors**: Check OPENAI_API_KEY validity

### Platform-Specific

**Railway:**
- Check logs: `railway logs`
- Redeploy: `railway up --detach`

**Render:**
- Check service logs in dashboard
- Verify build commands

**Vercel:**
- Check function logs
- Verify serverless configuration

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify environment variables
3. Test locally before deploying
4. Check platform-specific documentation

## 🎉 Success!

Once deployed, your Ketto Care application will be available at your platform's provided URL with full functionality:

- ✅ Employee chat interface
- ✅ AI-powered CareAI assistant
- ✅ Admin ticket management
- ✅ User management system
- ✅ Email notifications
- ✅ Responsive design

Happy deploying! 🚀