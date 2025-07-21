from django.conf import settings

from apps.media.models import Media, MediaLink
from apps.media.exceptions import InvalidMediaTypeError


class MediaService:
    """
    A service class to handle business logic for creating and managing media.
    """

    def __init__(self, content_object):
        """
        Initializes the service with the parent object to which media will be attached.

        Args:
            content_object: The instance of the model (e.g., Product, BlogPost).
        """
        self.content_object = content_object

    @staticmethod
    def _get_media_type(filename: str) -> str:
        """
        Determines the media type based on the file extension using settings.
        """
        extension = filename.lower().split('.')[-1]

        if extension in settings.ALLOWED_IMAGE_EXTENSIONS:
            return Media.MediaTypeChoices.IMAGE
        elif extension in settings.ALLOWED_VIDEO_EXTENSIONS:
            return Media.MediaTypeChoices.VIDEO
        elif extension in settings.ALLOWED_DOCUMENT_EXTENSIONS:
            return Media.MediaTypeChoices.DOCUMENT

        raise InvalidMediaTypeError(f"Unsupported file type: '.{extension}'")

    def create(self, *, file_obj, **kwargs) -> MediaLink:
        """
        Creates a Media instance and links it to the content_object.

        Args:
            file_obj: The uploaded file object.
            **kwargs: Optional data for MediaLink (is_featured, display_order)
                      and Media (alt_text, caption).

        Returns:
            The created MediaLink instance.
        """
        media_type = self._get_media_type(file_obj.name)

        media = Media.objects.create(
            file=file_obj,
            media_type=media_type,
            alt_text=kwargs.get('alt_text', ''),
            caption=kwargs.get('caption', ''),
            content_object=self.content_object  # Associate with the parent
        )

        media_link = MediaLink.objects.create(
            media=media,
            content_object=self.content_object,
            is_featured=kwargs.get('is_featured', False),
            display_order=kwargs.get('display_order', 0)
        )

        return media_link
