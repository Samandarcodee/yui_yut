"""Bot handlers with comprehensive security and error handling."""

import logging
import re
from typing import Awaitable, Callable, Optional

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

logger = logging.getLogger(__name__)

from aiogram.filters import CommandObject

from . import db
from .config import get_settings
from .keyboards import channel_subscription_menu, donation_options, main_menu, play_again_menu, withdraw_options
from .monitoring import log_error, log_payment, log_spin_result, metrics
from .slot import spin

# Define router/settings BEFORE any handlers use it
router = Router()
settings = get_settings()


def _sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""

    # Remove HTML tags and limit length
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip()[:max_length]

    # Remove potential script injections
    dangerous_patterns = [
        r"javascript:",
        r"data:",
        r"vbscript:",
        r"on\w+\s*=",
    ]
    for pattern in dangerous_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text


@router.message(Command("ask"))
async def cmd_ask(message: Message, command: CommandObject) -> None:
    """Secure user question handler with input sanitization."""
    if not message.from_user:
        return

    text = _sanitize_text(command.args or "", max_length=500)
    if not text:
        await message.answer("❓ <b>Savol yuborish:</b>\n\n/ask sizning savol matningiz")
        return

    if len(settings.admin_ids) == 0:
        await message.answer("❌ Admin mavjud emas.")
        return

    # Log the question for monitoring
    logger.info(f"User question from {message.from_user.id}: {text[:50]}...")

    # Send to admins with rate limiting info
    success_count = 0
    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_message(
                admin_id,
                f"❓ <b>Foydalanuvchi savoli</b>\n\n"
                f"👤 User: {message.from_user.id}\n"
                f"📝 Savol: {text}\n\n"
                f"💬 Javob: /reply {message.from_user.id} javob_matni",
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send question to admin {admin_id}: {e}")

    if success_count > 0:
        await message.answer("✅ <b>Savolingiz yuborildi!</b>\n\n⏳ Admin tez orada javob beradi.")
    else:
        await message.answer("❌ Xatolik yuz berdi. Keyinroq urinib ko'ring.")


@router.message(Command("reply"))
async def cmd_reply(message: Message, command: CommandObject) -> None:
    """Secure admin reply handler with validation."""
    if not message.from_user or message.from_user.id not in settings.admin_ids:
        return

    args = _sanitize_text(command.args or "", max_length=1000)
    if not args or " " not in args:
        await message.answer("📝 <b>Javob yuborish:</b>\n\n/reply user_id javob_matni")
        return

    parts = args.split(" ", 1)
    to_id_str, reply_text = parts[0], parts[1]

    # Validate user_id
    try:
        to_id = int(to_id_str)
        if to_id <= 0:
            raise ValueError("Invalid user ID")
    except ValueError:
        await message.answer("❌ Noto'g'ri user_id")
        return

    # Sanitize reply text
    reply_text = _sanitize_text(reply_text, max_length=1000)
    if not reply_text:
        await message.answer("❌ Bo'sh javob yuborib bo'lmaydi")
        return

    try:
        await message.bot.send_message(to_id, f"💬 <b>Admin javobi:</b>\n\n{reply_text}")
        await message.answer("✅ Javob yuborildi.")
        logger.info(f"Admin {message.from_user.id} replied to user {to_id}")
    except Exception as e:
        await message.answer("❌ Yuborib bo'lmadi (user botni bloklagan bo'lishi mumkin)")
        logger.error(f"Failed to send reply to user {to_id}: {e}")


def _parse_utm(arg: str) -> tuple[Optional[str], Optional[str]]:
    try:
        qs = arg.split("?", 1)[1]
        params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
    except Exception:
        params = {}
    return params.get("src"), params.get("cmp") or params.get("campaign")


def _extract_ref_with_utm(text: Optional[str]) -> tuple[Optional[int], Optional[str], Optional[str]]:
    # Format: /start or /start ref_123[?src=...&cmp=...]
    if not text:
        return None, None, None
    parts = text.split()
    if len(parts) < 2:
        return None, None, None
    arg = parts[1]
    if arg.startswith("ref_"):
        try:
            base = arg.split("?", 1)[0]
            ref_id = int(base[4:])
            src, cmp_ = _parse_utm(arg)
            return ref_id, src, cmp_
        except ValueError:
            return None, None, None
    return None, None, None


async def _check_channel_subscription(bot, user_id: int, channel_username: str) -> bool:
    """Foydalanuvchining kanalga a'zoligini tekshirish.
    Xatoliklarda qat'iy ravishda False qaytaramiz (tekshiruv majburiy)."""
    try:
        member = await bot.get_chat_member(chat_id=f"@{channel_username.lstrip('@')}", user_id=user_id)
        return getattr(member, "status", "") in {"member", "administrator", "creator"}
    except Exception:
        # Bot kanalga qo'shilmagan yoki admin emas — tekshiruvdan o'tkazmaymiz
        return False


async def _spin_flow(
    user_id: int, reply: Callable[..., Awaitable[None]], edit_message: Optional[Message] = None
) -> None:
    """Optimallashtirilgan o'yin oqimi - tez va sodda"""
    # 1. User tekshirish va yaratish
    data = await db.get_user(user_id)
    if not data:
        await db.upsert_user(
            user_id=user_id, username=None, first_name=None, last_name=None, initial_spins=settings.initial_spins
        )
        data = await db.get_user(user_id)
        if not data:
            await reply("❌ Xatolik. Qayta urinib ko'ring.")
            return

    # 2. Ruxsat tekshirish
    is_admin = _is_admin(user_id) or bool(data.get("free_play"))
    if data.get("is_banned"):
        await reply("🚫 Bloklangansiz.")
        return

    # 3. Spin mavjudligini tekshirish
    current_spins = data["spins"]
    current_stars = data.get("stars", 0)

    if not is_admin and current_spins <= 0:
        if current_stars > 0:
            # 1⭐ → 1 spin avtomatik
            await db.add_stars(user_id, -1)
            await db.add_spins(user_id, 1)
            current_spins = 1
            current_stars -= 1
        else:
            msg = "🎰 <b>Spinlar tugadi!</b>\n\n⭐ Yangi spinlar sotib oling:"
            markup = donation_options(settings.channel_username)
            if edit_message:
                await edit_message.edit_text(msg, reply_markup=markup)
            else:
                await reply(msg, reply_markup=markup)
            return

    # 4. Spin sarflash (admin emas bo'lsa)
    if not is_admin:
        await db.add_spins(user_id, -1)
        current_spins -= 1

    # 5. O'yin o'tkazish
    result = spin(with_house_edge=True)

    # 6. Yutuqni qo'llash
    stars_won = 0
    spins_won = 0
    if result.is_win:
        stars_won = result.payout
        await db.add_stars(user_id, stars_won)
        await db.set_biggest_win_if_greater(user_id, stars_won)

        # Yutganda qo'shimcha spin
        if settings.win_adds_spins and not is_admin:
            spins_won = stars_won
            await db.add_spins(user_id, spins_won)
            current_spins += spins_won

    # 7. Logga yozish va monitoring
    await db.record_spin(user_id, result.reels, result.payout, result.is_win)
    log_spin_result(result.is_win)

    # 8. Chiroyli natija xabari
    reels_text = f"{result.reels[0]} {result.reels[1]} {result.reels[2]}"
    if result.is_win:
        # Yutuq darajasiga qarab emoji
        if stars_won >= 50:
            celebration = "🎆🎊🎆"
            win_emoji = "💎"
        elif stars_won >= 10:
            celebration = "🎉✨🎉"
            win_emoji = "🏆"
        else:
            celebration = "🎉"
            win_emoji = "⭐"

        bonus_text = f"\n🎁 <b>+{spins_won} bonus spin!</b>" if spins_won > 0 else ""
        text = (
            f"{celebration}\n"
            f"🎰 <code>[ {reels_text} ]</code>\n\n"
            f"{win_emoji} <b>YUTUQ: {stars_won} ⭐</b>{bonus_text}\n\n"
            f"🎮 Qolgan spinlar: <b>{current_spins}</b>"
        )
    else:
        text = (
            f"🎰 <code>[ {reels_text} ]</code>\n\n"
            f"💔 <b>Yutqazdingiz</b>\n"
            f"🎮 Qolgan spinlar: <b>{current_spins}</b>\n\n"
            f"🍀 Keyingi urinishda omad!"
        )

    # 9. Javob yuborish
    markup = play_again_menu()
    if edit_message:
        try:
            await edit_message.edit_text(text, reply_markup=markup)
        except TelegramBadRequest:
            await reply(text, reply_markup=markup)
    else:
        await reply(text, reply_markup=markup)


async def _profile_flow(user_id: int, reply: Callable[..., Awaitable[None]]) -> None:
    data = await db.get_user_with_stats(user_id)
    if not data:
        # Avtomatik ro'yxatga olish
        await db.upsert_user(
            user_id=user_id, username=None, first_name=None, last_name=None, initial_spins=settings.initial_spins
        )
        data = await db.get_user_with_stats(user_id)
        if not data:  # Bu holat bo'lmasligi kerak
            await reply("Xatolik yuz berdi. Iltimos qayta urinib ko'ring.")
            return
    invited = await db.count_invited(user_id)
    text = (
        f"👤 ID: {user_id}\n"
        f"⭐ Yulduzlar: {data['stars']}\n"
        f"🎰 Urinishlar: {data['spins']}\n"
        f"🏆 Eng katta yutuq: {data['biggest_win']}\n"
        f"🧮 Jami spinlar: {data.get('total_spins') or 0}\n"
        f"🥇 Jami yutuqlar (⭐): {data.get('total_stars_won') or 0}\n"
        f"👥 Taklif qilingan do‘stlar: {invited}"
    )
    await reply(text)


async def _daily_flow(user_id: int, reply: Callable[..., Awaitable[None]]) -> None:
    from datetime import datetime

    today = datetime.utcnow().strftime("%Y-%m-%d")
    # ensure user exists
    if not await db.get_user(user_id):
        await db.upsert_user(
            user_id=user_id, username=None, first_name=None, last_name=None, initial_spins=settings.initial_spins
        )
    if await db.can_claim_daily_bonus(user_id, today):
        await db.add_spins(user_id, settings.daily_bonus_spins)
        await db.set_daily_claimed(user_id, today)
        await reply(f"Kunlik bonus: +{settings.daily_bonus_spins} spin berildi! 🎁")
    else:
        await reply("Bugun allaqachon bonus olgansiz. Ertaga qaytib keling!")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    user = message.from_user
    assert user is not None

    # Debug ma'lumotlari
    print(f"DEBUG: User ID: {user.id}")
    print(f"DEBUG: Mandatory channel: {settings.mandatory_channel}")
    print(f"DEBUG: Is admin: {_is_admin(user.id)}")
    print(f"DEBUG: Admin IDs: {settings.admin_ids}")

    # Majburiy kanal a'zoligini tekshirish
    if settings.mandatory_channel and not _is_admin(user.id):
        print(f"DEBUG: Checking subscription for channel: {settings.mandatory_channel}")
        is_subscribed = await _check_channel_subscription(message.bot, user.id, settings.mandatory_channel)
        print(f"DEBUG: Is subscribed: {is_subscribed}")
        if not is_subscribed:
            await message.answer(
                "🔒 <b>Botdan foydalanish uchun avval kanalga a'zo bo'ling!</b>\n\n"
                "📢 Quyidagi kanalga a'zo bo'ling va keyin \"✅ A'zolikni tekshirish\" tugmasini bosing:",
                reply_markup=channel_subscription_menu(settings.mandatory_channel),
            )
            return

    referrer_id, utm_src, utm_cmp = _extract_ref_with_utm(message.text)
    # If user exists already, keep their original referred_by
    existing = await db.get_user(user.id)
    referred_by = existing.get("referred_by") if existing else referrer_id
    await db.upsert_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        referred_by=referred_by,
        initial_spins=settings.initial_spins if existing is None else 0,  # Faqat yangi userlar uchun
    )
    # Save UTM tags
    await db.update_user_utm(user.id, utm_src, utm_cmp)

    # Apply referral on first join
    if referrer_id and (existing is None) and referrer_id != user.id:
        await db.increment_referrer_stars(referrer_id, settings.referral_bonus)
        # Level-2
        ref1 = await db.get_user(referrer_id)
        if ref1 and ref1.get("referred_by") and int(ref1["referred_by"]) != user.id:
            from math import floor

            await db.increment_level2_referrer_stars(
                int(ref1["referred_by"]), max(1, floor(settings.referral_bonus / 2))
            )

    # Faqat reply keyboard menyu ko'rsatish
    await message.answer(
        f"✨🎰✨ <b>STARS YUT</b> ✨🎰✨\n\n"
        f"🎊 <b>Slot o'yiniga xush kelibsiz!</b>\n\n"
        f"🎁 <b>{settings.initial_spins} BEPUL SPIN</b> bilan start!\n"
        f"📅 Har kuni <b>BONUS</b> oling\n"
        f"🍀 <b>70% YUTISH IMKONIYATI!</b>\n\n"
        f"⬇️ <b>Menyudan tanlang:</b>",
        reply_markup=main_menu(),
    )


