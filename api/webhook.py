"""
🎰 Slot Game Bot — Vercel Webhook Handler
"""
import os
import sys
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from config.settings import BOT_TOKEN
from api.database_config import init_vercel_db, get_vercel_db
from bot.logging_config import setup_logging

# Import handlers
from handlers import (
    start, game, profile, admin, contact,
    start_uz, game_uz, profile_uz, bonus_uz, purchase_uz, admin_uz
)

# Setup logging
logger, _, _ = setup_logging()

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Include all routers
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
        
        # English language handlers
        dp.include_router(start.router)
        dp.include_router(game.router)
        dp.include_router(profile.router)
        dp.include_router(admin.router)
        dp.include_router(contact.router)
        
        logger.info("All routers included successfully")
        
    except Exception as e:
        logger.error(f"Failed to include routers: {e}")

# Initialize database and include routers
async def on_startup():
    """Initialize bot on startup"""
    try:
        # Initialize Vercel database
        success = await init_vercel_db()
        if success:
            logger.info("Vercel database initialized successfully")
        else:
            logger.error("Failed to initialize Vercel database")
        
        # Include routers
        include_routers()
        
        # Set webhook
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            await bot.set_webhook(url=f"{webhook_url}/api/webhook")
            logger.info(f"Webhook set to: {webhook_url}/api/webhook")
        else:
            logger.warning("WEBHOOK_URL not set, using polling mode")
            
    except Exception as e:
        logger.error(f"Startup error: {e}")

async def on_shutdown():
    """Cleanup on shutdown"""
    try:
        await bot.session.close()
        logger.info("Bot session closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Webhook handler
async def webhook_handler(request):
    """Handle incoming webhook requests"""
    try:
        # Parse update
        update_data = await request.json()
        update = types.Update(**update_data)
        
        # Process update
        await dp.feed_update(bot, update)
        
        return web.Response(status=200)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(status=500)

# Health check endpoint
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "bot": "Slot Game Bot",
        "version": "1.0.0"
    })

# Main application
app = web.Application()

# Setup webhook
webhook_handler_obj = SimpleRequestHandler(
    dispatcher=dp,
    bot=bot
)

# Routes
app.router.add_post("/api/webhook", webhook_handler)
app.router.add_get("/", health_check)
app.router.add_get("/health", health_check)

# Startup and shutdown events
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# For local development
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
