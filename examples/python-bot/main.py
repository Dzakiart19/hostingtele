#!/usr/bin/env python3
"""
Contoh Bot Telegram sederhana menggunakan python-telegram-bot
Bot ini akan merespons pesan /start dan /help
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token dari environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable tidak ditemukan!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk command /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"Halo {user.mention_html()}!\n\n"
        f"Saya adalah bot yang di-deploy menggunakan ZipHostBot! 🤖\n\n"
        f"Gunakan /help untuk melihat perintah yang tersedia."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk command /help"""
    help_text = """
🤖 <b>Bot Commands:</b>

/start - Memulai bot
/help - Menampilkan bantuan ini
/info - Informasi tentang bot
/echo [pesan] - Mengulangi pesan Anda

<i>Bot ini berjalan di platform ZipHostBot!</i>
    """
    await update.message.reply_html(help_text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk command /info"""
    info_text = """
ℹ️ <b>Informasi Bot:</b>

• Platform: ZipHostBot
• Runtime: Python 3.10
• Library: python-telegram-bot
• Status: Berjalan dengan baik! ✅

Dibuat dengan ❤️ menggunakan ZipHostBot
    """
    await update.message.reply_html(info_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk command /echo"""
    if context.args:
        message = " ".join(context.args)
        await update.message.reply_text(f"🔄 Echo: {message}")
    else:
        await update.message.reply_text("Gunakan: /echo [pesan yang ingin diulang]")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk pesan biasa"""
    user_message = update.message.text
    await update.message.reply_text(
        f"Anda mengirim: \"{user_message}\"\n\n"
        f"Gunakan /help untuk melihat perintah yang tersedia."
    )

def main() -> None:
    """Fungsi utama bot"""
    logger.info("🚀 Memulai bot...")
    
    # Buat aplikasi bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Tambahkan handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Bot siap menerima pesan!")
    
    # Jalankan bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()