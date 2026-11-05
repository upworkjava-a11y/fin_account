"""Paths and environment for the FinAccount Telegram bot."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = Path(__file__).resolve().parent
STORAGE = PACKAGE / "storage"
DB_PATH = PACKAGE / "bot.sqlite3"


def load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def token() -> str:
    load_env()
    return os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
