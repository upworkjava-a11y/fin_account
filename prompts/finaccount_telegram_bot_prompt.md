# Prompt — FinAccount Telegram bot (same features as the website)

Copy everything below the line into a new chat or agent and run it as the task and I provide 

---

You are a senior Python developer. Build a **Telegram bot version of FinAccount.uz** (digital accounting ecosystem for Uzbekistan). The bot must cover the **same product and the same features** as the existing traditional Django website in this repository. Do not invent a different product.

SOURCE OF TRUTH (in this order):
1. This repository’s Django app (apps, URLs, templates, demo data, labels in `core/i18n_labels.py`).
2. `MVP TI(yakuniy).docx` (final technical specification).
3. This prompt.

GOAL:
A working Telegram bot that lets a company user do everything the website MVP lets them do: language, guest vs registered, profile, and all 8 modules. Map every website screen to a bot conversation (inline keyboards, step-by-step wizards, files, lists). Keep the same Uzbek names, statuses, columns, and business rules.

Do NOT rebuild the website. Do NOT call live my.soliq.uz, my.mehnat.uz, Didox, or SMS gateways. Use the same demo data and the same “next step” placeholders the website uses, but the **menus, fields, validations, and restrictions must already match the spec**.

============================================================
STACK
============================================================
- Python 3.10+
- New package folder: `telegram_bot/` at the repo root (do not break the Django site)
- aiogram 3.x (preferred) OR python-telegram-bot v21+ — pick one and stay consistent
- SQLite via the same style of local storage (SQLAlchemy or aiosqlite). A separate `bot.sqlite3` is fine for this step
- Bot token from environment variable `TELEGRAM_BOT_TOKEN` (never hardcode). Add it to `.env.example` as a blank key
- `requirements-bot.txt` for bot dependencies
- README section: how to create a bot with BotFather and run `python -m telegram_bot`

============================================================
BOT UX RULES (must feel like the website)
============================================================
- Default language: O‘zbekcha. Switch anytime: O‘zbekcha | Русский | English. Store language per Telegram user. Reuse the label keys from `core/i18n_labels.py` (UZ / RU / EN). Do not leave mixed languages in one screen.
- Persistent reply keyboard OR a single “🏠 Menyu” button always returns to the main module menu. Every screen also has “⬅️ Orqaga”.
- Main menu is the website sidebar, same order:
  1. Bosh sahifa (Dashboard)
  2. Tashkilot ma'lumotlari
  3. Soliq
  4. Bank hisob raqamlari
  5. To'lovlar va solishtirma
  6. Asosiy vositalar
  7. Inventar va TMZ
  8. EHF
  9. HR
  10. Profil
  11. Til
- Long tables must be paginated (5–8 rows per message) with ◀️ ▶️ and a short summary line. Do not dump huge walls of text.
- Statuses use the same words as the site (Qabul qilingan, Tekshirish talab etiladi, Tasdiqlangan, Aktiv, Bo‘shagan, Faol, and so on).
- Guest users see a “Mehmon” badge in the menu header.
- Destructive actions (ishdan bo‘shatish, delete phone, delete document) require an inline confirmation: HA / YO‘Q.
- File uploads: accept the document in the chat (xlsx/xls/csv/pdf) and answer with the same success or error text the website would show.
- Every module opens on the same default page the website opens (listed below).

============================================================
START, GUEST, REGISTER, PROFILE
============================================================
`/start` shows:
- Brand line: FinAccount — Raqamli buxgalteriya ekotizimi
- Subtitle: Biz bilan korxonangizni rivojlantiring
- Buttons: Ro‘yxatdan o‘tish | Mehmon sifatida tashrif buyurish | Til

Guest:
- Can open every module and try Bank file upload and auto-provodka review.
- CANNOT send reports, invoices, payment orders, EHF, contracts, or HR orders to external systems. If they tap Yuborish / Jo‘natish, reply that this is only for registered users with the right permissions. They can still preview and draft locally.

Registration wizard (same fields as `/register/`):
1. STIR (this becomes the login)
2. Company name and requisites shown as auto-filled and locked (demo fill, same as the site: “Demo Korxona MChJ”). TODO comment: real fill comes from STIR / my.soliq.uz later
3. Password, then password again
4. After each password character group, show a checklist and mark passed rules:
   - at least 8 characters
   - uppercase
   - lowercase
   - digit
   - special character
5. Contact phone
6. Oferta: user must confirm they read and accept it
7. On success, save the company user and enter the main menu
8. Note in code: future SMS confirmation of the phone is planned, not built now

