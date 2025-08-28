# 🚀 New Device Setup Guide

Follow this guide to replicate the Neona Chat Demo on a new device.

## 📋 Required Documents/Information

### 1. API Keys (Critical) 🔑
You'll need these API keys from your original setup:

```env
# REQUIRED - Azure OpenAI (for LLM responses)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# OPTIONAL - TTS Services (app works with fallback if missing)
TYPECAST_API_KEY=your-typecast-key
SEOLMINSEOK_API_KEY=your-seolminseok-key
SEOLMINSEOK_ACTOR_ID=your-actor-id

# OPTIONAL - STT Service (for voice input)
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=your-region
```

### 2. MongoDB Connection Info
Choose one option:

**Option A: Local MongoDB (Recommended for development)**
- Install MongoDB Community Edition
- Default connection: `mongodb://localhost:27017/neona_chat`

**Option B: MongoDB Atlas (Cloud)**
- Connection string from your Atlas cluster
- Format: `mongodb+srv://username:password@cluster.mongodb.net/neona_chat?retryWrites=true&w=majority`

## 🛠️ Step-by-Step Setup

### Step 1: Prerequisites Installation

**Install Required Software:**
- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Git](https://git-scm.com/downloads/)
- [MongoDB Community](https://docs.mongodb.com/manual/installation/) (if using local)

**macOS (Homebrew):**
```bash
brew install python node git mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm git
# Follow MongoDB installation guide for your OS
```

### Step 2: Clone Repository
```bash
git clone https://github.com/sagheepark/neona_turn_based_demo.git
cd neona_turn_based_demo

# Switch to memory_cache branch (contains deployment features)
git checkout memory_cache
```

### Step 3: Backend Setup
```bash
cd backend_clean

# Run automated setup
./setup.sh

# If setup.sh doesn't run, make it executable:
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Copy `.env.example` to `.env`
- ✅ Check MongoDB status
- ✅ Install frontend dependencies

### Step 4: Configure Environment
Edit the `.env` file in `backend_clean/`:

```bash
# Edit with your favorite editor
nano .env
# or
code .env
# or
vim .env
```

**Paste your API keys** from the original setup.

### Step 5: Import Sample Data
```bash
# Start with sample data (recommended for first setup)
python3 import_mongodb_data.py

# Choose option 1 to import all sample data
# This creates:
# - 3 Characters (설민석, 박현, 윤아리)
# - Korean history knowledge base
# - Sample conversations
```

### Step 6: Start Application

**Terminal 1 - Backend:**
```bash
cd backend_clean
source venv/bin/activate  # Activate virtual environment
python3 main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the app:** `http://localhost:3000`

## ✅ Verification Checklist

Test these features to confirm everything works:

- [ ] **Frontend loads** at `http://localhost:3000`
- [ ] **Characters display** (설민석, 박현, 윤아리)
- [ ] **Chat functionality** - can send messages
- [ ] **Greeting works** - character responds with predefined greeting
- [ ] **TTS audio** - character speech plays (may use fallback if API keys missing)
- [ ] **Memory system** - character remembers context from previous messages
- [ ] **Korean text** - displays correctly throughout the app

## 🔧 Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
ps aux | grep mongod

# Start MongoDB (macOS)
brew services start mongodb-community

# Start MongoDB (Ubuntu)
sudo systemctl start mongod

# Check connection from Python
cd backend_clean
python3 -c "from pymongo import MongoClient; print('MongoDB connected!' if MongoClient().admin.command('ping') else 'Connection failed')"
```

### Python Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### API Key Issues
- **Azure OpenAI required** - app won't work without this
- **TTS optional** - will use silent fallback audio
- **STT optional** - voice input disabled if missing

### Frontend Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## 📁 Important Files on New Device

Make sure these files exist after setup:

```
neona_turn_based_demo/
├── backend_clean/
│   ├── .env                     # Your API keys (created from .env.example)
│   ├── venv/                    # Python virtual environment  
│   └── mongodb_data/            # Sample data (included in repo)
├── frontend/
│   └── node_modules/            # Frontend dependencies
└── DEPLOYMENT.md                # Full deployment guide
```

## 🆘 Need Help?

1. **Check logs** in terminal for error messages
2. **Verify API keys** in `.env` file
3. **Ensure MongoDB** is running and accessible
4. **Review DEPLOYMENT.md** for detailed troubleshooting

## 🎯 Success Indicators

You'll know setup is successful when:
- Backend shows: `Server running on http://localhost:8000`
- Frontend shows: `Ready - started server on 0.0.0.0:3000`
- Browser shows character selection screen
- 설민석 character greets you in Korean when selected

---

**Repository:** https://github.com/sagheepark/neona_turn_based_demo
**Branch:** memory_cache
**Full Guide:** DEPLOYMENT.md