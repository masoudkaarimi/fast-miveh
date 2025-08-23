from django.conf import settings

from apps.media.exceptions import InvalidMediaTypeError
from apps.media.models import Media, MediaLink


class MediaService:
    """Service to manage media files and their associations with content objects."""

    def __init__(self, content_object):
        self.content_object = content_object

    @staticmethod
    def _get_media_type(filename):
        """Determines the media type based on the file extension using settings."""
        extension = filename.lower().split('.')[-1]

        if extension in settings.ALLOWED_IMAGE_EXTENSIONS:
            return Media.MediaTypeChoices.IMAGE
        elif extension in settings.ALLOWED_VIDEO_EXTENSIONS:
            return Media.MediaTypeChoices.VIDEO
        elif extension in settings.ALLOWED_DOCUMENT_EXTENSIONS:
            return Media.MediaTypeChoices.DOCUMENT

        raise InvalidMediaTypeError(f"Unsupported file type: '.{extension}'")

    @staticmethod
    def get_media_links_for(obj):
        """Retrieves all MediaLink objects for a given content object."""
        if not hasattr(obj, 'media_links'):
            return MediaLink.objects.none()

        return obj.media_links.order_by('display_order').select_related('media')

    def create(self, *, file_obj, **kwargs):
        """Creates a Media instance and links it to the content_object."""
        media_type = self._get_media_type(file_obj.name)

        # The Media object is now created independently.
        media = Media.objects.create(
            file=file_obj,
            media_type=media_type,
            alt_text=kwargs.get('alt_text', ''),
            caption=kwargs.get('caption', '')
        )

        # The MediaLink is then created to connect the new Media to the content_object.
        media_link = MediaLink.objects.create(
            media=media,
            content_object=self.content_object,
            is_featured=kwargs.get('is_featured', False),
            display_order=kwargs.get('display_order', 0)
        )

        return media_link