Profile screen (same fields as the website dropdown):
- Ro‘yxatdan o‘tgan sana
- Joriy tarif rejasi (demo: Standart, badge Faol)
- Tarifning amal qilish muddati
- To‘lov muddati
- To‘lovlar bo‘yicha telefon: +998 71 200 00 01
- Telegram support link
- Chiqish (guest exits back to /start; registered user logs out of the company session)

Dashboard (Bosh sahifa), same demo KPIs as the website:
- Sof foyda 125.4M (+12.5%)
- Daromadlar 853.2M (+8.7%)
- Xarajatlar 727.7M (+6.3%)
- Soliq majburiyatlari 98.4M (−3.2%)
- Bank qoldig‘i 312.5M (+9.1%)
Then short lines for: daromad/xarajat dinamikasi, xarajatlar tarkibi, bank aylanmalari, debitor/kreditor. No charts required; text cards are enough. Also show the “Nima uchun FinAccount?” points once from /start or a “Xizmatlar” button: all processes in one system, tax and HR integration, AI assistant, cloud, secure storage, fast reports. Contact block: +998 71 200 00 01, info@finaccount.uz, Toshkent.

============================================================
1) TASHKILOT MA'LUMOTLARI
============================================================
Submenu:
- Asosiy ma'lumotlar (default)
- Hujjatlar
- Bank hisob raqamlari
- Telegram bot telefonlari

Asosiy ma'lumotlar — readonly (from my.soliq.uz, user cannot edit):
STIR, OKED, SOOGU, Korxona nomi, Soliq to‘lovchisi turi, other ID fields.
Demo: STIR 305556789, OKED 62010, SOOGU 12345, Demo Korxona MChJ, QQS to‘lovchisi.
Show a line: my.soliq.uz dan yuklangan.

Editable (rahbar and bosh buxgalter, because the tax portal is often stale):
F.I.O., lavozim, phone, email. Save button updates local demo storage.

Hujjatlar:
List: Korxona guvohnomasi, Korxona ustavi, Boshqa hujjatlar.
Each row: name, file, uploaded date, download, delete (confirm).
“Hujjat yuklash” asks for a file in chat and stores it.

Bank hisob raqamlari (organization master list, not the turnover page):
Cards: Asosiy 20208000486684884001 MFO 00580 Ipoteka bank Tinchlik filiali; Ikkilamchi Hamkorbank. “Yangi qo‘shish” wizard: type, number, MFO, bank name. A new account must appear later in the Bank module turnover list.

Telegram bot telefonlari:
List of phones with role labels (rahbar, bosh buxgalter, other).
“+” adds another phone. These numbers are the future audience for automatic news, reminders, and warnings. Saving is local for now.

============================================================
2) SOLIQ
============================================================
Default section: Jurnal. Default jurnal tab: Qabul qilinganlar.
Submenu:
- Elektron shakllar
- Jurnal
- Shakllanayotgan hisobotlar

Jurnal:
Ask Paket raqami and Yil, then a Yangilash button.
If year is not selected: do not list reports. Say: “Hisobotlarni ko‘rish uchun yilni tanlang” and tell the user to press Yangilash.
Tabs (inline): Tekshirish jarayonida, Xatolik mavjud, Qabul qilinganlar, Jo‘natilgan, Rad etilgan, Xomaki, Avtomat.
After year + Yangilash, show rows with: Hisobot nomi, Hisobot davri, Paket raqami, Jo‘natilgan sana, Holati, Oxirgi yangilanish sanasi.
Demo rows (same idea as the site): QQS hisoboti and JShDS for the chosen year, status Qabul qilingan.

Elektron shakllar:
Filters: Soliq hisobotlari (default), Moliyaviy hisobotlar, Budjetdan tashqari fondlar, Boshqalar.
List code + name, each with Yaratish:
- 100 Qo‘shilgan qiymat solig‘i hisoboti
- 101 Aylanmadan olinadigan soliq hisoboti
- 102 Foyda solig‘i hisoboti
Pagination: total count and page size. Yaratish opens a stub card (real my.soliq.uz form engine is a later step) and must refuse Yuborish for guests.

Shakllanayotgan hisobotlar:
Logic: Organization → Soliq to‘lovchisi turi → only matching cards.
Demo taxpayer is QQS, so show QQS hisoboti, not the turnover-tax-only card.
Also show when relevant: Buxgalteriya balansi; Moliyaviy natijalar; JShDS va ijtimoiy soliq; Mol-mulkni ijaraga berish daromad solig‘i; INPS reyestri; Mol-mulk, yer va suv soliqlari.
Each card: title, period, status, Shakllantirish. Unrelated reports stay hidden.

