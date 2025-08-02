# 📱 ZipHostBot untuk Termux

Panduan khusus untuk menjalankan ZipHostBot di Termux Android.

## 🚀 Quick Start untuk Termux

### 1. Setup Awal
```bash
# Jalankan setup otomatis
chmod +x termux-setup.sh
./termux-setup.sh
```

### 2. Install Dependencies Manual (Jika Diperlukan)
```bash
# Update Termux
pkg update -y && pkg upgrade -y

# Install packages yang diperlukan
pkg install -y python nodejs-lts redis postgresql git make curl

# Install Python tools
pip install --upgrade pip virtualenv

# Setup PostgreSQL
mkdir -p $PREFIX/var/lib/postgresql
initdb $PREFIX/var/lib/postgresql
pg_ctl -D $PREFIX/var/lib/postgresql -l $PREFIX/var/lib/postgresql/logfile start
createdb ziphostbot_db

# Start Redis
redis-server --daemonize yes
```

### 3. Setup Project
```bash
# Setup environment
chmod +x run-local.sh
./run-local.sh
```

### 4. Jalankan Services

#### Opsi A: Start Semua Manual
```bash
# Terminal 1: Backend
./start-backend.sh

# Terminal 2: Frontend (buka tab baru)
./start-frontend.sh

# Terminal 3: Worker (opsional)
./start-worker.sh
```

#### Opsi B: Start Individual
```bash
# Backend
cd backend && python main_local.py &

# Frontend
cd frontend && npm start &

# Worker (opsional)
cd worker && celery -A tasks worker --loglevel=info &
```

### 5. Akses Platform
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Troubleshooting Termux

### Permission Denied
```bash
chmod +x *.sh
```

### Python Import Error
```bash
export PYTHONPATH=$PWD/backend:$PWD/worker:$PYTHONPATH
```

### PostgreSQL Error
```bash
# Restart PostgreSQL
pg_ctl -D $PREFIX/var/lib/postgresql restart

# Check status
pg_ctl -D $PREFIX/var/lib/postgresql status
```

### Redis Error
```bash
# Start Redis
redis-server --daemonize yes

# Check Redis
redis-cli ping
```

### Node.js Error
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd frontend && rm -rf node_modules && npm install
```

## 📋 Environment Variables untuk Termux

Buat file `.env.local`:
```bash
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
```

## 🎯 Fitur yang Bekerja di Termux

✅ **Frontend Dashboard** - Login dan UI lengkap  
✅ **Backend API** - Semua endpoints  
✅ **Database** - PostgreSQL dengan semua tabel  
✅ **Authentication** - Telegram Login Widget  
✅ **File Upload** - Upload ZIP files  
⚠️ **Worker** - Simplified (tanpa Docker build)  
⚠️ **Bot Deployment** - Manual processing  

## 🔄 Restart Services

```bash
# Kill all processes
pkill -f "python"
pkill -f "node"
pkill -f "celery"

# Restart
./start-backend.sh
./start-frontend.sh
./start-worker.sh
```

## 📱 Tips untuk Termux

1. **Gunakan multiple sessions** di Termux untuk menjalankan services terpisah
2. **Simpan logs** untuk debugging: `./start-backend.sh > backend.log 2>&1 &`
3. **Monitor resource usage** karena Termux memiliki keterbatasan RAM
4. **Backup database** secara berkala: `pg_dump ziphostbot_db > backup.sql`

## 🆘 Bantuan

Jika mengalami masalah:

1. **Cek logs**: `tail -f backend.log`
2. **Restart services**: `pkill python && ./start-backend.sh`
3. **Cek port**: `netstat -tlnp | grep :8000`
4. **Test API**: `curl http://localhost:8000/health`

---

**Happy coding di Termux! 📱✨**