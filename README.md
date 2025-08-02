# ZipHostBot - Platform Hosting Bot Telegram Berbasis Upload ZIP

Platform PaaS (Platform-as-a-Service) yang dirancang khusus untuk mendeploy dan menjalankan Bot Telegram dari file .zip dengan otentikasi web Telegram yang terintegrasi.

## 🚀 Fitur Utama

- **Otentikasi Tunggal via Telegram**: Login menggunakan Telegram Login Widget tanpa registrasi terpisah
- **Deploy dari ZIP**: Upload file .zip berisi kode bot dan platform akan otomatis menjalankannya
- **Multi-Runtime Support**: Mendukung Python (requirements.txt) dan Node.js (package.json)
- **Keamanan Berlapis**: Enkripsi token bot, scanning virus dengan ClamAV, validasi otentikasi Telegram
- **Monitoring Real-time**: Dashboard untuk monitoring status bot, log error, dan kontrol start/stop
- **Arsitektur Microservices**: Scalable dengan Docker Compose

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │    │     Backend     │    │     Worker      │
│    (Next.js)    │◄──►│    (FastAPI)    │◄──►│    (Celery)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────►│      Nginx      │◄─────────────┘
                        │ (Reverse Proxy) │
                        └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Redis      │    │      MinIO      │
│   (Database)    │    │   (Queue)       │    │   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
┌─────────────────┐
│     ClamAV      │
│  (Antivirus)    │
└─────────────────┘
```

## 🛠️ Teknologi yang Digunakan

### Backend
- **FastAPI** (Python 3.12) - API Gateway dan otentikasi
- **Celery + Redis** - Task queue untuk pemrosesan asinkron
- **PostgreSQL 15** - Database utama
- **MinIO** - Object storage untuk file ZIP
- **ClamAV** - Antivirus scanner
- **Docker SDK** - Untuk build dan run container bot

### Frontend
- **Next.js 14** (App Router) - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Telegram Login Widget** - Otentikasi

### Infrastructure
- **Docker + Docker Compose** - Containerization dan orkestrasi
- **Nginx** - Reverse proxy dan load balancer

## 📋 Prasyarat

- Docker dan Docker Compose terinstall
- Minimal 4GB RAM dan 10GB storage
- Domain yang sudah dikonfigurasi di BotFather (untuk production)

## 🚀 Instalasi dan Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd ziphostbot
```

### 2. Konfigurasi Environment

```bash
# Copy file environment template
cp .env.example .env

# Edit konfigurasi sesuai kebutuhan
nano .env
```

### 3. Konfigurasi Environment Variables

Buka file `.env` dan sesuaikan konfigurasi berikut:

```bash
# Domain yang sudah di-set di BotFather
DOMAIN=mgx.dev

# Username bot untuk Login Widget
NEXT_PUBLIC_TELEGRAM_BOT_USERNAME=pocketwiner_Bot

# Token bot platform (RAHASIA!)
PLATFORM_BOT_TOKEN=8219457512:AAHviOB7vxgBW6sgTWTd-nEwY-Z5wIkBa3Q

# Generate JWT secret (32 karakter random)
JWT_SECRET=$(openssl rand -hex 32)

# Generate encryption key (32 karakter random)  
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Database credentials
POSTGRES_PASSWORD=your_secure_db_password

# MinIO credentials
MINIO_ROOT_PASSWORD=your_secure_minio_password
```

### 4. Jalankan Platform

```bash
# Build dan jalankan semua layanan
docker-compose up -d

# Lihat logs untuk memastikan semua berjalan dengan baik
docker-compose logs -f
```

### 5. Verifikasi Instalasi

1. Buka browser dan akses `http://localhost` (atau domain Anda)
2. Anda akan melihat halaman login dengan Telegram Login Widget
3. Klik tombol login dan authorize dengan akun Telegram Anda
4. Setelah login berhasil, Anda akan diarahkan ke dashboard

## 🎯 Cara Menggunakan Platform

### 1. Login ke Platform
- Kunjungi website platform
- Klik tombol "Login & Kelola Bot Anda"
- Authorize menggunakan akun Telegram Anda

### 2. Deploy Bot Baru
- Di dashboard, klik "Deploy Bot Baru dari .zip"
- Isi form dengan:
  - **Nama Proyek**: Nama deskriptif untuk bot Anda
  - **Token Bot**: Token bot Telegram yang akan dijalankan
  - **File ZIP**: File .zip berisi kode bot Anda
- Klik "Deploy Bot"

### 3. Monitoring Bot
- Status bot akan ditampilkan di dashboard
- Status yang mungkin:
  - **PENDING**: Bot sedang dalam antrian
  - **PROCESSING**: Bot sedang diproses (build Docker image)
  - **RUNNING**: Bot berjalan dengan baik
  - **STOPPED**: Bot dihentikan
  - **FAILED**: Bot gagal dijalankan (lihat error log)

