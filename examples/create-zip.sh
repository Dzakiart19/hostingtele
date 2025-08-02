#!/bin/bash

# Script untuk membuat file ZIP dari contoh bot
# Usage: ./create-zip.sh [python|nodejs]

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 [python|nodejs]"
    echo "Contoh:"
    echo "  $0 python   # Membuat python-bot.zip"
    echo "  $0 nodejs   # Membuat nodejs-bot.zip"
    exit 1
fi

BOT_TYPE=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case $BOT_TYPE in
    python)
        echo "🐍 Membuat ZIP untuk Python bot..."
        cd "$SCRIPT_DIR/python-bot"
        zip -r "../python-bot.zip" . -x "*.pyc" "__pycache__/*" ".git/*"
        echo "✅ File python-bot.zip berhasil dibuat!"
        echo "📍 Lokasi: $SCRIPT_DIR/python-bot.zip"
        ;;
    nodejs)
        echo "🟢 Membuat ZIP untuk Node.js bot..."
        cd "$SCRIPT_DIR/nodejs-bot"
        zip -r "../nodejs-bot.zip" . -x "node_modules/*" ".git/*" "*.log"
        echo "✅ File nodejs-bot.zip berhasil dibuat!"
        echo "📍 Lokasi: $SCRIPT_DIR/nodejs-bot.zip"
        ;;
    *)
        echo "❌ Bot type tidak valid: $BOT_TYPE"
        echo "Gunakan 'python' atau 'nodejs'"
        exit 1
        ;;
esac

echo ""
echo "🚀 File ZIP siap untuk diupload ke ZipHostBot!"
echo "💡 Jangan lupa untuk mengganti BOT_TOKEN dengan token bot Anda yang sebenarnya saat upload."