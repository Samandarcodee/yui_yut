"""
🎰 Boshlash va ro'yxatdan o'tish handlerlari (O'zbek tilida)
"""
import random
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db.database import Database
from keyboards.inline import get_verification_keyboard, get_main_menu, get_channel_subscription_keyboard
from config.settings import (
    WELCOME_MESSAGE, VERIFICATION_SUCCESS, MAIN_MENU_MESSAGE, REQUIRED_CHANNEL, CHANNEL_URL,
    CHANNEL_SUBSCRIPTION_REQUIRED, SUBSCRIPTION_SUCCESS, SUBSCRIPTION_FAILED
)

logger = logging.getLogger(__name__)
router = Router()
db = Database()


class RegistrationStates(StatesGroup):
    waiting_verification = State()


async def check_channel_subscription(bot, user_id: int) -> bool:
    """Foydalanuvchining kanal obunasini tekshirish - majburiy"""
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        # Foydalanuvchi a'zo, admin yoki owner bo'lishi kerak
        is_subscribed = isinstance(member, (ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember))
        
        if is_subscribed:
            logger.info(f"Foydalanuvchi {user_id} kanalga obuna")
        else:
            logger.info(f"Foydalanuvchi {user_id} kanalga obuna emas")
            
        return is_subscribed
    except Exception as e:
        logger.error(f"Kanal obunasini tekshirishda xato {user_id}: {e}")
        # Xato bo'lsa ham False qaytarish (xavfsizlik uchun)
        return False


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """Start buyrug'ini boshqarish"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name
    
    # Referral linkini tekshirish
    referrer_id = None
    args = message.text.split()
    if len(args) > 1 and args[1].startswith('ref_'):
        try:
            referrer_id = int(args[1][4:])  # ref_ qismini olib tashlash
        except ValueError:
            pass
    
    # Foydalanuvchi mavjudligini va tasdiqlangligini tekshirish
    user = await db.get_user(user_id)
    
    if user and user.get('is_verified'):
        # Foydalanuvchi allaqachon ro'yxatdan o'tgan va tasdiqlangan
        await message.answer(
            f"Salom {first_name}! Qaytganingiz bilan! 🎰\n\n{MAIN_MENU_MESSAGE}",
            reply_markup=get_main_menu()
        )
        return
    
    # Foydalanuvchini ro'yxatdan o'tkazish (agar mavjud bo'lmasa)
    if not user:
        await db.register_user(user_id, username, first_name, referrer_id)
        logger.info(f"Yangi foydalanuvchi ro'yxatdan o'tdi: {user_id} ({username})")
    
    # Captcha yaratish
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    answer = num1 + num2
    
    # Javobni state ga saqlash
    await state.update_data(verification_answer=answer)
    await state.set_state(RegistrationStates.waiting_verification)
    
    captcha_text = f"{WELCOME_MESSAGE}\n\n🧮 {num1} + {num2} = ?"
    
    await message.answer(
        captcha_text,
        reply_markup=get_verification_keyboard(answer)
    )


@router.callback_query(F.data.startswith("verify_"))
async def verify_user(callback: CallbackQuery, state: FSMContext):
    """Foydalanuvchini tasdiqlash"""
    data = callback.data.split("_")
    user_answer = int(data[1])
    correct_answer = int(data[2])
    
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name
    
    if user_answer == correct_answer:
        # To'g'ri javob - foydalanuvchini tasdiqlash
        await db.verify_user(user_id)
        await state.clear()
        
        # Kanal obunasini tekshirish (majburiy)
        try:
            is_subscribed = await check_channel_subscription(callback.bot, user_id)
            
            if is_subscribed:
                # Kanal obunasini bazaga saqlash
                await db.set_channel_subscription(user_id, True)
                
                await callback.message.edit_text(
                    SUBSCRIPTION_SUCCESS,
                    reply_markup=get_main_menu()
                )
                logger.info(f"Foydalanuvchi {user_id} ({username}) tasdiqlandi va kanalga obuna")
            else:
                # Kanal obunasi majburiy - asosiy menyuga o'tkazish mumkin emas
                await callback.message.edit_text(
                    CHANNEL_SUBSCRIPTION_REQUIRED.format(channel_url=CHANNEL_URL),
                    reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
                )
                logger.info(f"Foydalanuvchi {user_id} ({username}) tasdiqlandi, lekin kanal obunasini kerak")
        except Exception as e:
            logger.error(f"Kanal obunasini tekshirishda xato: {e}")
            # Xato bo'lsa ham kanal obunasini talab qilish
            await callback.message.edit_text(
                CHANNEL_SUBSCRIPTION_REQUIRED.format(channel_url=CHANNEL_URL),
                reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
            )
    else:
        # Noto'g'ri javob - yangi captcha yaratish
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        answer = num1 + num2
        
        await state.update_data(verification_answer=answer)
        
        await callback.message.edit_text(
            f"❌ Noto'g'ri javob! Iltimos qaytadan urinib ko'ring.\n\n🧮 {num1} + {num2} = ?",
            reply_markup=get_verification_keyboard(answer)
        )
    
    await callback.answer()


@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery):
    """Kanal obunasini tekshirish handler - majburiy"""
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name
    
    # Kanal obunasini tekshirish
    is_subscribed = await check_channel_subscription(callback.bot, user_id)
    
    if is_subscribed:
        # Obuna tasdiqlandi
        await db.set_channel_subscription(user_id, True)
        
        await callback.message.edit_text(
            SUBSCRIPTION_SUCCESS,
            reply_markup=get_main_menu()
        )
        logger.info(f"Foydalanuvchi {user_id} ({username}) kanal obunasi tasdiqlandi")
    else:
        # Obuna topilmadi - majburiy
        await callback.message.edit_text(
            SUBSCRIPTION_FAILED.format(channel_url=CHANNEL_URL),
            reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
        )
        await callback.answer("❌ Kanal obunasi majburiy! Iltimos avval kanalga obuna bo'ling!", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Asosiy menyuni ko'rsatish"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Iltimos avval ro'yxatdan o'ting!", show_alert=True)
        return
    
    # Kanal obunasini tekshirish (majburiy)
    try:
        if not user.get('channel_subscribed', False):
            is_subscribed = await check_channel_subscription(callback.bot, user_id)
            if is_subscribed:
                await db.set_channel_subscription(user_id, True)
            else:
                # Kanal obunasi majburiy - asosiy menyuga o'tkazish mumkin emas
                await callback.message.edit_text(
                    CHANNEL_SUBSCRIPTION_REQUIRED.format(channel_url=CHANNEL_URL),
                    reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
                )
                await callback.answer("⚠️ Kanal obunasi majburiy! Iltimos avval kanalga obuna bo'ling!", show_alert=True)
                return
    except Exception as e:
        logger.error(f"Main menu da kanal obunasini tekshirishda xato: {e}")
        # Xato bo'lsa ham kanal obunasini talab qilish
        await callback.message.edit_text(
            CHANNEL_SUBSCRIPTION_REQUIRED.format(channel_url=CHANNEL_URL),
            reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
        )
        await callback.answer("⚠️ Kanal obunasi tekshirishda xato! Iltimos qaytadan urinib ko'ring!", show_alert=True)
        return
    
    await callback.message.edit_text(
        MAIN_MENU_MESSAGE,
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(Command("check_sub"))
async def manual_check_subscription(message: Message):
    """Manual channel subscription check command"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Admin huquqini tekshirish
    from config.settings import ADMIN_IDS
    if user_id not in ADMIN_IDS:
        await message.answer("❌ Bu buyruq faqat adminlar uchun!")
        return
    
    # Kanal obunasini tekshirish
    is_subscribed = await check_channel_subscription(message.bot, user_id)
    
    if is_subscribed:
        await message.answer(f"✅ {username}, siz kanalga obunasiz!")
    else:
        await message.answer(f"❌ {username}, siz kanalga obuna emassiz!")


