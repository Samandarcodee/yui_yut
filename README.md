## Slot Game Bot — "Yut, Yulduz, Qayta O‘yna!"

### Qisqacha
Telegram slot o‘yini boti. Foydalanuvchi kanalga yulduz (Telegram Stars) hadya qiladi va shuncha urinish (spin) oladi. Spinlarda kombinatsiyaga qarab yulduz yutadi yoki urinish kamayadi. Referral, top, profil va admin panel mavjud.

### O‘rnatish
- Python 3.10+
- Windows PowerShell yoki Linux/macOS shell

1) Reponi tayyorlang va kutubxonalarni o‘rnating:
```bash
python -m venv .venv
.venv/Scripts/Activate.ps1  # Windows
pip install -r requirements.txt
```

2) `.env` yarating (loyiha ildizida `uyin_bot/.env`):
```bash
BOT_TOKEN=123456:ABC...
ADMIN_IDS=123456789,987654321
CHANNEL_USERNAME=@your_channel  # yulduz hadya tekshiruvi uchun kanal
REFERRAL_BONUS=5
SIMULATE_DONATION=true
PROVIDER_TOKEN=
STARS_ENABLED=true
DAILY_BONUS_SPINS=5
INITIAL_SPINS=10  # Yangi userlar uchun boshlang'ich spinlar
```

3) Ishga tushirish:
```bash
python -m src.main
```

4) Modul sifatida emas, bevosita ham ishga tushirishingiz mumkin:
```bash
python main.py
```

### Buyruqlar
- /start — ro‘yxatdan o‘tish, referral aniqlash
- /spin — slot o‘ynash
- /profile — profilni ko‘rish
- /top — eng yaxshi o‘yinchilar
- /referral — referral havola
- /help — yordam

### Admin buyruqlari
- /broadcast <matn>
- /stats
- /addspins @username 10
- /addstars @username 20

### Slot kombinatsiyalari
- 💎💎💎 → +100
- 🔔🔔🔔 → +50
- 🍒🍒🍒 → +25
- ⭐⭐⭐ → +10
- 🍀🍀🍀 → +5
- 🔥🔥🔥 → +3
- 🎲🎲🎲 → +1
- 2 ta bir xil + 1 → +1
- Aralash → 0

O'yin: kombinatsiyaga qarab yulduzlar beriladi (detallar kodda ko'rsatilgan).


### Foydali eslatmalar
- Windows PowerShell’da virtual muhitni faollashtirish uchun: `Set-ExecutionPolicy -Scope Process RemoteSigned`.
- `.env` bo‘lmasa, bot ishga tushmaydi. `BOT_TOKEN` majburiy.
- Telegram Stars to‘lovlari uchun @BotFather → MyBots → Payments → Stars bo‘limini yoqing. Aks holda bot dev-rejimda spin qo‘shishni emulyatsiya qiladi va foydalanuvchiga izoh beradi.

# yui_yut
