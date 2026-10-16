# FinAccount.uz — MVP (yakuniy)

Traditional Django UI based on `MVP TI(yakuniy).docx`.

## Run (venv)

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/

## PythonAnywhere (`finaccount.pythonanywhere.com`)

Use `config.settings_pa` on the server. Copy `.env.example` to `.env` and set a real `SECRET_KEY`. Then migrate, `collectstatic`, point the Web app WSGI file at this project, map `/static/` to `staticfiles`, and Reload.

## Modules in sidebar

1. **Tashkilot ma’lumotlari** — asosiy ma’lumotlar, hujjatlar, bank hisoblari, Telegram
2. **Soliq** — elektron shakllar, jurnal, shakllanayotgan hisobotlar
3. **Bank** — aylanma, avto-provodka, arxiv (+ sana ketma-ketligi tekshiruvi)
4. **To‘lovlar va solishtirma** — to‘lovlar tarixi/shakllantirish, soliq va kontragent solishtirma
5. **Asosiy vositalar** — reyestr, amortizatsiya, inventarizatsiya
6. **Inventar va TMZ** — reyestr, kirim-chiqim, omborlar, inventarizatsiya
7. **EHF** — kiruvchi/chiquvchi/loyiha/shartnomalar/arxiv
8. **HR** — xodimlar, ish haqi, JShDS, buyruqlar arxivi

## Notes

- Landing: Register / Guest, UZ/RU/EN
- App shell: blue sidebar + topbar profile + watermark
- Demo data is in views (no my.soliq.uz / my.mehnat.uz live APIs yet)
- Guest can browse UI; send/report integrations are deferred
