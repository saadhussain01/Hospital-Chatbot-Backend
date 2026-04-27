#!/bin/bash

# Hospital Chatbot Backend - Quick Start Script
# This script sets up and runs the backend server

echo "╔════════════════════════════════════════════════════════╗"
echo "║   Hospital Chatbot Backend - Quick Start Setup        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo ""
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "   ✅ .env file created - please configure it with your settings"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python3 -c "
from database import Database
db = Database()
db.initialize()
print('   ✅ Database initialized with sample data')
"

# Check if initialization was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║              Setup Complete! 🎉                        ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "📝 Next Steps:"
    echo ""
    echo "   1. Review and configure .env file"
    echo "   2. Start the server with: python main.py"
    echo "   3. Access API docs at: http://localhost:8000/docs"
    echo "   4. Run tests with: python test_system.py"
    echo ""
    echo "🚀 To start the server now, run:"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    echo ""
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi
