#!/bin/bash

# Script untuk menjalankan ZipHostBot tanpa Docker di Termux
# Usage: ./run-local.sh

set -e

echo "🚀 Starting ZipHostBot in Local Mode (Termux Compatible)"

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install worker dependencies
echo "📥 Installing worker dependencies..."
cd worker
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Build frontend
echo "🔨 Building frontend..."
cd frontend
npm run build
cd ..

echo "✅ Setup complete!"
echo ""
echo "🌟 To start the services manually:"
echo "1. Start Redis: redis-server &"
echo "2. Start PostgreSQL: postgres -D /data/postgres &"
echo "3. Start Backend: cd backend && python main.py &"
echo "4. Start Worker: cd worker && celery -A tasks worker &"
echo "5. Start Frontend: cd frontend && npm start &"
echo ""
echo "💡 Or use the individual start scripts:"
echo "   ./start-backend.sh"
echo "   ./start-worker.sh"  
echo "   ./start-frontend.sh"