"""Text screens that mirror the website modules."""

from __future__ import annotations

import html
from datetime import date

from . import db
from .keyboards import kb, pager, slice_page, with_back

GROUPS = {
    "building": "🏢 Bino va inshootlar",
    "transport": "🚗 Transport vositalari",
    "it": "💻 Kompyuter va ofis texnikasi",
    "equipment": "🏭 Uskunalar va jihozlar",
    "furniture": "🪑 Mebel va inventarlar",
    "other": "⚙️ Boshqa asosiy vositalar",
}
MONTHS = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]
TAX_TABS = [
    ("checking", "tab_checking"),
    ("error", "tab_error"),
    ("accepted", "tab_accepted"),
    ("sent", "tab_sent"),
    ("rejected", "tab_rejected"),
    ("draft", "tab_draft"),
    ("auto", "tab_auto"),
]
EHF_TABS = [
    ("all", "Barchasi"),
    ("pending", "Imzolanishi kutilmoqda"),
    ("signed", "Imzolangan"),
    ("rejected", "Rad etilgan"),
    ("cancelled", "Bekor qilingan"),
]
FORM_CATS = [
    ("tax", "Soliq hisobotlari"),
    ("fin", "Moliyaviy hisobotlar"),
    ("fund", "Budjetdan tashqari"),
    ("other", "Boshqalar"),
]
FORMS = {
    "tax": [("100", "Qo‘shilgan qiymat solig‘i hisoboti"), ("101", "Aylanmadan olinadigan soliq hisoboti"), ("102", "Foyda solig‘i hisoboti")],
    "fin": [("200", "Buxgalteriya balansi"), ("201", "Moliyaviy natijalar to‘g‘risidagi hisobot")],
    "fund": [("300", "INPS reyestri")],
    "other": [("400", "Mol-mulk, yer va suv soliqlari")],
}


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def guest_line(user: dict, t: dict) -> str:
    if user.get("mode") == "guest":
        return f" <i>[{esc(t['guest_badge'])}]</i>"
    return ""


def title(user, t, text) -> str:
    return f"<b>{esc(text)}</b>{guest_line(user, t)}\n"


def render(user: dict, t: dict, screen: str, page: int = 0):
    parts = screen.split(":")
    head = parts[0]
    dispatch = {
        "home": scr_home,
        "dash": scr_dash,
        "lang": scr_lang,
        "profile": scr_profile,
        "why": scr_why,
        "org": scr_org,
        "tax": scr_tax,
        "bank": scr_bank,
        "pay": scr_pay,
        "asset": scr_asset,
        "tmz": scr_tmz,
        "ehf": scr_ehf,
        "hr": scr_hr,
    }
    fn = dispatch.get(head, scr_dash)
    return fn(user, t, parts, page)


def scr_home(user, t, parts, page):
    if user.get("mode") in {"guest", "registered"}:
        return scr_menu(user, t, parts, page)
    text = (
        f"{title(user, t, t['tagline'])}\n"
        f"{esc(t['hero_sub'])}\n\n{esc(t['contact_line'])}"
    )
    return text, kb([
        [(t["register"], "do:reg")],
        [(t["guest"], "do:guest")],
        [(t["services"], "nav:why")],
        [("O‘zbekcha", "do:lang:uz"), ("Русский", "do:lang:ru"), ("English", "do:lang:en")],
    ])


def scr_why(user, t, parts, page):
    text = f"{title(user, t, t['why'])}\n{esc(t['why_body'])}\n\n{esc(t['contact_line'])}"
    return text, kb([[(t["back"], "nav:home")]])


def scr_menu(user, t, parts, page):
    text = f"{title(user, t, t['brand'])}{esc(t['choose'])}\n{esc(t['help_phone'])}"
    return text, kb([
        [("📊 " + t["dashboard"], "nav:dash")],
        [("🏢 " + t["mod_org"], "nav:org")],
        [("📑 " + t["mod_tax"], "nav:tax")],
        [("🏦 " + t["mod_bank"], "nav:bank")],
        [("💳 " + t["mod_payments"], "nav:pay")],
        [("🏗️ " + t["mod_assets"], "nav:asset")],
        [("📦 " + t["mod_tmz"], "nav:tmz")],
        [("📄 " + t["mod_ehf"], "nav:ehf")],
        [("👥 " + t["mod_hr"], "nav:hr")],
        [("👤 " + t["profile"], "nav:profile")],
        [(t["lang_btn"], "nav:lang")],
    ])


