"""
Contact admin handlers
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from keyboards.inline import get_main_menu, get_contact_keyboard, get_faq_keyboard
from config.settings import ADMIN_CONTACT_INFO, CONTACT_ADMIN_MESSAGE, FAQ

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "contact_admin")
async def contact_admin(callback: CallbackQuery):
    """Admin bilan bog'lanish"""
    contact_text = CONTACT_ADMIN_MESSAGE.format(
        bot_username=ADMIN_CONTACT_INFO["bot_username"],
        admin_username=ADMIN_CONTACT_INFO["admin_username"],
        support_channel=ADMIN_CONTACT_INFO["support_channel"],
        response_time=ADMIN_CONTACT_INFO["response_time"],
        working_hours=ADMIN_CONTACT_INFO["working_hours"]
    )
    
    await callback.message.edit_text(
        contact_text,
        reply_markup=get_contact_keyboard()
    )
    await callback.answer()


@router.message(Command("contact"))
async def contact_command(message: Message):
    """Contact command handler"""
    contact_text = CONTACT_ADMIN_MESSAGE.format(
        bot_username=ADMIN_CONTACT_INFO["bot_username"],
        admin_username=ADMIN_CONTACT_INFO["admin_username"],
        support_channel=ADMIN_CONTACT_INFO["support_channel"],
        response_time=ADMIN_CONTACT_INFO["response_time"],
        working_hours=ADMIN_CONTACT_INFO["working_hours"]
    )
    
    await message.answer(
        contact_text,
        reply_markup=get_contact_keyboard()
    )


@router.callback_query(F.data == "contact_support_channel")
async def contact_support_channel(callback: CallbackQuery):
    """Support kanaliga o'tish"""
    if ADMIN_CONTACT_INFO["support_channel"]:
        # Create a direct link to the channel
        channel_link = f"https://t.me/{ADMIN_CONTACT_INFO['support_channel'].replace('@', '')}"
        await callback.message.edit_text(
            f"📢 **SUPPORT KANALIGA O'TISH** 📢\n\n"
            f"Kanalimizga obuna bo'ling va yangiliklar, e'lonlar va yordam oling!\n\n"
            f"🔗 **Kanal:** {ADMIN_CONTACT_INFO['support_channel']}\n"
            f"📱 **Link:** {channel_link}\n\n"
            f"Kanalga o'tish uchun yuqoridagi linkni bosing yoki kanal nomini qidiring.",
            reply_markup=get_contact_keyboard()
        )
    else:
        await callback.answer("Support kanali mavjud emas", show_alert=True)
    await callback.answer()


@router.callback_query(F.data == "contact_admin_direct")
async def contact_admin_direct(callback: CallbackQuery):
    """Admin bilan to'g'ridan-to'g'ri bog'lanish"""
    if ADMIN_CONTACT_INFO["admin_username"]:
        # Create a direct link to the admin
        admin_link = f"https://t.me/{ADMIN_CONTACT_INFO['admin_username'].replace('@', '')}"
        await callback.message.edit_text(
            f"👤 **ADMIN BILAN BOG'LANISH** 👤\n\n"
            f"Admin bilan to'g'ridan-to'g'ri yozing va yordam oling!\n\n"
            f"👨‍💼 **Admin:** {ADMIN_CONTACT_INFO['admin_username']}\n"
            f"📱 **Link:** {admin_link}\n\n"
            f"💡 **Maslahat:**\n"
            f"• Muammoni aniq tasvirlab yuboring\n"
            f"• Screenshot qo'shing\n"
            f"• To'lov ma'lumotlarini ko'rsating (agar kerak bo'lsa)\n\n"
            f"Admin bilan bog'lanish uchun yuqoridagi linkni bosing.",
            reply_markup=get_contact_keyboard()
        )
    else:
        await callback.answer("Admin username mavjud emas", show_alert=True)
    await callback.answer()


@router.callback_query(F.data == "faq")
async def show_faq(callback: CallbackQuery):
    """Ko'p uchraydigan savollarni ko'rsatish"""
    faq_text = "❓ **KO'P UCHRAYDIGAN SAVOLLAR** ❓\n\n"
    
    for key, item in FAQ.items():
        faq_text += f"**{item['question']}**\n{item['answer']}\n\n"
    
    faq_text += "💡 **Qo'shimcha yordam kerakmi?** Admin bilan bog'laning!"
    
    await callback.message.edit_text(
        faq_text,
        reply_markup=get_faq_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("faq_"))
async def show_faq_detail(callback: CallbackQuery):
    """FAQ ning batafsil ma'lumotini ko'rsatish"""
    faq_key = callback.data.replace("faq_", "")
    
    if faq_key in FAQ:
        item = FAQ[faq_key]
        detail_text = f"❓ **{item['question']}** ❓\n\n"
        detail_text += f"💡 **Javob:**\n{item['answer']}\n\n"
        detail_text += "🔗 **Qo'shimcha yordam:** Admin bilan bog'laning!"
        
        await callback.message.edit_text(
            detail_text,
            reply_markup=get_faq_keyboard()
        )
    else:
        await callback.answer("FAQ topilmadi", show_alert=True)
    
    await callback.answer()