async def _ensure_access(user_id: int, bot, reply: Callable[..., Awaitable[None]]) -> bool:
    """Majburiy kanalga a'zolikni umumiy tekshiruvchi yordamchi."""
    if settings.mandatory_channel and not _is_admin(user_id):
        is_subscribed = await _check_channel_subscription(bot, user_id, settings.mandatory_channel)
        if not is_subscribed:
            await reply(
                "🔒 Iltimos, avval kanalga a'zo bo'ling, so'ngra qayta urinib ko'ring.",
                reply_markup=channel_subscription_menu(settings.mandatory_channel),
            )
            return False
    return True


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "❓ <b>Yordam bo'limi</b>\n\n"
        "🎰 <b>O'ynash</b> — slot aylantirib yulduz yuting\n"
        "👤 <b>Profil</b> — balans va statistikangiz\n"
        "🏆 <b>Reyting</b> — eng yaxshi o'yinchilar\n"
        "🎁 <b>Referral</b> — do'stlarni taklif qiling\n\n"
        "⭐ <b>Sotib olish</b> — yangi spinlar\n"
        "💸 <b>Chiqarish</b> — yulduzlarni naqd qiling\n"
        "📆 <b>Bonus</b> — kunlik bepul spin\n\n"
        "💬 <b>Savol:</b> /ask matn\n"
        "📞 <b>Admin:</b> @STARS_YUTT_ADMIN"
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    user = message.from_user
    assert user is not None
    data = await db.get_user_with_stats(user.id)
    if not data:
        await message.answer("Avval /start bosing.")
        return
    invited = await db.count_invited(user.id)
    total_spins = data.get("total_spins") or 0
    total_won = data.get("total_stars_won") or 0
    win_rate = (total_won / total_spins * 100) if total_spins > 0 else 0

    await message.answer(
        f"👤 <b>{user.full_name}</b>\n\n"
        f"💰 <b>Balans:</b>\n"
        f"⭐ Yulduzlar: <b>{data['stars']}</b>\n"
        f"🎰 Spinlar: <b>{data['spins']}</b>\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"🎮 Jami o'yinlar: <b>{total_spins}</b>\n"
        f"🏆 Eng katta yutuq: <b>{data['biggest_win']} ⭐</b>\n"
        f"🥇 Jami yutuq: <b>{total_won} ⭐</b>\n"
        f"📈 Yutish foizi: <b>{win_rate:.1f}%</b>\n\n"
        f"👥 <b>Referral:</b> {invited} do'st"
    )


