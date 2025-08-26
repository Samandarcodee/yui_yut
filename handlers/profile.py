"""
User profile and statistics handlers
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
    """Show user profile"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Please complete registration first!", show_alert=True)
        return
    
    # Calculate win rate
    win_rate = 0
    if user['total_spins'] > 0:
        win_rate = (user['wins'] / user['total_spins']) * 100
    
    # Format registration date
    reg_date = datetime.fromisoformat(user['reg_date']).strftime("%B %d, %Y")
    
    profile_text = f"""
👤 **YOUR PROFILE** 👤

🆔 **User:** {user['username'] or 'Unknown'}
📅 **Joined:** {reg_date}

💰 **Current Balance:**
⭐ Stars: {user['stars']}
🎮 Attempts: {user['attempts']}

📊 **Game Statistics:**
🏆 Wins: {user['wins']}
😔 Losses: {user['losses']}
🎯 Total Spins: {user['total_spins']}
📈 Win Rate: {win_rate:.1f}%

🎰 Ready to play more? 🎰
"""
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_profile_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "statistics")
async def show_statistics(callback: CallbackQuery):
    """Show global statistics"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Please complete registration first!", show_alert=True)
        return
    
    # Get global stats
    stats = await db.get_total_stats()
    
    # Calculate global win rate
    global_win_rate = 0
    if stats.get('total_spins', 0) > 0:
        global_win_rate = (stats.get('total_wins', 0) / stats.get('total_spins', 0)) * 100
    
    stats_text = f"""
📊 **GLOBAL STATISTICS** 📊

👥 **Community:**
• Total Players: {stats.get('total_users', 0)}
• Total Spins: {stats.get('total_spins', 0):,}

🎯 **Game Results:**
• Total Wins: {stats.get('total_wins', 0):,}
• Total Losses: {stats.get('total_losses', 0):,}
• Global Win Rate: {global_win_rate:.1f}%

💰 **Economy:**
• Stars in Circulation: {stats.get('total_stars', 0):,} ⭐

🎰 Join the fun and climb the leaderboard! 🎰
"""
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "leaderboard")
async def show_leaderboard(callback: CallbackQuery):
    """Show top players leaderboard"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Please complete registration first!", show_alert=True)
        return
    
    # Get leaderboard
    top_players = await db.get_leaderboard(10)
    
    leaderboard_text = "🏆 **TOP PLAYERS** 🏆\n\n"
    
    if not top_players:
        leaderboard_text += "No players yet! Be the first to play! 🎰"
    else:
        for i, player in enumerate(top_players, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            username = player['username'] or 'Anonymous'
            stars = player['stars']
            wins = player['wins']
            total_spins = player['total_spins']
            
            leaderboard_text += f"{medal} **{username}**\n"
            leaderboard_text += f"   ⭐ {stars} stars | 🏆 {wins} wins | 🎮 {total_spins} spins\n\n"
    
    leaderboard_text += "💫 Climb the ranks and become a slot champion! 💫"
    
    await callback.message.edit_text(
        leaderboard_text,
        reply_markup=get_main_menu()
    )
    await callback.answer()
