#!/bin/bash

# Setup ZipHostBot untuk Termux
echo "📱 Setting up ZipHostBot for Termux..."

# Update packages
echo "📦 Updating Termux packages..."
pkg update -y

# Install required packages
echo "📥 Installing required packages..."
pkg install -y python nodejs-lts redis postgresql git make curl

# Install Python packages
echo "🐍 Installing Python packages..."
pip install --upgrade pip
pip install virtualenv

# Setup PostgreSQL
echo "🗄️ Setting up PostgreSQL..."
mkdir -p $PREFIX/var/lib/postgresql
initdb $PREFIX/var/lib/postgresql

# Start PostgreSQL
echo "▶️ Starting PostgreSQL..."
pg_ctl -D $PREFIX/var/lib/postgresql -l $PREFIX/var/lib/postgresql/logfile start

# Create database
echo "🏗️ Creating database..."
createdb ziphostbot_db

# Start Redis
echo "▶️ Starting Redis..."
redis-server --daemonize yes

# Make scripts executable
chmod +x run-local.sh
chmod +x start-*.sh

# Create .env file for local development
echo "⚙️ Creating local .env file..."
cat > .env.local << 'EOF'
# Local Termux Configuration
DOMAIN=localhost
NEXT_PUBLIC_TELEGRAM_BOT_USERNAME=pocketwiner_Bot
PLATFORM_BOT_TOKEN=8219457512:AAHviOB7vxgBW6sgTWTd-nEwY-Z5wIkBa3Q
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
POSTGRES_USER=postgres
POSTGRES_PASSWORD=
POSTGRES_DB=ziphostbot_db
POSTGRES_HOST=localhost
REDIS_HOST=localhost
REDIS_PORT=6379
BACKEND_URL=http://localhost:8000
WORKER_CONCURRENCY=1
EOF

echo "✅ Termux setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Run: ./run-local.sh"
echo "2. Then start services individually:"
echo "   ./start-backend.sh"
echo "   ./start-frontend.sh"
echo "   ./start-worker.sh"
echo ""
echo "🌐 Access the platform at: http://localhost:3000"