@router.message(Command("top"))
async def cmd_top(message: Message) -> None:
    players = await db.get_top_by_stars(10)
    if not players:
        await message.answer("Hali reyting bo‘sh.")
        return
    lines = ["🏆 Eng yaxshi o‘yinchilar (yulduzlar):"]
    for idx, p in enumerate(players, start=1):
        uname = p.get("username") or str(p["user_id"])
        lines.append(f"{idx}. @{uname} — ⭐ {p['stars']}")
    await message.answer("\n".join(lines))


@router.message(Command("referral"))
async def cmd_referral(message: Message) -> None:
    user = message.from_user
    assert user is not None
    me = await message.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{user.id}?src=telegram&cmp=share"
    invited = await db.count_invited(user.id)

    # Calculate total referral earnings
    data = await db.get_user_with_stats(user.id)
    referral_earnings = 0
    if data:
        # Simple estimate: invited * bonus (could be more accurate with payments table)
        referral_earnings = invited * settings.referral_bonus

    await message.answer(
        f"🎁✨ <b>REFERRAL DASTURI</b> ✨🎁\n\n"
        f"🔗 <b>Sizning maxsus havolangiz:</b>\n"
        f"<code>{link}</code>\n\n"
        f"💰 <b>MUKOFOTLAR:</b>\n"
        f"🥇 1-daraja: <b>+{settings.referral_bonus} ⭐</b>\n"
        f"🥈 2-daraja: <b>+{max(1, settings.referral_bonus // 2)} ⭐</b>\n\n"
        f"📊 <b>SIZNING NATIJALARI:</b>\n"
        f"👥 Taklif qilganlar: <b>{invited}</b>\n"
        f"💎 Jami daromad: <b>{referral_earnings} ⭐</b>\n\n"
        f"🚀 <b>Do'stlaringizga ulashing!</b>"
    )


