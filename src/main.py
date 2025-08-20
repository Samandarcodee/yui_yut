import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from .config import get_settings
from .handlers import router
from .db import init_db


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
    settings = get_settings()
    await init_db()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    # Warm up bot.me cache for referral links
    await bot.get_me()

    logging.info("Bot started. Waiting for updates...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


