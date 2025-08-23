from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel
from apps.common.utils import GenerateUploadPath
from apps.common.validators import FileExtensionValidator, FileSizeValidator
from apps.media.managers import MediaLinkManager


class Media(TimeStampedModel):
    """A generic model to store media files in a central library."""

    class MediaTypeChoices(models.TextChoices):
        IMAGE = 'image', _("Image")
        VIDEO = 'video', _("Video")
        DOCUMENT = 'document', _("Document")

    file = models.FileField(
        upload_to=GenerateUploadPath(base_path='uploads/'),
        validators=[
            FileSizeValidator(max_size_mb=settings.MAX_FILES_UPLOAD_SIZE_MB),
            FileExtensionValidator(allowed_extensions=settings.ALLOWED_FILE_EXTENSIONS)
        ],
        verbose_name=_("Media File"),
        help_text=_(
            'This file represents a media item.<br />'
            'Allowed file types: {allowed_extensions}.<br />'
            'Maximum file size: {max_size_mb} MB.'
        ).format(
            allowed_extensions=', '.join(settings.ALLOWED_FILE_EXTENSIONS),
            max_size_mb=settings.MAX_FILES_UPLOAD_SIZE_MB
        )
    )
    media_type = models.CharField(
        max_length=10,
        choices=MediaTypeChoices.choices,
        default=MediaTypeChoices.IMAGE,
        verbose_name=_("Media Type"),
        help_text=_("Type of media file (image, video, document).")
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Alternative text (Optional)"),
        help_text=_("A descriptive text for the media, used for accessibility and SEO.")
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Caption"),
        help_text=_("A short caption for the media, displayed alongside it.")
    )

    class Meta:
        verbose_name = _("Media")
        verbose_name_plural = _("Media Library")
        ordering = ['-created_at']

    def __str__(self):
        return self.file.name if self.file else f"Media ID: {self.id}"


class MediaLink(models.Model):
    """A model to create links between media files and other models (e.g., Product, BlogPost)."""
    media = models.ForeignKey(
        "Media",
        on_delete=models.CASCADE,
        related_name="links",
        verbose_name=_("Media"),
        help_text=_("The media file to link to this object.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("The order in which this item appears in the list. Lower numbers appear first.")
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Is Featured")
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content Type"),
        help_text=_("The model to which this media link is attached.")
    )
    object_id = models.CharField(
        max_length=255,
        verbose_name=_("Object ID"),
        help_text=_("The primary key of the related object.")
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = MediaLinkManager()

    class Meta:
        verbose_name = _("Media Link")
        verbose_name_plural = _("Media Links")
        ordering = ['display_order']
