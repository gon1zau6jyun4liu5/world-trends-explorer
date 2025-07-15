#!/bin/bash

# World Trends Explorer - SerpAPI Start Script

echo "🌍 Starting World Trends Explorer with SerpAPI..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Navigate to backend directory
cd backend

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
pip install -r requirements.txt
pip install python-dotenv requests  # Ensure required packages are installed

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo ""
    echo "📝 To use real Google Trends data:"
    echo "1. Copy .env.example to .env:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. Edit .env and add your SerpAPI key:"
    echo "   SERPAPI_API_KEY=your-api-key-here"
    echo ""
    echo "3. Get a free API key from: https://serpapi.com/"
    echo ""
    echo "🎭 Starting in MOCK MODE (sample data only)"
    echo ""
    sleep 3
else
    echo "✅ .env file found"
    # Check if API key is set
    if grep -q "your-serpapi-api-key-here" .env; then
        echo "⚠️  WARNING: API key not configured in .env file!"
        echo "Please edit .env and add your actual SerpAPI key"
        echo ""
        sleep 3
    fi
fi

# Start the SerpAPI backend server
echo "🚀 Starting SerpAPI backend server..."
echo "Backend will be available at: http://localhost:5000"
echo "API documentation: http://localhost:5000/api/trends/health"
echo ""
echo "📝 To start the frontend:"
echo "1. Open a new terminal"
echo "2. Navigate to the frontend directory"
echo "3. Open index.html in a web browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app_serpapi.py
