"""Navigation, wizards, and actions."""

from __future__ import annotations

import csv
from datetime import date
from io import StringIO

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

from . import db, screens
from .i18n import labels
from .keyboards import kb, reply_menu

router = Router()


class Flow(StatesGroup):
    step = State()


def _t(user) -> dict:
    return labels(user.get("lang") or "uz")


def _uid(event) -> int:
    return event.from_user.id


async def open_screen(event, screen: str, page: int = 0, state: FSMContext | None = None):
    user = db.get_user(_uid(event))
    if user.get("mode") in {"guest", "registered"} and screen in {"menu", "dash", "org", "tax", "bank", "pay", "asset", "tmz", "ehf", "hr"}:
        db.ensure_company(user["telegram_id"])
    if screen == "menu":
        screen = "home"
        user = db.get_user(_uid(event))
        if user.get("mode") in {"guest", "registered"}:
            text, markup = screens.scr_menu(user, _t(user), [], 0)
        else:
            text, markup = screens.render(user, _t(user), "home", 0)
    else:
        text, markup = screens.render(user, _t(user), screen, page)
    reply = reply_menu(_t(user))
    if isinstance(event, CallbackQuery):
        await event.answer()
        try:
            await event.message.edit_text(text, reply_markup=markup)
        except Exception:
            await event.message.answer(text, reply_markup=markup)
    else:
        await event.answer(text, reply_markup=markup)
        if screen in {"home", "menu"} or (isinstance(event, Message) and event.text and event.text.startswith("🏠")):
            await event.answer(_t(user)["menu_btn"], reply_markup=reply)


MENU_TEXTS = {"🏠 Menyu", "🏠 Меню", "🏠 Menu", "🌐 Til", "🌐 Язык", "🌐 Language"}


def is_menu_text(text: str) -> bool:
    return (text or "").strip() in MENU_TEXTS or (text or "").startswith("🏠") or (text or "").startswith("🌐")


async def begin_flow(message: Message, state: FSMContext, flow: str, preset: dict | None = None, user_id: int | None = None):
    user = db.get_user(user_id or message.from_user.id)
    t = _t(user)
    await state.set_state(Flow.step)
    await state.update_data(flow=flow, step=0, answers=preset or {})
    prompt = FLOW_STEPS[flow][0][1]
    await message.answer(t[prompt], reply_markup=kb([[(t["cancel"], "do:cancel")]]))


FLOW_STEPS = {
    "reg": [("stir", "enter_stir"), ("password", "enter_pw"), ("password2", "enter_pw2"), ("phone", "enter_phone")],
    "director": [("director_name", "dir_name"), ("director_position", "dir_pos"), ("director_phone", "dir_phone"), ("director_email", "dir_email")],
    "accountant": [("accountant_name", "acc_name2"), ("accountant_position", "acc_pos"), ("accountant_phone", "acc_phone"), ("accountant_email", "acc_email")],
    "phone": [("phone", "enter_phone"), ("role", "role")],
    "doc": [("name", "doc_name"), ("file", "need_file")],
    "account": [("kind", "acc_kind"), ("number", "acc_no"), ("mfo", "mfo"), ("bank", "bank_name")],
    "bankup": [("start", "d_start"), ("end", "d_end"), ("file", "send_file")],
    "opedit": [("debit_acc", "debit_acc"), ("credit_acc", "credit_acc")],
    "pay": [("name", "tax_type"), ("code", "tax_code"), ("amount", "amount"), ("pay_date", "pay_date"), ("note", "note")],
    "asset": [("name", "asset_name"), ("buy_date", "buy_date"), ("initial", "initial"), ("rate", "rate"), ("place", "place"), ("person", "person")],
    "tmz": [("name", "prod_name"), ("unit", "unit"), ("price", "price"), ("qty", "qty"), ("warehouse", "wh")],
    "tmzxls": [("file", "excel_hint")],
    "emp": [
        ("fio", "emp_fio"), ("pinfl", "emp_pin"), ("birth", "emp_birth"), ("phone", "emp_phone"),
        ("position", "emp_pos"), ("dept", "emp_dept"), ("hired", "emp_hired"), ("salary", "emp_salary"),
    ],
    "empedit": [("value", "new_value")],
    "packet": [("packet", "packet_enter")],
    "ehfdraft": [("doc_type", "create"), ("counterparty", "reg_company"), ("amount", "amount")],
}

