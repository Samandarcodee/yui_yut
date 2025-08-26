#!/bin/bash
# 🎰 Slot Game Bot — Yut, Yulduz, Qayta O'yna! Ishga tushirish skripti

echo "================================"
echo "🎰 Slot Game Bot ishga tushirish"
echo "================================"

# Python mavjudligini tekshirish
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 topilmadi! Python 3.11+ o'rnating."
    exit 1
fi

# Ma'lumotlar va log papkalarini yaratish
mkdir -p data logs

# Virtual environment yaratish (ixtiyoriy)
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment yaratilmoqda..."
    python3 -m venv venv
fi

# Virtual environment ni faollashtirish
if [ -f "venv/bin/activate" ]; then
    echo "🔧 Virtual environment faollashtirilmoqda..."
    source venv/bin/activate
fi

# Bog'liqliklarni o'rnatish
echo "📥 Bog'liqliklar o'rnatilmoqda..."
pip install -r requirements.txt

# Botni ishga tushirish
echo "🚀 Bot ishga tushirilmoqda..."
echo "❗ To'xtatish uchun Ctrl+C bosing"
echo

python3 main_uz.py

echo
echo "✅ Bot to'xtatildi"
