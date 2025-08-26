#!/usr/bin/env python3
"""
Enhanced Slot Game Bot - Main Entry Point
Features: Performance monitoring, error tracking, health checks, and advanced logging
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Import enhanced modules
from bot.logging_config import setup_logging, monitor_performance, log_exception
from bot.security import setup_middleware, verify_all_channel_subscriptions
from db.database import Database
from config.settings import BOT_TOKEN, ADMIN_IDS

# Import handlers
from handlers import (
    start, game, profile, admin, contact,
    start_uz, game_uz, profile_uz, bonus_uz, purchase_uz, admin_uz
)

# Global variables
bot: Bot = None
dp: Dispatcher = None
db: Database = None
logger, performance_monitor, error_tracker = None, None, None

@monitor_performance("bot_initialization")
async def initialize_bot():
    """Initialize bot with enhanced features"""
    global bot, dp, db, logger, performance_monitor, error_tracker
    
    try:
        # Setup enhanced logging
        logger, performance_monitor, error_tracker = setup_logging()
        
        # Initialize bot with enhanced properties
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                link_preview_is_disabled=True
            )
        )
        
        # Initialize dispatcher with memory storage
        dp = Dispatcher(storage=MemoryStorage())
        
        # Initialize database with connection pooling
        db = Database(max_connections=20)
        await db.init_db()
        logger.info("Database initialized with connection pooling")
        
        # Setup security middleware
        channel_middleware, admin_middleware = setup_middleware(db)
        
        # Apply middleware
        dp.message.middleware(channel_middleware)
        dp.callback_query.middleware(channel_middleware)
        
        # Apply admin middleware to admin handlers
        dp.message.middleware(admin_middleware)
        dp.callback_query.middleware(admin_middleware)
        
        logger.info("Security middleware setup completed")
        
        # Include routers
        include_routers()
        
        # Create necessary directories
        create_directories()
        
        return True
        
    except Exception as e:
        if logger:
            log_exception(logger, "Failed to initialize bot", e)
        else:
            print(f"Failed to initialize bot: {e}")
        return False

def include_routers():
    """Include all router handlers"""
    try:
        # Uzbek language handlers
        dp.include_router(start_uz.router)
        dp.include_router(game_uz.router)
        dp.include_router(profile_uz.router)
        dp.include_router(bonus_uz.router)
        dp.include_router(purchase_uz.router)
        dp.include_router(admin_uz.router)
        
        # English language handlers (if needed)
        dp.include_router(start.router)
        dp.include_router(game.router)
        dp.include_router(profile.router)
        dp.include_router(admin.router)
        dp.include_router(contact.router)
        
        logger.info("All routers included successfully")
        
    except Exception as e:
        log_exception(logger, "Failed to include routers", e)

def create_directories():
    """Create necessary directories"""
    try:
        directories = ["data", "logs", "temp"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        logger.info("Directories created successfully")
        
    except Exception as e:
        log_exception(logger, "Failed to create directories", e)

@monitor_performance("periodic_subscription_check")
async def periodic_subscription_check():
    """Enhanced periodic subscription check with error handling"""
    while True:
        try:
            await asyncio.sleep(3600)  # 1 hour
            await verify_all_channel_subscriptions(bot, db)
            logger.info("Periodic subscription check completed successfully")
            
        except Exception as e:
            log_exception(logger, "Periodic subscription check failed", e)
            # Continue running even if this fails
            await asyncio.sleep(300)  # Wait 5 minutes before retrying

@monitor_performance("periodic_cleanup")
async def periodic_cleanup():
    """Periodic cleanup tasks"""
    while True:
        try:
            await asyncio.sleep(86400)  # 24 hours
            
            # Cleanup old database data
            await db.cleanup_old_data(days=30)
            
            # Cleanup security data
            if hasattr(security_manager, 'cleanup_expired_data'):
                security_manager.cleanup_expired_data()
            
            # Log performance summary
            if performance_monitor:
                perf_summary = performance_monitor.get_performance_summary()
                logger.info("Performance summary", perf_summary)
            
            # Log error summary
            if error_tracker:
                error_tracker.log_error_summary()
            
            logger.info("Periodic cleanup completed successfully")
            
        except Exception as e:
            log_exception(logger, "Periodic cleanup failed", e)
            await asyncio.sleep(3600)  # Wait 1 hour before retrying

@monitor_performance("health_check")
async def health_check():
    """Periodic health check"""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            
            # Check database connectivity
            try:
                await db.get_database_stats()
                db_healthy = True
            except Exception:
                db_healthy = False
            
            # Check bot status
            try:
                bot_info = await bot.get_me()
                bot_healthy = True
            except Exception:
                bot_healthy = False
            
            # Log health status
            health_data = {
                'database_healthy': db_healthy,
                'bot_healthy': bot_healthy,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            if db_healthy and bot_healthy:
                logger.debug("Health check: All systems operational")
            else:
                logger.warning("Health check: Some systems unhealthy", health_data)
                
        except Exception as e:
            log_exception(logger, "Health check failed", e)
            await asyncio.sleep(60)  # Wait 1 minute before retrying

async def graceful_shutdown():
    """Graceful shutdown with cleanup"""
    try:
        logger.info("Starting graceful shutdown...")
        
        # Stop periodic tasks
        for task in asyncio.all_tasks():
            if not task.done():
                task.cancel()
        
        # Close database connections
        if db:
            await db.close()
            logger.info("Database connections closed")
        
        # Close bot
        if bot:
            await bot.session.close()
            logger.info("Bot session closed")
        
        logger.info("Graceful shutdown completed")
        
    except Exception as e:
        log_exception(logger, "Graceful shutdown failed", e)

async def main():
    """Main bot function with enhanced error handling"""
    try:
        # Initialize bot
        if not await initialize_bot():
            logger.critical("Failed to initialize bot, exiting")
            return
        
        # Start periodic tasks
        subscription_task = asyncio.create_task(periodic_subscription_check())
        cleanup_task = asyncio.create_task(periodic_cleanup())
        health_task = asyncio.create_task(health_check())
        
        logger.info("Periodic tasks started")
        
        # Start bot polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        log_exception(logger, "Main bot loop failed", e)
    finally:
        # Graceful shutdown
        await graceful_shutdown()

if __name__ == "__main__":
    try:
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
