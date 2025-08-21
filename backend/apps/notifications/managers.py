from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class NotificationQuerySet(models.QuerySet):
    """QuerySet for the Notification model."""

    def for_user(self, user):
        """Returns notifications for a specific user."""
        return self.filter(recipient=user)

    def unread(self):
        """Returns only unread notifications."""
        return self.filter(is_read=False)

    def read(self):
        """Returns only read notifications."""
        return self.filter(is_read=True)

    def mark_all_as_read(self):
        """Marks all notifications in the queryset as read."""
        return self.update(is_read=True, read_at=timezone.now())


class NotificationManager(models.Manager):
    """Manager for the Notification model."""

    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def unread_for_user(self, user):
        """A shortcut method to get all unread notifications for a user."""
        return self.get_queryset().for_user(user).unread()
