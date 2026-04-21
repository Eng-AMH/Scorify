# Deploying Scorify to PythonAnywhere

## 1. Create PythonAnywhere Account
Sign up at [pythonanywhere.com](https://pythonanywhere.com). Free tier works.

---

## 2. Open a Bash Console

Go to **Consoles → Bash**.

```bash
# Clone the project
git clone https://github.com/AMHSystems/scorify.git scorify
cd scorify

# Install dependencies
pip install -r requirements.txt --user

# Set up environment
cp .env.example .env
nano .env
```

Fill in `.env` — minimum required:
```
SECRET_KEY=some-long-random-string-here
DEBUG=False
ALLOWED_HOSTS=YourUsername.pythonanywhere.com,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://YourUsername.pythonanywhere.com
SITE_URL=https://YourUsername.pythonanywhere.com
GROQ_API_KEY=your-groq-key
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

```bash
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

---

## 3. Create Web App

Go to **Web tab → Add a new web app**:
- Framework: **Manual configuration**
- Python version: **3.10** (or latest available)

---

## 4. WSGI Configuration

Click your web app → **WSGI configuration file**.

Delete everything and paste:

```python
import os, sys
from pathlib import Path
from dotenv import load_dotenv

project_path = '/home/YourUsername/scorify'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

load_dotenv(Path(project_path) / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scorify.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

> Replace `YourUsername` with your actual PythonAnywhere username.

---

## 5. Static & Media Files

In **Web tab → Static files**, add:

| URL | Directory |
|---|---|
| `/static/` | `/home/YourUsername/scorify/staticfiles` |
| `/media/` | `/home/YourUsername/scorify/media` |

---

## 6. Reload & Test

Click **Reload** and visit `https://YourUsername.pythonanywhere.com`

---

## Updating After Code Changes

```bash
cd ~/scorify
git pull
python manage.py migrate          # only if models changed
python manage.py collectstatic --noinput   # only if static files changed
# Then click Reload in Web tab
```
