from core.settings.base import env

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

MAX_FILES_UPLOAD_SIZE_MB = 50
ALLOWED_FILE_EXTENSIONS = ["pdf", "doc", "docx", "xls", "xlsx", "txt", "zip", "rar"]

# --- CKEditor 5 Configuration ---
from core.settings.ckeditor_configs import *

# --- Phone Number Fields Configuration ---
# PHONENUMBER_DEFAULT_REGION = "IR"
