# 🚀 Quick Start - ZipHostBot

Panduan cepat untuk menjalankan platform ZipHostBot dalam 5 menit!

## ⚡ Setup Super Cepat

### 1. Clone & Setup
```bash
git clone <repository-url>
cd ziphostbot
make setup
```

### 2. Edit Konfigurasi
```bash
# Edit file .env yang baru dibuat
nano .env

# Minimal yang harus diubah:
POSTGRES_PASSWORD=password_aman_anda
MINIO_ROOT_PASSWORD=password_minio_anda
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
```

### 3. Jalankan Platform
```bash
make dev
```

### 4. Akses Platform
- Buka browser: `http://localhost`
- Login dengan Telegram
- Upload bot ZIP dan enjoy! 🎉

## 📦 Test dengan Bot Contoh

### Buat Bot Contoh
```bash
# Buat contoh bot Python dan Node.js
make examples

# File ZIP akan dibuat di folder examples/
ls examples/*.zip
```

### Upload Bot
1. Login ke platform
2. Klik "Deploy Bot Baru dari .zip"
3. Upload file `python-bot.zip` atau `nodejs-bot.zip`
4. Masukkan token bot Telegram Anda
5. Tunggu hingga status menjadi "RUNNING"

## 🛠️ Perintah Berguna

```bash
make help        # Lihat semua perintah
make logs        # Lihat logs
make status      # Cek status containers
make restart     # Restart semua services
make clean       # Bersihkan containers
make backup      # Backup database
```

## 🔧 Troubleshooting Cepat

### Platform tidak bisa diakses?
```bash
make status      # Cek status
make logs        # Lihat error logs
```

### Login Telegram gagal?
- Pastikan `PLATFORM_BOT_TOKEN` benar
- Pastikan domain sudah dikonfigurasi di BotFather

### Bot gagal deploy?
- Pastikan file ZIP berisi `requirements.txt` (Python) atau `package.json` (Node.js)
- Pastikan token bot valid
- Cek error log di dashboard

## 📚 Dokumentasi Lengkap

Lihat [README.md](README.md) untuk dokumentasi lengkap dan konfigurasi production.

---

**Happy Bot Hosting! 🤖✨**