# Voice API - Django Rest Framework

"Voice" o'quv platformasi uchun Topic va Quiz boshqaruv API.

## Texnologiyalar

- Python 3.11
- Django 5.2.9
- Django Rest Framework
- SQLite (development), PostgreSQL (production tavsiya)
- drf-spectacular (API dokumentatsiya)

## O'rnatish

### 1. Loyihani klonlash

```bash
git clone <repository-url>
cd book_api
```

### 2. Virtual environment va paketlar

Pipenv ishlatiladi:

```bash
pipenv install
pipenv shell
```

### 3. Environment variables

`.env.example` faylini `.env` ga nusxalang va sozlamalarni to'ldiring:

```bash
cp .env.example .env
```

`.env` faylini tahrirlang va `SECRET_KEY` va boshqa qiymatlarni o'zgartiring.

### 4. Ma'lumotlar bazasi

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Static fayllar (production uchun)

```bash
python manage.py collectstatic
```

### 6. Serverni ishga tushirish

Development:

```bash
python manage.py runserver
```

## API Endpointlar

- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **API Schema**: `http://127.0.0.1:8000/api/schema/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`

### Asosiy endpointlar

- `GET /api/topics/` - Barcha topiclar ro'yxati
- `GET /api/topics/{id}/` - Bitta topic ma'lumoti
- `PATCH /api/topics/{id}/` - Topic statusini o'zgartirish
- `POST /api/topics/{id}/complete_quiz/` - Quizni tugatish

## Deploy (PythonAnywhere)

### 1. Kodni yuklash

GitHub orqali:

```bash
git clone <repository-url>
cd book_api
```

### 2. Virtual environment

```bash
pipenv install --deploy
pipenv shell
```

### 3. Environment variables

PythonAnywhere dashboard → **Files** → `.env` fayl yarating:

```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
CORS_ALLOW_ALL_ORIGINS=False
CSRF_TRUSTED_ORIGINS=https://yourusername.pythonanywhere.com
```

### 4. Migratsiyalar va superuser

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

### 5. Web app sozlamalari

**Web** → **Add a new web app** → **Manual configuration**

- **Virtualenv**: `/home/yourusername/.local/share/virtualenvs/book_api-XXXXX` (pipenv virtualenv yo'li)
- **WSGI config**: Django'ga moslang

WSGI faylida:

```python
import os
import sys

path = '/home/yourusername/book_api'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 6. Static va Media fayllar

**Web** → **Static files**:

- `/static/` → `/home/yourusername/book_api/staticfiles`
- `/media/` → `/home/yourusername/book_api/media`

**Reload** web app.

## Admin Panel

Admin panelda quiz fayllarni yuklash:

1. Topic yaratish/tahrirlash
2. `quiz_file` maydoniga `.docx` yoki `.txt` fayl yuklash
3. Save bosilganda avtomatik savollar import qilinadi

Quiz fayl formati (har savol 6 qator):

```
Savol matni?
A) Variant 1
B) Variant 2
C) Variant 3
D) Variant 4
Javob: A
```

## Muammolar

Agar `python-docx` topilmasa:

```bash
pipenv install python-docx
```

Agar static fayllar ko'rinmasa:

```bash
python manage.py collectstatic --noinput
```

## Muallif

Voice Platform Development Team

