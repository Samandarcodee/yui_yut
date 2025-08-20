from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎰 O'ynash"),
                KeyboardButton(text="👤 Profil"),
                KeyboardButton(text="🏆 Reyting"),
                KeyboardButton(text="🎁 Referral"),
            ],
            [
                KeyboardButton(text="⭐ Sotib olish"),
                KeyboardButton(text="💸 Chiqarish"),
                KeyboardButton(text="📆 Bonus"),
                KeyboardButton(text="❓ Yordam"),
            ],
        ],
        resize_keyboard=True,
    )


def donation_options(channel_username: str | None) -> InlineKeyboardMarkup:
    # Kengaytirilgan Stars paketlari
    amounts = [5, 10, 25, 50, 100, 250, 500]
    rows: list[list[InlineKeyboardButton]] = []
    
    # Group in rows of 3
    for i in range(0, len(amounts), 3):
        row = [InlineKeyboardButton(text=f"{a} ⭐", callback_data=f"donate:{a}") for a in amounts[i:i+3]]
        rows.append(row)
    
    # Special offers
    rows.append([
        InlineKeyboardButton(text="🎁 Starter (10⭐+2 bonus)", callback_data="donate:starter"),
        InlineKeyboardButton(text="🔥 Mega (100⭐+20 bonus)", callback_data="donate:mega")
    ])
    
    if channel_username:
        rows.append([InlineKeyboardButton(text="📢 Kanal", url=f"https://t.me/{channel_username.lstrip('@')}")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def play_again_menu(last_win: int | None = None) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="▶️ Yana o'ynash", callback_data="play_again")],
    ]
    if last_win and last_win > 0:
        buttons.insert(0, [InlineKeyboardButton(text="🎲 Yutishni xavfga qo'yish (x2)", callback_data=f"gamble:{last_win}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Home menu olib tashlandi - barcha funksiyalar asosiy menyuda

def channel_subscription_menu(channel_username: str) -> InlineKeyboardMarkup:
    """Kanal a'zoligi tekshirish menyusi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=f"https://t.me/{channel_username.lstrip('@')}")],
            [InlineKeyboardButton(text="✅ A'zolikni tekshirish", callback_data="check_subscription")],
        ]
    )


def withdraw_options(user_balance: int) -> InlineKeyboardMarkup:
    # Dynamic options based on balance
    options = []
    for amount in [50, 100, 200, 500]:
        if amount <= user_balance:
            options.append(InlineKeyboardButton(text=f"{amount} ⭐", callback_data=f"withdraw:{amount}"))
    
    rows: list[list[InlineKeyboardButton]] = []
    # Group in rows of 2
    for i in range(0, len(options), 2):
        rows.append(options[i:i+2])
    
    # Always add Max and Cancel
    rows.append([
        InlineKeyboardButton(text="🔥 Max", callback_data="withdraw:max"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="withdraw:cancel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


