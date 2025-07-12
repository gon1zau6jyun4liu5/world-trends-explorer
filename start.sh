#!/bin/bash

# World Trends Explorer - Quick Start Script

echo "🌍 Starting World Trends Explorer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Start the backend server
echo "🚀 Starting backend server..."
echo "Backend will be available at: http://localhost:5555"
echo "API documentation: http://localhost:5555/api/trends/health"
echo ""
echo "📝 To start the frontend:"
echo "1. Open a new terminal"
echo "2. Navigate to the frontend directory"
echo "3. Open index.html in a web browser or use a local server"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