@router.message(Command("spin"))
async def cmd_spin(message: Message) -> None:
    user = message.from_user
    assert user is not None
    # Access check
    ok = await _ensure_access(user.id, message.bot, message.answer)
    if not ok:
        return
    await _spin_flow(user.id, message.answer)


# Simplified button handlers
@router.message(F.text == "🎰 O'ynash")
async def btn_play(message: Message) -> None:
    ok = await _ensure_access(message.from_user.id, message.bot, message.answer)  # type: ignore[arg-type]
    if not ok:
        return
    await cmd_spin(message)


@router.message(F.text == "👤 Profil")
async def btn_profile(message: Message) -> None:
    await cmd_profile(message)


@router.message(F.text == "🏆 Reyting")
async def btn_top(message: Message) -> None:
    await cmd_top(message)


@router.message(F.text == "🎁 Referral")
async def btn_referral(message: Message) -> None:
    await cmd_referral(message)


@router.message(F.text == "⭐ Sotib olish")
async def btn_buy_stars(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if _is_admin(user.id):
        await message.answer("🔧 <b>Admin rejimi:</b> Sizga cheksiz spin!")
        return
    await message.answer(
        "⭐ <b>Stars paketlari</b>\n\n"
        "🎯 <b>1 Stars = 1 Spin</b>\n"
        "🎁 <b>Maxsus takliflar bonus bilan!</b>\n\n"
        "Paketni tanlang:",
        reply_markup=donation_options(settings.channel_username),
    )


@router.message(F.text == "💸 Chiqarish")
async def btn_withdraw(message: Message) -> None:
    user = message.from_user
    assert user is not None
    data = await db.get_user(user.id)
    balance = data.get("stars", 0) if data else 0

    if balance < 50:
        await message.answer(
            "💸 <b>Yulduz chiqarish</b>\n\n"
            f"💰 Balansingiz: <b>{balance} ⭐</b>\n"
            "❌ Minimal: <b>50 ⭐</b>\n\n"
            "🎰 Ko'proq o'ynab yulduz to'plang!"
        )
        return

    await message.answer(
        f"💸 <b>Yulduz chiqarish</b>\n\n"
        f"💰 Balansingiz: <b>{balance} ⭐</b>\n"
        f"💳 <b>Real pul</b> ga almashtiriladi\n\n"
        "Miqdorni tanlang:",
        reply_markup=withdraw_options(balance),
    )


@router.message(F.text == "📆 Bonus")
async def btn_daily(message: Message) -> None:
    await cmd_daily(message)


@router.message(F.text == "❓ Yordam")
async def btn_help(message: Message) -> None:
    await cmd_help(message)


# Home menu callbacks olib tashlandi - endi Reply keyboard orqali ishlaydi


@router.callback_query(F.data == "play_again")
async def cb_play_again(call: CallbackQuery) -> None:
    try:
        await call.answer("🎰 Aylantirish...")
    except TelegramBadRequest:
        pass  # Query expired, ignore

    user = call.from_user
    assert user is not None

    # Access check
    ok = await _ensure_access(user.id, call.bot, call.message.answer)  # type: ignore[arg-type]
    if not ok:
        return

    # Ensure user exists
    if not await db.get_user(user.id):
        await db.upsert_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            initial_spins=settings.initial_spins,
        )

    # Spin with message edit
    await _spin_flow(user.id, call.message.answer, edit_message=call.message)


