"""Run: python -m telegram_bot"""

from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import token
from .db import init_db
from .handlers import router


def telegram_session() -> AiohttpSession:
    # PythonAnywhere free accounts reach the internet only through this proxy.
    # On a normal PC or a VPS these variables are empty, so the bot connects directly.
    proxy = (
        os.environ.get("https_proxy")
        or os.environ.get("HTTPS_PROXY")
        or os.environ.get("http_proxy")
        or os.environ.get("HTTP_PROXY")
        or ""
    ).strip()
    if proxy:
        logging.info("Using HTTP proxy for Telegram")
        return AiohttpSession(proxy=proxy)
    return AiohttpSession()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    value = token()
    if not value:
        raise SystemExit("TELEGRAM_BOT_TOKEN is missing. Put it in .env")
    init_db()
    bot = Bot(
        value,
        session=telegram_session(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
