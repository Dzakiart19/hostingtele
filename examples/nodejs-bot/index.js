#!/usr/bin/env node
/**
 * Contoh Bot Telegram sederhana menggunakan Telegraf
 * Bot ini akan merespons pesan /start dan /help
 */

const { Telegraf } = require('telegraf');

// Bot token dari environment variable
const BOT_TOKEN = process.env.BOT_TOKEN;

if (!BOT_TOKEN) {
    console.error('❌ BOT_TOKEN environment variable tidak ditemukan!');
    process.exit(1);
}

// Buat instance bot
const bot = new Telegraf(BOT_TOKEN);

// Middleware untuk logging
bot.use((ctx, next) => {
    console.log(`📨 Pesan dari ${ctx.from.first_name} (${ctx.from.id}): ${ctx.message?.text || 'Non-text message'}`);
    return next();
});

// Handler untuk command /start
bot.start((ctx) => {
    const user = ctx.from;
    ctx.replyWithHTML(
        `Halo <b>${user.first_name}</b>!\n\n` +
        `Saya adalah bot yang di-deploy menggunakan ZipHostBot! 🤖\n\n` +
        `Gunakan /help untuk melihat perintah yang tersedia.`
    );
});

// Handler untuk command /help
bot.help((ctx) => {
    const helpText = `
🤖 <b>Bot Commands:</b>

/start - Memulai bot
/help - Menampilkan bantuan ini
/info - Informasi tentang bot
/echo [pesan] - Mengulangi pesan Anda

<i>Bot ini berjalan di platform ZipHostBot!</i>
    `;
    ctx.replyWithHTML(helpText);
});

// Handler untuk command /info
bot.command('info', (ctx) => {
    const infoText = `
ℹ️ <b>Informasi Bot:</b>

• Platform: ZipHostBot
• Runtime: Node.js 18
• Library: Telegraf
• Status: Berjalan dengan baik! ✅

Dibuat dengan ❤️ menggunakan ZipHostBot
    `;
    ctx.replyWithHTML(infoText);
});

// Handler untuk command /echo
bot.command('echo', (ctx) => {
    const message = ctx.message.text.replace('/echo', '').trim();
    if (message) {
        ctx.reply(`🔄 Echo: ${message}`);
    } else {
        ctx.reply('Gunakan: /echo [pesan yang ingin diulang]');
    }
});

// Handler untuk pesan biasa
bot.on('text', (ctx) => {
    const userMessage = ctx.message.text;
    
    // Skip jika pesan adalah command
    if (userMessage.startsWith('/')) {
        return;
    }
    
    ctx.reply(
        `Anda mengirim: "${userMessage}"\n\n` +
        `Gunakan /help untuk melihat perintah yang tersedia.`
    );
});

// Error handler
bot.catch((err, ctx) => {
    console.error('❌ Bot error:', err);
    console.error('Context:', ctx);
});

// Graceful shutdown
process.once('SIGINT', () => {
    console.log('🛑 Menerima SIGINT, menghentikan bot...');
    bot.stop('SIGINT');
});

process.once('SIGTERM', () => {
    console.log('🛑 Menerima SIGTERM, menghentikan bot...');
    bot.stop('SIGTERM');
});

// Jalankan bot
console.log('🚀 Memulai bot...');
bot.launch()
    .then(() => {
        console.log('✅ Bot siap menerima pesan!');
    })
    .catch((err) => {
        console.error('❌ Gagal memulai bot:', err);
        process.exit(1);
    });