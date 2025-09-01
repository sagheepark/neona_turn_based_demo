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