@router.callback_query(F.data == "show_store")
async def cb_show_store(call: CallbackQuery) -> None:
    try:
        await call.answer("💳 Do'kon ochilmoqda...")
    except TelegramBadRequest:
        pass

    await call.message.answer(
        "⭐🛒 <b>STARS DO'KONI</b> 🛒⭐\n\n"
        "🎯 <b>1 Stars = 1 Spin</b>\n"
        "🎁 <b>BONUS paketlar mavjud!</b>\n\n"
        "💳 <b>Paketni tanlang:</b>",
        reply_markup=donation_options(settings.channel_username),
    )


@router.callback_query(F.data == "show_profile")
async def cb_show_profile(call: CallbackQuery) -> None:
    await call.answer()
    user = call.from_user
    assert user is not None
    data = await db.get_user_with_stats(user.id)
    if not data:
        await call.message.answer("Avval /start bosing.")
        return

    invited = await db.count_invited(user.id)
    total_spins = data.get("total_spins") or 0
    total_won = data.get("total_stars_won") or 0
    win_rate = (total_won / total_spins * 100) if total_spins > 0 else 0

    await call.message.answer(
        f"👤 <b>{user.full_name}</b>\n\n"
        f"💰 <b>Balans:</b>\n"
        f"⭐ Yulduzlar: <b>{data['stars']}</b>\n"
        f"🎰 Spinlar: <b>{data['spins']}</b>\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"🎮 Jami o'yinlar: <b>{total_spins}</b>\n"
        f"🏆 Eng katta yutuq: <b>{data['biggest_win']} ⭐</b>\n"
        f"🥇 Jami yutuq: <b>{total_won} ⭐</b>\n"
        f"📈 Yutish foizi: <b>{win_rate:.1f}%</b>\n\n"
        f"👥 <b>Referral:</b> {invited} do'st"
    )


