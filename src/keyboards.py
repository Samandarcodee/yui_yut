from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎰 O'ynash"),
                KeyboardButton(text="👤 Profil"),
                KeyboardButton(text="🏆 TOP"),
            ],
            [
                KeyboardButton(text="📆 Kunlik bonus"),
                KeyboardButton(text="⭐ Stars hisobim"),
                KeyboardButton(text="🎁 Referral"),
            ],
            [
                KeyboardButton(text="📜 Qoidalar"),
                KeyboardButton(text="⭐ Yulduz olish"),
                KeyboardButton(text="📈 Tarix"),
            ],
            [
                KeyboardButton(text="❓ Yordam"),
            ],
        ],
        resize_keyboard=True,
    )


def donation_options(channel_username: str | None) -> InlineKeyboardMarkup:
    # Zamonaviy ko'rinish: bir qatorga bir nechta tugmalar
    amounts = (1, 20, 30, 50)
    row: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=f"{a} ⭐", callback_data=f"donate:{a}") for a in amounts
    ]

    rows: list[list[InlineKeyboardButton]] = [row]
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


