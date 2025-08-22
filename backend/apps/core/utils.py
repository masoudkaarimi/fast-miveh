from django.conf import settings


def get_provider_choices(provider_type):
    """Dynamically generates a list of choices for the admin panel based on providers defined in settings.py."""
    choices = [
        (key, f"{key.split('_')[0].capitalize()} ({data['CHANNEL_CLASS'].split('.')[-1]})")
        for key, data in settings.NOTIFICATION_PROVIDERS.items()
        if key.endswith(f'_{provider_type}')
    ]
    return [('', '---------')] + choices