def scr_lang(user, t, parts, page):
    text = title(user, t, t["lang_btn"])
    return text, kb([
        [("O‘zbekcha", "do:lang:uz"), ("Русский", "do:lang:ru"), ("English", "do:lang:en")],
        [(t["back"], "nav:menu")],
    ])


def scr_dash(user, t, parts, page):
    text = (
        f"{title(user, t, t['dashboard'])}{esc(t['dash_sub'])}\n\n"
        "Sof foyda: <b>125.4M</b> +12.5%\n"
        "Daromadlar: <b>853.2M</b> +8.7%\n"
        "Xarajatlar: <b>727.7M</b> +6.3%\n"
        "Soliq majburiyatlari: <b>98.4M</b> −3.2%\n"
        "Bank qoldig‘i: <b>312.5M</b> +9.1%\n\n"
        "Daromad/xarajat dinamikasi: o‘sish.\n"
        "Xarajatlar: ish haqi 35%, xomashyo 25%, ijara 15%.\n"
        "Bank aylanmasi va debitor/kreditor kartochkalari modullarda."
    )
    return text, kb([
        [(t["why"], "nav:why")],
        [(t["back"], "nav:menu")],
    ])


def scr_profile(user, t, parts, page):
    company = user.get("company_name") or "Demo Korxona MChJ"
    text = (
        f"{title(user, t, t['profile'])}"
        f"{esc(company)}\n"
        f"STIR: {esc(user.get('stir') or '305556789')}\n"
        f"{esc(t['reg_date'])}: {esc(user.get('reg_date') or '—')}\n"
        f"{esc(t['tariff'])}: {esc(user.get('tariff') or 'Standart')} · Faol\n"
        f"{esc(t['tariff_until'])}: {esc(user.get('tariff_until') or '—')}\n"
        f"{esc(t['payment_due'])}: {esc(user.get('payment_due') or '—')}\n"
        f"{esc(t['payment_phone'])}: +998 71 200 00 01\n"
        "Telegram: https://t.me/finaccount_support"
    )
    return text, kb([
        [(t["logout_guest"], "do:logout")],
        [(t["back"], "nav:menu")],
    ])


def scr_org(user, t, parts, page):
    db.ensure_company(user["telegram_id"])
    section = parts[1] if len(parts) > 1 else "menu"
    uid = user["telegram_id"]
    if section == "menu":
        text = f"{title(user, t, t['mod_org'])}{esc(t['choose'])}"
        return text, with_back([
            [(t["org_main"], "nav:org:main")],
            [(t["org_docs"], "nav:org:docs")],
            [(t["org_banks"], "nav:org:banks")],
            [(t["org_tg"], "nav:org:phones")],
        ], t, "menu")
    if section == "main":
        org = db.org_of(uid)
        text = (
            f"{title(user, t, t['org_main'])}<i>{esc(t['synced'])}</i>\n\n"
            f"STIR: {esc(org['stir'])} · readonly\n"
            f"OKED: {esc(org['oked'])} · readonly\n"
            f"SOOGU: {esc(org['soogu'])} · readonly\n"
            f"{esc(t['reg_company'])}: {esc(org['name'])} · readonly\n"
            f"Soliq to‘lovchisi turi: {esc(org['tax_type'])} · readonly\n\n"
            f"<b>Rahbar</b>\n{esc(org['director_name'])}, {esc(org['director_position'])}\n"
            f"{esc(org['director_phone'])} · {esc(org['director_email'])}\n\n"
            f"<b>Bosh buxgalter</b>\n{esc(org['accountant_name'])}, {esc(org['accountant_position'])}\n"
            f"{esc(org['accountant_phone'])} · {esc(org['accountant_email'])}"
        )
        return text, with_back([
            [(t["edit"] + " · rahbar", "do:edit:director")],
            [(t["edit"] + " · buxgalter", "do:edit:accountant")],
        ], t, "org")
    if section == "docs":
        items = db.rows("org_docs", uid)
        chunk, page, pages = slice_page(items, page)
        lines = [f"{esc(r['name'])}\n{esc(r['filename'])} · {esc(r['uploaded'])}" for r in chunk] or [esc(t["empty"])]
        text = f"{title(user, t, t['org_docs'])}" + "\n\n".join(lines)
        rows = [[(t["upload_doc"], "do:adddoc")]]
        rows += [[(t["delete"] + f" #{r['id']}", f"do:deldoc:{r['id']}")] for r in chunk]
        rows.append(pager("org:docs", page, pages))
        return text, with_back(rows, t, "org")
    if section == "banks":
        items = db.rows("org_accounts", uid)
        lines = [
            f"<b>{esc(r['kind'])}</b>\n{esc(r['number'])}\nMFO {esc(r['mfo'])} · {esc(r['bank'])}"
            for r in items
        ]
        text = f"{title(user, t, t['org_banks'])}" + "\n\n".join(lines)
        return text, with_back([[(t["add_account"], "do:addacc")]], t, "org")
    phones = db.rows("org_phones", uid)
    lines = [f"{esc(r['phone'])} · {esc(r['role'])}" for r in phones] or [esc(t["empty"])]
    text = f"{title(user, t, t['org_tg'])}" + "\n".join(lines) + f"\n\n{esc(t['next_integration'])}"
    rows = [[(t["add_phone"], "do:addphone")]]
    rows += [[(t["delete"] + " " + r["phone"], f"do:delphone:{r['id']}")] for r in phones]
    return text, with_back(rows, t, "org")


