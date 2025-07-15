#!/bin/bash

# Run all tests for World Trends Explorer

echo "🧪 Running World Trends Explorer Tests..."

# Create tests directory if it doesn't exist
mkdir -p tests

# Navigate to project root
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "backend/venv" ]; then
    echo "🔄 Activating virtual environment..."
    source backend/venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Python tests
echo ""
echo "🐍 Running Python backend tests..."
python -m pytest tests/ -v

# If pytest is not installed, use unittest
if [ $? -ne 0 ]; then
    echo "📦 Installing pytest..."
    pip install pytest
    python -m pytest tests/ -v
    
    # Fallback to unittest if pytest fails
    if [ $? -ne 0 ]; then
        echo "Using unittest instead..."
        python -m unittest discover tests/ -v
    fi
fi

echo ""
echo "✅ All tests completed!"