# Profile va top callback'lari olib tashlandi


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(call: CallbackQuery) -> None:
    """Kanal a'zoligini tekshirish callback'i"""
    await call.answer()
    user = call.from_user
    assert user is not None

    if not settings.mandatory_channel:
        await call.message.edit_text("⚠️ Majburiy kanal sozlanmagan.")
        return

    # Admin bo'lsa, a'zolik tekshirmasdan o'tkazish
    if _is_admin(user.id):
        await call.message.edit_text(
            "👑 <b>Admin sifatida botga xush kelibsiz!</b>\n\n"
            "🎰 <b>Slot o'yiniga xush kelibsiz!</b>\n\n"
            "🎁 Cheksiz spin sizning ixtiyoringizda!\n"
            "📆 Har kuni kunlik bonus oling\n\n"
            "Quyidagi menyudan foydalaning:",
            reply_markup=None,
        )
        await call.message.answer("Admin menyusi faol!", reply_markup=main_menu())
        return

    # Oddiy foydalanuvchi uchun a'zolik tekshirish
    is_subscribed = await _check_channel_subscription(call.bot, user.id, settings.mandatory_channel)
    if is_subscribed:
        # A'zo bo'lgan, botga kirish ruxsati berish
        await call.message.edit_text(
            "✅ <b>Ajoyib! Siz kanalga a'zo bo'lgansiz!</b>\n\n"
            "🎰 <b>Slot o'yiniga xush kelibsiz!</b>\n\n"
            "🎁 Yangi foydalanuvchilar uchun <b>10 ta bepul spin!</b>\n"
            "📆 Har kuni kunlik bonus oling\n\n"
            "Quyidagi menyudan foydalaning:",
            reply_markup=None,
        )
        await call.message.answer("Menyu faol!", reply_markup=main_menu())

        # Foydalanuvchini bazaga qo'shish
        existing = await db.get_user(user.id)
        if not existing:
            await db.upsert_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                initial_spins=settings.initial_spins,
            )
    else:
        # Hali a'zo bo'lmagan
        await call.message.edit_text(
            "❌ <b>Siz hali kanalga a'zo bo'lmagansiz!</b>\n\n"
            "📢 Iltimos, avval kanalga a'zo bo'ling va keyin qayta tekshiring:",
            reply_markup=channel_subscription_menu(settings.mandatory_channel),
        )


@router.message(F.text.regexp(r"^⭐"))
async def btn_donate(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if _is_admin(user.id):
        await message.answer("Siz admin siz. Bepul o‘ynashingiz mumkin. 🎰 /spin")
        return
    if settings.stars_enabled:
        await message.answer("Qancha ⭐ xarid qilasiz?", reply_markup=donation_options(settings.channel_username))
    else:
        await message.answer("To‘lov hozircha o‘chirilgan.")


# Simulated donation via callbacks (20/30/50 stars → equal spins)
@router.callback_query(F.data.startswith("donate:"))
async def cb_donate(call: CallbackQuery) -> None:
    user = call.from_user
    assert user is not None
    amount_str = call.data.split(":", 1)[1]

    # Handle special packages
    if amount_str == "starter":
        amount, bonus = 10, 2
        title = "🎁 Starter paket"
        description = f"{amount} Stars + {bonus} bonus spin"
    elif amount_str == "mega":
        amount, bonus = 100, 20
        title = "🔥 Mega paket"
        description = f"{amount} Stars + {bonus} bonus spin"
    else:
        try:
            amount = int(amount_str)
            bonus = 0
            title = f"{amount} ⭐ paket"
            description = "Slot o'yini uchun spinlar"
        except ValueError:
            await call.answer("Xatolik", show_alert=True)
            return

    if settings.stars_enabled:
        payload = f"stars:{amount}:{bonus}"
        currency = "XTR"
        prices = [LabeledPrice(label=f"{amount} ⭐", amount=amount)]
        try:
            invoice_kwargs = dict(
                title=title,
                description=description,
                payload=payload,
                currency=currency,
                prices=prices,
            )
            if settings.provider_token:
                invoice_kwargs["provider_token"] = settings.provider_token
            await call.message.answer_invoice(**invoice_kwargs)
        except TelegramBadRequest:
            await call.message.answer(
                "❌ <b>To'lov xatoligi!</b>\n\n"
                "🔧 <b>Yechim:</b>\n"
                "• @BotFather → Bot Settings → Payments → Stars: ON\n"
                "• Qayta urinib ko'ring"
            )
        await call.answer()
        return

    # Fallback: simulated
    total_spins = amount + bonus
    await db.add_spins(user.id, total_spins)
    await call.message.answer(f"✅ <b>Demo:</b> {total_spins} spin berildi!")
    await call.answer()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_q: PreCheckoutQuery) -> None:
    # Approve checkout
    await pre_checkout_q.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message) -> None:
    user = message.from_user
    assert user is not None
    sp = message.successful_payment
    if not sp:
        return
    payload = sp.invoice_payload or ""
    if payload.startswith("stars:"):
        try:
            parts = payload.split(":")
            amount = int(parts[1])
            bonus = int(parts[2]) if len(parts) > 2 else 0
            total_spins = amount + bonus
        except (ValueError, IndexError):
            return
        await db.add_spins(user.id, total_spins)
        await db.log_payment(user.id, kind="stars_invoice", stars=amount, spins_added=total_spins)
        log_payment(amount)

        bonus_text = f" + {bonus} bonus" if bonus > 0 else ""
        await message.answer(
            f"✅ <b>To'lov muvaffaqiyatli!</b>\n\n"
            f"🎁 <b>{total_spins} spin</b> berildi{bonus_text}\n"
            f"🎰 Endi o'ynashingiz mumkin!"
        )


