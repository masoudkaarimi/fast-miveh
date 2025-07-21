import os
from pathlib import Path
from datetime import timedelta

from django.utils.translation import gettext_lazy as _

from celery.schedules import crontab
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
    "apps.media",
    "apps.products",
    # "apps.reviews",
    # "apps.orders",
    # "apps.payments",
    # "apps.discounts",
    # "apps.analytics",
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

# --- OTP configuration ---
OTP_SETTINGS = {
    'OTP_LENGTH': 6,
    'OTP_EXPIRY_MINUTES': 2,
    'MAX_ATTEMPTS': 5,
    'COOLDOWN_SECONDS': 60,
}

# --- Notification settings ---
NOTIFICATIONS_SETTINGS = {
    'ACTIVE_EMAIL_PROVIDER': env.str('DJANGO_ACTIVE_EMAIL_PROVIDER', default='default'),
    'EMAIL_PROVIDERS': {
        'default': {
            'CHANNEL_CLASS': 'apps.notification.channels.email.EmailChannel',
            'CONFIG': {}
        },
        # You can add other providers like SendGrid here in the future
        # 'sendgrid': {
        #     'CHANNEL_CLASS': 'apps.notification.channels.email.SendGridEmailChannel',
        #     'CONFIG': { 'API_KEY': 'YOUR_SENDGRID_API_KEY' }
        # },
    },

    # --- SMS CHANNEL ---
    'ACTIVE_SMS_PROVIDER': env.str('DJANGO_ACTIVE_SMS_PROVIDER', default='console'),
    'SMS_PROVIDERS': {
        'console': {
            'CHANNEL_CLASS': 'apps.notification.channels.sms.ConsoleSMSChannel',
            'CONFIG': {}
        },
        # 'twilio': {
        #     'CHANNEL_CLASS': 'apps.notification.channels.sms.TwilioSMSChannel',
        #     'CONFIG': {
        #         'ACCOUNT_SID': 'YOUR_TWILIO_ACCOUNT_SID',
        #         'AUTH_TOKEN': 'YOUR_TWILIO_AUTH_TOKEN',
        #         'FROM_NUMBER': 'YOUR_TWILIO_PHONE_NUMBER',
        #     }
        # },
        'kavenegar': {
            'CHANNEL_CLASS': 'apps.notification.channels.sms.KavenegarSMSChannel',
            'CONFIG': {
                'API_KEY': env.str('DJANGO_KAVENEGAR_API_KEY', default=''),
            }
        },
    },

    # --- TELEGRAM CHANNEL (NEW) ---
    'ACTIVE_TELEGRAM_PROVIDER': env.str('DJANGO_ACTIVE_TELEGRAM_PROVIDER', default='default'),
    'TELEGRAM_PROVIDERS': {
        'default': {
            'CHANNEL_CLASS': 'apps.notification.channels.telegram.TelegramBotChannel',
            'CONFIG': {
                'TELEGRAM_BOT_TOKEN': env.str('DJANGO_TELEGRAM_BOT_TOKEN', default=''),
            }
        }
    },
}

# --- Rosetta configuration ---
# https://django-rosetta.readthedocs.io/
ROSETTA_MESSAGES_PER_PAGE = 100
ROSETTA_SHOW_AT_ADMIN_PANEL = True
# ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = "en-us"
# ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = "English"
# ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True

# --- File Upload Configuration ---
MAX_IMAGE_UPLOAD_SIZE_MB = 5
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp"]
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'mov', 'avi', 'webm']
ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt']

MAX_FILES_UPLOAD_SIZE_MB = 50
ALLOWED_FILE_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS + ALLOWED_VIDEO_EXTENSIONS + ALLOWED_DOCUMENT_EXTENSIONS

# --- Phone Number Fields Configuration ---
# PHONENUMBER_DEFAULT_REGION = "IR"

# --- Celery Configuration ---
# Set the celery broker url
CELERY_BROKER_URL = f'redis://redis:{env("REDIS_PORT")}/0'

# Set the celery result backend
CELERY_RESULT_BACKEND = f'redis://redis:{env("REDIS_PORT")}'

# Set the celery timezone
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    # 'clear-expired-reservations': {
    #     'task': 'apps.checkout.tasks.clear_expired_reservations',
    #     'schedule': crontab(minute='0', hour='0'),
    # }
}

