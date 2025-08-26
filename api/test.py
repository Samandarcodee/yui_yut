"""
Test endpoint for Vercel
"""
from aiohttp import web

async def test_handler(request):
    """Simple test handler"""
    return web.json_response({
        "message": "Hello from Vercel!",
        "status": "working",
        "endpoint": "/api/test"
    })

# Create app
app = web.Application()
app.router.add_get("/", test_handler)

# For local testing
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
