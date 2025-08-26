"""
🎰 Slot Game Bot — Vercel Webhook Handler (Minimal)
"""
from aiohttp import web

# Simple health check endpoint
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "bot": "Slot Game Bot",
        "version": "1.0.0"
    })

# Main application
app = web.Application()

# Routes
app.router.add_get("/", health_check)

# For local development
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
