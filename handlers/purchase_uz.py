"""
🛒 Telegram Stars bilan yulduz sotib olish handlerlari (O'zbek tilida)
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from aiogram.filters import Command

from db.database import Database
from keyboards.inline import get_buy_stars_keyboard, get_main_menu
from config.settings import PURCHASE_MESSAGE, STAR_TO_ATTEMPT_RATIO

logger = logging.getLogger(__name__)
router = Router()
db = Database()


@router.callback_query(F.data == "buy_stars")
async def show_buy_stars(callback: CallbackQuery):
    """Yulduz sotib olish menyusini ko'rsatish"""
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
        await callback.answer("⚠️ Yulduz sotib olish uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    purchase_text = f"""
🛒 **YULDUZLAR SOTIB OLISH** 🛒

💫 **Joriy balans:**
• Yulduzlar: {user['stars']} ⭐
• Urinishlar: {user['attempts']} 🎮

{PURCHASE_MESSAGE}

⚡ Tezda to'lov qiling va o'ynashni davom eting!
"""
    
    await callback.message.edit_text(
        purchase_text,
        reply_markup=get_buy_stars_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_"))
async def handle_purchase(callback: CallbackQuery):
    """Sotib olish so'rovini boshqarish"""
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
        await callback.answer("⚠️ Yulduz sotib olish uchun kanal obunasi talab qilinadi!", show_alert=True)
        return
    
    # Miqdorni callback ma'lumotlaridan olish
    amount = int(callback.data.split("_")[1])
    
    try:
        # Telegram Stars uchun hisob-faktura yaratish
        prices = [LabeledPrice(label=f"{amount} Yulduz", amount=amount)]
        
        await callback.message.answer_invoice(
            title=f"🎮 {amount} O'yin Urinishi",
            description=f"Slot o'yini uchun {amount} ta urinish sotib oling!",
            payload=f"stars_{amount}_{user_id}",
            provider_token="",  # Telegram Stars uchun bo'sh
            currency="XTR",  # Telegram Stars valyutasi
            prices=prices,
            start_parameter=f"stars_{amount}",
            photo_url="https://i.imgur.com/stars.png",  # Ixtiyoriy: chiroyli rasm
            photo_width=512,
            photo_height=512,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
            is_flexible=False
        )
        
        await callback.answer("💳 Hisob-faktura yuborildi! To'lovni amalga oshirib urinishlarni oling.")
        
    except Exception as e:
        logger.error(f"Foydalanuvchi {user_id} uchun hisob-faktura yaratishda xato: {e}")
        await callback.answer("❌ To'lov yaratishda xato. Iltimos qaytadan urinib ko'ring.", show_alert=True)


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """To'lov oldidan tekshirish"""
    # Hozircha barcha to'lovlarni tasdiqlash
    # Ishlab chiqarishda qo'shimcha tekshiruvlar qo'shishingiz mumkin
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """Muvaffaqiyatli to'lovni qayta ishlash"""
    payment = message.successful_payment
    user_id = message.from_user.id
    
    try:
        # Payload ni tahlil qilish
        payload_parts = payment.invoice_payload.split("_")
        if len(payload_parts) != 3 or payload_parts[0] != "stars":
            logger.error(f"Noto'g'ri payload: {payment.invoice_payload}")
            return
        
        amount = int(payload_parts[1])
        payload_user_id = int(payload_parts[2])
        
        # Foydalanuvchi ID sini tekshirish
        if user_id != payload_user_id:
            logger.error(f"Foydalanuvchi ID mosligi yo'q: {user_id} vs {payload_user_id}")
            return
        
        # Foydalanuvchiga urinishlar berish (1 yulduz = 1 urinish)
        success = await db.update_user_balance(user_id, 0, amount)
        
        if success:
            # Tranzaktsiyani qayd qilish
            await db.add_transaction(
                user_id, 
                "purchase", 
                amount,  # sarflangan yulduzlar
                amount,  # olingan urinishlar
                f"Telegram Stars orqali {amount} urinish sotib olindi"
            )
            
            # Yangilangan foydalanuvchi ma'lumotlarini olish
            user = await db.get_user(user_id)
            
            success_message = f"""
✅ **TO'LOV MUVAFFAQIYATLI!** ✅

🎉 Siz muvaffaqiyatli {amount} ta urinish sotib oldingiz!

💫 **Yangilangan balans:**
⭐ Yulduzlar: {user['stars']}
🎮 Urinishlar: {user['attempts']}

🎰 O'ynashga tayyormisiz? Qani ketdik! 🎰
"""
            
            await message.answer(
                success_message,
                reply_markup=get_main_menu()
            )
            
            logger.info(f"Foydalanuvchi {user_id} uchun to'lov muvaffaqiyatli qayta ishlandi: {amount} urinish")
            
        else:
            logger.error(f"Foydalanuvchi {user_id} uchun balansni yangilashda xato")
            await message.answer("❌ To'lovni qayta ishlashda xato. Iltimos admin bilan bog'laning.")
            
    except Exception as e:
        logger.error(f"Foydalanuvchi {user_id} uchun to'lovni qayta ishlashda xato: {e}")
        await message.answer("❌ To'lovni qayta ishlashda xato. Iltimos admin bilan bog'laning.")


# Test uchun buyruq (ishlab chiqarishda olib tashlang yoki adminlarga cheklang)
@router.message(Command("testpay"))
async def test_payment(message: Message):
    """Test to'lov buyrug'i (faqat test uchun)"""
    user_id = message.from_user.id
    
    # Test uchun - to'lovsiz 5 urinish qo'shish
    # Ishlab chiqarishda buni olib tashlang yoki adminlarga cheklang
    success = await db.update_user_balance(user_id, 0, 5)
    
    if success:
        await message.answer(
            "🧪 Test: Hisobingizga 5 urinish qo'shildi!",
            reply_markup=get_main_menu()
        )
        
        # Test tranzaktsiyasini qayd qilish
        await db.add_transaction(user_id, "test", 0, 5, "Test to'lov")
        
        logger.info(f"Test to'lov amalga oshirildi: {user_id}")
    else:
        await message.answer("❌ Test to'lov xato.")



