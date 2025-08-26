"""
🎰 Profil va statistika handlerlari (O'zbek tilida)
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime

from db.database import Database
from keyboards.inline import get_profile_keyboard, get_main_menu

logger = logging.getLogger(__name__)
router = Router()
db = Database()


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    """Foydalanuvchi profilini ko'rsatish"""
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
        await callback.answer("⚠️ Profilni ko'rish uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    # G'alaba foizini hisoblash
    win_rate = 0
    if user['total_spins'] > 0:
        win_rate = (user['wins'] / user['total_spins']) * 100
    
    # Ro'yxatdan o'tgan sanani formatlash
    reg_date = datetime.fromisoformat(user['reg_date']).strftime("%d.%m.%Y")
    
    # Foydalanuvchi ismini aniqlash
    username = user['first_name'] or user['username'] or 'Noma\'lum'
    
    from config.settings import PROFILE_MESSAGE
    
    profile_text = PROFILE_MESSAGE.format(
        username=username,
        reg_date=reg_date,
        stars=user['stars'],
        attempts=user['attempts'],
        wins=user['wins'],
        losses=user['losses'],
        total_games=user['total_spins'],
        win_rate=win_rate,
        biggest_win=user['biggest_win']
    )
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_profile_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "statistics")
async def show_statistics(callback: CallbackQuery):
    """Global statistikalarni ko'rsatish"""
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
        await callback.answer("⚠️ Statistikalarni ko'rish uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    # Global statistikalarni olish
    stats = await db.get_total_stats()
    
    # Global g'alaba foizini hisoblash
    global_win_rate = 0
    if stats.get('total_spins', 0) > 0:
        global_win_rate = (stats.get('total_wins', 0) / stats.get('total_spins', 0)) * 100
    
    stats_text = f"""
📊 **GLOBAL STATISTIKALAR** 📊

👥 **Jamoa:**
• Jami o'yinchilar: {stats.get('total_users', 0):,}
• Jami o'yinlar: {stats.get('total_spins', 0):,}

🎯 **O'yin natijalari:**
• Jami g'alabalar: {stats.get('total_wins', 0):,}
• Jami mag'lubiyatlar: {stats.get('total_losses', 0):,}
• Global g'alaba foizi: {global_win_rate:.1f}%

💰 **Iqtisodiyot:**
• Aylanayotgan yulduzlar: {stats.get('total_stars', 0):,} ⭐
• Eng katta g'alaba: {stats.get('biggest_win', 0)} ⭐

👮 **Boshqaruv:**
• Bloklangan foydalanuvchilar: {stats.get('banned_users', 0)}

🎰 O'yinga qo'shiling va yuqori o'rinlarga chiqing! 🎰
"""
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "leaderboard")
async def show_leaderboard(callback: CallbackQuery):
    """Top o'yinchilar ro'yxatini ko'rsatish"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Iltimos avval ro'yxatdan o'ting!", show_alert=True)
        return
    
    # Top o'yinchilarni olish
    top_players = await db.get_leaderboard(10)
    
    leaderboard_text = "🏆 **TOP O'YINCHILAR** 🏆\n\n"
    
    if not top_players:
        leaderboard_text += "Hali o'yinchilar yo'q! Birinchi bo'lib o'ynang! 🎰"
    else:
        for i, player in enumerate(top_players, 1):
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            # Foydalanuvchi ismini aniqlash
            username = player['first_name'] or player['username'] or 'Noma\'lum'
            stars = player['stars']
            wins = player['wins']
            total_spins = player['total_spins']
            biggest_win = player.get('biggest_win', 0)
            
            leaderboard_text += f"{medal} **{username}**\n"
            leaderboard_text += f"   ⭐ {stars} yulduz | 🏆 {wins} g'alaba"
            if biggest_win > 0:
                leaderboard_text += f" | 💎 {biggest_win} max"
            leaderboard_text += f"\n   🎮 {total_spins} o'yin\n\n"
    
    leaderboard_text += "💫 Yuqori o'rinlarga chiqing va slot chempioni bo'ling! 💫"
    
    await callback.message.edit_text(
        leaderboard_text,
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "contact_admin")
async def contact_admin(callback: CallbackQuery):
    """Admin bilan bog'lanish"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Iltimos avval ro'yxatdan o'ting!", show_alert=True)
        return
    
    # Admin bilan bog'lanish xabari
    contact_text = f"""
📞 **ADMIN BILAN BOG'LANISH** 📞

👤 **Sizning ma'lumotlaringiz:**
• ID: `{user_id}`
• Username: @{callback.from_user.username or 'Yo\'q'}
• Ism: {callback.from_user.first_name}

📝 **Savol yoki muammo:**
Iltimos, savolingiz yoki muammongizni yozing va admin siz bilan bog'lanishini kutib turing.

⏰ **Javob vaqti:** 24 soat ichida

💡 **Maslahat:** Savolingizni aniq va tushunarli yozing!
"""
    
    await callback.message.edit_text(
        contact_text,
        reply_markup=get_contact_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "send_message_to_admin")
async def send_message_to_admin(callback: CallbackQuery):
    """Adminga xabar yuborish"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Iltimos avval ro'yxatdan o'ting!", show_alert=True)
        return
    
    # Admin ID larni olish
    from config.settings import ADMIN_IDS
    
    if not ADMIN_IDS:
        await callback.answer("❌ Admin mavjud emas!", show_alert=True)
        return
    
    # Foydalanuvchi ma'lumotlari
    user_info = f"""
📨 **YANGI XABAR ADMINGA**

👤 **Foydalanuvchi:**
• ID: `{user_id}`
• Username: @{callback.from_user.username or 'Yo\'q'}
• Ism: {callback.from_user.first_name}
• Ro'yxatdan o'tgan: {user.get('reg_date', 'Noma\'lum')}

📊 **Statistika:**
• Yulduzlar: {user.get('stars', 0)}
• O'yinlar: {user.get('total_spins', 0)}
• G'alabalar: {user.get('wins', 0)}

💬 **Xabar:** Foydalanuvchi admin bilan bog'lanishni xohlaydi
"""
    
    # Barcha adminlarga xabar yuborish
    sent_count = 0
    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                chat_id=admin_id,
                text=user_info,
                reply_markup=get_admin_contact_keyboard(user_id)
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Admin {admin_id} ga xabar yuborishda xato: {e}")
    
    if sent_count > 0:
        await callback.answer(f"✅ Xabar {sent_count} adminga yuborildi!", show_alert=True)
        
        # Foydalanuvchiga tasdiq xabari
        success_text = f"""
✅ **XABAR YUBORILDI!** ✅

📨 Sizning xabaringiz {sent_count} adminga yuborildi.

⏰ **Javob vaqti:** 24 soat ichida

📱 **Eslatma:** Admin siz bilan to'g'ridan-to'g'ri bog'lanadi.

🎰 O'yinga qaytish uchun "🏠 Asosiy Menyu" tugmasini bosing.
"""
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu()
        )
    else:
        await callback.answer("❌ Xabar yuborishda xato!", show_alert=True)
