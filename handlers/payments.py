"""
Payment handlers for Telegram Stars
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types import Message
from aiogram.filters import Command

from db.database import Database
from keyboards.inline import get_buy_attempts_keyboard, get_main_menu
from config.settings import STAR_TO_ATTEMPT_RATIO

logger = logging.getLogger(__name__)
router = Router()
db = Database()


@router.callback_query(F.data == "buy_attempts")
async def show_buy_attempts(callback: CallbackQuery):
    """Show buy attempts menu"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Please complete registration first!", show_alert=True)
        return
    
    buy_text = f"""
⭐ **BUY ATTEMPTS** ⭐

💫 **Current Balance:**
• Stars: {user['stars']} ⭐
• Attempts: {user['attempts']} 🎮

💰 **Exchange Rate:**
1 Telegram Star = 1 Game Attempt

🎁 **Purchase Options:**
Choose how many attempts you want to buy:
"""
    
    await callback.message.edit_text(
        buy_text,
        reply_markup=get_buy_attempts_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_"))
async def handle_purchase(callback: CallbackQuery):
    """Handle attempt purchase"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.get('is_verified'):
        await callback.answer("❌ Please complete registration first!", show_alert=True)
        return
    
    # Extract amount from callback data
    amount = int(callback.data.split("_")[1])
    
    try:
        # Create invoice for Telegram Stars
        prices = [LabeledPrice(label=f"{amount} Game Attempts", amount=amount)]
        
        await callback.message.answer_invoice(
            title=f"🎮 {amount} Game Attempts",
            description=f"Purchase {amount} attempts to play the slot game!",
            payload=f"attempts_{amount}_{user_id}",
            provider_token="",  # Empty for Telegram Stars
            currency="XTR",  # Telegram Stars currency
            prices=prices,
            start_parameter=f"attempts_{amount}",
            photo_url="https://i.imgur.com/placeholder.jpg",  # Optional: add a nice image
            photo_width=512,
            photo_height=512
        )
        
        await callback.answer("💳 Invoice sent! Complete the payment to get your attempts.")
        
    except Exception as e:
        logger.error(f"Error creating invoice for user {user_id}: {e}")
        await callback.answer("❌ Error creating payment. Please try again.", show_alert=True)


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """Process pre-checkout query"""
    # Always approve the payment for now
    # In production, you might want to add additional validation
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """Process successful payment"""
    payment = message.successful_payment
    user_id = message.from_user.id
    
    try:
        # Parse payload to get amount and verify user
        payload_parts = payment.invoice_payload.split("_")
        if len(payload_parts) != 3 or payload_parts[0] != "attempts":
            logger.error(f"Invalid payload: {payment.invoice_payload}")
            return
        
        amount = int(payload_parts[1])
        payload_user_id = int(payload_parts[2])
        
        # Verify user ID matches
        if user_id != payload_user_id:
            logger.error(f"User ID mismatch: {user_id} vs {payload_user_id}")
            return
        
        # Credit attempts to user
        success = await db.update_user_balance(user_id, 0, amount)
        
        if success:
            # Record transaction
            await db.add_transaction(
                user_id, 
                "purchase", 
                amount,  # stars spent
                amount   # attempts gained
            )
            
            # Get updated user data
            user = await db.get_user(user_id)
            
            success_message = f"""
✅ **PAYMENT SUCCESSFUL!** ✅

🎉 You have successfully purchased {amount} attempts!

💫 **Updated Balance:**
⭐ Stars: {user['stars']}
🎮 Attempts: {user['attempts']}

🎰 Ready to play? Let's go! 🎰
"""
            
            await message.answer(
                success_message,
                reply_markup=get_main_menu()
            )
            
            logger.info(f"Successfully processed payment for user {user_id}: {amount} attempts")
            
        else:
            logger.error(f"Failed to update balance for user {user_id}")
            await message.answer("❌ Error processing payment. Please contact admin.")
            
    except Exception as e:
        logger.error(f"Error processing payment for user {user_id}: {e}")
        await message.answer("❌ Error processing payment. Please contact admin.")


# Alternative command for testing payments (admin only)
@router.message(Command("testpay"))
async def test_payment(message: Message):
    """Test payment command for development"""
    user_id = message.from_user.id
    
    # For testing - add 5 attempts without payment
    # Remove this in production or restrict to admins
    success = await db.update_user_balance(user_id, 0, 5)
    
    if success:
        await message.answer(
            "🧪 Test: Added 5 attempts to your account!",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer("❌ Test payment failed.")
