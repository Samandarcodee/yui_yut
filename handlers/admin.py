"""
Admin panel handlers
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db.database import Database
from keyboards.inline import get_admin_menu, get_close_keyboard, get_main_menu
from config.settings import ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()
db = Database()


class AdminStates(StatesGroup):
    waiting_broadcast_message = State()
    waiting_bonus_user_id = State()
    waiting_bonus_amount = State()
    waiting_win_rate = State()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Show admin panel"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ Access denied. Admin only.")
        return
    
    admin_text = """
👑 **ADMIN PANEL** 👑

Welcome to the administration panel.
Choose an option from the menu below:

📊 Monitor bot statistics
👥 Manage users and bonuses
📢 Send announcements
⚙️ Configure game settings
"""
    
    await message.answer(
        admin_text,
        reply_markup=get_admin_menu()
    )


@router.callback_query(F.data == "admin_users")
async def show_admin_users(callback: CallbackQuery):
    """Show total users count"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    stats = await db.get_total_stats()
    
    users_text = f"""
👥 **USER STATISTICS** 👥

📊 **Overview:**
• Total Registered Users: {stats.get('total_users', 0)}
• Active Players: {stats.get('total_users', 0)}

🎮 **Activity:**
• Total Game Sessions: {stats.get('total_spins', 0):,}
• Total Wins: {stats.get('total_wins', 0):,}
• Total Losses: {stats.get('total_losses', 0):,}

💰 **Economy:**
• Stars in Circulation: {stats.get('total_stars', 0):,} ⭐

📈 **Performance:**
• Average Spins per User: {(stats.get('total_spins', 0) / max(stats.get('total_users', 1), 1)):.1f}
"""
    
    await callback.message.edit_text(
        users_text,
        reply_markup=get_admin_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def show_admin_stats(callback: CallbackQuery):
    """Show detailed statistics"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    stats = await db.get_total_stats()
    win_probability = await db.get_win_probability()
    
    # Calculate additional metrics
    total_spins = stats.get('total_spins', 0)
    total_wins = stats.get('total_wins', 0)
    total_losses = stats.get('total_losses', 0)
    
    actual_win_rate = (total_wins / max(total_spins, 1)) * 100 if total_spins > 0 else 0
    
    stats_text = f"""
📈 **DETAILED STATISTICS** 📈

🎯 **Game Configuration:**
• Set Win Probability: {win_probability * 100:.1f}%
• Actual Win Rate: {actual_win_rate:.1f}%

🎰 **Game Results:**
• Total Spins: {total_spins:,}
• Wins: {total_wins:,} ({(total_wins/max(total_spins,1)*100):.1f}%)
• Losses: {total_losses:,} ({(total_losses/max(total_spins,1)*100):.1f}%)

💰 **Economy Health:**
• Total Stars Distributed: {stats.get('total_stars', 0):,} ⭐
• Average Stars per User: {(stats.get('total_stars', 0) / max(stats.get('total_users', 1), 1)):.1f}

👥 **User Base:**
• Total Users: {stats.get('total_users', 0)}
• Engagement Rate: {(total_spins / max(stats.get('total_users', 1), 1)):.1f} spins/user
"""
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_admin_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Start broadcast process"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 **BROADCAST MESSAGE**\n\n"
        "Send me the message you want to broadcast to all users.\n\n"
        "⚠️ This will be sent to ALL registered users!",
        reply_markup=get_close_keyboard()
    )
    
    await state.set_state(AdminStates.waiting_broadcast_message)
    await callback.answer()


@router.message(AdminStates.waiting_broadcast_message)
async def process_broadcast(message: Message, state: FSMContext):
    """Process broadcast message"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ Access denied.")
        return
    
    broadcast_text = message.text
    
    # Get all users (you might want to implement this method in Database class)
    # For now, we'll show a confirmation
    await message.answer(
        f"📢 **BROADCAST PREVIEW**\n\n"
        f"Message: {broadcast_text}\n\n"
        f"⚠️ This feature requires additional implementation to get all user IDs.\n"
        f"Would you like to proceed?",
        reply_markup=get_close_keyboard()
    )
    
    await state.clear()


