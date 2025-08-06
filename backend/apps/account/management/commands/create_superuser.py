import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a superuser from environment variables if it does not already exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        phone_number = os.environ.get('DJANGO_SUPERUSER_PHONE_NUMBER')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, phone_number, email, password]):
            self.stdout.write(self.style.WARNING("Superuser environment variables are not fully set."))
            return

        if User.objects.filter(phone_number=phone_number).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser with phone number '{phone_number}' already exists."))
        else:
            self.stdout.write(f"Creating superuser: {username} ({phone_number})")
            User.objects.create_superuser(username=username, phone_number=phone_number, email=email, password=password)
            self.stdout.write(self.style.SUCCESS("Superuser created successfully."))
