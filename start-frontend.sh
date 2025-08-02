#!/bin/bash

# Start Frontend Next.js
echo "🚀 Starting Frontend (Next.js)..."

cd frontend

# Set environment variables
export NEXT_PUBLIC_TELEGRAM_BOT_USERNAME=pocketwiner_Bot
export NEXT_PUBLIC_DOMAIN=localhost

# Start frontend
npm start &

echo "✅ Frontend started at http://localhost:3000"
echo "📋 PID: $!"