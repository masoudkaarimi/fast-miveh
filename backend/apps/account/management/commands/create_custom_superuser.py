# apps/account/management/commands/create_custom_superuser.py

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

# Todo: Bug fix
class Command(BaseCommand):
    help = 'Creates a superuser from environment variables if it does not already exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING("Superuser environment variables are not fully set."))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists."))
        else:
            self.stdout.write(f"Creating superuser: {username}")

            User.objects.create_superuser(username=username, email=email, password=password)

            self.stdout.write(self.style.SUCCESS("Superuser created successfully."))