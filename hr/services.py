"""Validation helpers for the HR module."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

CYRILLIC_RE = re.compile(r'^[А-Яа-яЁёІіЇїЄєҒғҚқҢңӨөҮүҰұҺһ0-9\s\.,\-\(\)«»\"\'/:;]+$')
PINFL_RE = re.compile(r'^\d{14}$')
PASSPORT_SERIES_RE = re.compile(r'^[A-Za-z]{2}$')
PASSPORT_NUMBER_RE = re.compile(r'^\d{7}$')


def is_cyrillic_name(value: str) -> bool:
    value = (value or '').strip()
    if not value:
        return True
    return bool(CYRILLIC_RE.match(value))


def parse_date(value: str):
    value = (value or '').strip()
    if not value:
        return None
    for fmt in ('%d.%m.%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def format_date(value) -> str:
    if not value:
        return '—'
    return value.strftime('%d.%m.%Y')


def parse_stavka(whole: str, fraction: str) -> Decimal | None:
    try:
        w = int(whole)
        f = int(fraction)
    except (TypeError, ValueError):
        return None
    if w not in (0, 1):
        return None
    if w == 0 and not (0 <= f <= 99):
        return None
    if w == 1 and not (0 <= f <= 50):
        return None
    return Decimal(f'{w}.{f:02d}')


def parse_money(value: str) -> Decimal | None:
    raw = (value or '').replace(' ', '').replace(',', '.').strip()
    if not raw:
        return None
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        return None
    if amount < 0:
        return None
    return amount


def validate_uz_personal(data: dict) -> list[str]:
    errors = []
    series = (data.get('passport_series') or '').strip().upper()
    number = (data.get('passport_number') or '').strip()
    pinfl = (data.get('pinfl') or '').strip()
    if not PASSPORT_SERIES_RE.match(series):
        errors.append('Pasport seriyasi 2 harf bo‘lishi kerak.')
    if not PASSPORT_NUMBER_RE.match(number):
        errors.append('Pasport raqami 7 raqam bo‘lishi kerak.')
    if not PINFL_RE.match(pinfl):
        errors.append('JShShIR 14 raqamdan iborat bo‘lishi kerak.')
    if not (data.get('last_name') or '').strip():
        errors.append('Familiya majburiy.')
    if not (data.get('first_name') or '').strip():
        errors.append('Ism majburiy.')
    if not parse_date(data.get('birth_date') or ''):
        errors.append('Tug‘ilgan sana noto‘g‘ri.')
    if (data.get('gender') or '') not in ('male', 'female'):
        errors.append('Jinsni tanlang.')
    return errors