@router.callback_query(F.data == "admin_bonus")
async def admin_bonus(callback: CallbackQuery, state: FSMContext):
    """Start bonus sending process"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🎁 **SEND BONUS**\n\n"
        "Send me the user ID (Telegram ID) you want to send a bonus to.\n\n"
        "Example: 123456789",
        reply_markup=get_close_keyboard()
    )
    
    await state.set_state(AdminStates.waiting_bonus_user_id)
    await callback.answer()


@router.message(AdminStates.waiting_bonus_user_id)
async def process_bonus_user_id(message: Message, state: FSMContext):
    """Process bonus user ID"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ Access denied.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        
        # Check if user exists
        target_user = await db.get_user(target_user_id)
        if not target_user:
            await message.answer(
                "❌ User not found. Please check the user ID.",
                reply_markup=get_close_keyboard()
            )
            await state.clear()
            return
        
        await state.update_data(target_user_id=target_user_id)
        
        await message.answer(
            f"🎁 **BONUS FOR USER {target_user_id}**\n\n"
            f"User: {target_user['username'] or 'Unknown'}\n\n"
            f"How many stars do you want to send?\n"
            f"Example: 100",
            reply_markup=get_close_keyboard()
        )
        
        await state.set_state(AdminStates.waiting_bonus_amount)
        
    except ValueError:
        await message.answer(
            "❌ Invalid user ID. Please send a valid number.",
            reply_markup=get_close_keyboard()
        )


@router.message(AdminStates.waiting_bonus_amount)
async def process_bonus_amount(message: Message, state: FSMContext):
    """Process bonus amount"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ Access denied.")
        return
    
    try:
        bonus_amount = int(message.text.strip())
        
        if bonus_amount <= 0:
            await message.answer(
                "❌ Bonus amount must be positive.",
                reply_markup=get_close_keyboard()
            )
            return
        
        state_data = await state.get_data()
        target_user_id = state_data['target_user_id']
        
        # Send bonus
        success = await db.update_user_balance(target_user_id, bonus_amount, 0)
        
        if success:
            # Record transaction
            await db.add_transaction(target_user_id, "admin_bonus", bonus_amount, 0)
            
            await message.answer(
                f"✅ **BONUS SENT!**\n\n"
                f"Sent {bonus_amount} ⭐ stars to user {target_user_id}",
                reply_markup=get_admin_menu()
            )
            
            logger.info(f"Admin {user_id} sent {bonus_amount} stars to user {target_user_id}")
        else:
            await message.answer(
                "❌ Failed to send bonus. Please try again.",
                reply_markup=get_close_keyboard()
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Invalid amount. Please send a valid number.",
            reply_markup=get_close_keyboard()
        )


@router.callback_query(F.data == "admin_winrate")
async def admin_winrate(callback: CallbackQuery, state: FSMContext):
    """Adjust win rate"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    current_probability = await db.get_win_probability()
    
    await callback.message.edit_text(
        f"⚙️ **ADJUST WIN RATE**\n\n"
        f"Current win probability: {current_probability * 100:.1f}%\n\n"
        f"Send new win probability (0-100):\n"
        f"Example: 70 (for 70%)",
        reply_markup=get_close_keyboard()
    )
    
    await state.set_state(AdminStates.waiting_win_rate)
    await callback.answer()


@router.message(AdminStates.waiting_win_rate)
async def process_win_rate(message: Message, state: FSMContext):
    """Process new win rate"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ Access denied.")
        return
    
    try:
        win_rate = float(message.text.strip())
        
        if not 0 <= win_rate <= 100:
            await message.answer(
                "❌ Win rate must be between 0 and 100.",
                reply_markup=get_close_keyboard()
            )
            return
        
        probability = win_rate / 100
        success = await db.set_win_probability(probability)
        
        if success:
            await message.answer(
                f"✅ **WIN RATE UPDATED!**\n\n"
                f"New win probability: {win_rate}%",
                reply_markup=get_admin_menu()
            )
            
            logger.info(f"Admin {user_id} updated win rate to {win_rate}%")
        else:
            await message.answer(
                "❌ Failed to update win rate.",
                reply_markup=get_close_keyboard()
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Invalid win rate. Please send a valid number.",
            reply_markup=get_close_keyboard()
        )


@router.callback_query(F.data == "close_admin")
async def close_admin(callback: CallbackQuery):
    """Close admin panel"""
    await callback.message.edit_text(
        "👑 Admin panel closed.",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "close_message")
async def close_message(callback: CallbackQuery):
    """Close current message"""
    await callback.message.delete()
    await callback.answer()
