"""
🎰 Slot Game Bot — Yut, Yulduz, Qayta O'yna! konfiguratsiyasi
"""
import os
from typing import List
from datetime import timedelta

# Bot konfiguratsiyasi
BOT_TOKEN = os.getenv("BOT_TOKEN", "8245319536:AAE9ofodgLDe38G44wRoiucsAjiADh5jdjI")

# Admin foydalanuvchilar ro'yxati (haqiqiy Telegram ID larni qo'shing)
ADMIN_IDS: List[int] = [
    5928372261,  # @Samandar_kk
    # Boshqa adminlarni bu yerga qo'shing
]

# Admin aloqa ma'lumotlari
ADMIN_CONTACT_INFO = {
    "bot_username": "@STARS_YUTT_BOT",
    "admin_username": "@Samandar_kk",
    "support_channel": "@premim_002",
    "support_group": None,  # Agar support guruhi bo'lsa, bu yerga qo'shing
    "email": None,  # Agar email bo'lsa, bu yerga qo'shing
    "response_time": "24 soat ichida",
    "working_hours": "24/7"
}

# Ko'p uchraydigan savollar va javoblar
FAQ = {
    "payment_issues": {
        "question": "To'lov bilan bog'liq muammolar",
        "answer": "Telegram Stars orqali to'lov qilishda muammo bo'lsa, to'lov ID va screenshot bilan admin bilan bog'laning."
    },
    "game_issues": {
        "question": "O'yin ishlamayapti",
        "answer": "O'yin ishlamayotgan bo'lsa, botni qayta ishga tushiring yoki admin bilan bog'laning."
    },
    "bonus_issues": {
        "question": "Bonus ololmayapman",
        "answer": "Kunlik bonus olishda muammo bo'lsa, vaqtni tekshiring va admin bilan bog'laning."
    },
    "account_issues": {
        "question": "Hisobim yo'qoldi",
        "answer": "Hisobingiz yo'qolgan bo'lsa, username va eski ma'lumotlarni admin bilan bog'laning."
    }
}

# Majburiy kanal obunasi
REQUIRED_CHANNEL = "@premim_002"
CHANNEL_URL = "https://t.me/premim_002"

# Ma'lumotlar bazasi konfiguratsiyasi
DATABASE_PATH = "data/slot_game.db"

# O'yin konfiguratsiyasi
DEFAULT_WIN_PROBABILITY = 0.7  # 70% g'alaba imkoniyati
STAR_TO_ATTEMPT_RATIO = 1  # 1 Yulduz = 1 Urinish

# Slot o'yin belgilari va mukofotlar
SLOT_EMOJIS = ["💎", "🔔", "🍒", "⭐", "🍀"]

# G'alaba kombinatsiyalari
WINNING_COMBINATIONS = {
    "💎💎💎": 100,  # Olmos uchlik
    "🔔🔔🔔": 50,   # Qo'ng'iroq uchlik
    "🍒🍒🍒": 25,   # Gilos uchlik
    "⭐⭐⭐": 10,   # Yulduz uchlik
    "🍀🍀🍀": 5,    # Yonca uchlik
}

# Qo'shimcha mukofotlar
PARTIAL_COMBINATIONS = {
    2: 3,  # 2 ta bir xil belgi = +3 yulduz
    1: 1,  # 1 ta bir xil belgi = +1 yulduz
}

# Kunlik bonus
DAILY_BONUS_AMOUNT = 5  # Kunlik 5 yulduz
DAILY_BONUS_COOLDOWN = timedelta(hours=24)

# Referal tizimi
REFERRAL_BONUS = 10  # Har bir referal uchun 10 yulduz
REFERRAL_FRIEND_BONUS = 10  # Do'st ham 10 yulduz oladi

# Xabarlar (O'zbek tilida)
WELCOME_MESSAGE = """
🎰 **Slot Game Bot — Yut, Yulduz, Qayta O'yna!** ga xush kelibsiz! 🎰

🌟 Yulduzlarni yuting va zavqlaning! 🌟

Boshlashdan oldin, siz robot emasligingizni tasdiqlang:
"""

VERIFICATION_SUCCESS = """
✅ **Tasdiqlash muvaffaqiyatli!** O'yinga xush kelibsiz!

Siz ro'yxatdan o'tkazildingiz va o'ynashga tayyorsiz! 🎉

Quyidagi menyudan foydalaning:
🎮 Slot o'yinini o'ynang
⭐ Telegram Stars bilan urinishlar sotib oling
👤 Profilingizni ko'ring
📊 Statistikalarni ko'ring

Omad tilaymiz! 🍀
"""

# Kanal obunasi xabarlari
CHANNEL_SUBSCRIPTION_REQUIRED = """
⚠️ **KANAL OBUNASI TALAB QILINADI** ⚠️

Botdan foydalanishni davom ettirish uchun avval bizning kanalimizga obuna bo'lishingiz kerak.

📢 **Kanal:** {channel_url}

Obuna bo'lgandan so'ng "✅ Obunani Tekshirish" tugmasini bosing.
"""

SUBSCRIPTION_SUCCESS = """
🎉 **AJOYIB!** 🎉

Tabriklaymiz! Siz muvaffaqiyatli kanalga obuna bo'ldingiz.

Endi botning barcha xususiyatlaridan foydalanishingiz mumkin:
🎰 Slot o'yini
⭐ Yulduzlar to'plash
🎁 Kunlik bonuslar
👥 Do'stlarni taklif qilish

Omad tilaymiz!
"""

SUBSCRIPTION_FAILED = """
❌ **OBUNA TOPILMADI** ❌

Siz hali kanalga obuna bo'lmagansiz yoki obuna private holatda.

Iltimos:
1. Kanalga obuna bo'ling
2. Obunangiz public (ochiq) ekanligiga ishonch hosil qiling
3. "✅ Obunani Tekshirish" tugmasini qayta bosing

📢 **Kanal:** {channel_url}
"""