FILE_KEYS = {"file"}


def _check_step(flow: str, key: str, message: Message, answers: dict, t: dict):
    if key in FILE_KEYS:
        if not message.document:
            return t["need_file"]
        return None
    if not message.text:
        return t["need_text"]
    text = message.text.strip()
    if key == "stir" and (not text.isdigit() or len(text) != 9):
        return t["bad_stir"]
    if key == "password":
        flags = db.password_ok(text)
        lines = [
            ("✅" if flags["len"] else "▫️") + " " + t["pw_len"],
            ("✅" if flags["upper"] else "▫️") + " " + t["pw_upper"],
            ("✅" if flags["lower"] else "▫️") + " " + t["pw_lower"],
            ("✅" if flags["digit"] else "▫️") + " " + t["pw_digit"],
            ("✅" if flags["special"] else "▫️") + " " + t["pw_special"],
        ]
        if not all(flags.values()):
            return t["pw_fail"] + "\n" + "\n".join(lines)
    if key == "password2" and text != answers.get("password"):
        return t["pw_mismatch"]
    if key in {"start", "end", "buy_date", "pay_date", "birth", "hired"} and not db.parse_date(text):
        return t["bad_date"]
    if key in {"initial", "price", "qty", "salary", "amount", "rate"}:
        cleaned = text.replace(" ", "").replace(",", ".")
        try:
            float(cleaned)
        except ValueError:
            return t["need_text"]
    return None


