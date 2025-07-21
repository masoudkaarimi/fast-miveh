from django.db import models
from django.contrib.contenttypes.models import ContentType


class MediaLinkManager(models.Manager):
    """Custom manager for the MediaLink model."""

    def get_for_object(self, obj):
        """
        Returns a queryset of MediaLink instances for a given object.
        Example: MediaLink.objects.get_for_object(my_product)
        """
        content_type = ContentType.objects.get_for_model(obj)
        return self.get_queryset().filter(content_type=content_type, object_id=obj.pk)
