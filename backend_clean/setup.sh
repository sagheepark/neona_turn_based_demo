#!/bin/bash
# ===========================================
# NEONA CHAT DEMO - Setup Script
# ===========================================
# This script sets up the development environment

set -e  # Exit on any error

echo "🚀 Setting up Neona Chat Demo..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if MongoDB is running (for local setup)
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Please start MongoDB or use MongoDB Atlas."
    echo "   Local MongoDB: brew services start mongodb/brew/mongodb-community"
    echo "   Or configure MongoDB Atlas in .env file"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
    echo "   Required: AZURE_OPENAI_* settings"
    echo "   Optional: TYPECAST_*, SEOLMINSEOK_*, AZURE_SPEECH_*"
fi

# Setup frontend
echo "🎨 Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
npm install

# Go back to backend
cd ../backend_clean

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start MongoDB (if using local): brew services start mongodb/brew/mongodb-community"
echo "3. Start backend: python3 main.py"
echo "4. In another terminal, start frontend: cd ../frontend && npm run dev"
echo "5. Open http://localhost:3000 in your browser"
echo ""
echo "🔧 Troubleshooting:"
echo "- If TTS doesn't work, check TYPECAST_* and SEOLMINSEOK_* keys in .env"
echo "- If STT doesn't work, check AZURE_SPEECH_* keys in .env"
echo "- If MongoDB connection fails, check MONGODB_URL in .env"