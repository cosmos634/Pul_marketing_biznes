# Biznes Akademiya

O‘zbek tilidagi 30 kunlik moliya, psixologiya, marketing, savdo va biznes strategiyasi kursini o‘rganish uchun lokal web-ilova.

## Imkoniyatlar
- 5 modul va 30 kunlik dars dasturi
- Har bir darsda nazariya, misol, amaliy vazifa va vaziyatli mashq
- Har dars uchun 3 ta bilim tekshiruvi savoli
- 60% yoki undan yuqori natijada darsni tugallangan deb belgilash
- Progress, shaxsiy qaydlar va saqlangan darslar
- Dars qidiruvi, JSON zaxira nusxasi va import
- SQLite; tashqi API yoki doimiy internet talab qilinmaydi
- Mobil va desktop ekranlariga mos interfeys

## Ishga tushirish

Python 3.10 yoki undan yangiroq versiya kerak.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Brauzerda http://127.0.0.1:5000 manzilini oching.

## Dastlabki o‘quv holati
1–3-kunlar tugallangan va 4-kun keyingi dars qilib belgilangan.

## Loyiha tuzilmasi
- `app.py` — Flask ilovasi, SQLite modellari va API
- `seed.py` — 5 modul, 30 dars va testlarni boshlang‘ich bazaga joylash
- `templates/index.html` — interfeys
- `static/style.css` — dizayn va responsive layout
- `static/app.js` — sahifa boshqaruvi va interaktivlik
- `tests/test_app.py` — asosiy endpoint testlari
- `instance/academy.db` — lokal ma’lumotlar bazasi (Git'ga yuborilmaydi)

## Testlar
```bash
python -m unittest discover -s tests
```

## Litsenziya
MIT — [LICENSE](LICENSE).
