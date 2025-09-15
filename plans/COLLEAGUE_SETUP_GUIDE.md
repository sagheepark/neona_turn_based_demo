# 🚀 Neona Quiz Characters - Colleague Setup Guide

This guide helps your colleague set up the Neona Quiz system (`seol_min_seok_quiz` and `dr_genie_science_quiz`) on a new laptop.

## 📋 System Overview

**What Works**: The two quiz characters with full TTS, quiz flow, and knowledge base integration.
**What's Skipped**: MongoDB-dependent features (memory system, advanced character management) - these are not needed for quiz functionality.

---

## 🛠️ Prerequisites Installation

### 1. Required Software
Install these on the new laptop:

**macOS:**
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required software
brew install python@3.11 node git
```

**Windows:**
- [Python 3.11+](https://www.python.org/downloads/) ✅ Add to PATH
- [Node.js 18+](https://nodejs.org/) ✅ LTS version
- [Git](https://git-scm.com/downloads/)

**Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm git
```

### 2. Verify Installation
```bash
python3 --version  # Should show 3.11+
node --version     # Should show 18+
npm --version      # Should show 8+
git --version      # Should show 2.0+
```

---

## 🔑 Required API Keys

### **CRITICAL: Azure OpenAI (Required)**
The system will NOT work without these:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

