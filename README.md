<div align="center">

<br/>


# Scorify

**AI-Powered CV Roaster & Scorer**

Score your CV. Fix your flaws. Land your dream job.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=flat)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-8B5CF6?style=flat)](LICENSE)
[![Deploy](https://img.shields.io/badge/Deploy-PythonAnywhere-1D8348?style=flat)](https://pythonanywhere.com)

[Live Demo](https://Scorify.pythonanywhere.com) · [Report Bug](https://github.com/AMHSystems/scorify/issues) · [Request Feature](https://github.com/AMHSystems/scorify/issues)

</div>

---

## ✨ Features

| Feature | Free | Pro | VIP |
|---|:---:|:---:|:---:|
| CV Scoring (0–100) | ✅ 3/day | ✅ Unlimited | ✅ Unlimited |
| Section Breakdown | ✅ | ✅ | ✅ |
| AI Roast Feedback | ✅ | ✅ | ✅ |
| Detailed Improvements | ❌ | ✅ | ✅ |
| PDF Export | ❌ | ✅ | ✅ |
| CV Comparison | ❌ | ✅ | ✅ |
| S×X Mode (Ultra AI) | ❌ | ❌ | ✅ |
| Rewrite Suggestions | ❌ | ❌ | ✅ |

### 🎨 3-Mode Visual System
- **Scorify Mode** — Fire & purple — default experience
- **Xray Mode** — Cyan & blue — technical scan aesthetic
- **S×X Mode** — Purple & cyan fusion — VIP ultra mode

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Groq API Key](https://console.groq.com) (free)
- Gmail account (for OTP emails)

### Local Setup

```bash
# 1. Clone
git clone https://github.com/AMHSystems/scorify.git
cd scorify

# 2. Virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — add your GROQ_API_KEY and email credentials

# 5. Database
python manage.py migrate

# 6. Run
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000)

---

## 🌐 Deploy to PythonAnywhere

See **[DEPLOY.md](DEPLOY.md)** for the full step-by-step guide.

**Quick version:**

```bash
# In PA Bash console
cd ~
git clone https://github.com/AMHSystems/scorify.git scorify
cd scorify
pip install -r requirements.txt --user
cp .env.example .env && nano .env   # fill in your values
python manage.py migrate
python manage.py collectstatic --noinput
```

Then in the **Web tab**:
- Set source directory: `/home/Scorify/scorify`
- WSGI file: copy content from `WSGI_PYTHONANYWHERE.py`
- Static: `/static/` → `/home/Scorify/scorify/staticfiles`
- Media: `/media/` → `/home/Scorify/scorify/media`

---

## 🗂️ Project Structure

```
scorify/
├── manage.py
├── requirements.txt
├── .env.example
├── WSGI_PYTHONANYWHERE.py   ← PythonAnywhere WSGI config
│
├── scorify/                 ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── roaster/                 ← Main app
    ├── views.py             ← All page & API views
    ├── models.py            ← User, CVAnalysis, Profile, etc.
    ├── ai.py                ← Groq LLaMA integration
    ├── emails.py            ← OTP & notification emails
    ├── urls.py
    │
    ├── static/roaster/
    │   ├── css/
    │   │   ├── shared.css   ← Global vars, layout, modes
    │   │   ├── index.css    ← Landing page
    │   │   ├── dashboard.css
    │   │   ├── profile.css
    │   │   ├── compare.css
    │   │   ├── auth.css
    │   │   └── admin.css
    │   ├── js/
    │   │   ├── mode.js      ← 3-mode system (Scorify/Xray/S×X)
    │   │   ├── shared.js    ← Sidebar, theme, utilities
    │   │   ├── index.js     ← Landing page logic
    │   │   ├── dashboard.js ← Upload, analysis, chart
    │   │   └── ...
    │   └── img/
    │       ├── logo-scorify.png
    │       ├── logo-xray.png
    │       └── logo-sx.png
    │
    └── templates/roaster/
        ├── base.html        ← Base template (all pages extend this)
        ├── index.html
        ├── dashboard.html
        ├── profile.html
        ├── compare.html
        ├── login.html
        ├── register.html
        └── ...
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `False` in production |
| `ALLOWED_HOSTS` | Your domain(s) |
| `GROQ_API_KEY` | From [console.groq.com](https://console.groq.com) |
| `EMAIL_HOST_USER` | Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail App Password |
| `PADDLE_API_KEY` | Paddle payments (optional) |

---

## 🤖 AI Stack

- **Model:** `llama-3.3-70b-versatile` via [Groq](https://groq.com)
- **CV Parsing:** `pdfplumber` (PDF) + `python-docx` (Word)
- **Output:** Structured JSON scores per section + roast lines + rewrite suggestions

---

## 🛠️ Tech Stack

- **Backend:** Django 4.2, Python 3.10+
- **AI:** Groq API — LLaMA 3.3 70B
- **Frontend:** Vanilla JS + CSS custom properties (no framework)
- **Database:** SQLite (dev) → SQLite on PythonAnywhere (prod)
- **Static:** WhiteNoise
- **Payments:** Paddle
- **Email:** Gmail SMTP (OTP auth)

---

## 📄 License

MIT © [AMH Systems](https://github.com/AMHSystems)

---

<div align="center">
  Built with 🔥 by <a href="https://github.com/AMHSystems">AMH Systems</a>
</div>