### 4. Kontrol Bot
- **Start**: Memulai bot yang stopped/failed
- **Stop**: Menghentikan bot yang sedang running
- **Delete**: Menghapus bot dan semua datanya

## 📁 Struktur File ZIP Bot

### Untuk Bot Python:
```
bot.zip
├── main.py              # File utama bot (atau bot.py, app.py, run.py)
├── requirements.txt     # Dependencies Python (WAJIB)
├── config.py           # Konfigurasi bot (opsional)
└── modules/            # Modul tambahan (opsional)
    ├── handlers.py
    └── utils.py
```

### Untuk Bot Node.js:
```
bot.zip
├── index.js            # File utama bot
├── package.json        # Dependencies Node.js (WAJIB dengan script "start")
├── package-lock.json   # Lock file (opsional)
└── src/               # Source code (opsional)
    ├── handlers.js
    └── utils.js
```

### Contoh requirements.txt (Python):
```
python-telegram-bot==20.7
requests==2.31.0
python-dotenv==1.0.0
```

### Contoh package.json (Node.js):
```json
{
  "name": "my-telegram-bot",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "telegraf": "^4.12.2",
    "dotenv": "^16.3.1"
  }
}
```

## 🔒 Keamanan

### Otentikasi Telegram
Platform menggunakan Telegram Login Widget dengan validasi hash menggunakan bot token platform untuk memastikan otentikasi yang aman.

### Enkripsi Token Bot
Token bot pengguna dienkripsi menggunakan Fernet (AES 128) sebelum disimpan di database.

### Scanning Malware
Setiap file ZIP yang diupload akan dipindai menggunakan ClamAV sebelum diproses.

### Rate Limiting
Nginx dikonfigurasi dengan rate limiting untuk mencegah abuse:
- API umum: 10 requests/detik
- Upload endpoint: 2 requests/detik

## 🐛 Troubleshooting

### Bot Gagal Start (Status FAILED)
1. Periksa error log di dashboard
2. Pastikan file ZIP berisi `requirements.txt` (Python) atau `package.json` (Node.js)
3. Pastikan token bot valid dan tidak expired
4. Periksa syntax error dalam kode bot

### Login Gagal
1. Pastikan domain sudah dikonfigurasi di BotFather
2. Pastikan `PLATFORM_BOT_TOKEN` benar
3. Pastikan `NEXT_PUBLIC_TELEGRAM_BOT_USERNAME` sesuai

### Upload File Gagal
1. Pastikan file berformat .zip
2. Pastikan ukuran file < 50MB
3. Periksa koneksi internet

### Container Tidak Bisa Start
```bash
# Periksa logs semua layanan
docker-compose logs

# Restart layanan tertentu
docker-compose restart backend worker

# Rebuild jika ada perubahan kode
docker-compose up -d --build
```

## 📊 Monitoring dan Maintenance

### Melihat Logs
```bash
# Logs semua layanan
docker-compose logs -f

# Logs layanan tertentu
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend
```

### Database Backup
```bash
# Backup database
docker-compose exec db pg_dump -U zippy ziphostbot_db > backup.sql

# Restore database
docker-compose exec -T db psql -U zippy ziphostbot_db < backup.sql
```

### Cleanup Storage
```bash
# Hapus image Docker yang tidak terpakai
docker image prune -f

# Hapus container yang stopped
docker container prune -f

# Hapus volume yang tidak terpakai (HATI-HATI!)
docker volume prune -f
```

## 🔧 Konfigurasi Production

### 1. SSL Certificate
Uncomment dan konfigurasi blok HTTPS di `nginx/conf.d/default.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name mgx.dev www.mgx.dev;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # ... rest of configuration
}
```

### 2. Environment Variables Production
```bash
# Set ke production
NODE_ENV=production

# Gunakan domain production
DOMAIN=yourdomain.com

# Generate secret yang kuat
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
```

### 3. Firewall Configuration
```bash
# Buka port yang diperlukan
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📈 Scaling

### Horizontal Scaling Worker
```yaml
# Di docker-compose.yml, tambah replicas
worker:
  # ... existing config
  deploy:
    replicas: 3
```

### Database Connection Pooling
Sesuaikan `POSTGRES_MAX_CONNECTIONS` di environment variables.

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Support

Jika Anda menemui masalah atau butuh bantuan:

1. Periksa dokumentasi troubleshooting di atas
2. Buat issue di GitHub repository
3. Join grup Telegram support (jika tersedia)

## 🔄 Changelog

### v1.0.0
- Initial release
- Basic bot deployment functionality
- Telegram authentication integration
- Multi-runtime support (Python & Node.js)
- Security features (ClamAV, encryption)
- Web dashboard interface

---

**Dibuat dengan ❤️ untuk komunitas developer Bot Telegram Indonesia**