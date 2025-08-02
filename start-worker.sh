#!/bin/bash

# Start Celery Worker
echo "🚀 Starting Worker (Celery)..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH=$PWD/worker:$PYTHONPATH

# Start worker
cd worker
celery -A tasks worker --loglevel=info --concurrency=2 &

echo "✅ Worker started"
echo "📋 PID: $!"