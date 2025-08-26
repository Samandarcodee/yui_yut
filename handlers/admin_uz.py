"""
👑 Admin panel handlerlari (O'zbek tilida)
"""
import asyncio
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

from db.database import Database
from keyboards.inline import get_admin_menu, get_back_to_admin_keyboard
from config.settings import ADMIN_IDS
from bot.security import security_manager
from bot.logging_config import monitor_performance, log_exception

router = Router()

class AdminStates(StatesGroup):
    """Admin operation states"""
    waiting_for_user_id = State()
    waiting_for_bonus_amount = State()
    waiting_for_ban_reason = State()
    waiting_for_win_probability = State()

@router.callback_query(F.data == "admin_menu")
async def show_admin_menu(callback: CallbackQuery):
    """Show admin menu with enhanced features"""
    try:
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            await callback.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            return
        
        # Get system statistics
        db = Database()
        db_stats = await db.get_database_stats()
        
        # Get security statistics
        security_report = security_manager.get_security_report()
        
        # Get performance statistics
        from bot.logging_config import performance_monitor
        perf_summary = performance_monitor.get_performance_summary() if performance_monitor else {}
        
        message = "🔧 **ADMIN PANELI** 🔧\n\n"
        message += "📊 **Tizim statistikasi:**\n"
        message += f"👥 Jami foydalanuvchilar: {db_stats.get('total_users', 0)}\n"
        message += f"✅ Tasdiqlangan: {db_stats.get('verified_users', 0)}\n"
        message += f"❌ Bloklangan: {db_stats.get('banned_users', 0)}\n"
        message += f"📢 Obuna bo'lgan: {db_stats.get('subscribed_users', 0)}\n"
        message += f"💾 DB hajmi: {db_stats.get('database_size_mb', 0)} MB\n\n"
        
        message += "🛡️ **Xavfsizlik:**\n"
        message += f"🚫 Faol bloklar: {security_report.get('active_blocks', 0)}\n"
        message += f"⚠️ Shubhali faoliyat: {security_report.get('recent_suspicious_activities', 0)}\n\n"
        
        if perf_summary:
            message += "⚡ **Ishlash:**\n"
            for op, stats in list(perf_summary.items())[:3]:  # Show top 3
                message += f"📈 {op}: {stats['avg_ms']}ms (avg)\n"
        
        await callback.message.edit_text(
            message,
            reply_markup=get_admin_menu()
        )
        
    except Exception as e:
        log_exception(logger, "Failed to show admin menu", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "admin_users")
