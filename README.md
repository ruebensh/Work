# O'quv markazi to'lovlarini hisobga olish — mini-tizim

Ecomdev test topshirigi. Uch markazining o'quvchilari va oylik to'lovlarini
hisobga oladigan kichik tizim: **REST API**, **Telegram bot** va **mobil web-interfeys**.

- **Stack:** Python 3.11+, FastAPI, SQLAlchemy 2, SQLite, python-telegram-bot v22, vanilla HTML/CSS/JS
- **Muallif:** Jaloliddin Xalimov

## Imkoniyatlar

| Qism | Nima |
|------|------|
| 1. API | O'quvchilar CRUD, to'lovlar qo'shish/ro'yxat, `GET /debtors?month=YYYY-MM` |
| 2-A. Bot | `/debt`, `/pay <id> <summa>`, `/students`, `/help` |
| 2-B. Web | Dolzniklar ro'yxati + to'lov qo'shish formasi (mobilga mos) |
| Testlar | 37 ta pytest testi (API + bot yordamchilari) |

## Tuzilma

```
app/            FastAPI ilovasi
  config.py     .env'dan sozlamalar
  db.py         engine, SessionLocal, get_db
  models.py     Student, Payment (SQLAlchemy ORM)
  schemas.py    Pydantic kontraktlari + validatsiya
  routers/      students.py, payments.py, debtors.py
  services/     debtors.py — qarzdorlik hisobi (API va bot umumiy ishlatadi)
bot/            Telegram boti
  main.py        ishga tushirish (polling)
  handlers.py    /debt /pay /students /help
  formatting.py  DB'siz, testlanadigan formatlash/parsing
web/index.html  mobil web-interfeys (API bilan birga serve qilinadi)
tests/          pytest
data/           SQLite fayli (git'ga kirmaydi)
```

## Noladan ishga tushirish

> Talab: Python 3.11+.

```bash
# 1. Virtual muhit + bog'liqliklar
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Sozlamalar (.env — ixtiyoriy, API/DB uchun shart emas)
cp .env.example .env             # token kerak bo'lsa TELEGRAM_BOT_TOKEN to'ldiring

# 3. API + web-interfeys (http://127.0.0.1:8000)
uvicorn app.main:app --reload
```

- API hujjati (Swagger): http://127.0.0.1:8000/docs
- Web-interfeys: http://127.0.0.1:8000/  (telefon o'lchamida qulay)

### Telegram bot (alohida jarayon)

```bash
# @BotFather → /newbot → token oling → .env ichiga TELEGRAM_BOT_TOKEN=... yozing
python -m bot.main
```

Bot API bilan **bitta SQLite bazasi va `app/services` kodini** bo'lishadi —
ma'lumotlar bir xil qoladi.

### Testlar

```bash
pytest -q            # 37 passed
```

## API endpointlari

| Metod | Yo'l | Vazifa |
|-------|------|--------|
| POST | `/students` | O'quvchi yaratish (ism, telefon, guruh, oylik summa) |
| GET | `/students` | Ro'yxat |
| GET | `/students/{id}` | Bitta o'quvchi |
| PATCH | `/students/{id}` | Qisman tahrirlash |
| DELETE | `/students/{id}` | O'chirish (to'lovlar kaskad bilan ketadi) |
| POST | `/payments` | To'lov qo'shish (student_id, summa, sana) |
| GET | `/payments?student_id=` | O'quvchi to'lovlari (yangidan eski) |
| GET | `/debtors?month=YYYY-MM` | Oylik summasidan kam to'laganlar + qarz |

**Dolznik hisobi:** tanlangan oy ichidagi (chegaralar bilan) to'lovlar yig'indisi
oylik summadan kam bo'lsa — farq qarz sifatida qaytadi. Umuman to'lamagan ham
dolznik, to'liq/ortiqcha to'lagan ro'yxatga kirmaydi.

## Yana bir hafta vaqt bo'lsa yaxshilagan bo'lar edim

1. **Avtentifikatsiya va rollar.** Hozir API ochiq; administrator/oyovchi rollari,
   JWT yoki sessiya orqali kirish va har bir amaldagi audit-jurnal (kim qachon to'lov kiritdi).
2. **PostgreSQL + migratsiyalar (Alembic).** SQLite demo uchun qulay, lekin ko'p
   foydalanuvchida lock muammolari bo'ladi; sxema o'zgarishlarini migratsiya orqali boshqarish.
3. **To'lovlar bo'yicha to'liq CRUD va qaytarish (refund).** Hozir faqat qo'shish va
   ko'rish; xato kiritilgan to'lovni tahrirlash/o'chirish va oy oralig'i statistikasi kerak.
4. **Frontendni real framework'ga o'tkazish + testlar.** Hozir vanilla JS; Vue/React bilan
   komponentlarga bo'lish, o'quvchilarni qidiruv/filtr, grafik hisobotlar va Playwright E2E testlari.
5. **Docker + CI.** `docker-compose` (app + db), GitHub Actions'da lint + pytest + migratsiya,
   production uchun gunicorn/uvicorn workers va zaxira-nusxa (backup) rejasi.