# --- Django Rest Framework Configuration ---
REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     # 'rest_framework.permissions.IsAuthenticated',
    # ],
    # 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'VERSION_PARAM': 'version',
}

# --- Simple JWT Configuration ---
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),

    # # 'ROTATE_REFRESH_TOKENS': False,
    # # 'BLACKLIST_AFTER_ROTATION': True,
    # 'UPDATE_LAST_LOGIN': True,

    # # 'ALGORITHM': 'HS256',
    # # 'SIGNING_KEY': SECRET_KEY,
    # # 'VERIFYING_KEY': None,
    # # 'AUDIENCE': None,
    # # 'ISSUER': None,
    # # 'JWK_URL': None,
    # # 'LEEWAY': 0,

    # # 'AUTH_HEADER_TYPES': ('Bearer',),
    # # 'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    # # 'USER_ID_FIELD': 'id',
    # # 'USER_ID_CLAIM': 'user_id',
    # # 'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    # # 'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    # # 'TOKEN_TYPE_CLAIM': 'token_type',
    # # 'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    # # 'JTI_CLAIM': 'jti',

    # # 'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # # 'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    # # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# --- Spectacular Configuration ---
SPECTACULAR_SETTINGS = {
    # 'TITLE': 'Your Project API',
    # 'DESCRIPTION': 'Your project description',
    # 'VERSION': '1.0.0',
    # 'SERVE_INCLUDE_SCHEMA': False,
}