async def _finish(message: Message, state: FSMContext, flow: str, answers: dict):
    uid = message.from_user.id
    user = db.get_user(uid)
    t = _t(user)
    if flow == "director":
        db.q(
            """UPDATE org SET director_name=?, director_position=?, director_phone=?, director_email=? WHERE telegram_id=?""",
            (answers["director_name"], answers["director_position"], answers["director_phone"], answers["director_email"], uid),
        )
    elif flow == "accountant":
        db.q(
            """UPDATE org SET accountant_name=?, accountant_position=?, accountant_phone=?, accountant_email=? WHERE telegram_id=?""",
            (answers["accountant_name"], answers["accountant_position"], answers["accountant_phone"], answers["accountant_email"], uid),
        )
    elif flow == "phone":
        db.q("INSERT INTO org_phones(telegram_id, phone, role) VALUES (?,?,?)", (uid, answers["phone"], answers["role"]))
    elif flow == "doc":
        path = await _save_doc(message, uid)
        db.q(
            "INSERT INTO org_docs(telegram_id, name, filename, uploaded, path) VALUES (?,?,?,?,?)",
            (uid, answers["name"], message.document.file_name, date.today().strftime("%d.%m.%Y"), path),
        )
    elif flow == "account":
        db.q(
            """INSERT INTO org_accounts(telegram_id, kind, number, mfo, bank, balance, last_start, last_end)
               VALUES (?,?,?,?,?,?,?,?)""",
            (uid, answers["kind"], answers["number"], answers["mfo"], answers["bank"], "0", "", ""),
        )
    elif flow == "bankup":
        await _finish_bank(message, uid, t, answers)
        await state.clear()
        await open_screen(message, "bank:turn")
        return
    elif flow == "opedit":
        db.q(
            "UPDATE bank_ops SET debit_acc=?, credit_acc=?, suggestion=? WHERE id=? AND telegram_id=?",
            (answers["debit_acc"], answers["credit_acc"], f"Dt {answers['debit_acc']} Kt {answers['credit_acc']}", answers["op_id"], uid),
        )
    elif flow == "pay":
        number = f"TP-{date.today().year}-{db.q('SELECT COUNT(*) AS c FROM payments WHERE telegram_id=?', (uid,), one=True)['c'] + 1:04d}"
        db.q(
            """INSERT INTO payments(telegram_id, number, code, name, pay_date, amount, status, note)
               VALUES (?,?,?,?,?,?,?,?)""",
            (uid, number, answers["code"], answers["name"], answers["pay_date"], answers["amount"], "Loyiha", answers["note"]),
        )
        answers["payment_status"] = "draft"
    elif flow == "asset":
        grp = answers.get("grp") or "other"
        initial = int(float(answers["initial"].replace(" ", "").replace(",", ".")))
        rate = float(answers["rate"].replace(",", ".")) / 100
        count = db.q("SELECT COUNT(*) AS c FROM assets WHERE telegram_id=?", (uid,), one=True)["c"] + 1
        db.q(
            """INSERT INTO assets(telegram_id, inv, name, grp, buy_date, initial, rate, place, responsible, status, source, locked)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,0)""",
            (uid, f"AV-{count:03d}", answers["name"], grp, answers["buy_date"], initial, rate, answers["place"], answers["person"], "Aktiv", "manual"),
        )
    elif flow == "tmz":
        cost = int(float(answers["price"].replace(" ", "").replace(",", ".")))
        qty = float(answers["qty"].replace(",", "."))
        count = db.q("SELECT COUNT(*) AS c FROM tmz_items WHERE telegram_id=?", (uid,), one=True)["c"] + 1
        db.q(
            "INSERT INTO tmz_items(telegram_id, code, name, unit, warehouse, qty, cost) VALUES (?,?,?,?,?,?,?)",
            (uid, f"TMZ-{count:03d}", answers["name"], answers["unit"], answers["warehouse"], qty, cost),
        )
        db.q(
            "INSERT INTO tmz_moves(telegram_id, op_date, op_type, doc, product, qty) VALUES (?,?,?,?,?,?)",
            (uid, date.today().strftime("%d.%m.%Y"), "Kirim", "QO‘LDA", answers["name"], qty),
        )
    elif flow == "tmzxls":
        await _import_tmz(message, uid)
    elif flow == "emp":
        salary = int(float(answers["salary"].replace(" ", "").replace(",", ".")))
        db.q(
            """INSERT INTO employees(telegram_id, fio, pinfl, birth, phone, position, dept, hired, salary, status,
               passport, contract_type, schedule, card, inps, address)
               VALUES (?,?,?,?,?,?,?,?,?,'Aktiv','','mehnat','to‘liq','','','')""",
            (uid, answers["fio"], answers["pinfl"], answers["birth"], answers["phone"], answers["position"], answers["dept"], answers["hired"], salary),
        )
        db.add_order(uid, answers["fio"], "Ishga qabul qilish", "Avtomatik ishga qabul qilish buyrug'i. my.mehnat.uz keyingi bosqich.")
    elif flow == "empedit":
        field = answers["field"]
        value = answers["value"]
        if field == "salary":
            value = int(float(str(value).replace(" ", "").replace(",", ".")))
        allowed = {"phone", "position", "dept", "salary", "card", "inps", "address"}
        if field in allowed:
            db.q(f"UPDATE employees SET {field}=? WHERE id=? AND telegram_id=?", (value, answers["emp_id"], uid))
    elif flow == "packet":
        await state.clear()
        await open_screen(message, f"tax:journal:{answers['tab']}:{answers['year']}:{answers['packet']}")
        return
    elif flow == "ehfdraft":
        amount = int(float(answers["amount"].replace(" ", "").replace(",", ".")))
        count = db.q("SELECT COUNT(*) AS c FROM ehf_docs WHERE telegram_id=?", (uid,), one=True)["c"] + 1
        db.q(
            """INSERT INTO ehf_docs(telegram_id, direction, status, tab, doc_type, counterparty, stir, number, contract,
               without_vat, vat, with_vat, created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid, "draft", "Loyiha", "draft", answers["doc_type"], answers["counterparty"], "", f"DRAFT-{count:02d}", "",
             amount, 0, amount, date.today().strftime("%d.%m.%Y")),
        )
    await state.clear()
    await message.answer(t["saved"])
    back = {
        "director": "org:main", "accountant": "org:main", "phone": "org:phones", "doc": "org:docs",
        "account": "org:banks", "opedit": "bank:auto:2026:4", "pay": "pay:hist", "asset": "asset:reg:all",
        "tmz": "tmz:reg", "tmzxls": "tmz:reg", "emp": "hr:emp", "empedit": "hr:emp", "ehfdraft": "ehf:draft",
    }.get(flow, "menu")
    await open_screen(message, back)


async def _save_doc(message: Message, uid: int) -> str:
    from aiogram import Bot
    bot: Bot = message.bot
    file = await bot.get_file(message.document.file_id)
    dest = db.user_dir(uid) / (message.document.file_name or "file.bin")
    await bot.download_file(file.file_path, destination=dest)
    return str(dest)


async def _finish_bank(message: Message, uid: int, t: dict, answers: dict):
    account = db.q("SELECT * FROM org_accounts WHERE id=? AND telegram_id=?", (answers["account_id"], uid), one=True)
    start = db.parse_date(answers["start"])
    end = db.parse_date(answers["end"])
    if account and account["last_end"] and not db.consecutive(account["last_end"], start):
        await message.answer(t["gap"])
        return
    path = await _save_doc(message, uid)
    period = f"{db.fmt_date(start)} – {db.fmt_date(end)}"
    db.q(
        """INSERT INTO bank_files(telegram_id, account_id, kind, account_number, bank, period, uploaded, filename, ops_count, path)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (uid, account["id"], account["kind"], account["number"], account["bank"], period,
         date.today().strftime("%d.%m.%Y"), message.document.file_name, 2, path),
    )
    db.q(
        "UPDATE org_accounts SET last_start=?, last_end=? WHERE id=?",
        (db.iso(start), db.iso(end), account["id"]),
    )
    db.q(
        """INSERT INTO bank_ops(telegram_id, year, month, op_date, doc_no, counterparty, stir, purpose,
           money_in, money_out, debit_acc, credit_acc, suggestion, status, low_confidence)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (uid, start.year, start.month, db.fmt_date(start), "UP-1", "Yuklangan operatsiya", "000000000",
         "Bank aylanmasi", 0, 0, "5110", "6010", "Dt 5110 Kt 6010", "pending", 1),
    )
    await message.answer(t["upload_ok"])


async def _import_tmz(message: Message, uid: int):
    path = await _save_doc(message, uid)
    name = (message.document.file_name or "").lower()
    rows = []
    if name.endswith(".csv") or name.endswith(".txt"):
        raw = open(path, encoding="utf-8-sig").read()
        reader = csv.DictReader(StringIO(raw))
        for row in reader:
            rows.append(row)
    else:
        try:
            from openpyxl import load_workbook
            wb = load_workbook(path, read_only=True)
            sheet = wb.active
            data = list(sheet.iter_rows(values_only=True))
            if data:
                header = [str(c or "").strip().lower() for c in data[0]]
                for values in data[1:]:
                    rows.append({header[i]: values[i] for i in range(min(len(header), len(values)))})
        except Exception:
            rows = []
    for row in rows:
        keys = {k.lower(): v for k, v in row.items()}
        code = keys.get("kod") or keys.get("code") or ""
        title = keys.get("nomi") or keys.get("name") or ""
        unit = keys.get("birligi") or keys.get("unit") or "dona"
        qty = keys.get("miqdor") or keys.get("qty") or 0
        price = keys.get("narx") or keys.get("price") or 0
        if not title:
            continue
        db.q(
            "INSERT INTO tmz_items(telegram_id, code, name, unit, warehouse, qty, cost) VALUES (?,?,?,?,?,?,?)",
            (uid, str(code or "X"), str(title), str(unit), "Asosiy ombor", float(qty or 0), int(float(price or 0))),
        )


@router.message(CommandStart())
async def on_start(message: Message, state: FSMContext):
    await state.clear()
    user = db.get_user(message.from_user.id)
    t = _t(user)
    await message.answer(t["menu_btn"], reply_markup=reply_menu(t))
    await open_screen(message, "home")


@router.message(F.text.in_(MENU_TEXTS))
@router.message(F.text.startswith("🏠"))
@router.message(F.text.startswith("🌐"))
async def on_reply_menu(message: Message, state: FSMContext):
    await state.clear()
    if (message.text or "").startswith("🌐"):
        await open_screen(message, "lang")
    else:
        await open_screen(message, "menu")


@router.callback_query(F.data == "noop")
async def on_noop(cb: CallbackQuery):
    await cb.answer()


@router.callback_query(F.data == "do:cancel")
async def on_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await open_screen(cb, "menu", state=state)


@router.callback_query(F.data.startswith("nav:"))
async def on_nav(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await open_screen(cb, cb.data[4:], 0, state)


@router.callback_query(F.data.startswith("pg:"))
async def on_page(cb: CallbackQuery):
    body = cb.data[3:]
    screen, page_s = body.rsplit(":", 1)
    await open_screen(cb, screen, int(page_s))


@router.callback_query(F.data.startswith("do:"))
async def on_do(cb: CallbackQuery, state: FSMContext):
    user = db.get_user(cb.from_user.id)
    t = _t(user)
    parts = cb.data.split(":")
    action = parts[1]
    await cb.answer()

    if action == "lang":
        db.update_user(cb.from_user.id, lang=parts[2])
        await open_screen(cb, "menu")
        return
    if action == "guest":
        db.update_user(cb.from_user.id, mode="guest", company_name=user.get("company_name") or "Mehmon (Demo)", tariff="Guest / Demo")
        db.ensure_company(cb.from_user.id)
        await cb.message.answer(t["guest_ok"])
        await open_screen(cb, "menu")
        return
    if action == "logout":
        db.update_user(cb.from_user.id, mode="")
        await cb.message.answer(t["logged_out"])
        await open_screen(cb, "home")
        return
    if action == "reg":
        await begin_flow(cb.message, state, "reg", user_id=cb.from_user.id)
        return
    if action == "oferta":
        data = await state.get_data()
        answers = data.get("answers") or {}
        if parts[2] == "no":
            await state.clear()
            await cb.message.answer(t["cancel"])
            await open_screen(cb, "home")
            return
        today = date.today().strftime("%d.%m.%Y")
        db.update_user(
            cb.from_user.id,
            mode="registered",
            stir=answers.get("stir"),
            company_name="Demo Korxona MChJ",
            password_hash=db.hash_password(answers.get("password", "")),
            phone=answers.get("phone"),
            reg_date=today,
            tariff="Standart",
            tariff_until="08.10.2027",
            payment_due="08.11.2026",
        )
        db.ensure_company(cb.from_user.id)
        db.q("UPDATE org SET stir=?, name=? WHERE telegram_id=?", (answers.get("stir"), "Demo Korxona MChJ", cb.from_user.id))
        await state.clear()
        await cb.message.answer(t["reg_ok"] + "\n" + t["company_locked"] + ": Demo Korxona MChJ")
        await open_screen(cb, "menu")
        return
    if user.get("mode") not in {"guest", "registered"}:
        await cb.message.answer(t["guest"])
        return
    db.ensure_company(cb.from_user.id)

    if action == "edit":
        await begin_flow(cb.message, state, parts[2], user_id=cb.from_user.id)
        return
    if action == "addphone":
        await begin_flow(cb.message, state, "phone", user_id=cb.from_user.id)
        return
    if action == "delphone":
        await cb.message.answer(t["delete_ask"], reply_markup=kb([[(t["yes"], f"do:delphoneok:{parts[2]}"), (t["no"], "nav:org:phones")]]))
        return
    if action == "delphoneok":
        db.q("DELETE FROM org_phones WHERE id=? AND telegram_id=?", (int(parts[2]), cb.from_user.id))
        await open_screen(cb, "org:phones")
        return
    if action == "adddoc":
        await begin_flow(cb.message, state, "doc", user_id=cb.from_user.id)
        return
    if action == "deldoc":
        await cb.message.answer(t["delete_ask"], reply_markup=kb([[(t["yes"], f"do:deldocok:{parts[2]}"), (t["no"], "nav:org:docs")]]))
        return
    if action == "deldocok":
        db.q("DELETE FROM org_docs WHERE id=? AND telegram_id=?", (int(parts[2]), cb.from_user.id))
        await open_screen(cb, "org:docs")
        return
    if action == "addacc":
        await begin_flow(cb.message, state, "account", user_id=cb.from_user.id)
        return
    if action == "bankup":
        await begin_flow(cb.message, state, "bankup", {"account_id": int(parts[2])}, user_id=cb.from_user.id)
        return
    if action == "opok":
        op = db.q("SELECT * FROM bank_ops WHERE id=? AND telegram_id=?", (int(parts[2]), cb.from_user.id), one=True)
        db.q("UPDATE bank_ops SET status='confirmed' WHERE id=?", (op["id"],))
        closed = db.try_close_debt(cb.from_user.id, op["stir"], op["money_in"] or 0)
        await cb.message.answer(t["confirmed"] + ("\n" + t["debt_closed"] if closed else ""))
        await open_screen(cb, f"bank:auto:{parts[3]}:{parts[4]}")
        return
    if action == "opall":
        db.q(
            "UPDATE bank_ops SET status='confirmed' WHERE telegram_id=? AND year=? AND month=?",
            (cb.from_user.id, int(parts[2]), int(parts[3])),
        )
        await cb.message.answer(t["confirmed"])
        await open_screen(cb, f"bank:auto:{parts[2]}:{parts[3]}")
        return
    if action == "opedit":
        await begin_flow(cb.message, state, "opedit", {"op_id": int(parts[2])}, user_id=cb.from_user.id)
        return
    if action == "getfile":
        row = db.q("SELECT * FROM bank_files WHERE id=? AND telegram_id=?", (int(parts[2]), cb.from_user.id), one=True)
        if row and row["path"]:
            await cb.message.answer_document(FSInputFile(row["path"]))
        else:
            await cb.message.answer(t["empty"])
        return
    if action == "packet":
        await begin_flow(cb.message, state, "packet", {"tab": parts[2], "year": parts[3]}, user_id=cb.from_user.id)
        return
    if action == "taxform":
        if user.get("mode") == "guest":
            await cb.message.answer(t["guest_block"])
            return
        await cb.message.answer(t["formed"] + " " + parts[2] + "\n" + t["next_integration"])
        return
    if action == "pay":
        await begin_flow(cb.message, state, "pay", user_id=cb.from_user.id)
        return
    if action == "paysend":
        if user.get("mode") == "guest":
            await cb.message.answer(t["guest_block"])
            return
        db.q(
            "UPDATE payments SET status='Jo‘natilgan' WHERE id=? AND telegram_id=?",
            (int(parts[2]), cb.from_user.id),
        )
        await cb.message.answer(t["sent"])
        await open_screen(cb, "pay:hist")
        return
    if action == "asset":
        await cb.message.answer(t["group"], reply_markup=kb([
            [("🏢", "do:assetg:building"), ("🚗", "do:assetg:transport"), ("💻", "do:assetg:it")],
            [("🏭", "do:assetg:equipment"), ("🪑", "do:assetg:furniture"), ("⚙️", "do:assetg:other")],
        ]))
        return
    if action == "assetg":
        await begin_flow(cb.message, state, "asset", {"grp": parts[2]}, user_id=cb.from_user.id)
        return
    if action == "export":
        year, month = int(parts[2]), int(parts[3])
        items = db.rows("assets", cb.from_user.id)
        path = db.user_dir(cb.from_user.id) / f"amortizatsiya_{year}_{month}.csv"
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["inv", "name", "monthly", "accumulated", "residual"])
            for asset in items:
                calc = db.depreciation_row(asset, year, month)
                writer.writerow([asset["inv"], asset["name"], calc["monthly"], calc["accumulated"], calc["residual"]])
        await cb.message.answer_document(FSInputFile(path))
        return
    if action == "tmz":
        await begin_flow(cb.message, state, "tmz", user_id=cb.from_user.id)
        return
    if action == "tmzxls":
        await begin_flow(cb.message, state, "tmzxls", user_id=cb.from_user.id)
        return
    if action == "tmzehf":
        for name, unit, qty, cost in (("Shakar", "kg", 100, 12000), ("Yog'", "dona", 50, 45000)):
            current = db.q(
                "SELECT * FROM tmz_items WHERE telegram_id=? AND name=?",
                (cb.from_user.id, name),
                one=True,
            )
            if current:
                db.q("UPDATE tmz_items SET qty=qty+? WHERE id=?", (qty, current["id"]))
            else:
                db.q(
                    "INSERT INTO tmz_items(telegram_id, code, name, unit, warehouse, qty, cost) VALUES (?,?,?,?,?,?,?)",
                    (cb.from_user.id, name[:3].upper(), name, unit, "Asosiy ombor", qty, cost),
                )
            db.q(
                "INSERT INTO tmz_moves(telegram_id, op_date, op_type, doc, product, qty) VALUES (?,?,?,?,?,?)",
                (cb.from_user.id, date.today().strftime("%d.%m.%Y"), "Kirim", "EHF", name, qty),
            )
        await cb.message.answer(t["ehf_applied"])
        await open_screen(cb, "tmz:reg")
        return
    if action == "ehfdraft":
        await begin_flow(cb.message, state, "ehfdraft", user_id=cb.from_user.id)
        return
    if action == "ehfsend":
        if user.get("mode") == "guest":
            await cb.message.answer(t["guest_block"])
            return
        doc = db.q("SELECT * FROM ehf_docs WHERE id=? AND telegram_id=?", (int(parts[2]), cb.from_user.id), one=True)
        if doc:
            db.q("UPDATE ehf_docs SET direction='out', status='Jo‘natilgan', tab='sent' WHERE id=?", (doc["id"],))
            if doc["with_vat"]:
                db.q(
                    """INSERT INTO recon(telegram_id, name, stir, contract, ehf, debit, credit, last_op, status)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (cb.from_user.id, doc["counterparty"], doc["stir"] or "000000000", doc["contract"] or "—",
                     doc["number"], doc["with_vat"], 0, date.today().strftime("%d.%m.%Y"), "Debitor"),
                )
        await cb.message.answer(t["sent"])
        await open_screen(cb, "ehf:out")
        return
    if action == "emp":
        await begin_flow(cb.message, state, "emp", user_id=cb.from_user.id)
        return
    if action == "empedit":
        await cb.message.answer(
            t["edit"],
            reply_markup=kb([
                [("Telefon", f"do:empf:{parts[2]}:phone"), ("Lavozim", f"do:empf:{parts[2]}:position")],
                [("Bo'lim", f"do:empf:{parts[2]}:dept"), ("Oylik", f"do:empf:{parts[2]}:salary")],
                [("Karta", f"do:empf:{parts[2]}:card"), ("INPS", f"do:empf:{parts[2]}:inps")],
                [("Manzil", f"do:empf:{parts[2]}:address")],
            ]),
        )
        return
    if action == "empf":
        await begin_flow(cb.message, state, "empedit", {"emp_id": int(parts[2]), "field": parts[3]}, user_id=cb.from_user.id)
        return
    if action == "fireask":
        await cb.message.answer(
            t["fired_ask"],
            reply_markup=kb([[(t["yes"], f"do:fireok:{parts[2]}"), (t["no"], "nav:hr:emp")]]),
        )
        return
    if action == "fireok":
        emp = db.q("SELECT * FROM employees WHERE id=? AND telegram_id=?", (int(parts[2]), cb.from_user.id), one=True)
        if emp and emp["status"] == "Aktiv":
            db.q("UPDATE employees SET status=? WHERE id=?", ("Bo‘shagan", emp["id"]))
            db.add_order(cb.from_user.id, emp["fio"], "Ishdan bo‘shatish", "Ishdan bo'shatish. Keyingi davr ish haqi 0. my.mehnat.uz keyingi bosqich.")
        await cb.message.answer(t["fired_ok"])
        await open_screen(cb, "hr:emp")
        return
    if action == "orderfile":
        row = db.q("SELECT * FROM hr_orders WHERE id=? AND telegram_id=?", (int(parts[2]), cb.from_user.id), one=True)
        if row and row["body"] and row["body"].endswith(".txt"):
            await cb.message.answer_document(FSInputFile(row["body"]))
        elif row:
            path = db.user_dir(cb.from_user.id) / f"{row['number']}.txt"
            path.write_text(
                f"{row['number']}\n{row['order_date']}\n{row['employee']}\n{row['order_type']}\nQR: FA-{row['number']}\n",
                encoding="utf-8",
            )
            db.q("UPDATE hr_orders SET body=? WHERE id=?", (str(path), row["id"]))
            await cb.message.answer_document(FSInputFile(path))
        return


