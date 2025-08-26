@echo off
REM 🎰 Slot Game Bot — Yut, Yulduz, Qayta O'yna! Ishga tushirish skripti

echo ================================
echo 🎰 Slot Game Bot ishga tushirish
echo ================================

REM Python mavjudligini tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python topilmadi! Python 3.11+ o'rnating.
    pause
    exit /b 1
)

REM Ma'lumotlar va log papkalarini yaratish
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Virtual environment yaratish (ixtiyoriy)
if not exist "venv" (
    echo 📦 Virtual environment yaratilmoqda...
    python -m venv venv
)

REM Virtual environment ni faollashtirish
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Virtual environment faollashtirilmoqda...
    call venv\Scripts\activate.bat
)

REM Bog'liqliklarni o'rnatish
echo 📥 Bog'liqliklar o'rnatilmoqda...
pip install -r requirements.txt

REM Botni ishga tushirish
echo 🚀 Bot ishga tushirilmoqda...
echo ❗ To'xtatish uchun Ctrl+C bosing
echo.

python main_uz.py

echo.
echo ✅ Bot to'xtatildi
pause
