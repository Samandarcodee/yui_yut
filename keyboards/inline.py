"""
🎰 Slot Game Bot — Inline klaviaturalar (O'zbek tilida)
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu() -> InlineKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎰 O'ynash", callback_data="play_slot"),
        InlineKeyboardButton(text="👤 Profilim", callback_data="profile")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="statistics"),
        InlineKeyboardButton(text="🏆 Top O'yinchilar", callback_data="leaderboard")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Kunlik Bonus", callback_data="daily_bonus"),
        InlineKeyboardButton(text="👥 Referal", callback_data="referral")
    )
    builder.row(
        InlineKeyboardButton(text="🛒 Yulduz Sotib Olish", callback_data="buy_stars"),
        InlineKeyboardButton(text="ℹ️ Yordam", callback_data="help")
    )
    builder.row(
        InlineKeyboardButton(text="📞 Admin Bilan Bog'lanish", callback_data="contact_admin")
    )
    
    return builder.as_markup()


def get_verification_keyboard(answer: int) -> InlineKeyboardMarkup:
    """Tasdiqlash uchun matematik masala klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    # To'g'ri javob va noto'g'ri javoblar bilan tugmalar yaratish
    options = [answer, answer + 1, answer - 1, answer + 2]
    # Joyini tasodifiy qilish
    import random
    random.shuffle(options)
    
    for i in range(0, len(options), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(options):
                option = options[i + j]
                row_buttons.append(
                    InlineKeyboardButton(
                        text=str(option), 
                        callback_data=f"verify_{option}_{answer}"
                    )
                )
        builder.row(*row_buttons)
    
    return builder.as_markup()


def get_play_again_keyboard() -> InlineKeyboardMarkup:
    """Qayta o'ynash klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎰 Qayta O'ynash", callback_data="play_slot"),
        InlineKeyboardButton(text="👤 Profilim", callback_data="profile")
    )
    builder.row(
        InlineKeyboardButton(text="🛒 Yulduz Sotib Olish", callback_data="buy_stars"),
        InlineKeyboardButton(text="📞 Admin Bilan Bog'lanish", callback_data="contact_admin")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Asosiy Menyu", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_buy_stars_keyboard() -> InlineKeyboardMarkup:
    """Yulduz sotib olish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⭐ 1 Yulduz", callback_data="buy_1"),
        InlineKeyboardButton(text="⭐ 5 Yulduz", callback_data="buy_5")
    )
    builder.row(
        InlineKeyboardButton(text="⭐ 10 Yulduz", callback_data="buy_10"),
        InlineKeyboardButton(text="⭐ 25 Yulduz", callback_data="buy_25")
    )
    builder.row(
        InlineKeyboardButton(text="⭐ 50 Yulduz", callback_data="buy_50")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Asosiy Menyuga Qaytish", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_buy_attempts_keyboard() -> InlineKeyboardMarkup:
    """Urinishlar sotib olish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎮 1 Urinish", callback_data="buy_attempt_1"),
        InlineKeyboardButton(text="🎮 5 Urinish", callback_data="buy_attempt_5")
    )
    builder.row(
        InlineKeyboardButton(text="🎮 10 Urinish", callback_data="buy_attempt_10"),
        InlineKeyboardButton(text="🎮 25 Urinish", callback_data="buy_attempt_25")
    )
    builder.row(
        InlineKeyboardButton(text="🎮 50 Urinish", callback_data="buy_attempt_50")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Asosiy Menyuga Qaytish", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_daily_bonus_keyboard(can_claim: bool = True) -> InlineKeyboardMarkup:
    """Kunlik bonus klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    if can_claim:
        builder.row(
            InlineKeyboardButton(text="🎁 Bonusni Olish", callback_data="claim_daily_bonus")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="⏰ Kutish kerak", callback_data="wait_bonus")
        )
    
    builder.row(
        InlineKeyboardButton(text="🏠 Asosiy Menyu", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_referral_keyboard() -> InlineKeyboardMarkup:
    """Referal klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔗 Linkni Ulashish", callback_data="share_referral")
    )
    builder.row(
        InlineKeyboardButton(text="👥 Mening Referallarim", callback_data="my_referrals"),
        InlineKeyboardButton(text="ℹ️ Qanday Ishlaydi", callback_data="referral_info")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Asosiy Menyu", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
        InlineKeyboardButton(text="📈 Statistikalar", callback_data="admin_stats")
    )
    builder.row(
        InlineKeyboardButton(text="📢 Xabar Yuborish", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="🎁 Bonus Berish", callback_data="admin_bonus")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ G'alaba Foizi", callback_data="admin_winrate"),
        InlineKeyboardButton(text="🚫 Bloklash/Ochish", callback_data="admin_ban")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Yopish", callback_data="close_admin")
    )
    
    return builder.as_markup()


def get_admin_menu() -> InlineKeyboardMarkup:
    """Admin asosiy menyu klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")
    )
    builder.row(
        InlineKeyboardButton(text="🎮 O'yin Sozlamalari", callback_data="admin_game_settings"),
        InlineKeyboardButton(text="🔒 Xavfsizlik", callback_data="admin_security")
    )
    builder.row(
        InlineKeyboardButton(text="📢 Xabar Yuborish", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="🎁 Bonus Berish", callback_data="admin_bonus")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Tizim Sozlamalari", callback_data="admin_system"),
        InlineKeyboardButton(text="📈 Monitoring", callback_data="admin_monitoring")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Yopish", callback_data="close_admin")
    )
    
    return builder.as_markup()


def get_back_to_admin_keyboard() -> InlineKeyboardMarkup:
    """Asosiy menyuga qaytish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏠 Asosiy Menyu", callback_data="main_menu")
    )
    return builder.as_markup()


def get_channel_subscription_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """Kanal obunasi klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➡️ Kanalga Qo'shilish", url=channel_url)
    )
    builder.row(
        InlineKeyboardButton(text="✅ Obunani Tekshirish", callback_data="check_subscription")
    )
    
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Profil klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎰 O'ynash", callback_data="play_slot"),
        InlineKeyboardButton(text="🛒 Yulduz Sotib Olish", callback_data="buy_stars")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Kunlik Bonus", callback_data="daily_bonus"),
        InlineKeyboardButton(text="👥 Referal", callback_data="referral")
    )
    builder.row(
        InlineKeyboardButton(text="📞 Admin Bilan Bog'lanish", callback_data="contact_admin")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Asosiy Menyu", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_close_keyboard() -> InlineKeyboardMarkup:
    """Yopish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Yopish", callback_data="close_message")
    )
    return builder.as_markup()


def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Tasdiqlash klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_{action}"),
        InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_action")
    )
    
    return builder.as_markup()


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Yordam klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎰 O'yin Qoidalari", callback_data="game_rules"),
        InlineKeyboardButton(text="💰 G'alaba Jadvali", callback_data="winning_table")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Bonuslar Haqida", callback_data="bonus_info"),
        InlineKeyboardButton(text="❓ FAQ", callback_data="faq")
    )
    builder.row(
        InlineKeyboardButton(text="📞 Admin Bilan Bog'lanish", callback_data="contact_admin")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Asosiy Menyu", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_contact_keyboard() -> InlineKeyboardMarkup:
    """Admin bilan bog'lanish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👤 Admin Bilan Yozish", callback_data="contact_admin_direct"),
        InlineKeyboardButton(text="📢 Kanalga O'tish", callback_data="contact_support_channel")
    )
    builder.row(
        InlineKeyboardButton(text="❓ FAQ", callback_data="faq"),
        InlineKeyboardButton(text="ℹ️ Yordam", callback_data="help")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="contact_admin"),
        InlineKeyboardButton(text="🏠 Asosiy Menyu", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_faq_keyboard() -> InlineKeyboardMarkup:
    """FAQ klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💳 To'lov Muammolari", callback_data="faq_payment_issues"),
        InlineKeyboardButton(text="🎮 O'yin Muammolari", callback_data="faq_game_issues")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Bonus Muammolari", callback_data="faq_bonus_issues"),
        InlineKeyboardButton(text="👤 Hisob Muammolari", callback_data="faq_account_issues")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="contact_admin"),
        InlineKeyboardButton(text="🏠 Asosiy Menyu", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_contact_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin bilan bog'lanish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📨 Adminga Xabar Yuborish", callback_data="send_message_to_admin")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="profile")
    )
    
    return builder.as_markup()


def get_admin_contact_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Admin uchun foydalanuvchi bilan bog'lanish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💬 Foydalanuvchi bilan bog'lanish", callback_data=f"admin_contact_user_{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Bonus berish", callback_data=f"admin_bonus_user_{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Xabarni yopish", callback_data="close_message")
    )
    
    return builder.as_markup()


def get_admin_direct_contact_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Admin uchun to'g'ridan-to'g'ri bog'lanish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💬 Xabar yozish", callback_data=f"admin_write_message_{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_bonus_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Admin uchun bonus berish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⭐ 10 Yulduz", callback_data=f"admin_give_bonus_{user_id}_10"),
        InlineKeyboardButton(text="⭐ 25 Yulduz", callback_data=f"admin_give_bonus_{user_id}_25")
    )
    builder.row(
        InlineKeyboardButton(text="⭐ 50 Yulduz", callback_data=f"admin_give_bonus_{user_id}_50"),
        InlineKeyboardButton(text="⭐ 100 Yulduz", callback_data=f"admin_give_bonus_{user_id}_100")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_menu")
    )
    
    return builder.as_markup()
