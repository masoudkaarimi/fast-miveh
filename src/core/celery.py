import os
from celery import Celery

# Set the default Django settings module without importing from settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

# Create the Celery app
app = Celery('core')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
