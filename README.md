# 🏆 Matematika Sertifikati — Django Loyihasi

## O'rnatish va Ishga Tushirish

### 1. Django o'rnatish
```bash
pip install django
```

### 2. Loyiha papkasiga o'tish
```bash
cd matematika_django
```

### 3. Ma'lumotlar bazasini yaratish
```bash
python manage.py migrate
```

### 4. Savollarni yuklash (1080 ta savol)
```bash
python manage.py load_questions
```

### 5. Admin foydalanuvchi yaratish
```bash
python manage.py createsuperuser
```
(ism, email, parol kiriting)

### 6. Serverni ishga tushirish
```bash
python manage.py runserver
```

### 7. Brauzerda ochish
- **Quiz:** http://127.0.0.1:8000/
- **Admin panel:** http://127.0.0.1:8000/admin/
- **Reyting:** http://127.0.0.1:8000/leaderboard/

---

## Loyiha tuzilmasi

```
matematika_django/
├── manage.py
├── requirements.txt
├── db.sqlite3          (avtomatik yaratiladi)
├── matematika/         (asosiy Django settings)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── quiz/               (quiz ilovasi)
│   ├── models.py       (Question, QuizResult modellari)
│   ├── views.py        (barcha sahifalar)
│   ├── urls.py
│   ├── admin.py        (admin panel sozlamalari)
│   ├── questions_data.json  (1080 ta savol)
│   └── management/commands/load_questions.py
└── templates/quiz/     (HTML shablonlar)
    ├── base.html
    ├── home.html
    ├── level_select.html
    ├── quiz.html
    ├── result.html
    └── leaderboard.html
```

## Admin Panel imkoniyatlari
- **Savollar boshqaruvi:** yangi qo'shish, tahrirlash, o'chirish
- **Daraja bo'yicha filtrlash**
- **Natijalar kuzatuvi:** kim qanday natija olgan
- **Rang va foiz ko'rinishida baho**

## Xususiyatlar
- 6 daraja: C, C+, B, B+, A, A+
- 822 ta savol (HTML fayldan import qilingan)
- Har savolda 60 soniya taymer
- Javoblar rangli ko'rsatiladi (yashil/qizil)
- Natijalar saqlanadi
- Reyting sahifasi
- To'liq admin panel