def scr_tax(user, t, parts, page):
    db.ensure_company(user["telegram_id"])
    section = parts[1] if len(parts) > 1 else "menu"
    uid = user["telegram_id"]
    if section == "menu":
        text = f"{title(user, t, t['mod_tax'])}{esc(t['tax_journal'])} — standart"
        return text, with_back([
            [(t["tax_forms"], "nav:tax:forms:tax")],
            [(t["tax_journal"], "nav:tax:journal:accepted:0")],
            [(t["tax_forming"], "nav:tax:forming")],
        ], t, "menu")
    if section == "forms":
        cat = parts[2] if len(parts) > 2 else "tax"
        forms = FORMS.get(cat, FORMS["tax"])
        text = f"{title(user, t, t['tax_forms'])}" + "\n".join(f"{code} · {name}" for code, name in forms)
        text += f"\n\n{esc(t['next_integration'])}"
        rows = [[(label, f"nav:tax:forms:{key}")] for key, label in FORM_CATS]
        rows += [[(f"{t['create']} {code}", f"do:taxform:{code}")] for code, _name in forms]
        return text, with_back(rows, t, "tax")
    if section == "forming":
        org = db.org_of(uid)
        cards = [
            "QQS hisoboti · 1-chorak 2026 · Tayyorlash mumkin",
            "Buxgalteriya balansi · 2025",
            "Moliyaviy natijalar · 2025",
            "JShDS va ijtimoiy soliq · Mart 2026",
            "INPS reyestri · Mart 2026",
            "Mol-mulk, yer va suv · 2026",
        ]
        if "aylanma" in (org["tax_type"] or "").lower():
            cards[0] = "Aylanmadan olinadigan soliq hisoboti"
        text = f"{title(user, t, t['tax_forming'])}Soliq to‘lovchisi: <b>{esc(org['tax_type'])}</b>\n\n" + "\n".join(cards)
        return text, with_back([[(t["create"], "do:taxform:QQS")]], t, "tax")
    tab = parts[2] if len(parts) > 2 else "accepted"
    year = parts[3] if len(parts) > 3 else "0"
    packet = parts[4] if len(parts) > 4 else ""
    text = f"{title(user, t, t['tax_journal'])}"
    rows = []
    if year in {"", "0"}:
        text += esc(t["year_required"]) + "\n" + esc(t["refresh"])
    else:
        items = db.rows("tax_reports", uid, "year=? AND tab=?", (year, tab))
        if packet:
            items = [r for r in items if packet.lower() in (r["packet"] or "").lower()]
        chunk, page, pages = slice_page(items, page)
        if not chunk:
            text += esc(t["empty"])
        else:
            text += "\n\n".join(
                f"{esc(r['name'])}\n{esc(r['period'])} · {esc(r['packet'])}\n"
                f"{esc(t['col_sent'])}: {esc(r['sent'])}\n{esc(t['col_status'])}: {esc(r['status'])}\n"
                f"{esc(t['col_updated'])}: {esc(r['updated'])}"
                for r in chunk
            )
        rows.append(pager(f"tax:journal:{tab}:{year}:{packet}", page, pages))
    rows.extend([[(t[key], f"nav:tax:journal:{code}:{year}:{packet}")] for code, key in TAX_TABS])
    rows.append([(y, f"nav:tax:journal:{tab}:{y}:{packet}") for y in ("2024", "2025", "2026")])
    rows.append([(t["packet_enter"], f"do:packet:{tab}:{year}"), (t["refresh"], f"nav:tax:journal:{tab}:{year}:{packet}")])
    return text, with_back(rows, t, "tax")


