"""
🎰 Slot Game Bot — Vercel Webhook Handler (Ultra Simplified & Robust)
"""
import os
import json
from aiohttp import web

# Bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Simple webhook handler
async def webhook_handler(request):
    """Handle incoming webhook requests"""
    try:
        # Check if it's a POST request
        if request.method != "POST":
            return web.json_response({
                "status": "error",
                "message": "Only POST requests allowed"
            }, status=405)
        
        # Parse update
        update_data = await request.json()
        
        # Basic response
        return web.json_response({
            "status": "success",
            "message": "Update received",
            "bot_token_set": bool(BOT_TOKEN),
            "update_id": update_data.get("update_id", "unknown")
        })
        
    except json.JSONDecodeError:
        return web.json_response({
            "status": "error",
            "message": "Invalid JSON data"
        }, status=400)
    except Exception as e:
        return web.json_response({
            "status": "error",
            "message": f"Internal error: {str(e)}"
        }, status=500)

# Health check endpoint
async def health_check(request):
    """Health check endpoint"""
    try:
        return web.json_response({
            "status": "healthy",
            "bot": "Slot Game Bot",
            "version": "1.0.0",
            "bot_token_set": bool(BOT_TOKEN),
            "environment": "vercel"
        })
    except Exception as e:
        return web.json_response({
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }, status=500)

# Main application
app = web.Application()

# Routes
app.router.add_post("/api/webhook", webhook_handler)
app.router.add_get("/", health_check)

# Error handlers
async def error_handler(request, response):
    """Global error handler"""
    return web.json_response({
        "status": "error",
        "message": "Something went wrong",
        "path": str(request.path)
    }, status=response.status)

# Add error handlers
app.middlewares.append(error_handler)

# For local development
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
