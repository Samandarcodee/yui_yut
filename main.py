"""
Main bot application file
"""
import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import BOT_TOKEN
from db.database import Database
from bot.logging_config import setup_logging

# Import handlers
from handlers import start, game, profile, payments, admin, contact

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def main():
    """Main bot function"""
    
    # Validate bot token
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN not set! Please set your bot token in config/settings.py or environment variable")
        sys.exit(1)
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(start.router)
    dp.include_router(game.router)
    dp.include_router(profile.router)
    dp.include_router(payments.router)
    dp.include_router(admin.router)
    dp.include_router(contact.router)
    
    # Initialize database
    db = Database()
    await db.init_db()
    logger.info("Database initialized")
    
    # Create data directory for database
    os.makedirs("data", exist_ok=True)
    
    try:
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot session closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