def scr_bank(user, t, parts, page):
    db.ensure_company(user["telegram_id"])
    section = parts[1] if len(parts) > 1 else "menu"
    uid = user["telegram_id"]
    if section == "menu":
        text = f"{title(user, t, t['mod_bank'])}{esc(t['bank_turnover'])}"
        return text, with_back([
            [(t["bank_turnover"], "nav:bank:turn")],
            [(t["bank_auto"], "nav:bank:auto:2026:4")],
            [(t["bank_archive"], "nav:bank:arch")],
        ], t, "menu")
    if section == "turn":
        items = db.rows("org_accounts", uid)
        lines = []
        rows = []
        for acc in items:
            period = f"{db.fmt_date(acc['last_start'])} - {db.fmt_date(acc['last_end'])}" if acc["last_end"] else "—"
            lines.append(
                f"🏦 <b>{esc(acc['kind'])}</b>\n{esc(acc['number'])} · MFO {esc(acc['mfo'])}\n"
                f"{esc(acc['bank'])}\n{esc(t['balance'])}: {esc(acc['balance'])}\n"
                f"{esc(t['last_period'])}: {esc(period)}"
            )
            rows.append([(t["add_new"] + " · " + acc["kind"][:18], f"do:bankup:{acc['id']}")])
        text = f"{title(user, t, t['bank_turnover'])}" + "\n\n".join(lines)
        return text, with_back(rows, t, "bank")
    if section == "auto":
        year = int(parts[2]) if len(parts) > 2 else 2026
        month = int(parts[3]) if len(parts) > 3 else 4
        ops = db.rows("bank_ops", uid, "year=? AND month=?", (year, month))
        incomes = [r for r in ops if r["money_in"]]
        outcomes = [r for r in ops if r["money_out"]]
        def line(r):
            mark = " ⚠" if r["low_confidence"] else ""
            status = t["status_ok"] if r["status"] == "confirmed" else t["status_check"]
            amount = db.money(r["money_in"] or r["money_out"])
            side = t["incomes"] if r["money_in"] else t["outcomes"]
            return (
                f"{esc(r['op_date'])} · {esc(r['doc_no'])} · {side} {amount}{mark}\n"
                f"{esc(r['counterparty'])} · STIR {esc(r['stir'])}\n"
                f"{esc(r['purpose'])}\nDt {esc(r['debit_acc'])} Kt {esc(r['credit_acc'])}\n"
                f"{esc(r['suggestion'])} · {esc(status)}"
            )
        body = []
        if incomes:
            body.append("<b>" + esc(t["incomes"]) + "</b>\n" + "\n\n".join(line(r) for r in incomes))
        if outcomes:
            body.append("<b>" + esc(t["outcomes"]) + "</b>\n" + "\n\n".join(line(r) for r in outcomes))
        text = f"{title(user, t, t['bank_auto'])}{year} · {MONTHS[month - 1]}\n\n" + ("\n\n".join(body) or esc(t["empty"]))
        rows = []
        month_row = []
        for i, name in enumerate(MONTHS, start=1):
            month_row.append((name[:3], f"nav:bank:auto:{year}:{i}"))
            if len(month_row) == 4:
                rows.append(month_row)
                month_row = []
        if month_row:
            rows.append(month_row)
        rows.append([(str(y), f"nav:bank:auto:{y}:{month}") for y in (2024, 2025, 2026)])
        for r in ops:
            rows.append([
                (t["confirm_one"], f"do:opok:{r['id']}:{year}:{month}"),
                (t["edit_entry"], f"do:opedit:{r['id']}"),
            ])
        rows.append([(t["confirm_all"], f"do:opall:{year}:{month}")])
        return text, with_back(rows, t, "bank")
    items = db.rows("bank_files", uid)
    chunk, page, pages = slice_page(items, page, 4)
    lines = [
        f"{esc(r['kind'])} · {esc(r['account_number'])}\n{esc(r['bank'])}\n{esc(r['period'])}\n"
        f"{esc(r['uploaded'])} · {esc(r['filename'])} · {r['ops_count']} ops"
        for r in chunk
    ]
    text = f"{title(user, t, t['bank_archive'])}" + ("\n\n".join(lines) or esc(t["empty"]))
    rows = [[(t["download"] + " " + r["filename"][:20], f"do:getfile:{r['id']}")] for r in chunk if r["path"]]
    rows.append(pager("bank:arch", page, pages))
    return text, with_back(rows, t, "bank")


