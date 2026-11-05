"""Run: python -m telegram_bot"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import token
from .db import init_db
from .handlers import router


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    value = token()
    if not value:
        raise SystemExit("TELEGRAM_BOT_TOKEN is missing. Put it in .env")
    init_db()
    bot = Bot(value, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
