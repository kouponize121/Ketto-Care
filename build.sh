#!/bin/bash

# Build script for Render deployment
echo "🔧 Building Ketto Care for deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Node.js is available and build frontend
if command -v npm &> /dev/null; then
    echo "📦 Installing Node.js dependencies..."
    cd frontend
    npm install
    
    echo "🏗️ Building React frontend..."
    npm run build
    
    echo "✅ Frontend built successfully!"
    cd ..
else
    echo "⚠️ Node.js not found, skipping frontend build"
fi

# Set Python path
export PYTHONPATH=/opt/render/project/src

echo "✅ Build completed successfully!"