def scr_pay(user, t, parts, page):
    db.ensure_company(user["telegram_id"])
    section = parts[1] if len(parts) > 1 else "menu"
    uid = user["telegram_id"]
    if section == "menu":
        text = f"{title(user, t, t['mod_payments'])}{esc(t['choose'])}"
        return text, with_back([
            [(t["pay_history"], "nav:pay:hist")],
            [(t["pay_create"], "do:pay")],
            [(t["recon_tax"], "nav:pay:tax")],
            [(t["recon_cp"], "nav:pay:cp")],
        ], t, "menu")
    if section == "hist":
        items = db.rows("payments", uid)
        chunk, page, pages = slice_page(items, page)
        lines = [
            f"{esc(r['number'])} · {esc(r['code'])} {esc(r['name'])}\n{esc(r['pay_date'])} · {esc(r['amount'])} · {esc(r['status'])}"
            for r in chunk
        ]
        text = f"{title(user, t, t['pay_history'])}" + ("\n\n".join(lines) or esc(t["empty"]))
        rows = [[(t["pay_create"], "do:pay")]]
        rows += [[(t["send"] + " " + r["number"], f"do:paysend:{r['id']}")] for r in chunk if r["status"] == "Loyiha"]
        rows.append(pager("pay:hist", page, pages))
        return text, with_back(rows, t, "pay")
    if section == "tax":
        text = (
            f"{title(user, t, t['recon_tax'])}"
            "Soliq qarzdorligi: <b>2 150 000</b> so‘m\n"
            "Ortiqcha to‘lov: <b>0</b>\n"
            "Holat: Hisob-kitob ochiq\n\n"
            f"{esc(t['next_integration'])}"
        )
        return text, with_back([], t, "pay")
    items = db.rows("recon", uid)
    lines = [
        f"{esc(r['name'])}\nSTIR {esc(r['stir'])} · {esc(r['contract'])} · {esc(r['ehf'])}\n"
        f"Debit {db.money(r['debit'])} · Kredit {db.money(r['credit'])}\n"
        f"{esc(r['last_op'])} · {esc(r['status'])}"
        for r in items
    ]
    text = f"{title(user, t, t['recon_cp'])}" + "\n\n".join(lines)
    return text, with_back([], t, "pay")


