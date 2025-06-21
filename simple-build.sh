#!/bin/bash

# Simple deployment script for Render
echo "🚀 Building Ketto Care..."

# Install Python deps
pip install -r requirements.txt

# Build frontend
if [ -d "frontend" ]; then
    cd frontend
    npm install
    npm run build
    
    if [ -d "build" ]; then
        echo "✅ Frontend build successful"
        ls -la build/
    else
        echo "❌ Frontend build failed"
    fi
    cd ..
else
    echo "❌ Frontend directory not found"
fi

echo "✅ Build complete"