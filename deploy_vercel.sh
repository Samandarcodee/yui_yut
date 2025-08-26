#!/bin/bash
# 🚀 Vercel Deployment Automation Script

echo "================================"
echo "🚀 Vercel Deployment Script"
echo "================================"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Vercel CLI o'rnatilmoqda..."
    npm install -g vercel
else
    echo "✅ Vercel CLI mavjud"
fi

# Check if logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Vercel ga login qilish kerak..."
    vercel login
else
    echo "✅ Vercel ga login qilingan"
fi

# Create necessary directories
echo "📁 Kerakli papkalar yaratilmoqda..."
mkdir -p api data logs

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env fayli topilmadi!"
    echo "📝 env.example faylini .env ga nusxalang va sozlang"
    echo "cp env.example .env"
    echo "nano .env"
    exit 1
fi

# Deploy to Vercel
echo "🚀 Vercel ga deploy qilish..."
vercel --prod

echo "✅ Deployment tugadi!"
echo "🌐 Webhook URL ni Telegram Bot API ga o'rnating:"
echo "curl -X POST \"https://api.telegram.org/bot<BOT_TOKEN>/setWebhook\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"url\": \"https://your-app.vercel.app/api/webhook\"}'"
