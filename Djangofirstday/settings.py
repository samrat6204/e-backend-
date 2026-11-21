"""
Saauzi — Django Settings
========================
Project  : Saauzi E-Commerce
Backend  : Django 6.1 + Django REST Framework
Auth     : JWT (djangorestframework-simplejwt)
Database : SQLite (development)
Email    : Gmail SMTP via custom SSL backend
"""

from pathlib import Path
from datetime import timedelta

# ─── BASE PATH ───────────────────────────────────────────────────────────────
# All file paths inside the project are built from this base.
BASE_DIR = Path(__file__).resolve().parent.parent


# ─── SECURITY ────────────────────────────────────────────────────────────────
# WARNING: Keep the secret key private. Never commit a real key to GitHub.
SECRET_KEY = 'django-insecure-g7z6zx*8s5c7g%s#ue5a43-lo!q&3_97xasf-5zg0+@=#kansq'

# WARNING: Set DEBUG = False in production.
DEBUG = True

# Allow all hosts in development. Restrict this in production.
ALLOWED_HOSTS = ["*"]

# Prevent 500 error when a POST request is missing the trailing slash.
# Returns a clean 404 instead of crashing.
APPEND_SLASH = False


# ─── INSTALLED APPS ──────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Third-party
    "rest_framework",           # Django REST Framework — builds the API
    "rest_framework_simplejwt", # JWT authentication tokens
    "corsheaders",              # Allow React (port 5173) to call Django (port 8000)

    # Django built-ins
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Our app
    "app1",
]


# ─── REST FRAMEWORK ──────────────────────────────────────────────────────────
# Every API endpoint uses JWT for authentication by default.
# Endpoints marked @permission_classes([AllowAny]) skip this check.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}


# ─── JWT TOKEN SETTINGS ──────────────────────────────────────────────────────
# Access token: short-lived (60 min) — used for every API request.
# Refresh token: long-lived (7 days) — used to get a new access token.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),  # Authorization: Bearer <token>
}


# ─── CORS ────────────────────────────────────────────────────────────────────
# Allow the React frontend to call this API from a different port/domain.
CORS_ALLOW_ALL_ORIGINS = True  # Restrict to specific origins in production.


# ─── MIDDLEWARE ──────────────────────────────────────────────────────────────
# CorsMiddleware must be first so it handles OPTIONS preflight requests.
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ─── URL CONFIGURATION ───────────────────────────────────────────────────────
ROOT_URLCONF = "Djangofirstday.urls"


# ─── TEMPLATES ───────────────────────────────────────────────────────────────
# DIRS includes our custom email HTML templates folder.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "app1" / "Templets"],  # Email HTML templates live here
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ─── WSGI ────────────────────────────────────────────────────────────────────
WSGI_APPLICATION = "Djangofirstday.wsgi.application"


# ─── DATABASE ────────────────────────────────────────────────────────────────
# SQLite is fine for development. Switch to PostgreSQL for production.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ─── CUSTOM USER MODEL ───────────────────────────────────────────────────────
# We use a custom User model (app1.User) that adds full_name and phone_number.
AUTH_USER_MODEL = "app1.User"


# ─── PASSWORD VALIDATION ─────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ─── INTERNATIONALISATION ────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ─── STATIC & MEDIA FILES ────────────────────────────────────────────────────
# Static files (CSS, JS built assets)
STATIC_URL = "static/"

# Media files — product images uploaded by admin are saved here.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ─── EMAIL (Gmail SMTP) ──────────────────────────────────────────────────────
# We use a custom backend (NoVerifyEmailBackend) that skips SSL certificate
# verification. This is required on Windows where Python cannot verify
# Gmail's certificate chain.
#
# To change the sender email, update EMAIL_HOST_USER and DEFAULT_FROM_EMAIL.
# The password must be a Gmail App Password (not your Gmail login password).
# Generate one at: myaccount.google.com → Security → App passwords
EMAIL_BACKEND = "app1.email_backend.NoVerifyEmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True                             # Encrypt with STARTTLS
EMAIL_HOST_USER = "samratlamichhane46@gmail.com"
EMAIL_HOST_PASSWORD = "yxsm smyd ljtc elnn"     # Gmail App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