@router.callback_query(F.data.startswith("withdraw:"))
async def cb_withdraw(call: CallbackQuery) -> None:
    user = call.from_user
    assert user is not None
    arg = call.data.split(":", 1)[1]

    if arg == "cancel":
        await call.message.edit_text("❌ Chiqarish bekor qilindi.")
        await call.answer()
        return

    data = await db.get_user(user.id)
    if not data:
        await call.answer("Avval /start", show_alert=True)
        return
    balance = int(data.get("stars", 0))
    if balance < 50:
        await call.answer("Kamida 50 ⭐ kerak", show_alert=True)
        return

    if arg == "max":
        amount = balance
    else:
        try:
            amount = int(arg)
        except ValueError:
            await call.answer("Xato", show_alert=True)
            return

    if amount < 50 or amount > balance:
        await call.answer("Noto'g'ri summa", show_alert=True)
        return

    # Deduct stars immediately
    await db.add_stars(user.id, -amount)

    # Notify admins with user info
    user_info = f"👤 @{user.username or 'NoUsername'} (ID: {user.id})"
    for admin_id in settings.admin_ids:
        try:
            await call.bot.send_message(
                admin_id,
                f"💸 <b>Yangi yechib olish so'rovi</b>\n\n"
                f"{user_info}\n"
                f"💰 Miqdor: {amount} ⭐\n"
                f"📅 Vaqt: {call.message.date.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Tasdiqlash uchun foydalanuvchiga to'lov qiling.",
            )
        except Exception:
            pass

    await call.message.edit_text(
        f"✅ <b>So'rov yuborildi!</b>\n\n"
        f"💰 Miqdor: {amount} ⭐\n"
        f"⏳ Admin tasdiqlaydi va to'lov qiladi.\n"
        f"📞 Savollar bo'lsa: /ask matn"
    )
    await call.answer()


# Admin area
def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if not _is_admin(user.id):
        return
    kpis = await db.compute_kpis()
    await message.answer(
        "📈 Statistika:\n"
        f"DAU: {kpis['dau']} | WAU: {kpis['wau']} | MAU: {kpis['mau']}\n"
        f"Users: {kpis['users']} | Payers: {kpis['payers']}\n"
        f"Conversion: {kpis['conversion']:.2%}\n"
        f"ARPU (⭐): {kpis['arpu_stars']:.2f}\n"
    )


@router.message(Command("account"))
async def cmd_account(message: Message) -> None:
    user = message.from_user
    assert user is not None
    data = await db.get_user_with_stats(user.id)
    if not data:
        await message.answer("Avval /start bosing.")
        return
    spins_log = await db.get_recent_spins(user.id, 10)
    lines = ["📜 Oxirgi 10 o‘yin:"]
    for r in spins_log:
        status = "+" + str(r["payout"]) + "⭐" if r["is_win"] else "0"
        lines.append(f"{r['r1']}|{r['r2']}|{r['r3']} → {status}")
    await message.answer("\n".join(lines) if len(lines) > 1 else "Hali tarix yo‘q.")