============================================================
3) BANK HISOB RAQAMLARI
============================================================
Default: Joriy yil uchun bank hisob raqamlari aylanmasi.
Submenu: Joriy yil aylanmasi | Avto-provodkalar | Arxiv

Aylanma:
One card per organization bank account, including Valyuta hisob raqami.
Show: name, number, MFO, bank, balance, oxirgi yuklangan davr (read-only, last successful upload).
Demo:
- Asosiy 20208000486684884001, MFO 00580, Ipoteka bank Tinchlik filiali, 125 450 000 so‘m, 01.01.2026–31.03.2026
- 2-hisob, Hamkorbank, 42 100 000
- Valyuta, Kapitalbank, 12 500 USD
“Yangi qo‘shish” wizard: Boshlanish sanasi, Tugash sanasi, then ask the user to send the bank file.
On success: store rows, prepare them for auto-provodka, copy the file into Arxiv, and move that account’s last period forward (example: 01.01.2026–31.03.2026 becomes 01.04.2026–30.06.2026).
Gap rule: if the new start date is not the day after the previous end date, reject with exactly:
“Ma'lumotlar yuklashda sanalar ketma-ketligi buzilgan. Iltimos tekshirib, qaytadan urinib ko'ring!!!”

Avto-provodkalar:
Pick year, then months: Yanvar … Dekabr.
Inside a month: kirim first, then chiqim; each group sorted by date.
Columns: Operatsiya sanasi, Hujjat raqami, Kontragent nomi, Kontragent STIRi, To‘lov maqsadi, Kirim, Chiqim, Debet, Kredit, Avtomatik taklif etilgan provodka, Holati.
User can view, edit debit/credit, confirm one, or confirm many.
Unconfirmed = “Tekshirish talab etiladi”. Confirmed = “Tasdiqlangan”.
Low-confidence AI suggestions get a distinct mark. Use 2–3 demo operations so the flow is visible. Real AI parsing is a later step; a simple demo suggestion is enough now.

Arxiv:
Filters: Yil, Hisob raqami, Bank nomi, Davr.
Columns: Hisob raqami turi (Asosiy, Ikkilamchi, Uchlamchi, To‘rtlamchi…), Hisob raqami, Bank, Davr, Yuklangan sana, Fayl nomi, Operatsiyalar soni, Yuklash.
Demo files: oborotka_Q1.xlsx (128 ops), oborotka_Q2.xlsx (154), hamkor_Q1.xlsx (64).
Yuklash sends the stored file back to the chat.

============================================================
4) TO'LOVLAR VA SOLISHTIRMA
============================================================
Submenu:
- To'lovlar tarixi (default)
- To'lovni shakllantirish
- Soliq bilan solishtirma
- Kontragentlar bilan solishtirma

To'lovlar tarixi (my.soliq.uz “Soliqlarni to‘lash” equivalent, demo):
Columns: To‘lov topshiriqnomasi raqami, Soliq kodi, Soliq nomi, To‘lov sanasi, To‘lov summasi, To‘lov holati, Ko‘rish, Yuklab olish.
Demo: TP-2026-0142 QQS 101010 12 450 000 Qabul qilingan; TP-2026-0188 JShDS 103010 3 200 000 Jo‘natilgan.

To'lovni shakllantirish:
Fields: Soliq turi, Soliq kodi, To‘lov summasi, To‘lov sanasi, Izoh.
Actions: Shakllantirish, Yuborish, Tasdiqlash.
After a successful send, the order appears in To‘lovlar tarixi. Guests cannot Yuborish.

Soliq solishtirmasi:
Show Soliq qarzdorligi, Ortiqcha to‘lovlar, Hisob-kitoblar holati, o‘zaro hisob-kitoblar. Demo: debt 2 150 000, overpay 0, status Hisob-kitob ochiq.

Kontragent solishtirmasi (core product logic, demo data is enough):
If an outgoing EHF, contract, or invoice is confirmed by the counterparty, create a receivable.
Example: 1 000 000 so‘m “Ko‘rsatilgan xizmatlar uchun” to "SARDORBEK SERVIS" MCHJ → Debitor 1 000 000.
When a bank row matches counterparty name, STIR, amount, and purpose, close the debt (Qoldiq: 0, status Qarzdorlik yopildi). STIR example 305556789.
Table columns: Kontragent nomi, STIR, Shartnoma raqami, EHF raqami, Debitorka, Kreditorka, Oxirgi operatsiya sanasi, Holati, Shakllantirish, Yuklab olish.
Second demo row: "ORIENT TRADE" MCHJ, STIR 301112233, contract SH-12/26, EHF-9022, credit 4 500 000, status Kreditorka.