@router.message(Command("check_all_subs"))
async def check_all_subscriptions(message: Message):
    """Check all users' subscription status"""
    user_id = message.from_user.id
    
    # Admin huquqini tekshirish
    from config.settings import ADMIN_IDS
    if user_id not in ADMIN_IDS:
        await message.answer("❌ Bu buyruq faqat adminlar uchun!")
        return
    
    # Barcha foydalanuvchilarni olish
    users = await db.get_all_users()
    
    if not users:
        await message.answer("📊 Hali foydalanuvchilar yo'q!")
        return
    
    # Obuna statistikasini hisoblash
    total_users = len(users)
    subscribed_users = sum(1 for user in users if user.get('channel_subscribed', False))
    unsubscribed_users = total_users - subscribed_users
    
    stats_text = f"""
📊 **KANAL OBUNASI STATISTIKASI**

👥 **Jami foydalanuvchilar:** {total_users}
✅ **Obuna bo'lganlar:** {subscribed_users}
❌ **Obuna bo'lmaganlar:** {unsubscribed_users}
📈 **Obuna foizi:** {(subscribed_users/total_users*100):.1f}%

🔍 **Obuna bo'lmagan foydalanuvchilar:**
"""
    
    # Obuna bo'lmagan foydalanuvchilarni ko'rsatish
    unsubscribed_list = [user for user in users if not user.get('channel_subscribed', False)]
    
    if unsubscribed_list:
        for i, user in enumerate(unsubscribed_list[:10], 1):  # Faqat dastlabki 10 tasini
            username = user.get('username') or user.get('first_name') or 'Noma\'lum'
            stats_text += f"{i}. {username} (ID: {user['telegram_id']})\n"
        
        if len(unsubscribed_list) > 10:
            stats_text += f"\n... va yana {len(unsubscribed_list) - 10} ta"
    else:
        stats_text += "Barcha foydalanuvchilar obuna bo'lgan! 🎉"
    
    await message.answer(stats_text)


