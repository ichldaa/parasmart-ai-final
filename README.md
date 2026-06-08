# ParaSmart AI 🤖

Aplikasi web berbasis Django untuk **Parafrase AI** dan **Cek Plagiarisme** mahasiswa.

---

## 🚀 Cara Menjalankan di Lokal

### 1. Clone & Setup
```bash
git clone https://github.com/USERNAME/parasmart-ai.git
cd parasmart-ai

# Buat virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# atau
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Setting API Key
```bash
# Buat file .env di root folder (sejajar requirements.txt)
# Isi dengan:
ANTHROPIC_API_KEY=sk-ant-xxxxx-api-key-kamu
SECRET_KEY=django-secret-key-random
DEBUG=True
```

Edit `parasmart_project/settings.py`:
```python
# Ganti baris ini:
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', 'your-api-key-here')
# Menjadi (langsung):
ANTHROPIC_API_KEY = 'sk-ant-api-key-kamu-disini'
```

### 3. Jalankan Server
```bash
cd parasmart_project
python manage.py migrate
python manage.py runserver
```
Buka: http://127.0.0.1:8000

### 4. Login Pertama
- Buat akun baru lewat `/register/`
- Atau login admin: username=`admin`, password=`admin123`

---

## 📁 Struktur Folder
```
parasmart-ai/
├── requirements.txt
├── Procfile               # untuk deploy Render/Railway
├── .gitignore
├── README.md
└── parasmart_project/
    ├── manage.py
    ├── db.sqlite3
    ├── parasmart_project/
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── core/
        ├── models.py      # Database models
        ├── views.py       # Logic aplikasi
        ├── urls.py        # URL routing
        ├── admin.py
        └── templates/core/
            ├── base.html        # Layout utama (sidebar)
            ├── login.html
            ├── register.html
            ├── dashboard.html
            ├── parafrase.html
            ├── plagiarisme.html
            ├── upload.html
            └── history.html
```

---

## 🌐 Deploy ke Render

1. Push ke GitHub
2. Buka render.com → New Web Service
3. Connect GitHub repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `cd parasmart_project && python manage.py migrate && gunicorn parasmart_project.wsgi:application`
6. Environment Variables: tambahkan `ANTHROPIC_API_KEY`, `SECRET_KEY`, `DEBUG=False`

---

## 🔧 Teknologi
- **Backend**: Python Django 6.x
- **Database**: SQLite (Django ORM)
- **Frontend**: HTML + Bootstrap 5 + JavaScript
- **AI**: Anthropic Claude API (parafrase)
- **Plagiarisme**: TF-IDF + Cosine Similarity (custom)
- **File**: PyMuPDF (PDF), plain text (TXT)

---

## 👥 Tim Authentix
- Rina Herlina (2411102441184)
- Salwa Khairani (2411102441192)  
- Mahdillah (2411102441194)
- Hilda Angelica Agnes Saksono (2411102441195)
- S. Zahra Adelia (2411102441290)

**Universitas Muhammadiyah Kalimantan Timur - 2026**