MAIN_MENU_MESSAGE = """
🎰 **Slot Game Bot — Asosiy Menyu** 🎰

Quyidagi variantlardan birini tanlang:
"""

PROFILE_MESSAGE = """
👤 **SIZNING PROFILINGIZ** 👤

🆔 **Foydalanuvchi:** {username}
📅 **Qo'shilgan:** {reg_date}

💰 **Joriy balans:**
⭐ Yulduzlar: {stars}
🎮 Urinishlar: {attempts}

📊 **O'yin statistikalari:**
🏆 G'alabalar: {wins}
❌ Mag'lubiyatlar: {losses}
🎯 Jami o'yinlar: {total_games}
📈 G'alaba foizi: {win_rate}%

💎 **Eng katta g'alaba:** {biggest_win} yulduz

🎰 Yana o'ynashga tayyormisiz? 🎰
"""

DAILY_BONUS_MESSAGE = """
🎁 **KUNLIK BONUS** 🎁

Har 24 soatda bepul 5 yulduz oling!

⏰ **Keyingi bonus:** {next_bonus}

🌟 Bugun bonusingizni oldingizmi? 🌟
"""

REFERRAL_MESSAGE = """
👥 **REFERAL DASTURI** 👥

Do'stlaringizni taklif qiling va mukofot oling!

🎁 **Sizning bonusingiz:** {referrals} ta referal x 10 yulduz = {total_bonus} yulduz

🔗 **Sizning linkingiz:**

`{referral_link}`

📋 **Qanday ishlaydi:**
• Do'stingiz sizning linkingiz orqali botga qo'shiladi
• Ikkalangiz ham 10 yulduzdan olasiz!
• Cheksiz referal taklif qilishingiz mumkin

💫 Do'stlaringizni ulashing va birga yuting! 💫
"""

PURCHASE_MESSAGE = """
🛒 **YULDUZLAR SOTIB OLISH** 🛒

Telegram Stars orqali yulduzlar sotib oling!

💰 **Narxlar:**
⭐ 1 Yulduz = 1 Urinish
⭐ 5 Yulduz = 5 Urinish  
⭐ 10 Yulduz = 10 Urinish
⭐ 25 Yulduz = 25 Urinish
⭐ 50 Yulduz = 50 Urinish

🎮 Ko'proq o'ynash uchun yulduzlarni sotib oling!
"""

HELP_MESSAGE = """
ℹ️ **YORDAM** ℹ️

🎰 **O'yin qoidalari:**
• Har bir urinish uchun 1 yulduz kerak
• 3 ta belgi tasodifiy tanlanadi
• Bir xil belgilar uchun mukofot olasiz

🏆 **G'alaba kombinatsiyalari:**
💎💎💎 = +100 yulduz
🔔🔔🔔 = +50 yulduz  
🍒🍒🍒 = +25 yulduz
⭐⭐⭐ = +10 yulduz
🍀🍀🍀 = +5 yulduz
2 ta bir xil = +3 yulduz
1 ta bir xil = +1 yulduz

🎁 **Bepul yulduzlar:**
• Kunlik bonus: har 24 soatda 5 yulduz
• Referal dasturi: har bir do'st uchun 10 yulduz
• Admin mukofotlari

💳 **Yulduz sotib olish:**
Telegram Stars orqali to'lov qiling

📞 **Yordam:** Admin bilan bog'laning
"""

# Admin bilan bog'lanish xabari
CONTACT_ADMIN_MESSAGE = """
📞 **ADMIN BILAN BOG'LANISH** 📞

💬 **Yordam kerakmi?**
Agar savollaringiz bo'lsa yoki yordam kerak bo'lsa:

👤 **Admin ma'lumotlari:**
• **Bot:** {bot_username}
• **Admin:** {admin_username}
• **Kanal:** {support_channel}

📧 **Bog'lanish usullari:**
• Bot administratori bilan to'g'ridan-to'g'ri yozing
• Muammolarni batafsil tasvirlab yuboring
• Screenshot qo'shishni unutmang

⚡ **Tez yordam:**
• To'lov bilan bog'liq muammolar
• Texnik xatolar
• Hisobingiz bilan bog'liq savollar
• O'yin qoidalari haqida savollar

🕐 **Javob vaqti:**
{response_time} ichida javob beramiz

⏰ **Ish vaqti:**
{working_hours}

💡 **Maslahat:**
Muammoni aniq tasvirlab yuboring - bu tezroq yordam berishga yordam beradi!

🔗 **Qo'shimcha yordam:**
• Kanalimizga obuna bo'ling: {support_channel}
• Yangiliklar va e'lonlarni kuzatib boring
"""

ADMIN_HELP_MESSAGE = """
**📋 MAVJUD ADMIN BUYRUQLARI:**

🎛 **Asosiy buyruqlar:**
• `/admin` - Admin panelini ochish
• `/broadcast [xabar]` - Tez xabar yuborish
• `/testpay` - Test to'lov (5 urinish berish)

🎮 **Interfeys orqali:**
• 📢 Xabar yuborish - Barcha foydalanuvchilarga e'lon
• 🎁 Bonus berish - Foydalanuvchiga yulduz berish
• 🚫 Bloklash/Ochish - Foydalanuvchini boshqarish
• ⚙️ G'alaba foizini sozlash - O'yin sozlamalari
• 📊 Statistikalar - Bot hisobotlari

💡 **Maslahat:** Interfeys buyruqlari oson va xavfsizroq!
"""

# Logging konfiguratsiyasi
LOGGING_LEVEL = "INFO"
LOG_FILE = "logs/bot.log"