def scr_asset(user, t, parts, page):
    db.ensure_company(user["telegram_id"])
    section = parts[1] if len(parts) > 1 else "menu"
    uid = user["telegram_id"]
    if section == "menu":
        text = f"{title(user, t, t['mod_assets'])}{esc(t['asset_registry'])}"
        return text, with_back([
            [(t["asset_registry"], "nav:asset:reg:all")],
            [(t["asset_depr"], f"nav:asset:dep:{date.today().year}:{date.today().month}")],
            [(t["asset_inv"], "nav:asset:inv")],
        ], t, "menu")
    if section == "reg":
        group = parts[2] if len(parts) > 2 else "all"
        items = db.rows("assets", uid)
        if group != "all":
            items = [a for a in items if a["grp"] == group]
        chunk, page, pages = slice_page(items, page, 4)
        lines = []
        for a in chunk:
            tag = " · soliq" if a["source"] == "my.soliq.uz" else ""
            lines.append(
                f"{esc(a['inv'])} {esc(a['name'])}{tag}\n{GROUPS.get(a['grp'], a['grp'])}\n"
                f"{esc(a['buy_date'])} · {db.money(a['initial'])} · {int(a['rate']*100)}%\n"
                f"{esc(a['place'])} · {esc(a['responsible'])} · {esc(a['status'])}"
            )
        text = f"{title(user, t, t['asset_registry'])}" + ("\n\n".join(lines) or esc(t["empty"]))
        rows = [[(label[:22], f"nav:asset:reg:{key}")] for key, label in GROUPS.items()]
        rows.append([("Barchasi", "nav:asset:reg:all"), (t["add_new"], "do:asset")])
        rows.append(pager(f"asset:reg:{group}", page, pages))
        return text, with_back(rows, t, "asset")
    if section == "dep":
        year = int(parts[2]) if len(parts) > 2 else date.today().year
        month = int(parts[3]) if len(parts) > 3 else date.today().month
        items = db.rows("assets", uid)
        total_i = sum(a["initial"] for a in items)
        calcs = [(a, db.depreciation_row(a, year, month)) for a in items]
        total_a = sum(c["accumulated"] for _, c in calcs)
        total_m = sum(c["monthly"] for _, c in calcs)
        total_r = sum(c["residual"] for _, c in calcs)
        lines = [
            f"{esc(a['inv'])} {esc(a['name'])}\n"
            f"oylik {db.money(c['monthly'])} · yil {db.money(c['yearly'])}\n"
            f"jamg‘arma {db.money(c['accumulated'])} · qoldiq {db.money(c['residual'])} · Faol"
            for a, c in calcs
        ]
        text = (
            f"{title(user, t, t['asset_depr'])}{MONTHS[month-1]} {year}\n"
            f"Boshlang‘ich: {db.money(total_i)}\n"
            f"Jamg‘arilgan: {db.money(total_a)}\n"
            f"Joriy oy: {db.money(total_m)}\n"
            f"Qoldiq: {db.money(total_r)}\n\n" + "\n\n".join(lines)
        )
        return text, with_back([
            [(t["export"], f"do:export:{year}:{month}")],
            [(str(y), f"nav:asset:dep:{y}:{month}") for y in (2024, 2025, 2026)],
        ], t, "asset")
    items = db.rows("assets", uid)
    lines = [
        f"{esc(a['inv'])} {esc(a['name'])}\n01.04.2026 · {esc(a['place'])} · {esc(a['responsible'])}\nFaktik: bor · yetishmovchilik 0 · ortiqcha 0"
        for a in items
    ]
    text = f"{title(user, t, t['asset_inv'])}" + "\n\n".join(lines) + f"\n\n{esc(t['future'])}"
    return text, with_back([], t, "asset")


def scr_tmz(user, t, parts, page):
    db.ensure_company(user["telegram_id"])
    section = parts[1] if len(parts) > 1 else "menu"
    uid = user["telegram_id"]
    if section == "menu":
        text = f"{title(user, t, t['mod_tmz'])}{esc(t['tmz_registry'])}"
        return text, with_back([
            [(t["tmz_registry"], "nav:tmz:reg")],
            [(t["tmz_moves"], "nav:tmz:mov")],
            [(t["tmz_wh"], "nav:tmz:wh")],
            [(t["tmz_inv"], "nav:tmz:inv")],
        ], t, "menu")
    if section == "reg":
        items = db.rows("tmz_items", uid)
        lines = [
            f"{esc(i['code'])} {esc(i['name'])} · {esc(i['unit'])}\n{esc(i['warehouse'])} · qoldiq {i['qty']} · {db.money(i['cost'])} · jami {db.money(i['qty']*i['cost'])}"
            for i in items
        ]
        text = f"{title(user, t, t['tmz_registry'])}" + "\n\n".join(lines)
        return text, with_back([
            [(t["manual"], "do:tmz")],
            [(t["excel"], "do:tmzxls")],
            [(t["from_ehf"], "do:tmzehf")],
        ], t, "tmz")
    if section == "mov":
        items = db.rows("tmz_moves", uid)
        lines = [f"{esc(r['op_date'])} · {esc(r['op_type'])} · {esc(r['doc'])}\n{esc(r['product'])} · {r['qty']}" for r in items]
        text = f"{title(user, t, t['tmz_moves'])}Kirim · Chiqim · Ko‘chirish · Inventarizatsiya\n\n" + "\n\n".join(lines)
        return text, with_back([], t, "tmz")
    if section == "wh":
        items = db.rows("tmz_items", uid)
        names = ["Asosiy ombor", "Savdo ombori", "Ishlab chiqarish ombori"]
        lines = []
        for name in names:
            subset = [i for i in items if i["warehouse"] == name]
            detail = ", ".join(f"{i['name']} {i['qty']}" for i in subset) or "—"
            lines.append(f"<b>{esc(name)}</b> · {len(subset)} ta\n{esc(detail)}")
        text = f"{title(user, t, t['tmz_wh'])}" + "\n\n".join(lines)
        return text, with_back([], t, "tmz")
    items = db.rows("tmz_items", uid)
    lines = [f"{esc(i['code'])} {esc(i['name'])} · hisob {i['qty']} · faktik {i['qty']} · farq 0" for i in items]
    text = f"{title(user, t, t['tmz_inv'])}" + "\n".join(lines) + f"\n\n{esc(t['future'])}"
    return text, with_back([], t, "tmz")


