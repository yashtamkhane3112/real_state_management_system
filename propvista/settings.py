from pathlib import Path
from urllib.parse import urlparse

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-only-propvista-secret-key-change-me-2026-local")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "testserver"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_filters",
    "accounts",
    "properties",
    "inquiries",
    "favorites",
    "visits",
    "leads",
    "analytics",
    "notifications",
    "reports",
    "search",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "propvista.urls"
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
                "propvista.context.site_settings",
            ],
        },
    }
]
WSGI_APPLICATION = "propvista.wsgi.application"
ASGI_APPLICATION = "propvista.asgi.application"
AUTH_USER_MODEL = "accounts.User"

PLACEHOLDER_DB_VALUES = {"", "host", "db", "database", "user", "username", "password", "pass", "changeme", "change-me"}


def sqlite_database():
    return {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}


def is_placeholder(value):
    return str(value or "").strip().lower() in PLACEHOLDER_DB_VALUES


def valid_database_url(value):
    if not value:
        return False
    parsed = urlparse(value)
    if parsed.scheme not in {"postgres", "postgresql", "psql"}:
        return False
    return not any(is_placeholder(part) for part in [parsed.hostname, parsed.username, parsed.password, parsed.path.lstrip("/")])


def postgres_env_database():
    name = env("DB_NAME", default="")
    user = env("DB_USER", default="")
    password = env("DB_PASSWORD", default="")
    host = env("DB_HOST", default="")
    port = env("DB_PORT", default="5432")
    if any(is_placeholder(part) for part in [name, user, password, host]):
        return None
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port or "5432",
    }


DATABASE_URL = env("DATABASE_URL", default="")
if valid_database_url(DATABASE_URL):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {"default": postgres_env_database() or sqlite_database()}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:dashboard"
LOGOUT_REDIRECT_URL = "home"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticatedOrReadOnly",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "PropVista API",
    "DESCRIPTION": "Django REST API for the PropVista real estate portfolio platform.",
    "VERSION": "1.0.0",
}

GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
GOOGLE_MAPS_API_KEY = env("GOOGLE_MAPS_API_KEY", default="")

# Email SMTP Settings
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")

# Force SMTP if credentials are configured, overriding console fallback from .env
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD and EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="PropVista <noreply@propvista.com>")

# Landing page media configuration mode
LANDING_MEDIA_MODE = env("LANDING_MEDIA_MODE", default="VIDEO_HERO")

