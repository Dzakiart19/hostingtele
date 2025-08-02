#!/bin/bash

# Start Backend FastAPI
echo "🚀 Starting Backend (FastAPI)..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH=$PWD/backend:$PYTHONPATH

# Start backend
cd backend
python -c "
import uvicorn
if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
" &

echo "✅ Backend started at http://localhost:8000"
echo "📋 PID: $!"