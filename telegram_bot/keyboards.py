"""Inline keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def kb(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=data) for text, data in row]
            for row in rows
            if row
        ]
    )


def reply_menu(t: dict) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["menu_btn"])],
            [KeyboardButton(text=t["lang_btn"])],
        ],
        resize_keyboard=True,
    )


def with_back(rows: list[list[tuple[str, str]]], t: dict, back: str) -> InlineKeyboardMarkup:
    rows = list(rows)
    rows.append([(t["back"], f"nav:{back}")])
    return kb(rows)


def pager(screen: str, page: int, pages: int) -> list[tuple[str, str]]:
    nav = []
    if page > 0:
        nav.append(("◀️", f"pg:{screen}:{page - 1}"))
    nav.append((f"{page + 1}/{pages}", "noop"))
    if page + 1 < pages:
        nav.append(("▶️", f"pg:{screen}:{page + 1}"))
    return nav


def slice_page(items: list, page: int, size: int = 5):
    pages = max(1, (len(items) + size - 1) // size)
    page = max(0, min(page, pages - 1))
    start = page * size
    return items[start:start + size], page, pages
