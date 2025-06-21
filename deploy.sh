#!/bin/bash

# Ketto Care Deployment Script
# This script helps deploy the application to various platforms

echo "🚀 Ketto Care Deployment Helper"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Choose your deployment platform:${NC}"
echo "1. Railway (Full-Stack - Recommended)"
echo "2. Render (Full-Stack)"
echo "3. Vercel (Full-Stack)"
echo "4. Netlify (Frontend Only) + Railway (Backend)"
echo "5. Heroku (Full-Stack)"

read -p "Enter your choice (1-5): " choice

case $choice in
  1)
    echo -e "${GREEN}🚂 Railway Deployment${NC}"
    echo "1. Install Railway CLI: npm install -g @railway/cli"
    echo "2. Login: railway login"
    echo "3. Deploy: railway up"
    echo "4. Set environment variables in Railway dashboard:"
    echo "   - OPENAI_API_KEY=your_openai_key"
    echo "   - SECRET_KEY=your_secret_key"
    ;;
  2)
    echo -e "${GREEN}🎨 Render Deployment${NC}"
    echo "1. Connect your GitHub repo to Render"
    echo "2. Select 'Web Service'"
    echo "3. Render will automatically use render.yaml"
    echo "4. Set OPENAI_API_KEY in environment variables"
    ;;
  3)
    echo -e "${GREEN}▲ Vercel Deployment${NC}"
    echo "1. Install Vercel CLI: npm install -g vercel"
    echo "2. Login: vercel login"
    echo "3. Deploy: vercel"
    echo "4. Set environment variables: vercel env add"
    ;;
  4)
    echo -e "${GREEN}🌐 Netlify + Railway${NC}"
    echo "Frontend (Netlify):"
    echo "1. Connect frontend folder to Netlify"
    echo "2. Build command: npm run build"
    echo "3. Publish directory: build"
    echo ""
    echo "Backend (Railway):"
    echo "1. Deploy backend folder to Railway"
    echo "2. Update REACT_APP_BACKEND_URL in Netlify env vars"
    ;;
  5)
    echo -e "${GREEN}🟣 Heroku Deployment${NC}"
    echo "1. Install Heroku CLI"
    echo "2. heroku create your-app-name"
    echo "3. git push heroku main"
    echo "4. heroku config:set OPENAI_API_KEY=your_key"
    ;;
  *)
    echo -e "${RED}Invalid choice!${NC}"
    exit 1
    ;;
esac

echo ""
echo -e "${BLUE}📋 Required Environment Variables:${NC}"
echo "- OPENAI_API_KEY: Get from https://platform.openai.com/"
echo "- SECRET_KEY: Any random string (e.g., generate with: openssl rand -hex 32)"
echo "- DATABASE_URL: sqlite:///./ketto_care.db (default)"

echo ""
echo -e "${GREEN}✅ Configuration files created!${NC}"
echo "Your project is now ready for deployment on any platform."