async def show_users_management(callback: CallbackQuery):
    """Show users management options"""
    try:
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            await callback.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            return
        
        message = "👥 **FOYDALANUVCHILARNI BOSHQARISH** 👥\n\n"
        message += "🔍 Foydalanuvchi ma'lumotlarini ko'rish\n"
        message += "🎁 Bonus berish\n"
        message += "🚫 Bloklash/Blokdan chiqarish\n"
        message += "📊 Statistikalarni ko'rish\n"
        message += "✅ Foydalanuvchini tasdiqlash\n\n"
        message += "Kerakli amalni tanlang:"
        
        # Create users management keyboard
        from keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🔍 Foydalanuvchi qidirish", callback_data="search_user"),
            InlineKeyboardButton(text="📊 Barcha foydalanuvchilar", callback_data="all_users")
        )
        builder.row(
            InlineKeyboardButton(text="🎁 Bonus berish", callback_data="give_bonus"),
            InlineKeyboardButton(text="🚫 Bloklash", callback_data="ban_user")
        )
        builder.row(
            InlineKeyboardButton(text="✅ Blokdan chiqarish", callback_data="unban_user"),
            InlineKeyboardButton(text="📈 Statistika", callback_data="user_stats")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_menu")
        )
        
        await callback.message.edit_text(
            message,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        log_exception(logger, "Failed to show users management", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "admin_system")
async def show_system_management(callback: CallbackQuery):
    """Show system management options"""
    try:
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            await callback.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            return
        
        message = "⚙️ **TIZIMNI BOSHQARISH** ⚙️\n\n"
        message += "🎰 O'yin sozlamalari\n"
        message += "📊 Tizim statistikasi\n"
        message += "🧹 Eski ma'lumotlarni tozalash\n"
        message += "🔄 Ma'lumotlar bazasini qayta ishga tushirish\n"
        message += "📝 Log fayllarini ko'rish\n"
        message += "🛡️ Xavfsizlik sozlamalari\n\n"
        message += "Kerakli amalni tanlang:"
        
        # Create system management keyboard
        from keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🎰 O'yin sozlamalari", callback_data="game_settings"),
            InlineKeyboardButton(text="📊 Tizim statistikasi", callback_data="system_stats")
        )
        builder.row(
            InlineKeyboardButton(text="🧹 Tozalash", callback_data="cleanup_data"),
            InlineKeyboardButton(text="🔄 Qayta ishga tushirish", callback_data="restart_db")
        )
        builder.row(
            InlineKeyboardButton(text="📝 Log fayllar", callback_data="view_logs"),
            InlineKeyboardButton(text="🛡️ Xavfsizlik", callback_data="security_settings")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_menu")
        )
        
        await callback.message.edit_text(
            message,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        log_exception(logger, "Failed to show system management", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "game_settings")
async def show_game_settings(callback: CallbackQuery):
    """Show and modify game settings"""
    try:
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            await callback.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            return
        
        db = Database()
        win_prob = await db.get_win_probability()
        
        message = "🎰 **O'YIN SOZLAMALARI** 🎰\n\n"
        message += f"🎯 G'alaba ehtimoli: {win_prob * 100:.1f}%\n"
        message += "💰 Progressive jackpot: 1000 yulduz\n"
        message += "🎁 Kunlik bonus: 5 yulduz\n"
        message += "👥 Referral bonus: 10 yulduz\n\n"
        message += "Sozlamalarni o'zgartirish uchun tugmani bosing:"
        
        # Create game settings keyboard
        from keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🎯 G'alaba ehtimolini o'zgartirish", callback_data="change_win_prob")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_system")
        )
        
        await callback.message.edit_text(
            message,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        log_exception(logger, "Failed to show game settings", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "change_win_prob")
async def change_win_probability(callback: CallbackQuery, state: FSMContext):
    """Change win probability"""
    try:
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            await callback.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            return
        
        await state.set_state(AdminStates.waiting_for_win_probability)
        
        message = "🎯 **G'ALABA EHTIMOLINI O'ZGARTIRISH** 🎯\n\n"
        message += "Yangi g'alaba ehtimolini kiriting (0.1 - 0.9):\n"
        message += "Masalan: 0.7 (70%)\n\n"
        message += "❌ Bekor qilish uchun /cancel"
        
        await callback.message.edit_text(
            message,
            reply_markup=get_back_to_admin_keyboard()
        )
        
    except Exception as e:
        log_exception(logger, "Failed to change win probability", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

@router.message(AdminStates.waiting_for_win_probability)
async def process_win_probability(message: Message, state: FSMContext):
    """Process win probability input"""
    try:
        user_id = message.from_user.id
        if user_id not in ADMIN_IDS:
            return
        
        try:
            new_prob = float(message.text)
            if not 0.1 <= new_prob <= 0.9:
                await message.answer("❌ Ehtimol 0.1 va 0.9 oralig'ida bo'lishi kerak!")
                return
            
            # Update win probability
            db = Database()
            success = await db.set_win_probability(new_prob)
            
            if success:
                await message.answer(
                    f"✅ G'alaba ehtimoli muvaffaqiyatli yangilandi: {new_prob * 100:.1f}%",
                    reply_markup=get_back_to_admin_keyboard()
                )
            else:
                await message.answer("❌ G'alaba ehtimolini yangilashda xato yuz berdi!")
            
            await state.clear()
            
        except ValueError:
            await message.answer("❌ Noto'g'ri format! Iltimos raqam kiriting (masalan: 0.7)")
            
    except Exception as e:
        log_exception(logger, "Failed to process win probability", e)
        await message.answer("❌ Xato yuz berdi!")

@router.callback_query(F.data == "system_stats")
async def show_system_stats(callback: CallbackQuery):
    """Show detailed system statistics"""
    try:
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            await callback.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            return
        
        db = Database()
        db_stats = await db.get_database_stats()
        
        # Get performance summary
        from bot.logging_config import performance_monitor
        perf_summary = performance_monitor.get_performance_summary() if performance_monitor else {}
        
        # Get security summary
        security_summary = security_manager.get_security_report()
        
        message = "📊 **TIZIM STATISTIKASI** 📊\n\n"
        
        message += "🗄️ **Ma'lumotlar bazasi:**\n"
        message += f"👥 Jami foydalanuvchilar: {db_stats.get('total_users', 0)}\n"
        message += f"✅ Tasdiqlangan: {db_stats.get('verified_users', 0)}\n"
        message += f"❌ Bloklangan: {db_stats.get('banned_users', 0)}\n"
        message += f"📢 Obuna bo'lgan: {db_stats.get('subscribed_users', 0)}\n"
        message += f"🎮 Jami o'yinlar: {db_stats.get('total_games', 0)}\n"
        message += f"🏆 Jami g'alabalar: {db_stats.get('total_wins', 0)}\n"
        message += f"💰 O'rtacha yutish: {db_stats.get('avg_stars_won', 0):.1f} yulduz\n"
        message += f"💾 DB hajmi: {db_stats.get('database_size_mb', 0)} MB\n\n"
        
        if perf_summary:
            message += "⚡ **Ishlash statistikasi:**\n"
            for operation, stats in perf_summary.items():
                message += f"📈 {operation}: {stats['avg_ms']}ms (avg), {stats['count']} marta\n"
            message += "\n"
        
        message += "🛡️ **Xavfsizlik:**\n"
        message += f"🚫 Faol bloklar: {security_summary.get('active_blocks', 0)}\n"
        message += f"⚠️ Shubhali faoliyat: {security_summary.get('recent_suspicious_activities', 0)}\n"
        message += f"🔒 Jami bloklangan: {security_summary.get('total_blocked_users', 0)}\n"
        
        await callback.message.edit_text(
            message,
            reply_markup=get_back_to_admin_keyboard()
        )
        
    except Exception as e:
        log_exception(logger, "Failed to show system stats", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "cleanup_data")
async def cleanup_old_data(callback: CallbackQuery):
    """Clean up old data"""
    try:
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            await callback.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            return
        
        await callback.answer("🧹 Tozalash boshlandi...")
        
        db = Database()
        success = await db.cleanup_old_data(days=30)
        
        if success:
            await callback.message.edit_text(
                "✅ Eski ma'lumotlar muvaffaqiyatli tozalandi!\n\n"
                "30 kundan eski ma'lumotlar o'chirildi.",
                reply_markup=get_back_to_admin_keyboard()
            )
        else:
            await callback.message.edit_text(
                "❌ Ma'lumotlarni tozalashda xato yuz berdi!",
                reply_markup=get_back_to_admin_keyboard()
            )
        
    except Exception as e:
        log_exception(logger, "Failed to cleanup data", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "security_settings")
async def show_security_settings(callback: CallbackQuery):
    """Show security settings and statistics"""
    try:
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            await callback.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            return
        
        security_summary = security_manager.get_security_report()
        
        message = "🛡️ **XAVFSIZLIK SOZLAMALARI** 🛡️\n\n"
        message += "📊 **Xavfsizlik statistikasi:**\n"
        message += f"🚫 Faol bloklar: {security_summary.get('active_blocks', 0)}\n"
        message += f"⚠️ Shubhali faoliyat: {security_summary.get('recent_suspicious_activities', 0)}\n"
        message += f"🔒 Jami bloklangan: {security_summary.get('total_blocked_users', 0)}\n"
        message += f"👁️ Kuzatilayotgan: {security_summary.get('total_suspicious_users', 0)}\n\n"
        
        message += "⚙️ **Sozlamalar:**\n"
        message += "🕐 Rate limit: 60 so'rov/daqiqa\n"
        message += "⏰ Bloklash vaqti: 1 soat\n"
        message += "🚨 Shubhali faoliyat chegarasi: 5 ta\n\n"
        
        message += "Kerakli amalni tanlang:"
        
        # Create security settings keyboard
        from keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🚫 Bloklangan foydalanuvchilar", callback_data="blocked_users"),
            InlineKeyboardButton(text="⚠️ Shubhali faoliyat", callback_data="suspicious_activity")
        )
        builder.row(
            InlineKeyboardButton(text="🧹 Xavfsizlik ma'lumotlarini tozalash", callback_data="cleanup_security"),
            InlineKeyboardButton(text="📊 Xavfsizlik hisoboti", callback_data="security_report")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_system")
        )
        
        await callback.message.edit_text(
            message,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        log_exception(logger, "Failed to show security settings", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "blocked_users")
async def show_blocked_users(callback: CallbackQuery):
    """Show list of blocked users"""
    try:
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            await callback.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            return
        
        blocked_users = []
        for uid, block_info in security_manager.blocked_users.items():
            remaining_time = max(0, block_info['expires_at'] - time.time())
            blocked_users.append({
                'user_id': uid,
                'reason': block_info['reason'],
                'remaining_time': remaining_time
            })
        
        if not blocked_users:
            message = "✅ **Bloklangan foydalanuvchilar yo'q** ✅\n\n"
            message += "Barcha foydalanuvchilar faol holatda."
        else:
            message = "🚫 **BLOKLANGAN FOYDALANUVCHILAR** 🚫\n\n"
            for user in blocked_users[:10]:  # Show first 10
                minutes = int(user['remaining_time'] / 60)
                message += f"👤 ID: {user['user_id']}\n"
                message += f"📝 Sababi: {user['reason']}\n"
                message += f"⏰ Qolgan vaqt: {minutes} daqiqa\n\n"
            
            if len(blocked_users) > 10:
                message += f"... va yana {len(blocked_users) - 10} ta foydalanuvchi\n\n"
        
        await callback.message.edit_text(
            message,
            reply_markup=get_back_to_admin_keyboard()
        )
        
    except Exception as e:
        log_exception(logger, "Failed to show blocked users", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data.startswith("admin_contact_user_"))
async def admin_contact_user(callback: CallbackQuery):
    """Admin foydalanuvchi bilan bog'lanish"""
    admin_id = callback.from_user.id
    
    # Admin huquqini tekshirish
    if admin_id not in ADMIN_IDS:
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return
    
    # Foydalanuvchi ID sini olish
    user_id = int(callback.data.split("_")[-1])
    
    # Foydalanuvchi ma'lumotlarini olish
    user = await db.get_user(user_id)
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
        return
    
    # Admin uchun foydalanuvchi bilan bog'lanish xabari
    contact_text = f"""
💬 **Foydalanuvchi bilan bog'lanish**

👤 **Foydalanuvchi ma'lumotlari:**
• ID: `{user_id}`
• Username: @{user.get('username', 'Yo\'q')}
• Ism: {user.get('first_name', 'Noma\'lum')}
• Ro'yxatdan o'tgan: {user.get('reg_date', 'Noma\'lum')}

📊 **Statistika:**
• Yulduzlar: {user.get('stars', 0)}
• O'yinlar: {user.get('total_spins', 0)}
• G'alabalar: {user.get('wins', 0)}

💡 **Maslahat:** Foydalanuvchi bilan to'g'ridan-to'g'ri xabar yozing.
"""
    
    await callback.message.edit_text(
        contact_text,
        reply_markup=get_admin_direct_contact_keyboard(user_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_bonus_user_"))
async def admin_bonus_user(callback: CallbackQuery):
    """Admin foydalanuvchiga bonus berish"""
    admin_id = callback.from_user.id
    
    # Admin huquqini tekshirish
    if admin_id not in ADMIN_IDS:
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return
    
    # Foydalanuvchi ID sini olish
    user_id = int(callback.data.split("_")[-1])
    
    # Foydalanuvchi ma'lumotlarini olish
    user = await db.get_user(user_id)
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
        return
    
    # Admin uchun bonus berish xabari
    bonus_text = f"""
🎁 **Foydalanuvchiga bonus berish**

👤 **Foydalanuvchi ma'lumotlari:**
• ID: `{user_id}`
• Username: @{user.get('username', 'Yo\'q')}
• Ism: {user.get('first_name', 'Noma\'lum')}
• Joriy yulduzlar: {user.get('stars', 0)}

💡 **Maslahat:** Foydalanuvchiga qancha yulduz berishni tanlang.
"""
    
    await callback.message.edit_text(
        bonus_text,
        reply_markup=get_admin_bonus_keyboard(user_id)
    )
    await callback.answer()

# Add more admin functions as needed...

@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    """Go back to admin menu"""
    try:
        await show_admin_menu(callback)
    except Exception as e:
        log_exception(logger, "Failed to go back to admin", e)
        await callback.answer("❌ Xato yuz berdi", show_alert=True)

# Import logger at the end to avoid circular imports
import logging
logger = logging.getLogger(__name__)
