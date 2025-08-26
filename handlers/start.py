"""
Start and registration handlers
"""
import random
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db.database import Database
from keyboards.inline import get_verification_keyboard, get_main_menu
from config.settings import WELCOME_MESSAGE, VERIFICATION_SUCCESS, MAIN_MENU_MESSAGE

logger = logging.getLogger(__name__)
router = Router()
db = Database()


class RegistrationStates(StatesGroup):
    waiting_verification = State()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Check if user already exists and is verified
    user = await db.get_user(user_id)
    
    if user and user.get('is_verified'):
        # User already registered and verified
        await message.answer(
            f"{username}! Qaytganingiz bilan! 🎰\n\n{MAIN_MENU_MESSAGE}",
            reply_markup=get_main_menu()
        )
        return
    
    # Register user if not exists
    if not user:
        await db.register_user(user_id, username)
        logger.info(f"New user registered: {user_id} ({username})")
    
    # Generate captcha
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    answer = num1 + num2
    
    # Store the answer in state
    await state.update_data(verification_answer=answer)
    await state.set_state(RegistrationStates.waiting_verification)
    
    captcha_text = f"{WELCOME_MESSAGE}\n\n🧮 What is {num1} + {num2}?"
    
    await message.answer(
        captcha_text,
        reply_markup=get_verification_keyboard(answer)
    )


@router.callback_query(F.data.startswith("verify_"))
async def verify_user(callback: CallbackQuery, state: FSMContext):
    """Handle verification callback"""
    data = callback.data.split("_")
    user_answer = int(data[1])
    correct_answer = int(data[2])
    
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name
    
    if user_answer == correct_answer:
        # Correct answer - verify user
        await db.verify_user(user_id)
        await state.clear()
        
        await callback.message.edit_text(
            VERIFICATION_SUCCESS,
            reply_markup=get_main_menu()
        )
        
        logger.info(f"User verified successfully: {user_id} ({username})")
    else:
        # Wrong answer - generate new captcha
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        answer = num1 + num2
        
        await state.update_data(verification_answer=answer)
        
        await callback.message.edit_text(
            f"❌ Incorrect answer! Please try again.\n\n🧮 What is {num1} + {num2}?",
            reply_markup=get_verification_keyboard(answer)
        )
    
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Show main menu"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Please complete registration first!", show_alert=True)
        return
    
    await callback.message.edit_text(
        MAIN_MENU_MESSAGE,
        reply_markup=get_main_menu()
    )
    await callback.answer()
