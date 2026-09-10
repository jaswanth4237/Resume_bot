import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.config.settings import settings
from app.telegram.handlers import (
    start_handler, help_handler, document_handler,
    text_message_handler, callback_query_handler,
    reset_handler, status_handler
)

logger = logging.getLogger(__name__)


def create_telegram_app():
    token = settings.TELEGRAM_BOT_TOKEN.strip()
    if not token or token == "your_telegram_bot_token_here":
        logger.warning("TELEGRAM_BOT_TOKEN is not configured.")
        return None

    app = (
        ApplicationBuilder()
        .token(token)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("reset", reset_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_message_handler))
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    return app


async def start_telegram_bot():
    app = create_telegram_app()
    if app:
        logger.info("Starting Telegram bot polling...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
