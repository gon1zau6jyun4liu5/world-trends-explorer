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

# Show server options
echo ""
echo "🚀 Choose which server to start:"
echo "1. Real Google Trends API (port 5000) - Default"
echo "2. Mock Test Server (port 5001) - For development"
echo ""
read -p "Enter your choice (1 or 2, default is 1): " choice

case $choice in
    2)
        echo "🧪 Starting Mock Test Server..."
        echo "📍 Mock server will be available at: http://localhost:5001"
        echo "🔍 This provides realistic test data without API limits"
        echo ""
        python mock_server.py
        ;;
    *)
        echo "🌐 Starting Real Google Trends API Server..."
        echo "📍 Backend will be available at: http://localhost:5000"
        echo "🔗 API documentation: http://localhost:5000/api/trends/health"
        echo ""
        python app.py
        ;;
esac

echo ""
echo "📝 To start the frontend:"
echo "1. Open a new terminal"
echo "2. Navigate to the frontend directory"
echo "3. Open index.html in a web browser or use a local server"
echo ""
echo "💡 Tip: You can also run both servers simultaneously:"
echo "   - Terminal 1: python app.py (Real API on port 5000)"
echo "   - Terminal 2: python mock_server.py (Mock API on port 5001)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""