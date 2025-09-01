# Server Setup Guide
## Voice Character Chat System with Tool-Calling

### 🚀 Quick Start

The system consists of **two servers** that work together:

1. **Backend API Server** (FastAPI/Python) - Port 8000
2. **Frontend Web Server** (Next.js/React) - Port 3000

---

## 📋 Server Configuration

### Backend Server (Port 8000)
- **Framework**: FastAPI with Uvicorn
- **Language**: Python 3.9+
- **Main Features**:
  - Character chat API endpoints
  - Tool-based interactive conversations
  - Voice TTS/STT integration
  - Memory and knowledge management
  - Session persistence with MongoDB

### Frontend Server (Port 3000)  
- **Framework**: Next.js 15.4.6 with React 19.1.0
- **Language**: TypeScript
- **Main Features**:
  - Modern chat interface
  - UnifiedSelection component (chips/options)
  - Quiz validation and feedback
  - Tool-based UI interactions
  - Real-time voice playback

---

## 🔧 Manual Server Startup

### Option 1: Terminal Commands

**Backend (Terminal 1):**
```bash
cd /Users/bagsanghui/neona_turn_based_demo_with_agent/backend_clean
python3 main.py
```

**Frontend (Terminal 2):**
```bash
cd /Users/bagsanghui/neona_turn_based_demo_with_agent/frontend
npm run dev
```

### Option 2: Direct Python/Node Commands

**Backend:**
```bash
cd backend_clean
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev --turbopack
```

---

## 🎯 Server URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend App** | http://localhost:3000 | Main chat interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger docs |
| **API JSON Schema** | http://localhost:8000/openapi.json | OpenAPI specification |

---

## ⚡ Quick Startup Scripts

### Automated Startup Script

Create `start_servers.sh`:

```bash
#!/bin/bash
echo "🚀 Starting Voice Character Chat Servers..."

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "next dev" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
pkill -f "python3 main.py" 2>/dev/null

# Wait for processes to terminate
sleep 2

echo "📂 Starting Backend Server (Port 8000)..."
cd backend_clean
python3 main.py &
BACKEND_PID=$!

echo "📂 Starting Frontend Server (Port 3000)..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Servers started successfully!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop servers: kill $BACKEND_PID $FRONTEND_PID"
echo "   Or use: pkill -f 'next dev' && pkill -f 'python3 main.py'"

# Keep script running
wait
```

### Stop Servers Script

Create `stop_servers.sh`:

```bash
#!/bin/bash
echo "🛑 Stopping Voice Character Chat Servers..."

pkill -f "next dev"
pkill -f "uvicorn" 
pkill -f "python3 main.py"

echo "✅ All servers stopped."
echo "📊 Port status:"
lsof -i :3000 -i :8000 2>/dev/null || echo "   Ports 3000 and 8000 are free"
```

---

## 🔍 Health Checks

### Backend Health Check
```bash
curl http://localhost:8000/
# Should return: {"message": "Voice Character Chat API"}
```

### Frontend Health Check
```bash
curl http://localhost:3000/
# Should return HTML for the chat interface
```

### API Documentation Check
```bash
curl http://localhost:8000/docs
# Should return Swagger UI HTML
```

---

## 📊 Port Management

### Check Active Ports
```bash
lsof -i :3000 -i :8000
```

### Kill Processes on Specific Ports
```bash
# Kill port 3000 (Frontend)
lsof -ti :3000 | xargs kill

# Kill port 8000 (Backend) 
lsof -ti :8000 | xargs kill
```

### Find Process Details
```bash
ps aux | grep -E "(next dev|uvicorn|python3 main.py)" | grep -v grep
```

---

## 🚨 Troubleshooting

### Common Issues

**Issue**: Port already in use
```bash
Error: listen EADDRINUSE: address already in use :::3000
```
**Solution**: Kill existing processes or use different ports
```bash
pkill -f "next dev"
# or
lsof -ti :3000 | xargs kill
```

**Issue**: Backend not starting
```bash
ModuleNotFoundError: No module named 'services'
```
**Solution**: Ensure you're in the `backend_clean` directory
```bash
cd backend_clean
python3 main.py
```

**Issue**: Frontend build errors
```bash
npm ERR! missing script: dev
```
**Solution**: Install dependencies first
```bash
cd frontend
npm install
npm run dev
```

### Environment Issues

**Python Dependencies Missing**:
```bash
cd backend_clean
pip3 install -r requirements.txt
```

**Node Dependencies Missing**:
```bash
cd frontend
npm install
```

**Database Connection Issues**:
- Check MongoDB connection string in `.env`
- Ensure MongoDB service is running
- Verify database credentials

---

## 🔧 Development Workflow

### 1. Daily Startup
```bash
# Option A: Use startup script
./start_servers.sh

# Option B: Manual terminals
# Terminal 1: cd backend_clean && python3 main.py
# Terminal 2: cd frontend && npm run dev
```

### 2. Development Testing
- Frontend: http://localhost:3000
- API Testing: http://localhost:8000/docs
- Backend logs in Terminal 1
- Frontend logs in Terminal 2

### 3. Clean Shutdown
```bash
# Option A: Use stop script  
./stop_servers.sh

# Option B: Manual cleanup
pkill -f "next dev"
pkill -f "python3 main.py"
```

---

## 🎭 Features Ready to Test

### Backend API Endpoints (Port 8000)
- `/api/chat/interactive` - Tool-based chat conversations
- `/api/chat/continuation` - Multi-turn quiz flows
- `/api/tts` - Text-to-speech generation
- `/api/stt` - Speech-to-text conversion
- `/api/sessions/*` - Conversation session management

### Frontend Interface (Port 3000)
- Interactive chat with character selection
- UnifiedSelection component (chips/options)
- Quiz validation with correct/wrong feedback  
- Tool-based UI interactions
- Voice playback integration

### Tool-Calling System
- Character prompt-based control
- Knowledge-base driven triggers
- Smart decision logic for tool selection
- Loop prevention for continuous output

---

## 📚 Next Steps

1. **Start both servers** using the guide above
2. **Test the chat interface** at http://localhost:3000
3. **Try tool-calling features** like quizzes and selections
4. **Explore API documentation** at http://localhost:8000/docs
5. **Create custom characters** using the CONTENT_PROVIDER_GUIDE.md

---

*Ready to build amazing voice character experiences! 🎉*