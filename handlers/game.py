"""
Game handlers for slot machine
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from db.database import Database
from bot.game_logic import slot_game
from keyboards.inline import get_play_again_keyboard, get_main_menu, get_buy_attempts_keyboard

logger = logging.getLogger(__name__)
router = Router()
db = Database()


@router.callback_query(F.data == "play_slot")
async def play_slot_game(callback: CallbackQuery):
    """Handle slot game play"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Please complete registration first!", show_alert=True)
        return
    
    # Check if user has attempts
    if user['attempts'] <= 0:
        await callback.message.edit_text(
            "😔 **No Attempts Left!**\n\n"
            "You need to buy attempts with Telegram Stars to play.\n\n"
            "💫 1 Star = 1 Attempt 💫",
            reply_markup=get_buy_attempts_keyboard()
        )
        await callback.answer()
        return
    
    # Get current win probability
    win_probability = await db.get_win_probability()
    
    # Play the game
    reels, is_winner, stars_won = slot_game.play_round(win_probability)
    
    # Record the result
    await db.record_spin_result(user_id, is_winner, stars_won)
    
    # Format result message
    result_message = slot_game.format_reels_message(reels, is_winner, stars_won)
    
    # Add current stats
    updated_user = await db.get_user(user_id)
    stats_text = f"\n💰 **Your Stats:**\n"
    stats_text += f"⭐ Stars: {updated_user['stars']}\n"
    stats_text += f"🎮 Attempts left: {updated_user['attempts']}\n"
    stats_text += f"🏆 Wins: {updated_user['wins']}\n"
    stats_text += f"📊 Total spins: {updated_user['total_spins']}"
    
    full_message = result_message + stats_text
    
    await callback.message.edit_text(
        full_message,
        reply_markup=get_play_again_keyboard()
    )
    
    # Log the game result
    logger.info(f"User {user_id} played slot: {'won' if is_winner else 'lost'}, "
                f"stars: {stars_won}, attempts left: {updated_user['attempts']}")
    
    await callback.answer()


@router.callback_query(F.data == "bonuses")
async def show_bonuses(callback: CallbackQuery):
    """Show bonuses information"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Please complete registration first!", show_alert=True)
        return
    
    bonuses_text = """
🎁 **BONUSES & INFO** 🎁

💫 **How to Get Free Stars:**
• Complete daily challenges
• Refer friends to the bot
• Special events and promotions
• Admin rewards for active players

🎰 **Game Information:**
""" + slot_game.get_combination_info() + """

📞 **Contact Admin:**
Message the bot admin for bonuses and support!

🍀 Good luck and have fun! 🍀
"""
    
    await callback.message.edit_text(
        bonuses_text,
        reply_markup=get_main_menu()
    )
    await callback.answer()