def scr_ehf(user, t, parts, page):
    db.ensure_company(user["telegram_id"])
    section = parts[1] if len(parts) > 1 else "menu"
    uid = user["telegram_id"]
    if section == "menu":
        text = f"{title(user, t, t['mod_ehf'])}{esc(t['ehf_in'])}"
        return text, with_back([
            [(t["ehf_in"], "nav:ehf:in:all")],
            [(t["ehf_out"], "nav:ehf:out")],
            [(t["ehf_drafts"], "nav:ehf:draft")],
            [(t["ehf_contracts"], "nav:ehf:con:active")],
            [(t["ehf_archive"], "nav:ehf:arch")],
        ], t, "menu")
    if section == "in":
        tab = parts[2] if len(parts) > 2 else "all"
        items = db.rows("ehf_docs", uid, "direction='in'")
        if tab != "all":
            items = [d for d in items if d["tab"] == tab]
        lines = [
            f"{esc(d['status'])} · {esc(d['doc_type'])}\n{esc(d['counterparty'])} · {esc(d['stir'])}\n"
            f"{esc(d['number'])} · {esc(d['contract'])}\nQQSsiz {db.money(d['without_vat'])} · QQS {db.money(d['vat'])} · jami {db.money(d['with_vat'])}\n{esc(d['created'])}"
            for d in items
        ]
        text = f"{title(user, t, t['ehf_in'])}" + ("\n\n".join(lines) or esc(t["empty"]))
        rows = [[(label[:24], f"nav:ehf:in:{key}")] for key, label in EHF_TABS]
        return text, with_back(rows, t, "ehf")
    if section == "out":
        items = db.rows("ehf_docs", uid, "direction='out'")
        lines = [f"{esc(d['doc_type'])} {esc(d['number'])} · {esc(d['counterparty'])} · {db.money(d['with_vat'])}" for d in items]
        text = f"{title(user, t, t['ehf_out'])}" + ("\n".join(lines) or esc(t["empty"]))
        return text, with_back([], t, "ehf")
    if section == "draft":
        items = db.rows("ehf_docs", uid, "direction='draft'")
        lines = [f"{esc(d['doc_type'])} {esc(d['number'])} · {esc(d['counterparty'])} · {esc(d['status'])}" for d in items]
        text = f"{title(user, t, t['ehf_drafts'])}" + ("\n".join(lines) or esc(t["empty"]))
        rows = [[(t["add_new"], "do:ehfdraft")]]
        rows += [[(t["send"] + " " + d["number"], f"do:ehfsend:{d['id']}")] for d in items]
        return text, with_back(rows, t, "ehf")
    if section == "con":
        key = parts[2] if len(parts) > 2 else "active"
        items = db.rows("contracts", uid, "status_key=?", (key,))
        lines = [f"{esc(r['number'])} · {esc(r['party'])} · {esc(r['status'])}" for r in items]
        text = f"{title(user, t, t['ehf_contracts'])}" + ("\n".join(lines) or esc(t["empty"]))
        return text, with_back([
            [("Faol", "nav:ehf:con:active"), ("Tugagan", "nav:ehf:con:ended"), ("Bekor", "nav:ehf:con:cancelled")],
        ], t, "ehf")
    items = db.rows("ehf_docs", uid, "direction='archive'")
    lines = [f"{esc(d['doc_type'])} {esc(d['number'])} · {esc(d['created'])}" for d in items]
    text = f"{title(user, t, t['ehf_archive'])}" + ("\n".join(lines) or esc(t["empty"]))
    return text, with_back([], t, "ehf")


