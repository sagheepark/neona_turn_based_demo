# 🚀 Neona Chat Demo - Deployment Guide

This guide helps you replicate the Neona Chat Demo to another device using GitHub and local MongoDB.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Git** - [Download here](https://git-scm.com/downloads/)

**Note**: MongoDB is no longer required! The demo now uses local file storage for all data.

### API Keys Needed
- **Azure OpenAI** - Required for LLM responses
- **Typecast API** - Optional for TTS (will use fallback if missing)
- **SeolMinSeok TTS** - Optional for 설민석 character voice
- **Azure Speech Services** - Optional for STT (voice input)

## 🔧 Step-by-Step Setup

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd neona_turn_based_demo_with_agent
```

### 2. No Database Setup Required!
The demo now uses local file storage, so no MongoDB installation or setup is needed. All character data, knowledge, and conversations are stored in local files.

### 3. Run Setup Script
```bash
cd backend_clean
./setup.sh
```

The setup script will:
- ✅ Check Python 3 and Node.js installation
- ✅ Create Python virtual environment
- ✅ Install Python dependencies
- ✅ Copy `.env.example` to `.env`
- ✅ Install frontend dependencies

### 4. Configure Environment Variables
Edit the `.env` file in `backend_clean/` directory:

#### Required Configuration
```env
# Azure OpenAI (REQUIRED)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# MongoDB (NO LONGER REQUIRED - demo uses local files)
# MONGODB_URL=mongodb://localhost:27017/neona_chat
```

#### Optional Configuration
```env
# Typecast TTS (Optional - fallback used if missing)
TYPECAST_API_KEY=your-typecast-key
TYPECAST_API_URL=https://api.icepeak.ai/v1

# SeolMinSeok TTS (Optional - for 설민석 character)
SEOLMINSEOK_API_KEY=your-seolminseok-key
SEOLMINSEOK_ACTOR_ID=your-actor-id
SEOLMINSEOK_ENDPOINT=https://dev.icepeak.ai/api/text-to-speech

# Azure Speech (Optional - for voice input)
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=your-region
```

### 5. Start the Application

#### Terminal 1 - Backend
```bash
cd backend_clean
source venv/bin/activate  # Activate virtual environment
python3 main.py
```
Backend will run on `http://localhost:8000`

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
Frontend will run on `http://localhost:3000`

### 6. Sample Data Already Included!
The demo comes with pre-configured local data:

**Characters Available:**
- 설쌤 (Korean History Quiz Tutor)
- 닥터 지니 (Science Quiz Tutor)

**Knowledge Base:**
- Korean history knowledge (898 items)
- Science knowledge (188 items)

**Session Storage:**
- All conversations saved to `conversations/` folder
- No database import needed!

### 7. Test the Application
1. Open `http://localhost:3000` in your browser
2. Select a character (try 설민석 for full features)
3. Test greeting functionality
4. Try voice input/output if configured

## 🗂️ Project Structure

```
neona_turn_based_demo_with_agent/
├── backend_clean/                 # Python FastAPI backend
│   ├── main.py                   # Main application
│   ├── services/                 # Core services
│   ├── mongodb_data/             # Sample data for import
│   ├── conversations/            # Chat data storage (excluded in .gitignore)
│   ├── .env.example             # Environment template
│   ├── requirements.txt         # Python dependencies
│   ├── setup.sh                 # Setup script
│   ├── export_mongodb_data.py   # Export data script
│   ├── import_mongodb_data.py   # Import data script
│   └── populate_sample_data.py  # Create sample data script
├── frontend/                     # Next.js frontend
│   ├── src/                     # Source code
│   ├── package.json            # Node dependencies
│   └── ...
└── DEPLOYMENT.md               # This guide
```

## 🎯 Key Features

### Memory Cache System
- **Greeting-Triggered Knowledge Caching** - RAG runs proactively on greetings
- **Incremental Knowledge Addition** - New knowledge added during conversation
- **67% Latency Reduction** - Through intelligent caching

### Character-Specific Features
- **설민석 (Seol Min-seok)** - Dedicated TTS service with historical knowledge
- **Predefined Greetings** - Character-specific opening messages
- **Dynamic Voice Selection** - Different TTS services per character

### Audio System
- **TTS (Text-to-Speech)** - Multiple providers with fallback
- **STT (Speech-to-Text)** - Azure Speech Services integration
- **Audio Player** - Custom React component with waveform visualization

## 🔍 Troubleshooting

### MongoDB Issues
```bash
# Check if MongoDB is running
ps aux | grep mongod

# Check MongoDB logs
tail -f /usr/local/var/log/mongodb/mongo.log

# Restart MongoDB
brew services restart mongodb/brew/mongodb-community
```

### Python Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### TTS Not Working
1. Check if API keys are set in `.env`
2. Look for TTS errors in backend logs
3. Test with fallback TTS (no API keys needed)

### Frontend Build Issues
```bash
# Clear Node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📊 Data Transfer & Migration

### Exporting Your Data
If you have existing data you want to transfer:

```bash
cd backend_clean
python3 export_mongodb_data.py
```

This creates `mongodb_data/` folder with:
- JSON files for each collection
- Metadata with export information  
- README with import instructions

### Importing Data to New Device
After cloning the repository:

```bash
cd backend_clean
python3 import_mongodb_data.py
# Choose option 1 for all collections
# Or option 2 for specific collections
```

### Creating Fresh Sample Data
To start with demo data:

```bash
cd backend_clean  
python3 populate_sample_data.py
# This creates characters, knowledge base, and sample conversations
```

## 🌐 Using MongoDB Atlas (Cloud)

For cloud deployment, use MongoDB Atlas instead of local MongoDB:

1. Create MongoDB Atlas account
2. Create a cluster  
3. Get connection string
4. Update `.env`:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/neona_chat?retryWrites=true&w=majority
```

**Benefits of MongoDB Atlas:**
- ✅ No local MongoDB installation needed
- ✅ Data accessible from multiple devices
- ✅ Automatic backups and security
- ✅ Free tier available (512MB)

## 🔒 Security Notes

- Never commit `.env` file to Git
- Use environment variables for all secrets
- Regularly rotate API keys
- Use HTTPS in production

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)

---
*Generated with Claude Code* 🤖