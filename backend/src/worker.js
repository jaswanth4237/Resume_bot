const settings = require('./config/settings');
const { connectMongo } = require('./db/mongo');
const { createBot } = require('./telegram/bot');
(async () => { await connectMongo(); const bot = await createBot(); if (!bot) { console.error('TELEGRAM_BOT_TOKEN is required to start the worker.'); process.exitCode = 1; return; } await bot.start(); })().catch(error => { console.error(error); process.exitCode = 1; });
