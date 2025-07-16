from pathlib import Path

from django.utils.translation import gettext_lazy as _

from environ import Env

# --- Build paths inside the project like this: BASE_DIR / 'subdir'. ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Load environment variables from .env file ---
env = Env()
Env.read_env(str(BASE_DIR / ".env"))

# --- SECURITY WARNING: keep the secret key used in production secret! ---
SECRET_KEY = env.str("DJANGO_SECRET_KEY")

# --- Application definition ---
DEFAULT_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    # "rest_framework_simplejwt",
    # "phonenumber_field",
    "celery",
    "rosetta",
]

LOCAL_APPS = [
    "apps.common",
    "apps.account",
    "apps.notification",
    # "apps.store",
    # "apps.inventory",
    # "apps.checkout",
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --- Middleware configuration ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- URL configuration ---
ROOT_URLCONF = "core.urls"
# FORCE_SCRIPT_NAME = '/api'

# --- Template configuration ---
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
            ],
        },
    },
]

# --- WSGI application configuration ---
WSGI_APPLICATION = "core.wsgi.application"

# --- Password validation ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalization ---
# https://docs.djangoproject.com/en/5.0/topics/i18n/
USE_TZ = True
USE_I18N = True
USE_L10N = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
LANGUAGES = (
    ("en", _("English")),
    ("fa", _("Persian")),
)
LOCALE_PATHS = [BASE_DIR / "locale"]

# --- Default primary key field type ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Slug Configuration ---
ALLOW_UNICODE_SLUGS = True

# --- Authentication Configuration ---
AUTH_USER_MODEL = "account.User"
AUTHENTICATION_BACKENDS = [
    'apps.account.backends.IdentifierBackend',  # Custom backend for identifier (email or phone) + password login
    'apps.account.backends.OTPBackend',  # Custom backend for OTP login
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth backend
]
# LOGIN_URL = 'account:login'
PASSWORD_RESET_TIMEOUT = 259200  # Default: 259200 seconds = 3 days

# --- Site Configuration ---
SITE_NAME = _("Fast Miveh")
FRONTEND_URL = {
    'PASSWORD_RESET_CONFIRM': env.str("DJANGO_FRONTEND_URL_PASSWORD_RESET"),
}

# --- Third Party Configuration ---
from core.settings.third_party_config import *

# --- Celery Configuration ---
from core.settings.celery_config import *

# --- Django Rest Framework Configuration ---
from core.settings.drf_config import *

# --- Logging Configuration ---
from core.settings.logging_config import *
