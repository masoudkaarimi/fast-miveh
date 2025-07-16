from core.settings.base import env

from celery.schedules import crontab

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
