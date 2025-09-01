#!/bin/bash
echo "🛑 Stopping Voice Character Chat Servers..."

pkill -f "next dev"
pkill -f "uvicorn" 
pkill -f "python3 main.py"

echo "✅ All servers stopped."
echo "📊 Port status:"
lsof -i :3000 -i :8000 2>/dev/null || echo "   Ports 3000 and 8000 are free"