"""SQLite storage and demo seed for one company per Telegram user."""

from __future__ import annotations

import hashlib
import os
import sqlite3
import threading
from datetime import date, datetime, timedelta

from .config import DB_PATH, STORAGE

_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    lang TEXT NOT NULL DEFAULT 'uz',
    mode TEXT NOT NULL DEFAULT '',
    stir TEXT,
    company_name TEXT,
    password_hash TEXT,
    phone TEXT,
    reg_date TEXT,
    tariff TEXT,
    tariff_until TEXT,
    payment_due TEXT
);
CREATE TABLE IF NOT EXISTS org (
    telegram_id INTEGER PRIMARY KEY,
    stir TEXT, oked TEXT, soogu TEXT, name TEXT, tax_type TEXT,
    director_name TEXT, director_position TEXT, director_phone TEXT, director_email TEXT,
    accountant_name TEXT, accountant_position TEXT, accountant_phone TEXT, accountant_email TEXT
);
CREATE TABLE IF NOT EXISTS org_docs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, name TEXT, filename TEXT, uploaded TEXT, path TEXT
);
CREATE TABLE IF NOT EXISTS org_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, kind TEXT, number TEXT, mfo TEXT, bank TEXT,
    balance TEXT, last_start TEXT, last_end TEXT
);
CREATE TABLE IF NOT EXISTS org_phones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, phone TEXT, role TEXT
);
CREATE TABLE IF NOT EXISTS tax_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, name TEXT, period TEXT, packet TEXT,
    sent TEXT, status TEXT, updated TEXT, tab TEXT, year TEXT
);
CREATE TABLE IF NOT EXISTS bank_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, account_id INTEGER, kind TEXT, account_number TEXT,
    bank TEXT, period TEXT, uploaded TEXT, filename TEXT, ops_count INTEGER, path TEXT
);
CREATE TABLE IF NOT EXISTS bank_ops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, year INTEGER, month INTEGER, op_date TEXT, doc_no TEXT,
    counterparty TEXT, stir TEXT, purpose TEXT, money_in INTEGER, money_out INTEGER,
    debit_acc TEXT, credit_acc TEXT, suggestion TEXT, status TEXT, low_confidence INTEGER
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, number TEXT, code TEXT, name TEXT, pay_date TEXT,
    amount TEXT, status TEXT, note TEXT
);
CREATE TABLE IF NOT EXISTS recon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, name TEXT, stir TEXT, contract TEXT, ehf TEXT,
    debit INTEGER, credit INTEGER, last_op TEXT, status TEXT
);
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, inv TEXT, name TEXT, grp TEXT, buy_date TEXT,
    initial INTEGER, rate REAL, place TEXT, responsible TEXT, status TEXT,
    source TEXT, locked INTEGER
);
CREATE TABLE IF NOT EXISTS tmz_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, code TEXT, name TEXT, unit TEXT, warehouse TEXT,
    qty REAL, cost INTEGER
);
CREATE TABLE IF NOT EXISTS tmz_moves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, op_date TEXT, op_type TEXT, doc TEXT, product TEXT, qty REAL
);
CREATE TABLE IF NOT EXISTS ehf_docs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, direction TEXT, status TEXT, tab TEXT, doc_type TEXT,
    counterparty TEXT, stir TEXT, number TEXT, contract TEXT,
    without_vat INTEGER, vat INTEGER, with_vat INTEGER, created TEXT
);
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, number TEXT, party TEXT, status_key TEXT, status TEXT
);
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, fio TEXT, pinfl TEXT, birth TEXT, phone TEXT,
    position TEXT, dept TEXT, hired TEXT, salary INTEGER, status TEXT,
    passport TEXT, contract_type TEXT, schedule TEXT, card TEXT, inps TEXT, address TEXT
);
CREATE TABLE IF NOT EXISTS hr_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER, number TEXT, order_date TEXT, employee TEXT,
    order_type TEXT, status TEXT, body TEXT
);
"""


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    STORAGE.mkdir(parents=True, exist_ok=True)
    with _lock:
        conn = _conn()
        try:
            conn.executescript(SCHEMA)
            conn.commit()
        finally:
            conn.close()


def q(sql: str, params: tuple = (), one: bool = False, many: bool = False):
    with _lock:
        conn = _conn()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            if one:
                row = cur.fetchone()
                return dict(row) if row else None
            if many:
                return [dict(r) for r in cur.fetchall()]
            return cur.lastrowid
        finally:
            conn.close()


def money(value: int | float) -> str:
    return f"{int(round(value)):,}".replace(",", " ")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return salt.hex() + ":" + digest.hex()


def password_ok(password: str) -> dict:
    return {
        "len": len(password) >= 8,
        "upper": any(c.isupper() for c in password),
        "lower": any(c.islower() for c in password),
        "digit": any(c.isdigit() for c in password),
        "special": any(not c.isalnum() for c in password),
    }


def parse_date(text: str) -> date | None:
    raw = (text or "").strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def fmt_date(value: date | str) -> str:
    if isinstance(value, str):
        parsed = parse_date(value) or datetime.strptime(value, "%Y-%m-%d").date()
        return parsed.strftime("%d.%m.%Y")
    return value.strftime("%d.%m.%Y")


def iso(value: date) -> str:
    return value.isoformat()


def get_user(telegram_id: int) -> dict:
    row = q("SELECT * FROM users WHERE telegram_id=?", (telegram_id,), one=True)
    if not row:
        q("INSERT INTO users(telegram_id, lang) VALUES(?, 'uz')", (telegram_id,))
        row = q("SELECT * FROM users WHERE telegram_id=?", (telegram_id,), one=True)
    return row


def update_user(telegram_id: int, **fields) -> None:
    if not fields:
        return
    cols = ", ".join(f"{key}=?" for key in fields)
    q(f"UPDATE users SET {cols} WHERE telegram_id=?", tuple(fields.values()) + (telegram_id,))


def ensure_company(telegram_id: int) -> None:
    if q("SELECT telegram_id FROM org WHERE telegram_id=?", (telegram_id,), one=True):
        return
    user = get_user(telegram_id)
    name = user.get("company_name") or "Demo Korxona MChJ"
    stir = user.get("stir") or "305556789"
    q(
        """INSERT INTO org VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            telegram_id, stir, "62010", "12345", name, "QQS to‘lovchisi",
            "Rahimov Aziz", "Direktor", "+998 90 111 22 33", "rahimov@demo.uz",
            "Karimova Dilnoza", "Bosh buxgalter", "+998 93 444 55 66", "dilnoza@demo.uz",
        ),
    )
    q(
        "INSERT INTO org_docs(telegram_id, name, filename, uploaded, path) VALUES (?,?,?,?,?)",
        (telegram_id, "Korxona guvohnomasi", "guvohnoma.pdf", "01.02.2026", ""),
    )
    q(
        "INSERT INTO org_docs(telegram_id, name, filename, uploaded, path) VALUES (?,?,?,?,?)",
        (telegram_id, "Korxona ustavi", "ustav.pdf", "01.02.2026", ""),
    )
    q(
        """INSERT INTO org_accounts(telegram_id, kind, number, mfo, bank, balance, last_start, last_end)
           VALUES (?,?,?,?,?,?,?,?)""",
        (telegram_id, "Asosiy hisob raqami", "20208000486684884001", "00580",
         "Ipoteka bank, Tinchlik filiali", "125 450 000 so'm", "2026-01-01", "2026-03-31"),
    )
    q(
        """INSERT INTO org_accounts(telegram_id, kind, number, mfo, bank, balance, last_start, last_end)
           VALUES (?,?,?,?,?,?,?,?)""",
        (telegram_id, "2-hisob raqami", "20208000999887766002", "00014",
         "Hamkorbank", "42 100 000 so'm", "2026-01-01", "2026-03-31"),
    )
    q(
        """INSERT INTO org_accounts(telegram_id, kind, number, mfo, bank, balance, last_start, last_end)
           VALUES (?,?,?,?,?,?,?,?)""",
        (telegram_id, "Valyuta hisob raqami", "20208800111222333003", "00445",
         "Kapitalbank", "12 500 USD", "2026-01-01", "2026-03-31"),
    )
    q("INSERT INTO org_phones(telegram_id, phone, role) VALUES (?,?,?)",
      (telegram_id, "+998 90 111 22 33", "rahbar"))
    q("INSERT INTO org_phones(telegram_id, phone, role) VALUES (?,?,?)",
      (telegram_id, "+998 93 444 55 66", "bosh buxgalter"))
    for row in (
        ("QQS hisoboti", "1-chorak 2026", "P-10021", "15.04.2026", "Qabul qilingan", "16.04.2026", "accepted", "2026"),
        ("JShDS", "Mart 2026", "P-10045", "10.04.2026", "Qabul qilingan", "11.04.2026", "accepted", "2026"),
    ):
        q(
            """INSERT INTO tax_reports(telegram_id, name, period, packet, sent, status, updated, tab, year)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (telegram_id, *row),
        )
    q(
        """INSERT INTO bank_files(telegram_id, account_id, kind, account_number, bank, period, uploaded, filename, ops_count, path)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (telegram_id, 0, "Asosiy", "20208000486684884001", "Ipoteka bank",
         "01.01.2026 – 31.03.2026", "01.04.2026", "oborotka_Q1.xlsx", 128, ""),
    )
    q(
        """INSERT INTO bank_files(telegram_id, account_id, kind, account_number, bank, period, uploaded, filename, ops_count, path)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (telegram_id, 0, "Asosiy", "20208000486684884001", "Ipoteka bank",
         "01.04.2026 – 30.06.2026", "01.07.2026", "oborotka_Q2.xlsx", 154, ""),
    )
    q(
        """INSERT INTO bank_files(telegram_id, account_id, kind, account_number, bank, period, uploaded, filename, ops_count, path)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (telegram_id, 0, "Ikkilamchi", "20208000999887766002", "Hamkorbank",
         "01.01.2026 – 31.03.2026", "01.04.2026", "hamkor_Q1.xlsx", 64, ""),
    )
    q(
        """INSERT INTO bank_ops(telegram_id, year, month, op_date, doc_no, counterparty, stir, purpose,
           money_in, money_out, debit_acc, credit_acc, suggestion, status, low_confidence)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (telegram_id, 2026, 4, "12.04.2026", "145", '"SARDORBEK SERVIS" MCHJ', "305556789",
         "Ko‘rsatilgan xizmatlar uchun to‘lov", 1000000, 0, "5110", "6010",
         "Dt 5110 Kt 6010", "pending", 0),
    )
    q(
        """INSERT INTO bank_ops(telegram_id, year, month, op_date, doc_no, counterparty, stir, purpose,
           money_in, money_out, debit_acc, credit_acc, suggestion, status, low_confidence)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (telegram_id, 2026, 4, "18.04.2026", "188", "Ofis ijarasi", "300000001",
         "Ijara to‘lovi", 0, 2500000, "9430", "5110", "Dt 9430 Kt 5110", "pending", 1),
    )
    q(
        """INSERT INTO payments(telegram_id, number, code, name, pay_date, amount, status, note)
           VALUES (?,?,?,?,?,?,?,?)""",
        (telegram_id, "TP-2026-0142", "101010", "QQS", "15.03.2026", "12 450 000", "Qabul qilingan", ""),
    )
    q(
        """INSERT INTO payments(telegram_id, number, code, name, pay_date, amount, status, note)
           VALUES (?,?,?,?,?,?,?,?)""",
        (telegram_id, "TP-2026-0188", "103010", "JShDS", "05.04.2026", "3 200 000", "Jo‘natilgan", ""),
    )
    q(
        """INSERT INTO recon(telegram_id, name, stir, contract, ehf, debit, credit, last_op, status)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (telegram_id, '"SARDORBEK SERVIS" MCHJ', "305556789", "SH-45/26", "EHF-8891",
         1000000, 0, "12.04.2026", "Debitor"),
    )
    q(
        """INSERT INTO recon(telegram_id, name, stir, contract, ehf, debit, credit, last_op, status)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (telegram_id, '"ORIENT TRADE" MCHJ', "301112233", "SH-12/26", "EHF-9022",
         0, 4500000, "01.04.2026", "Kreditorka"),
    )
    assets = (
        ("AV-001", "Ofis binosi", "building", "01.01.2020", 1_200_000_000, 0.05, "Toshkent, Yakkasaroy", "Rahimov A.", "Aktiv", "my.soliq.uz", 1),
        ("AV-014", "Chevrolet Cobalt", "transport", "15.06.2023", 145_000_000, 0.20, "Asosiy ofis", "Karimov B.", "Aktiv", "manual", 0),
        ("AV-088", "Dell OptiPlex", "it", "10.02.2025", 8_500_000, 0.40, "Buxgalteriya", "Usmonova D.", "Aktiv", "manual", 0),
    )
    for item in assets:
        q(
            """INSERT INTO assets(telegram_id, inv, name, grp, buy_date, initial, rate, place, responsible, status, source, locked)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (telegram_id, *item),
        )
    q(
        "INSERT INTO tmz_items(telegram_id, code, name, unit, warehouse, qty, cost) VALUES (?,?,?,?,?,?,?)",
        (telegram_id, "TMZ-001", "Shakar", "kg", "Asosiy ombor", 100, 12000),
    )
    q(
        "INSERT INTO tmz_items(telegram_id, code, name, unit, warehouse, qty, cost) VALUES (?,?,?,?,?,?,?)",
        (telegram_id, "TMZ-002", "Yog'", "dona", "Savdo ombori", 50, 45000),
    )
    q(
        "INSERT INTO tmz_moves(telegram_id, op_date, op_type, doc, product, qty) VALUES (?,?,?,?,?,?)",
        (telegram_id, "02.04.2026", "Kirim", "EHF-8891", "Shakar", 100),
    )
    q(
        "INSERT INTO tmz_moves(telegram_id, op_date, op_type, doc, product, qty) VALUES (?,?,?,?,?,?)",
        (telegram_id, "03.04.2026", "Chiqim", "AKT-12", "Yog'", 5),
    )
    q(
        """INSERT INTO ehf_docs(telegram_id, direction, status, tab, doc_type, counterparty, stir, number, contract,
           without_vat, vat, with_vat, created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (telegram_id, "in", "Imzolangan", "signed", "EHF", '"ORIENT TRADE" MCHJ', "301112233",
         "EHF-9022", "SH-12/26", 3750000, 750000, 4500000, "01.04.2026"),
    )
    q(
        """INSERT INTO ehf_docs(telegram_id, direction, status, tab, doc_type, counterparty, stir, number, contract,
           without_vat, vat, with_vat, created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (telegram_id, "in", "Imzolanishi kutilmoqda", "pending", "Akt", '"SARDORBEK SERVIS" MCHJ',
         "305556789", "AKT-77", "SH-45/26", 1000000, 0, 1000000, "10.04.2026"),
    )
    q(
        """INSERT INTO ehf_docs(telegram_id, direction, status, tab, doc_type, counterparty, stir, number, contract,
           without_vat, vat, with_vat, created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (telegram_id, "draft", "Loyiha", "draft", "Faktura", "Demo LLC", "", "DRAFT-01", "",
         1000000, 0, 1000000, "01.05.2026"),
    )
    q(
        "INSERT INTO contracts(telegram_id, number, party, status_key, status) VALUES (?,?,?,?,?)",
        (telegram_id, "SH-12/26", '"ORIENT TRADE" MCHJ', "active", "Faol"),
    )
    q(
        "INSERT INTO contracts(telegram_id, number, party, status_key, status) VALUES (?,?,?,?,?)",
        (telegram_id, "SH-01/25", '"OLD PARTNER" MCHJ', "ended", "Tugagan"),
    )
    employees = (
        ("Karimova Dilnoza", "31234567890123", "12.03.1992", "+998 90 111 22 33", "Bosh buxgalter", "Buxgalteriya", "01.02.2021", 8500000, "Aktiv"),
        ("Rahimov Aziz", "30111223344556", "05.08.1988", "+998 93 444 55 66", "Direktor", "Boshqaruv", "15.01.2019", 15000000, "Aktiv"),
        ("Usmarov Jasur", "30999887766554", "21.11.1995", "+998 97 777 88 99", "Omborchi", "Ombor", "10.06.2022", 4200000, "Bo‘shagan"),
    )
    for item in employees:
        q(
            """INSERT INTO employees(telegram_id, fio, pinfl, birth, phone, position, dept, hired, salary, status,
               passport, contract_type, schedule, card, inps, address)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (telegram_id, *item, "", "mehnat", "to‘liq", "", "", ""),
        )
    q(
        """INSERT INTO hr_orders(telegram_id, number, order_date, employee, order_type, status, body)
           VALUES (?,?,?,?,?,?,?)""",
        (telegram_id, "BY-001", "01.02.2021", "Karimova Dilnoza", "Ishga qabul qilish", "Yuborilgan", "Ishga qabul qilish buyrug'i"),
    )
    q(
        """INSERT INTO hr_orders(telegram_id, number, order_date, employee, order_type, status, body)
           VALUES (?,?,?,?,?,?,?)""",
        (telegram_id, "BY-088", "01.03.2026", "Usmarov Jasur", "Ishdan bo‘shatish", "Yuborilgan", "Ishdan bo'shatish buyrug'i"),
    )


def org_of(telegram_id: int) -> dict:
    ensure_company(telegram_id)
    return q("SELECT * FROM org WHERE telegram_id=?", (telegram_id,), one=True)


def rows(table: str, telegram_id: int, where: str = "", params: tuple = ()) -> list[dict]:
    sql = f"SELECT * FROM {table} WHERE telegram_id=?"
    if where:
        sql += " AND " + where
    sql += " ORDER BY id"
    return q(sql, (telegram_id, *params), many=True)


def user_dir(telegram_id: int):
    path = STORAGE / str(telegram_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def next_order_no(telegram_id: int) -> str:
    count = q("SELECT COUNT(*) AS c FROM hr_orders WHERE telegram_id=?", (telegram_id,), one=True)["c"]
    return f"BY-{count + 1:03d}"


def add_order(telegram_id: int, employee: str, order_type: str, body: str) -> str:
    number = next_order_no(telegram_id)
    today = date.today().strftime("%d.%m.%Y")
    text = f"{number}\n{today}\n{employee}\n{order_type}\n{body}\nQR: FA-{number}"
    path = user_dir(telegram_id) / f"{number}.txt"
    path.write_text(text, encoding="utf-8")
    q(
        """INSERT INTO hr_orders(telegram_id, number, order_date, employee, order_type, status, body)
           VALUES (?,?,?,?,?,?,?)""",
        (telegram_id, number, today, employee, order_type, "Saqlangan", str(path)),
    )
    return str(path)


def try_close_debt(telegram_id: int, stir: str, amount: int) -> bool:
    row = q(
        "SELECT * FROM recon WHERE telegram_id=? AND stir=? AND debit=?",
        (telegram_id, stir, amount),
        one=True,
    )
    if not row:
        return False
    q(
        "UPDATE recon SET debit=0, status=?, last_op=? WHERE id=?",
        ("Qarzdorlik yopildi", date.today().strftime("%d.%m.%Y"), row["id"]),
    )
    return True


def depreciation_row(asset: dict, year: int, month: int) -> dict:
    monthly = int(asset["initial"] * asset["rate"] / 12)
    buy = datetime.strptime(asset["buy_date"], "%d.%m.%Y").date()
    end = date(year, month, 1)
    months = (end.year - buy.year) * 12 + (end.month - buy.month)
    if end < buy.replace(day=1):
        months = 0
    months = max(0, months)
    accumulated = min(asset["initial"], monthly * months)
    residual = max(0, asset["initial"] - accumulated)
    return {
        "monthly": monthly,
        "yearly": monthly * 12,
        "accumulated": accumulated,
        "residual": residual,
    }


def consecutive(last_end: str, start: date) -> bool:
    if not last_end:
        return True
    last = datetime.strptime(last_end, "%Y-%m-%d").date()
    return start == last + timedelta(days=1)
