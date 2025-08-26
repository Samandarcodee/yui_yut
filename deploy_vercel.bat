@echo off
REM 🚀 Vercel Deployment Automation Script (Windows)

echo ================================
echo 🚀 Vercel Deployment Script
echo ================================

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js topilmadi! Node.js o'rnating
    pause
    exit /b 1
)

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Vercel CLI o'rnatilmoqda...
    npm install -g vercel
) else (
    echo ✅ Vercel CLI mavjud
)

REM Check if logged in to Vercel
vercel whoami >nul 2>&1
if errorlevel 1 (
    echo 🔐 Vercel ga login qilish kerak...
    vercel login
) else (
    echo ✅ Vercel ga login qilingan
)

REM Create necessary directories
echo 📁 Kerakli papkalar yaratilmoqda...
if not exist "api" mkdir api
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env fayli topilmadi!
    echo 📝 env.example faylini .env ga nusxalang va sozlang
    echo copy env.example .env
    echo notepad .env
    pause
    exit /b 1
)

REM Deploy to Vercel
echo 🚀 Vercel ga deploy qilish...
vercel --prod

echo ✅ Deployment tugadi!
echo 🌐 Webhook URL ni Telegram Bot API ga o'rnating:
echo curl -X POST "https://api.telegram.org/bot^<BOT_TOKEN^>/setWebhook" ^
echo      -H "Content-Type: application/json" ^
echo      -d "{\"url\": \"https://your-app.vercel.app/api/webhook\"}"
pause