**How to get these:**
1. Go to [Azure Portal](https://portal.azure.com/)
2. Create/find your OpenAI resource
3. Copy the endpoint and API key
4. Note your deployment name (usually `gpt-4o`)

### **OPTIONAL: TTS Services (Recommended)**
For better voice quality:

```env
# For seol_min_seok_quiz and dr_genie_science_quiz characters
SEOLMINSEOK_API_KEY=your-seolminseok-key
SEOLMINSEOK_ACTOR_ID=your-actor-id

# For other characters (if needed)
TYPECAST_API_KEY=your-typecast-key
```

**Note**: If TTS keys are missing, the system uses fallback TTS (silent audio with proper timing).

---

## 📁 Repository Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/neona_turn_based_demo_with_agent.git
cd neona_turn_based_demo_with_agent
```

### 2. Backend Setup
```bash
cd backend_clean

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Create .env file in backend_clean directory
touch .env

# Add your API keys to .env file:
echo "AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/" >> .env
echo "AZURE_OPENAI_API_KEY=your-api-key-here" >> .env
echo "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o" >> .env

# Optional TTS keys:
echo "SEOLMINSEOK_API_KEY=your-seolminseok-key" >> .env
echo "SEOLMINSEOK_ACTOR_ID=your-actor-id" >> .env
```

### 4. Frontend Setup
```bash
cd ../frontend

# Install Node.js dependencies
npm install
```

---

## 🚀 Running the System

### 1. Start Backend Server
```bash
cd backend_clean
source venv/bin/activate  # Activate virtual environment
python3 main.py
```

**Expected Output:**
```
✅ Azure OpenAI client initialized successfully
✅ SeolMinSeok TTS Service initialized
📢 STT Service Status: ❌ Not Available (OK - not needed for quiz)
🚀 Server running on http://localhost:8001
```

### 2. Start Frontend Server
```bash
# In a new terminal
cd frontend
npm run dev
```

**Expected Output:**
```
▲ Next.js 15.4.6
- Local: http://localhost:3000
```

### 3. Test the System
1. Open browser: `http://localhost:3000`
2. Navigate to quiz characters:
   - **Korean History**: `http://localhost:3000/chat/seol_min_seok_quiz`
   - **Science Quiz**: `http://localhost:3000/chat/dr_genie_science_quiz`
3. Test quiz flow by sending a message

---

## 🔧 Environment Variables Reference

### Backend (.env file location: `backend_clean/.env`)

#### **Required (System won't work without these):**
```env
# Azure OpenAI - CRITICAL
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

#### **Optional (Improves experience):**
```env
# TTS Services
SEOLMINSEOK_API_KEY=your-seolminseok-key
SEOLMINSEOK_ACTOR_ID=your-actor-id
SEOLMINSEOK_ENDPOINT=https://dev.icepeak.ai/api/text-to-speech

TYPECAST_API_KEY=your-typecast-key
TYPECAST_API_URL=https://api.icepeak.ai/v1

# STT Service (for voice input - not used in quiz flow)
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=eastus

# MongoDB (not needed for quiz characters)
MONGODB_URI=mongodb://localhost:27017/neona_chat_db
```

### Frontend (No environment variables needed)
The frontend is configured to connect to `http://localhost:8001` automatically.

---

## 🧪 Testing & Verification

### 1. Backend Health Check
```bash
curl http://localhost:8001/health
# Expected: {"status": "healthy"}
```

### 2. Quiz Character Test
```bash
# Test seol_min_seok_quiz
curl -X POST http://localhost:8001/api/platform-chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "안녕하세요",
    "character_id": "seol_min_seok_quiz",
    "user_id": "test_user",
    "session_id": "test_session"
  }'
```

### 3. Frontend Test
1. Open `http://localhost:3000/chat/seol_min_seok_quiz`
2. Send message: "안녕하세요"
3. Should receive quiz question with multiple choice options
4. Select an answer and verify 2-step response flow

---

## ❗ Troubleshooting

### **Issue 1: Backend won't start**
```
❌ Failed to initialize Azure OpenAI client
```
**Solution**: Check your `.env` file has correct Azure OpenAI credentials.

### **Issue 2: Frontend can't connect to backend**
```
POST http://localhost:8001/api/platform-chat 500 (Internal Server Error)
```
**Solutions**:
- Verify backend is running on port 8001
- Check Azure OpenAI credentials in `.env`
- Restart backend server

### **Issue 3: No audio playback**
```
📢 TTS Service Status: ❌ Not Available
```
**Solutions**:
- Add TTS API keys to `.env` file
- Or ignore - system works with silent audio (proper timing maintained)

### **Issue 4: Quiz not working properly**
**Check**:
- Azure OpenAI credentials are correct
- Character ID is exactly `seol_min_seok_quiz` or `dr_genie_science_quiz`
- Backend logs show successful LLM responses

### **Issue 5: Port conflicts**
```
Error: listen EADDRINUSE: address already in use :::3000
```
**Solutions**:
```bash
# Kill processes on ports
lsof -ti:3000 | xargs kill -9
lsof -ti:8001 | xargs kill -9

# Or use different ports
npm run dev -- -p 3001  # Frontend on 3001
# Backend automatically handles CORS for 3001-3003
```

---

## 📦 Dependencies Summary

### Backend Python Dependencies (requirements.txt)
- **Core**: `fastapi==0.104.1`, `uvicorn[standard]==0.24.0`
- **LLM**: `openai==1.3.8`
- **Audio**: `azure-cognitiveservices-speech==1.34.0`, `pydub==0.25.1`
- **Database**: `motor==3.3.2`, `pymongo==4.6.0` (not used by quiz characters)
- **Utilities**: `requests==2.31.0`, `python-dotenv==1.0.0`

### Frontend Node Dependencies (package.json)
- **Core**: `next@15.4.6`, `react@19.1.0`, `react-dom@19.1.0`
- **UI**: `@radix-ui/*`, `tailwindcss@4`, `framer-motion@12.23.12`
- **State**: `zustand@5.0.7`
- **Assistant**: `@assistant-ui/react@0.10.45`

---

## 🎯 Success Checklist

- [ ] Python 3.11+ installed and accessible
- [ ] Node.js 18+ installed and accessible  
- [ ] Repository cloned successfully
- [ ] Backend virtual environment created and activated
- [ ] Python dependencies installed without errors
- [ ] `.env` file created with Azure OpenAI credentials
- [ ] Frontend dependencies installed without errors
- [ ] Backend starts successfully on port 8001
- [ ] Frontend starts successfully on port 3000
- [ ] Quiz characters accessible at `/chat/seol_min_seok_quiz` and `/chat/dr_genie_science_quiz`
- [ ] Quiz flow works (question → answer selection → 2-step response)
- [ ] TTS audio plays (or silent audio with proper timing if no TTS keys)

---

## 📞 Quick Help Commands

```bash
# Check if servers are running
lsof -i :8001  # Backend
lsof -i :3000  # Frontend

# Restart everything
pkill -f "python3 main.py"
pkill -f "next"
cd backend_clean && python3 main.py &
cd frontend && npm run dev &

# Check logs
tail -f backend_clean/logs/app.log  # If logging to file
# Or check terminal output
```

---

**🎉 That's it! Your colleague should now have a fully working quiz system with both characters.**

**Need help?** Check the troubleshooting section above or contact the original developer.
