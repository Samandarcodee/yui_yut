"""
🎰 O'yin handlerlari (O'zbek tilida)
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from db.database import Database
from bot.game_logic import slot_game
from keyboards.inline import get_play_again_keyboard, get_main_menu, get_buy_stars_keyboard

logger = logging.getLogger(__name__)
router = Router()
db = Database()


@router.callback_query(F.data == "play_slot")
async def play_slot_game(callback: CallbackQuery):
    """Slot o'yinini o'ynash"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Iltimos avval ro'yxatdan o'ting!", show_alert=True)
        return
    
    if user.get('is_banned'):
        await callback.answer("❌ Siz bloklangansiz!", show_alert=True)
        return
    
    # STRICT CHANNEL SUBSCRIPTION CHECK - Only subscribers can play
    if not user.get('channel_subscribed', False):
        from config.settings import CHANNEL_SUBSCRIPTION_REQUIRED, CHANNEL_URL
        from keyboards.inline import get_channel_subscription_keyboard
        
        await callback.message.edit_text(
            CHANNEL_SUBSCRIPTION_REQUIRED.format(channel_url=CHANNEL_URL),
            reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
        )
        await callback.answer("⚠️ O'ynash uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    # Urinishlar mavjudligini tekshirish
    if user['attempts'] <= 0:
        await callback.message.edit_text(
            "😔 **Urinishlar tugadi!**\n\n"
            "O'ynash uchun Telegram Stars bilan urinishlar sotib oling.\n\n"
            "💫 1 Yulduz = 1 Urinish 💫",
            reply_markup=get_buy_stars_keyboard()
        )
        await callback.answer()
        return
    
    # Joriy g'alaba ehtimolini olish
    win_probability = await db.get_win_probability()
    
    # O'yinni o'ynash - yangilangan algoritm bilan
    reels, is_winner, stars_won, extra_info = slot_game.play_round(
        win_probability, 
        user.get('total_spins', 0),
        user.get('daily_streak', 0)
    )
    
    # Natijani qayd qilish
    symbols_str = "".join(reels)
    await db.record_game_result(user_id, symbols_str, is_winner, stars_won)
    
    # Natija xabarini formatlash - yangilangan
    result_message = slot_game.format_reels_message(reels, is_winner, stars_won, extra_info)
    
    # Joriy statistikalarni qo'shish
    updated_user = await db.get_user(user_id)
    stats_text = f"\n💰 **Sizning statistikangiz:**\n"
    stats_text += f"⭐ Yulduzlar: {updated_user['stars']}\n"
    stats_text += f"🎮 Qolgan urinishlar: {updated_user['attempts']}\n"
    stats_text += f"🏆 G'alabalar: {updated_user['wins']}\n"
    stats_text += f"📊 Jami o'yinlar: {updated_user['total_spins']}"
    
    if updated_user['biggest_win'] > 0:
        stats_text += f"\n💎 Eng katta g'alaba: {updated_user['biggest_win']} yulduz"
    
    full_message = result_message + stats_text
    
    # Katta g'alaba bo'lsa maxsus xabar
    if is_winner and stars_won >= 50:
        await callback.answer("🎆 AJOYIB! KATTA G'ALABA! 🎆", show_alert=True)
    
    await callback.message.edit_text(
        full_message,
        reply_markup=get_play_again_keyboard()
    )
    
    # Log yozish
    logger.info(f"Foydalanuvchi {user_id} o'ynadi: {'yutdi' if is_winner else 'yutqazdi'}, "
                f"yulduzlar: {stars_won}, qolgan urinishlar: {updated_user['attempts']}")
    
    await callback.answer()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Yordam ma'lumotlarini ko'rsatish"""
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
        await callback.answer("⚠️ Yordam ko'rish uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    from config.settings import HELP_MESSAGE
    
    await callback.message.edit_text(
        HELP_MESSAGE,
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "game_rules")
async def show_game_rules(callback: CallbackQuery):
    """O'yin qoidalarini ko'rsatish"""
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
        await callback.answer("⚠️ O'yin qoidalarini ko'rish uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    rules_text = """
🎰 **O'YIN QOIDALARI** 🎰

📋 **Asosiy qoidalar:**
• Har bir o'yin uchun 1 yulduz (1 urinish) kerak
• 3 ta belgi tasodifiy ravishda tanlanadi
• Bir xil belgilar uchun mukofot olasiz

🎯 **Qanday o'ynash:**
1. "🎰 O'ynash" tugmasini bosing
2. Natijani kuting
3. G'alaba qilsangiz yulduzlar qo'shiladi
4. Yana o'ynash uchun urinishingiz bo'lishi kerak

💡 **Maslahatlar:**
• Kunlik bonusni unutmang (24 soatda bir marta)
• Do'stlaringizni taklif qiling - ikkalangiz ham bonus olasiz
• Katta mukofotlar uchun ko'proq o'ynang

🍀 Omad tilaymiz! 🍀
"""
    
    await callback.message.edit_text(
        rules_text,
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "winning_table")
async def show_winning_table(callback: CallbackQuery):
    """G'alaba jadvalini ko'rsatish"""
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
        await callback.answer("⚠️ G'alaba jadvalini ko'rish uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    await callback.message.edit_text(
        slot_game.get_combination_info(),
        reply_markup=get_main_menu()
    )
    await callback.answer()
