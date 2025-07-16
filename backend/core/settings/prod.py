from core.settings.base import *

# --- SECURITY WARNING: don't run with debug turned on in production! ---
DEBUG = env.bool("DJANGO_DEBUG", default=False)

# --- Allowed hosts ---
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# --- Email configuration ---
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")

DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL")

# --- Static files (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_VERSION = "1.0.0"
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- Media files (user-uploaded files) ---
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Database configuration ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSTGRES_DB", default=""),
        "USER": env.str("POSTGRES_USER", default=""),
        "PASSWORD": env.str("POSTGRES_PASSWORD", default=""),
        "HOST": env.str("POSTGRES_HOST", default="db"),  # Use 'db' for Docker container
        "PORT": env.int("POSTGRES_PORT", default=5432),
    }
}

# --- Cache Configuration ---
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://redis:{env("REDIS_PORT", default=6379)}/1',  # 1 to separate from celery
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'fast_miveh',
    }
}

# --- Session Configuration ---
# In order for sessions to be stored in Redis cache and subscribe to the workers
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# --- CORS configuration
CORS_ALLOWED_ORIGINS = [
    # "your_domain"
]