============================================================
5) ASOSIY VOSITALAR
============================================================
Default: Asosiy vositalar reyestri.
Submenu: Reyestr | Amortizatsiya | Inventarizatsiya

Reyestr groups:
🏢 Bino va inshootlar, 🚗 Transport, 💻 Kompyuter va ofis texnikasi, 🏭 Uskunalar, 🪑 Mebel, ⚙️ Boshqa.
Columns: Inventar raqami, Nomi, Turi, Xarid sanasi, Boshlang‘ich qiymat, Eskirish foizi, Qoldiq qiymati, Joyi, Mas'ul shaxs, Holati.
Demo: AV-001 Ofis binosi (source my.soliq.uz, cannot be deleted), AV-014 Cobalt, AV-088 Dell OptiPlex.
“Yangi asosiy vosita” for manual assets (cars, special equipment, computers, servers, printers, furniture). Property and land that came from my.soliq.uz cannot be deleted.

Amortizatsiya:
Year + month filters, Hisoblash, Excel eksport (send a simple xlsx or csv).
Summary cards: jami boshlang‘ich, jamg‘arilgan amortizatsiya, joriy oy, qoldiq qiymat.
Per asset: boshlang‘ich, norma, oylik, yillik, jamg‘arilgan, qoldiq, holati Faol.
If the user does not override the rate, calculate monthly = initial * annual rate / 12 and reduce residual. Keep a short history.

Inventarizatsiya:
Sana, joyi, mas'ul, faktik mavjudlik, yetishmovchilik, ortiqchalik, izoh.
Future hooks only as disabled or “keyinroq” notes: photo, purchase docs, branches, QR/barcode, print card, dalolatnoma. Do not build them now.

============================================================
6) INVENTAR VA TMZ
============================================================
Default: TMZ reyestri.
Submenu: TMZ reyestri | Kirim va chiqimlar | Omborlar | Inventarizatsiya

Reyestr columns: Mahsulot kodi, Nomi, O‘lchov birligi, Ombor, Qoldiq, O‘rtacha tannarx, Umumiy qiymat.
Demo: TMZ-001 Shakar 100 kg Asosiy ombor; TMZ-002 Yog‘ 50 dona Savdo ombori.
Three create paths:
- Qo‘lda: nomi, birligi, narxi
- Excel: Kod, Nomi, Birligi, Miqdor, Narx — user sends a file, bot creates rows
- EHF: explain and demo that a received EHF (Shakar 100 kg, Yog‘ 50 dona) posts an automatic kirim. A button “EHF dan olish” can apply the demo document.

Kirim va chiqimlar:
Sana, Operatsiya turi (Kirim, Chiqim, Ko‘chirish, Inventarizatsiya), Hujjat, Mahsulot, Miqdor.
Demo: 02.04.2026 Kirim EHF-8891 Shakar 100; 03.04.2026 Chiqim AKT-12 Yog‘ 5.

Omborlar:
Asosiy ombor, Savdo ombori, Ishlab chiqarish ombori, with item counts. Opening a warehouse lists products stored there.

Inventarizatsiya:
Hisob qoldig‘i vs faktik, yetishmovchilik, ortiqcha, dalolatnoma summary.

Future POS / online-kassa / barcode note only, not implemented: a sold unit would decrease stock. Mention it in a “Keyinroq” info screen, do not build POS.

============================================================
7) EHF
============================================================
Default: Kiruvchi hujjatlar.
Submenu: Kiruvchi | Chiquvchi | Shakllanayotgan | Shartnomalar | Arxiv

Kiruvchi tabs: Barchasi, Imzolanishi kutilmoqda, Imzolangan, Rad etilgan, Bekor qilingan.
Columns: Holati, Hujjat turi, Kontragent, STIR, Hujjat raqami, Shartnoma raqami, QQSsiz summa, QQS summasi, QQS bilan summa, Yaratilgan sana.
Demo: EHF-9022 ORIENT TRADE signed 4 500 000 with VAT; AKT-77 SARDORBEK SERVIS pending 1 000 000.

Chiquvchi: EHF, Akt, Shartnoma sent by the company. Same columns, shorter list is ok.

Shakllanayotgan: Faktura, Akt, Shartnoma drafts. Each item: Ochish, Tahrirlash, Yuborish. Guests cannot Yuborish. A sent document moves to Chiquvchi and, when the counterparty confirms, feeds the counterparty reconciliation receivable.