@router.message(Command("ban"))
async def cmd_ban(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if not _is_admin(user.id):
        return
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("Foydalanish: /ban @username")
        return
    target = await db.get_user_by_username(parts[1].lstrip("@"))
    if not target:
        await message.answer("Topilmadi")
        return
    await db.set_ban(int(target["user_id"]), True)
    await message.answer("Foydalanuvchi ban qilindi")


@router.message(Command("unban"))
async def cmd_unban(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if not _is_admin(user.id):
        return
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("Foydalanish: /unban @username")
        return
    target = await db.get_user_by_username(parts[1].lstrip("@"))
    if not target:
        await message.answer("Topilmadi")
        return
    await db.set_ban(int(target["user_id"]), False)
    await message.answer("Ban olib tashlandi")


@router.message(Command("freeplay"))
async def cmd_freeplay(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if not _is_admin(user.id):
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("Foydalanish: /freeplay @username on|off")
        return
    target = await db.get_user_by_username(parts[1].lstrip("@"))
    if not target:
        await message.answer("Topilmadi")
        return
    await db.set_free_play(int(target["user_id"]), parts[2].lower() == "on")
    await message.answer("Free play yangilandi")


@router.message(Command("setvip"))
async def cmd_setvip(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if not _is_admin(user.id):
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("Foydalanish: /setvip @username 0|1|2|3")
        return
    try:
        level = int(parts[2])
    except ValueError:
        await message.answer("Noto‘g‘ri daraja")
        return
    target = await db.get_user_by_username(parts[1].lstrip("@"))
    if not target:
        await message.answer("Topilmadi")
        return
    await db.set_vip_level(int(target["user_id"]), level)
    await message.answer("VIP daraja yangilandi")


@router.message(Command("daily"))
async def cmd_daily(message: Message) -> None:
    from datetime import datetime

    user = message.from_user
    assert user is not None
    # Ensure user exists
    if not await db.get_user(user.id):
        await db.upsert_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            initial_spins=settings.initial_spins,
        )
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if await db.can_claim_daily_bonus(user.id, today):
        await db.add_spins(user.id, settings.daily_bonus_spins)
        await db.set_daily_claimed(user.id, today)
        await message.answer(f"Kunlik bonus: +{settings.daily_bonus_spins} spin berildi! 🎁")
    else:
        await message.answer("Bugun allaqachon bonus olgansiz. Ertaga qaytib keling!")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if not _is_admin(user.id):
        return
    # Usage: /broadcast all|active7|vip <matn>
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Foydalanish: /broadcast all|active7|vip <matn>")
        return
    segment, text = parts[1], parts[2]
    if segment == "all":
        targets = await db.get_active_user_ids(90)
    elif segment.startswith("active") and segment[6:].isdigit():
        targets = await db.get_active_user_ids(int(segment[6:]))
    elif segment == "vip":
        targets = await db.get_vip_user_ids()
    else:
        await message.answer("Segment noto‘g‘ri. all|active7|vip")
        return
    sent = 0
    for uid in targets:
        try:
            await message.bot.send_message(uid, text)
            sent += 1
        except Exception:
            pass
    await message.answer(f"Broadcast yuborildi: {sent}/{len(targets)}")


@router.message(Command("addspins"))
async def cmd_addspins(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if not _is_admin(user.id):
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("Foydalanish: /addspins @username 10")
        return
    target_username = parts[1].lstrip("@")
    try:
        amount = int(parts[2])
    except ValueError:
        await message.answer("Noto‘g‘ri miqdor")
        return

    target = await db.get_user_by_username(target_username)
    target_id = target["user_id"] if target else user.id
    await db.add_spins(int(target_id), amount)
    await message.answer(f"{('@'+target_username) if target else '(self)'} ga {amount} spin qo‘shildi.")


@router.message(Command("addstars"))
async def cmd_addstars(message: Message) -> None:
    user = message.from_user
    assert user is not None
    if not _is_admin(user.id):
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("Foydalanish: /addstars @username 20")
        return
    target_username = parts[1].lstrip("@")
    try:
        amount = int(parts[2])
    except ValueError:
        await message.answer("Noto‘g‘ri miqdor")
        return

    target = await db.get_user_by_username(target_username)
    target_id = target["user_id"] if target else user.id
    await db.add_stars(int(target_id), amount)
    await message.answer(f"{('@'+target_username) if target else '(self)'} ga {amount} ⭐ qo‘shildi.")
