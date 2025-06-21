#!/bin/bash

# Build script for Render deployment
echo "🔧 Building Ketto Care for deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set Python path
export PYTHONPATH=/opt/render/project/src

echo "✅ Build completed successfully!"