# --- Logging Configuration ---
LOGS_DIR = '/var/log/django'
Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_app': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'app.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file_app'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_app'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# --- CKEditor 5 Configuration ---
# CKEDITOR_5_CUSTOM_CSS = 'path_to.css'  # optional
# CKEDITOR_5_FILE_STORAGE = "path_to_storage.CustomStorage"  # optional
customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]
customColors = [
    {
        "color": 'hsl(0, 0%, 0%)',
        "label": 'Black'
    },
    {
        "color": 'hsl(0, 0%, 30%)',
        "label": 'Dim grey'
    },
    {
        "color": 'hsl(0, 0%, 60%)',
        "label": 'Grey'
    },
    {
        "color": 'hsl(0, 0%, 90%)',
        "label": 'Light grey'
    },
    {
        "color": 'hsl(0, 0%, 100%)',
        "label": 'White',
        "hasBorder": True
    },
    {
        "color": 'hsl(0, 75%, 60%)',
        "label": 'Red'
    },
    {
        "color": 'hsl(30, 75%, 60%)',
        "label": 'Orange'
    },
    {
        "color": 'hsl(60, 75%, 60%)',
        "label": 'Yellow'
    },
    {
        "color": 'hsl(90, 75%, 60%)',
        "label": 'Light green'
    },
    {
        "color": 'hsl(120, 75%, 60%)',
        "label": 'Green'
    },
    {
        "color": 'hsl(150, 75%, 60%)',
        "label": 'Aquamarine'
    },
    {
        "color": 'hsl(180, 75%, 60%)',
        "label": 'Turquoise'
    },
    {
        "color": 'hsl(210, 75%, 60%)',
        "label": 'Light blue'
    },
    {
        "color": 'hsl(240, 75%, 60%)',
        "label": 'Blue'
    },
    {
        "color": 'hsl(270, 75%, 60%)',
        "label": 'Purple'
    },
    {
        "color": 'hsl(300, 75%, 60%)',
        "label": 'Pink'
    },
    {
        "color": 'hsl(330, 75%, 60%)',
        "label": 'Magenta'
    },
    {
        "color": 'hsl(45, 75%, 60%)',
        "label": 'Gold'
    },
    {
        "color": 'hsl(75, 75%, 60%)',
        "label": 'Olive'
    },
    {
        "color": 'hsl(105, 75%, 60%)',
        "label": 'Lime'
    },
    {
        "color": 'hsl(135, 75%, 60%)',
        "label": 'Teal'
    },
    {
        "color": 'hsl(165, 75%, 60%)',
        "label": 'Cyan'
    },
    {
        "color": 'hsl(195, 75%, 60%)',
        "label": 'Sky blue'
    },
    {
        "color": 'hsl(225, 75%, 60%)',
        "label": 'Navy'
    },
    {
        "color": 'hsl(255, 75%, 60%)',
        "label": 'Indigo'
    },
    {
        "color": 'hsl(285, 75%, 60%)',
        "label": 'Violet'
    },
    {
        "color": 'hsl(315, 75%, 60%)',
        "label": 'Rose'
    },
    {
        "color": 'hsl(15, 75%, 60%)',
        "label": 'Sunset'
    },
    {
        "color": 'hsl(135, 90%, 60%)',
        "label": 'Bright Cyan'
    },
    {
        "color": 'hsl(270, 40%, 60%)',
        "label": 'Pastel Purple'
    },
    {
        "color": 'hsl(60, 90%, 60%)',
        "label": 'Intense Yellow'
    },
    {
        "color": 'hsl(90, 60%, 60%)',
        "label": 'Lemon'
    },
    {
        "color": 'hsl(210, 40%, 60%)',
        "label": 'Powder Blue'
    },
    {
        "color": 'hsl(120, 60%, 60%)',
        "label": 'Emerald'
    },
    {
        "color": 'hsl(30, 60%, 60%)',
        "label": 'Vivid Orange'
    },
    {
        "color": 'hsl(225, 50%, 60%)',
        "label": 'Sky'
    },
    {
        "color": 'hsl(150, 70%, 60%)',
        "label": 'Mint'
    },
    {
        "color": 'hsl(300, 70%, 60%)',
        "label": 'Candy Pink'
    },
    {
        "color": 'hsl(330, 60%, 60%)',
        "label": 'Lavender'
    },
    {
        "color": 'hsl(180, 90%, 60%)',
        "label": 'Hot Pink'
    },
]
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "styles",
            "heading",
            "|",
            "bold",
            "italic",
            "Underline",
            "link",
            "|",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "alignment",
        ],
    },
    "comment": {
        "language": {"ui": "en", "content": "en"},
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
        ],
    },
    "admin": {
        "language": "en",
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote"
        ],
        "toolbar": [
            "undo",
            "redo",
            "|",
            "heading",
            "codeBlock",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "alignment",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "insertImage",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
            "sourceEditing",
            "|",
            "horizontalLine",
        ],
        "fontColor": {
            "colors": customColors
        },
        "fontBackgroundColor": {
            "colors": customColors
        },
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:full",
                "imageStyle:side",
                "|",
                "toggleImageCaption",
                "|"
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter"
            ]
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties"
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette
            }
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph"
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1"
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2"
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3"
                },
                {
                    "model": "heading4",
                    "view": "h4",
                    "title": "Heading 4",
                    "class": "ck-heading_heading4"
                },
                {
                    "model": "heading5",
                    "view": "h5",
                    "title": "Heading 5",
                    "class": "ck-heading_heading5"
                },
                {
                    "model": "heading6",
                    "view": "h6",
                    "title": "Heading 6",
                    "class": "ck-heading_heading6"
                }
            ]
        },
        "list": {
            "properties": {
                "styles": True,
                "startIndex": True,
                "reversed": True
            }
        },
        "htmlSupport": {
            "allow": [
                {"name": "/.*/", "attributes": True,
                 "classes": True, "styles": True}
            ]
        },
        "simpleUpload": {
            "uploadUrl": "/uploads/"
        },
        "link": {
            "addTargetToExternalLinks": True
        },
        "extraPlugins": [
            "Essentials", "CodeBlock", "Autoformat", "Bold", "Italic", "Underline", "Strikethrough", "Code", "Subscript", "Superscript", "BlockQuote", "Heading", "Image",
            "ImageCaption", "ImageStyle", "ImageToolbar", "ImageResize", "Link", "List", "Paragraph", "Alignment", "Font", "PasteFromOffice", "SimpleUploadAdapter",
            "MediaEmbed", "RemoveFormat", "Table", "TableToolbar", "TableCaption", "TableProperties", "TableCellProperties", "Indent", "IndentBlock", "Highlight", "TodoList",
            "ListProperties", "SourceEditing", "GeneralHtmlSupport", "ImageInsert", "WordCount", "Mention", "Style", "HorizontalLine", "LinkImage"
        ]
    }
}
