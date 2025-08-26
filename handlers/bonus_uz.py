"""
🎁 Kunlik bonus va referal tizimi handlerlari (O'zbek tilida)
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta

from db.database import Database
from keyboards.inline import (
    get_daily_bonus_keyboard, get_referral_keyboard, 
    get_main_menu, get_back_to_admin_keyboard
)
from config.settings import DAILY_BONUS_MESSAGE, REFERRAL_MESSAGE, DAILY_BONUS_AMOUNT

logger = logging.getLogger(__name__)
router = Router()
db = Database()


@router.callback_query(F.data == "daily_bonus")
async def show_daily_bonus(callback: CallbackQuery):
    """Kunlik bonusni ko'rsatish"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Iltimos avval ro'yxatdan o'ting!", show_alert=True)
        return
    
    # STRICT CHANNEL SUBSCRIPTION CHECK
    if not user.get('channel_subscribed', False):
        from config.settings import CHANNEL_SUBSCRIPTION_REQUIRED, CHANNEL_URL
        from keyboards.inline import get_channel_subscription_keyboard
        
        await callback.message.edit_text(
            CHANNEL_SUBSCRIPTION_REQUIRED.format(channel_url=CHANNEL_URL),
            reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
        )
        await callback.answer("⚠️ Bonusni ko'rish uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    # Bonus olish mumkinligini tekshirish
    can_claim = await db.can_claim_daily_bonus(user_id)
    
    if can_claim:
        bonus_text = f"""
🎁 **KUNLIK BONUS** 🎁

Har 24 soatda bepul {DAILY_BONUS_AMOUNT} yulduz oling!

✅ **Bonus tayyor!**
Bonusni olish uchun tugmani bosing.

🌟 Kunlik bonusni unutmang! 🌟
"""
    else:
        # Keyingi bonus vaqtini hisoblash
        next_bonus_time = await db.get_next_daily_bonus_time(user_id)
        if next_bonus_time:
            now = datetime.now()
            time_left = next_bonus_time - now
            
            if time_left.total_seconds() > 0:
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                next_bonus_str = f"{hours} soat {minutes} daqiqa"
            else:
                next_bonus_str = "Hozir"
        else:
            next_bonus_str = "Noma'lum"
        
        bonus_text = DAILY_BONUS_MESSAGE.format(next_bonus=next_bonus_str)
    
    await callback.message.edit_text(
        bonus_text,
        reply_markup=get_daily_bonus_keyboard(can_claim)
    )
    await callback.answer()


@router.callback_query(F.data == "claim_daily_bonus")
async def claim_daily_bonus(callback: CallbackQuery):
    """Kunlik bonusni olish"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Iltimos avval ro'yxatdan o'ting!", show_alert=True)
        return
    
    # STRICT CHANNEL SUBSCRIPTION CHECK
    if not user.get('channel_subscribed', False):
        from config.settings import CHANNEL_SUBSCRIPTION_REQUIRED, CHANNEL_URL
        from keyboards.inline import get_channel_subscription_keyboard
        
        await callback.message.edit_text(
            CHANNEL_SUBSCRIPTION_REQUIRED.format(channel_url=CHANNEL_URL),
            reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
        )
        await callback.answer("⚠️ Bonusni olish uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    # Bonusni olishga urinish
    success = await db.claim_daily_bonus(user_id)
    
    if success:
        await callback.answer(f"🎉 {DAILY_BONUS_AMOUNT} yulduz bonus olindi!", show_alert=True)
        
        # Yangilangan profilni ko'rsatish
        updated_user = await db.get_user(user_id)
        
        success_text = f"""
🎉 **BONUS OLINDI!** 🎉

+{DAILY_BONUS_AMOUNT} ⭐ yulduz hisobingizga qo'shildi!

💰 **Joriy balans:**
⭐ Yulduzlar: {updated_user['stars']}
🎮 Urinishlar: {updated_user['attempts']}

⏰ **Keyingi bonus:** 24 soat ichida

🎰 Endi o'ynashingiz mumkin! 🎰
"""
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu()
        )
        
        logger.info(f"Foydalanuvchi {user_id} kunlik bonus oldi: {DAILY_BONUS_AMOUNT} yulduz")
    else:
        await callback.answer("❌ Bonus hali tayyor emas!", show_alert=True)


@router.callback_query(F.data == "wait_bonus")
async def wait_bonus(callback: CallbackQuery):
    """Bonus kutish xabari"""
    await callback.answer("⏰ Bonusni olish uchun kutishingiz kerak!", show_alert=True)


@router.callback_query(F.data == "referral")
async def show_referral(callback: CallbackQuery):
    """Referal dasturini ko'rsatish"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Iltimos avval ro'yxatdan o'ting!", show_alert=True)
        return
    
    # Referal statistikasini olish
    stats = await db.get_referral_stats(user_id)
    
    # Bot username ini olish (bot obyektini callback orqali olish)
    bot: Bot = callback.bot
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    
    # Referal linkini yaratish
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    referral_text = REFERRAL_MESSAGE.format(
        referrals=stats['referrals'],
        total_bonus=stats['total_bonus'],
        referral_link=referral_link
    )
    
    await callback.message.edit_text(
        referral_text,
        reply_markup=get_referral_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "share_referral")
async def share_referral(callback: CallbackQuery):
    """Referal linkini ulashish"""
    user_id = callback.from_user.id
    
    # Bot username ini olish
    bot: Bot = callback.bot
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    
    # Referal linkini yaratish
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    share_text = f"""
🔗 **SIZNING REFERAL LINKINGIZ** 🔗

`{referral_link}`

📱 **Qanday ulashish:**
• Do'stlaringizga yuborish
• Ijtimoiy tarmoqlarda ulashish
• Guruh va kanallarda reklama qilish

🎁 **Mukofot:**
• Har bir do'st uchun sizga 10 yulduz
• Do'stingiz ham 10 yulduz oladi

💫 Ko'proq taklif qiling, ko'proq yuting! 💫
"""
    
    await callback.message.edit_text(
        share_text,
        reply_markup=get_referral_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "my_referrals")
async def show_my_referrals(callback: CallbackQuery):
    """Mening referallarimni ko'rsatish"""
    user_id = callback.from_user.id
    stats = await db.get_referral_stats(user_id)
    
    referrals_text = f"""
👥 **MENING REFERALLARIM** 👥

📊 **Statistika:**
• Jami referallar: {stats['referrals']}
• Jami bonus: {stats['total_bonus']} ⭐ yulduz

💰 **Daromad:**
• Har bir referal: 10 ⭐ yulduz
• Jami qilingan: {stats['total_bonus']} ⭐ yulduz

🎯 **Maqsad:**
Ko'proq do'stlaringizni taklif qiling va ko'proq yulduz yuting!

🔗 Referal linkingizni ulashishni unutmang! 🔗
"""
    
    await callback.message.edit_text(
        referrals_text,
        reply_markup=get_referral_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "referral_info")
async def show_referral_info(callback: CallbackQuery):
    """Referal tizimi haqida ma'lumot"""
    info_text = """
ℹ️ **REFERAL TIZIMI HAQIDA** ℹ️

🎯 **Maqsad:**
Do'stlaringizni botga taklif qiling va ikkalangiz ham mukofot oling!

📋 **Qanday ishlaydi:**
1. Sizning maxsus linkingizni oling
2. Do'stlaringizga yuboring
3. Do'stingiz link orqali botga kiradi
4. Ikkalangiz ham 10 yulduzdan olasiz!

🎁 **Mukofotlar:**
• Siz: 10 ⭐ yulduz
• Do'stingiz: 10 ⭐ yulduz
• Cheklov yo'q - cheksiz taklif qilishingiz mumkin!

💡 **Maslahatlar:**
• Linkni ijtimoiy tarmoqlarda ulashing
• Do'stlar guruhlarida reklama qiling
• Oila a'zolarini taklif qiling

🚀 Boshlang va birinchi referalingizni oling! 🚀
"""
    
    await callback.message.edit_text(
        info_text,
        reply_markup=get_referral_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bonus_info")
async def show_bonus_info(callback: CallbackQuery):
    """Bonuslar haqida ma'lumot"""
    bonus_info = f"""
🎁 **BONUSLAR HAQIDA** 🎁

⏰ **Kunlik bonus:**
• Har 24 soatda {DAILY_BONUS_AMOUNT} bepul yulduz
• Vaqtni unutmang!

👥 **Referal bonusi:**
• Har bir do'st uchun 10 yulduz
• Do'stingiz ham 10 yulduz oladi
• Cheksiz referal taklif qilishingiz mumkin

🎰 **O'yin bonuslari:**
• Yutganingizda yulduzlar qo'shiladi
• Katta g'alabalar uchun qo'shimcha mukofotlar

👑 **Admin bonuslari:**
• Faol o'yinchilar uchun maxsus mukofotlar
• Musobaqalar va tadbirlar

💡 **Maslahat:**
Barcha bonus imkoniyatlaridan foydalaning va ko'proq yulduz to'plang!

🌟 Har kun botga kiring va bonuslaringizni oling! 🌟
"""
    
    await callback.message.edit_text(
        bonus_info,
        reply_markup=get_main_menu()
    )
    await callback.answer()
