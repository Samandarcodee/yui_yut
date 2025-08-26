"""
🎰 Test bot to verify basic functionality
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import BOT_TOKEN, MAIN_MENU_MESSAGE
from keyboards.inline import get_main_menu
from db.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
db = Database()

@dp.message(CommandStart())
async def start_command(message: Message):
    """Test start command"""
    await message.answer(
        f"🎰 Salom {message.from_user.first_name}!\n\n{MAIN_MENU_MESSAGE}",
        reply_markup=get_main_menu()
    )

async def main():
    """Main function"""
    try:
        await db.init_db()
        logger.info("Database initialized successfully")
        
        logger.info("Starting test bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
