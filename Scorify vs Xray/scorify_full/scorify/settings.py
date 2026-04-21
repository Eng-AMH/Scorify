from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _bool_env(name, default="False"):
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _csv_env(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def _trusted_origins_env(name, default_site_url):
    """
    Returns a list like:
    ['https://scorify.pythonanywhere.com']
    """
    values = _csv_env(name, default_site_url)
    normalized = []
    for value in values:
        value = value.rstrip("/")
        if value.startswith("http://") or value.startswith("https://"):
            normalized.append(value)
        else:
            normalized.append(f"https://{value}")
    return normalized


SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = _bool_env("DEBUG", "False")
ALLOWED_HOSTS = _csv_env(
    "ALLOWED_HOSTS",
    "scorify.pythonanywhere.com,127.0.0.1,localhost",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "roaster",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "roaster.middleware.DBRateLimitMiddleware",
]

ROOT_URLCONF = "scorify.urls"
WSGI_APPLICATION = "scorify.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "roaster.context_processors.branding",
            ]
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "django_cache",
        "TIMEOUT": 604800,
        "OPTIONS": {"MAX_ENTRIES": 1000},
    }
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", os.environ["EMAIL_HOST_USER"])
DEFAULT_FROM_EMAIL = f'Scorify <{os.environ["EMAIL_HOST_USER"]}>'

SITE_URL = os.getenv("SITE_URL", "https://scorify.pythonanywhere.com").rstrip("/")
CSRF_TRUSTED_ORIGINS = _trusted_origins_env("CSRF_TRUSTED_ORIGINS", SITE_URL)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG and SITE_URL.startswith("https://")

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
PADDLE_API_KEY = os.getenv("PADDLE_API_KEY", "")
PADDLE_VENDOR_ID = os.getenv("PADDLE_VENDOR_ID", "")
PADDLE_PRODUCT_ID = os.getenv("PADDLE_PRODUCT_ID", "")

UPLOAD_RATE_LIMIT_ANON = int(os.getenv("UPLOAD_RATE_LIMIT_ANON", "5"))
UPLOAD_RATE_LIMIT_WINDOW = int(os.getenv("UPLOAD_RATE_LIMIT_WINDOW", "3600"))
REFERRAL_BONUS_UPLOADS = int(os.getenv("REFERRAL_BONUS_UPLOADS", "3"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: "error",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
}

# Security: do not keep admin/front-end sessions around forever
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 8
