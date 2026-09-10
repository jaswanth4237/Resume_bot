"""
run_bot.py — Standalone Telegram Bot runner.
Runs only the Telegram bot polling service (no FastAPI server required).
"""
import asyncio
import logging
import sys
import os
from telegram.error import NetworkError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    from app.config.settings import settings
    from app.telegram.bot import create_telegram_app

    token = settings.TELEGRAM_BOT_TOKEN.strip()
    if not token or token == "your_telegram_bot_token_here":
        logger.error("TELEGRAM_BOT_TOKEN is not set. Set it in backend/.env to start the bot.")
        return

    logger.info("Starting ResumeMatch AI Telegram Bot...")
    app = create_telegram_app()
    if not app:
        return

    while True:
        try:
            await app.initialize()
            break
        except NetworkError as error:
            logger.warning("Telegram is unreachable (%s). Retrying in 5 seconds...", error)
            await asyncio.sleep(5)

    await app.start()
    logger.info("Bot is running. Send /start to your Telegram bot to begin.")
    await app.updater.start_polling(drop_pending_updates=True)

    # Keep running until Ctrl+C
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down bot...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