def scr_hr(user, t, parts, page):
    db.ensure_company(user["telegram_id"])
    section = parts[1] if len(parts) > 1 else "menu"
    uid = user["telegram_id"]
    if section == "menu":
        text = f"{title(user, t, t['mod_hr'])}{esc(t['hr_employees'])}"
        return text, with_back([
            [(t["hr_employees"], "nav:hr:emp")],
            [(t["hr_payroll"], "nav:hr:pay")],
            [(t["hr_pit"], "nav:hr:pit")],
            [(t["hr_orders"], "nav:hr:ord")],
        ], t, "menu")
    if section == "emp":
        items = db.rows("employees", uid)
        chunk, page, pages = slice_page(items, page, 3)
        lines = []
        rows = [[(t["add_new"], "do:emp")]]
        for e in chunk:
            mark = "🟢" if e["status"] == "Aktiv" else "🔴"
            lines.append(
                f"{mark} <b>{esc(e['fio'])}</b>\nJShShIR {esc(e['pinfl'])} · {esc(e['birth'])}\n"
                f"{esc(e['phone'])}\n{esc(e['position'])} · {esc(e['dept'])}\n"
                f"{esc(e['hired'])} · {db.money(e['salary'])} · {esc(e['status'])}"
            )
            rows.append([
                (t["edit"], f"do:empedit:{e['id']}"),
                (t["orders"], f"nav:hr:oneord:{e['id']}"),
            ])
            if e["status"] == "Aktiv":
                rows.append([(t["fire"] + " " + e["fio"].split()[0], f"do:fireask:{e['id']}")])
        text = f"{title(user, t, t['hr_employees'])}" + ("\n\n".join(lines) or esc(t["empty"]))
        rows.append(pager("hr:emp", page, pages))
        return text, with_back(rows, t, "hr")
    if section == "pay":
        items = [e for e in db.rows("employees", uid) if e["status"] == "Aktiv"]
        lines = [
            f"{esc(e['fio'])}\noyl {db.money(e['salary'])} · ustama 0 · bonus 0 · jarima 0\n"
            f"jami {db.money(e['salary'])} · to‘lanadi {db.money(e['salary'])}"
            for e in items
        ]
        text = f"{title(user, t, t['hr_payroll'])}{esc(t['active_only'])}\n\n" + "\n\n".join(lines)
        return text, with_back([], t, "hr")
    if section == "pit":
        items = db.rows("employees", uid)
        lines = []
        for e in items:
            base = e["salary"] if e["status"] == "Aktiv" else 0
            lines.append(f"{esc(e['fio'])} · {esc(e['pinfl'])}\nbaza {db.money(base)} · JShDS — · ijtimoiy — · {esc(e['status'])}")
        text = f"{title(user, t, t['hr_pit'])}" + "\n\n".join(lines) + f"\n\n{esc(t['next_integration'])}"
        return text, with_back([], t, "hr")
    if section == "oneord":
        emp = db.q("SELECT * FROM employees WHERE id=? AND telegram_id=?", (int(parts[2]), uid), one=True)
        orders = db.rows("hr_orders", uid, "employee=?", (emp["fio"],)) if emp else []
        lines = [f"{esc(o['number'])} · {esc(o['order_date'])} · {esc(o['order_type'])} · {esc(o['status'])}" for o in orders]
        text = f"{title(user, t, t['hr_orders'])}{esc(emp['fio'] if emp else '')}\n\n" + ("\n".join(lines) or esc(t["empty"]))
        rows = [[(t["download"] + " " + o["number"], f"do:orderfile:{o['id']}")] for o in orders]
        return text, with_back(rows, t, "hr:emp")
    items = db.rows("hr_orders", uid)
    lines = [f"{esc(o['number'])} · {esc(o['order_date'])}\n{esc(o['employee'])} · {esc(o['order_type'])} · {esc(o['status'])}" for o in items]
    text = f"{title(user, t, t['hr_orders'])}" + "\n\n".join(lines)
    rows = [[(t["download"] + " " + o["number"], f"do:orderfile:{o['id']}")] for o in items]
    return text, with_back(rows, t, "hr")