Shartnomalar filters: Faol, Tugagan, Bekor qilingan.
Demo: SH-12/26 ORIENT TRADE Faol; SH-01/25 OLD PARTNER Tugagan.

Arxiv: finished and old documents, same columns, download if a file exists.

============================================================
8) HR
============================================================
Default: Xodimlar.
Submenu: Xodimlar | Ish haqi | JShDS va ijtimoiy soliq | Buyruqlar arxivi

Xodimlar columns:
F.I.O., JShShIR, Tug‘ilgan sana, Telefon, Lavozimi, Bo‘limi, Ishga kirgan sana, Oylik ish haqi, Holati (Aktiv / Bo‘shagan), Buyruqlar, Amallar.
Demo: Karimova Dilnoza bosh buxgalter Aktiv 8 500 000; Rahimov Aziz direktor Aktiv 15 000 000; Usmarov Jasur omborchi Bo‘shagan 4 200 000.

Yangi xodim fields:
F.I.O., JShShIR, Tug‘ilgan sana, Telefon, Pasport, Lavozim, Bo‘lim, Ishga kirish sanasi, Oylik, Ish vaqti turi, Shartnoma turi, Bank kartasi, INPS.
On save (local demo, no live my.mehnat.uz):
- create Ishga qabul qilish buyrug‘i
- fill a simple text/PDF-like summary (a text file or minimal PDF is enough)
- mark QR as a placeholder token in that file
- set status Aktiv
- include the employee in payroll and in the JShDS list
- store the order in Buyruqlar arxivi
Say clearly that my.mehnat.uz and the electronic labor book send are the next integration, not done now.

Tahrirlash may change: phone, lavozim, bo‘lim, oylik, ish sharoiti, karta, INPS, manzil.
A salary change applies to later payroll calculations only.

Buyruq types per employee: Ishga qabul qilish, Lavozim o‘zgartirish, Oylik o‘zgartirish, Ta'til, Ishdan bo‘shatish. Each can be downloaded.

Ishdan bo‘shatish: only on Aktiv rows. Ask “Xodimni ishdan bo'shatishni tasdiqlaysizmi?” HA / YO‘Q.
On HA: create the dismissal order, archive it, set status Bo‘shagan, exclude them from future payroll, and show their later tax amounts as zero.

Ish haqi (Aktiv only):
Oylik, ustamalar, bonuslar, qo‘shimcha, jarimalar, jami hisoblangan, to‘lanadigan. Pull the base salary from the employee card.

JShDS va ijtimoiy soliq:
Table: xodim, JShShIR, oylik baza (0 if Bo‘shagan), JShDS, ijtimoiy soliq, holati. Calculation can be a clearly marked demo percent if you document the rates in one place; do not pretend it was filed to the tax office.

Buyruqlar arxivi columns: Buyruq raqami, Sana, Xodim, Buyruq turi, Holati, PDF/Yuklab olish.
Demo: BY-001 Karimova hire; BY-088 Usmarov dismissal.

============================================================
DATA AND QUALITY
============================================================
- Seed the demo company, accounts, tax rows, archive files metadata, payments, assets, TMZ, EHF, employees, and orders on first run so every menu is non-empty.
- Persist user actions (new phone, new asset, uploaded file metadata, confirmed provodka, new employee, fired employee, new payment draft) in SQLite so a restart keeps them.
- Validate dates, required fields, and password rules before saving.
- Reply in the user’s language. Errors are short and specific.
- Log exceptions; never send stack traces to the user.
- Add a short `prompts` note is not needed. Do update the root README with a “Telegram bot” section and exact run commands.

============================================================
OUT OF SCOPE FOR THIS BUILD
============================================================
- Live my.soliq.uz, my.mehnat.uz, Didox, bank API, SMS OTP, real payment sending, real QR signing, POS/online cashbox.
- Changing the existing Django website, except a README mention and `.env.example` key.
- Hosting, Docker, or payments for the bot itself.

============================================================
DELIVERABLES
============================================================
1. `telegram_bot/` package: config, db models, seed, i18n, handlers per module, keyboards, file storage under `telegram_bot/storage/`.
2. `requirements-bot.txt`.
3. `.env.example` includes `TELEGRAM_BOT_TOKEN=`.
4. README run steps.
5. A manual test checklist covering: /start language switch, guest blocked send, register password rules, each of the 8 module menus, bank date-gap error, tax year gate, HR fire confirmation.

Start by scaffolding the bot and the main menu, then implement modules in the order above. Keep handlers small and named after the website sections.