@router.message(StateFilter(Flow.step))
async def on_flow(message: Message, state: FSMContext):
    if is_menu_text(message.text or "") or (message.text or "").startswith("/"):
        return
    data = await state.get_data()
    flow = data.get("flow")
    step = int(data.get("step") or 0)
    answers = dict(data.get("answers") or {})
    user = db.get_user(message.from_user.id)
    t = _t(user)
    if flow not in FLOW_STEPS:
        await state.clear()
        return
    key, prompt_key = FLOW_STEPS[flow][step]
    error = _check_step(flow, key, message, answers, t)
    if error:
        await message.answer(error, reply_markup=kb([[(t["cancel"], "do:cancel")]]))
        return
    if key in FILE_KEYS:
        answers[key] = message.document.file_name
    else:
        answers[key] = message.text.strip()
        if key == "stir":
            await message.answer(t["company_locked"] + ": Demo Korxona MChJ\n" + t["next_integration"])
        if key == "password":
            flags = db.password_ok(message.text.strip())
            checklist = "\n".join([
                ("✅" if flags["len"] else "▫️") + " " + t["pw_len"],
                ("✅" if flags["upper"] else "▫️") + " " + t["pw_upper"],
                ("✅" if flags["lower"] else "▫️") + " " + t["pw_lower"],
                ("✅" if flags["digit"] else "▫️") + " " + t["pw_digit"],
                ("✅" if flags["special"] else "▫️") + " " + t["pw_special"],
            ])
            await message.answer(checklist)
    step += 1
    if flow == "reg" and step >= len(FLOW_STEPS[flow]):
        await state.update_data(step=step, answers=answers)
        await message.answer(t["oferta_ask"], reply_markup=kb([[(t["yes"], "do:oferta:yes"), (t["no"], "do:oferta:no")]]))
        return
    if step >= len(FLOW_STEPS[flow]):
        await state.update_data(answers=answers)
        await _finish(message, state, flow, answers)
        return
    await state.update_data(step=step, answers=answers)
    nxt = FLOW_STEPS[flow][step][1]
    await message.answer(t[nxt], reply_markup=kb([[(t["cancel"], "do:cancel")]]))