@router.message(Command("force_check_subs"))
async def force_check_subscriptions(message: Message):
    """Force check and update all subscriptions"""
    user_id = message.from_user.id
    
    # Admin huquqini tekshirish
    from config.settings import ADMIN_IDS
    if user_id not in ADMIN_IDS:
        await message.answer("❌ Bu buyruq faqat adminlar uchun!")
        return
    
    await message.answer("🔄 Barcha foydalanuvchilarning kanal obunasi tekshirilmoqda...")
    
    try:
        # Barcha foydalanuvchilarni olish
        users = await db.get_all_users()
        
        if not users:
            await message.answer("📊 Hali foydalanuvchilar yo'q!")
            return
        
        # Obuna statistikasini hisoblash
        total_users = len(users)
        updated_count = 0
        errors_count = 0
        
        for user in users:
            try:
                user_id_check = user['telegram_id']
                current_status = user.get('channel_subscribed', False)
                
                # Kanal obunasini tekshirish
                is_subscribed = await check_channel_subscription(message.bot, user_id_check)
                
                # Status o'zgargan bo'lsa yangilash
                if is_subscribed != current_status:
                    await db.set_channel_subscription(user_id_check, is_subscribed)
                    updated_count += 1
                    
                    # Agar obuna bekor qilingan bo'lsa, foydalanuvchiga xabar yuborish
                    if not is_subscribed and current_status:
                        try:
                            await message.bot.send_message(
                                user_id_check,
                                "⚠️ **OGOHLANTIRISH!** ⚠️\n\n"
                                "Siz kanaldan obunani bekor qildingiz!\n\n"
                                "Botning barcha funksiyalarini ishlatish uchun qaytadan obuna bo'lishingiz kerak:\n"
                                "📢 @premim_002\n\n"
                                "Obuna bo'lgandan so'ng /start buyrug'ini yuboring."
                            )
                        except Exception as e:
                            logger.error(f"Foydalanuvchi {user_id_check} ga xabar yuborishda xato: {e}")
                            errors_count += 1
                            
            except Exception as e:
                logger.error(f"Foydalanuvchi {user.get('telegram_id', 'Noma\'lum')} obunasini tekshirishda xato: {e}")
                errors_count += 1
        
        # Natijani xabar qilish
        result_text = f"""
✅ **OBUNA TEKSHIRISH TUGALLANDI!**

📊 **Natijalar:**
• Jami foydalanuvchilar: {total_users}
• Yangilangan: {updated_count}
• Xatolar: {errors_count}

🔄 Keyingi tekshirish: 1 soatdan keyin
"""
        
        await message.answer(result_text)
        
    except Exception as e:
        logger.error(f"Force check subscriptions failed: {e}")
        await message.answer(f"❌ Xato yuz berdi: {e}")
