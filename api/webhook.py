"""
🎰 Slot Game Bot — Vercel Webhook Handler (Ultra Simplified)
"""
import os
import json
from aiohttp import web

# Bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Simple webhook handler
async def webhook_handler(request):
    """Handle incoming webhook requests"""
    try:
        # Parse update
        update_data = await request.json()
        
        # Basic response
        return web.json_response({
            "status": "success",
            "message": "Update received",
            "bot_token_set": bool(BOT_TOKEN)
        })
        
    except Exception as e:
        return web.json_response({
            "status": "error",
            "message": str(e)
        }, status=500)

# Health check endpoint
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "bot": "Slot Game Bot",
        "version": "1.0.0",
        "bot_token_set": bool(BOT_TOKEN)
    })

# Main application
app = web.Application()

# Routes
app.router.add_post("/api/webhook", webhook_handler)
app.router.add_get("/", health_check)

# For local development
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
