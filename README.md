# 🎰 STARS YUT - Professional Telegram Slot Bot

[![Tests](https://github.com/Samandarcodee/yui_yut/actions/workflows/ci.yml/badge.svg)](https://github.com/Samandarcodee/yui_yut/actions)
[![Security](https://img.shields.io/badge/security-hardened-green.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()

Professional Telegram Stars slot game bot with enterprise-grade security, monitoring, and deployment.

## ✨ Features

### 🎮 Game Features
- **Slot Game**: 7 symbols, balanced 70% win rate
- **Telegram Stars**: Real payment integration
- **Referral System**: 2-level rewards (L1: +5⭐, L2: +2⭐)
- **Daily Bonuses**: Free spins every day
- **Withdrawal System**: Convert stars to real money
- **VIP Management**: Admin-controlled tiers

### 🔒 Security
- **Input Sanitization**: XSS/injection protection
- **SQL Injection Prevention**: Parameterized queries
- **Admin Access Control**: Role-based permissions
- **Audit Logging**: Security event tracking
- **Rate Limiting Ready**: Anti-abuse measures

### 📊 Analytics & Monitoring
- **Real-time Metrics**: DAU/WAU/MAU tracking
- **Business KPIs**: Conversion, ARPU, LTV
- **Performance Monitoring**: Response times, errors
- **Game Balance**: Win rate verification
- **User Behavior**: Engagement analytics

### ⚙️ Admin Panel
- **User Management**: Ban/unban, free play, VIP
- **Broadcast System**: Segmented messaging
- **Manual Operations**: Add spins/stars
- **Support System**: User questions & replies
- **Statistics Dashboard**: Comprehensive metrics

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/Samandarcodee/yui_yut.git
cd yui_yut

# 2. Setup environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# or source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure bot
cp env.example .env
# Edit .env with your BOT_TOKEN

# 5. Run bot
python main.py
```

### Production Deployment

#### Render.com (Recommended)
1. Push to GitHub
2. Connect repo to Render
3. Set `BOT_TOKEN` environment variable
4. Deploy automatically

#### Railway.app
```bash
railway init
railway up
railway variables set BOT_TOKEN=your_token
```

#### Docker
```bash
docker build -t stars-yut-bot .
docker run -e BOT_TOKEN=your_token stars-yut-bot
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🎯 Configuration

### Required Environment Variables
- `BOT_TOKEN` - Get from @BotFather

### Optional Settings
- `ADMIN_IDS` - Comma-separated admin user IDs
- `STARS_ENABLED` - Enable Telegram Stars (default: true)
- `INITIAL_SPINS` - Free spins for new users (default: 5)
- `REFERRAL_BONUS` - Stars per referral (default: 5)
- `DAILY_BONUS_SPINS` - Daily bonus amount (default: 5)

## 🎰 Game Mechanics

### Slot Combinations
- 💎💎💎 → +100 ⭐ (Diamond jackpot)
- 🔔🔔🔔 → +50 ⭐ (Bell bonus)
- 🍒🍒🍒 → +25 ⭐ (Cherry win)
- ⭐⭐⭐ → +10 ⭐ (Star combo)
- 🍀🍀🍀 → +5 ⭐ (Lucky clover)
- 🔥🔥🔥 → +3 ⭐ (Fire streak)
- 🎲🎲🎲 → +1 ⭐ (Dice roll)
- 2 matching → +1 ⭐ (Partial match)

### Game Balance
- **70% win probability** (house edge: 30%)
- **Mathematically verified** with unit tests
- **Fair play guaranteed** with auditable code

## 🛠️ Development

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Security tests
python -m pytest tests/test_security.py -v
```

### Code Quality
```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## 📈 Business Metrics

Access via `/stats` command (admin only):
- **DAU/WAU/MAU**: Active user tracking
- **Conversion Rate**: Payment conversion
- **ARPU**: Average revenue per user
- **Referral Performance**: Viral growth metrics

## 🔧 Admin Commands

- `/stats` - Business metrics dashboard
- `/broadcast all|active7|vip <message>` - Segmented messaging
- `/ban @username` - Ban user
- `/unban @username` - Unban user
- `/freeplay @username on|off` - Toggle free play
- `/setvip @username 0|1|2|3` - Set VIP level
- `/addspins @username 10` - Add spins
- `/addstars @username 20` - Add stars
- `/reply user_id message` - Reply to user question

## 🎁 User Commands

- `/start` - Register and get free spins
- `/spin` - Play slot game
- `/profile` - View stats and balance
- `/top` - Leaderboard
- `/referral` - Get referral link
- `/daily` - Claim daily bonus
- `/ask question` - Contact admin
- `/help` - Command help

## 📱 User Interface

Clean, modern Telegram interface:
- **2-row menu**: Simplified navigation
- **Rich formatting**: HTML, emojis, animations
- **Inline actions**: Quick play, profile access
- **Visual feedback**: Loading states, celebrations

## 🏗️ Architecture

```
src/
├── main.py          # Bot entry point
├── config.py        # Configuration management
├── db.py           # Database operations
├── handlers.py     # Command handlers
├── keyboards.py    # UI components
├── slot.py         # Game mechanics
└── monitoring.py   # Metrics & logging

tests/
├── test_slot.py     # Game logic tests
├── test_security.py # Security tests
└── test_handlers.py # Handler tests
```

## 🔐 Security Features

- **Input Validation**: All user inputs sanitized
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: HTML tag removal
- **Admin Access Control**: Role-based permissions
- **Audit Logging**: Security events tracked
- **Rate Limiting Ready**: Anti-abuse framework

## 📊 Monitoring

Built-in observability:
- **Performance Metrics**: Response times, throughput
- **Error Tracking**: Categorized error monitoring
- **Business Analytics**: Revenue, engagement, retention
- **Health Checks**: Docker/Kubernetes ready

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: See `DEPLOYMENT.md`
- **Security**: Report to admin privately

---

**Built with ❤️ by professional developers**