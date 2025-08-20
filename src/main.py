"""Main bot entry point with enhanced logging and monitoring."""
import asyncio
import logging
import signal
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import get_settings
from .db import init_db
from .handlers import router
from .monitoring import metrics, PerformanceMiddleware


def setup_logging() -> None:
    """Configure structured logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("bot.log", encoding="utf-8"),
        ],
    )
    
    # Reduce aiogram noise
    logging.getLogger("aiogram").setLevel(logging.WARNING)


async def main() -> None:
    """Main bot function with comprehensive error handling."""
    setup_logging()
    
    try:
        settings = get_settings()
        logging.info("📋 Configuration loaded successfully")
        
        # Initialize database
        await init_db()
        logging.info("🗄️ Database initialized")
        
        # Create bot and dispatcher
        bot = Bot(
            token=settings.bot_token, 
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        # Add performance monitoring
        dp.message.middleware(PerformanceMiddleware())
        dp.callback_query.middleware(PerformanceMiddleware())
        
        # Include router
        dp.include_router(router)
        
        # Warm up bot.me cache
        await bot.get_me()
        logging.info("🤖 Bot authenticated")
        
        # Start bot
        logging.info("🚀 Bot started. Waiting for updates...")
        await dp.start_polling(bot)
            
    except Exception as e:
        logging.error(f"💥 Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
