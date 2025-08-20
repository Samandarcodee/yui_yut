# 🚀 Deployment Guide

## Production Deployment Options

### 1. Render.com (Recommended)
```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to production"
git push

# 2. Connect GitHub repo to Render
# 3. Set BOT_TOKEN environment variable
# 4. Deploy automatically
```

### 2. Railway.app
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up

# 3. Set BOT_TOKEN
railway variables set BOT_TOKEN=your_token_here
```

### 3. Heroku
```bash
# 1. Install Heroku CLI
# 2. Create app
heroku create stars-yut-bot

# 3. Set config
heroku config:set BOT_TOKEN=your_token_here
heroku config:set ADMIN_IDS=5928372261

# 4. Deploy
git push heroku main
```

### 4. VPS/Dedicated Server
```bash
# 1. Clone repository
git clone https://github.com/Samandarcodee/yui_yut.git
cd yui_yut

# 2. Setup environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\Activate.ps1  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your BOT_TOKEN

# 5. Run with systemd (Linux)
sudo cp deploy/stars-yut.service /etc/systemd/system/
sudo systemctl enable stars-yut
sudo systemctl start stars-yut
```

### 5. Docker Deployment
```bash
# 1. Build image
docker build -t stars-yut-bot .

# 2. Run container
docker run -d \
  --name stars-yut-bot \
  --restart unless-stopped \
  -e BOT_TOKEN=your_token_here \
  -e ADMIN_IDS=5928372261 \
  -v $(pwd)/data:/app/data \
  stars-yut-bot

# 3. Check logs
docker logs stars-yut-bot
```

## Environment Variables

Required:
- `BOT_TOKEN` - Telegram bot token from @BotFather

Optional:
- `ADMIN_IDS` - Comma-separated admin user IDs (default: empty)
- `STARS_ENABLED` - Enable Telegram Stars payments (default: true)
- `INITIAL_SPINS` - Free spins for new users (default: 5)
- `REFERRAL_BONUS` - Stars per referral (default: 5)
- `DAILY_BONUS_SPINS` - Daily bonus spins (default: 5)
- `WIN_ADDS_SPINS` - Add spins on win (default: true)
- `MANDATORY_CHANNEL` - Required channel username (optional)

## Monitoring

The bot includes built-in monitoring:
- Performance metrics
- Error tracking
- User analytics
- Business KPIs

Access via `/stats` command (admin only).

## Security Notes

- Never commit `.env` file
- Use environment variables in production
- Enable Telegram Stars in @BotFather
- Monitor logs for suspicious activity
- Keep dependencies updated
