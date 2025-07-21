from django.utils.translation import gettext_lazy as _


class MediaException(Exception):
    """Base exception for the media app."""
    default_message = _("A media-related error occurred.")

    def __init__(self, message=None):
        if message is None:
            message = self.default_message
        super().__init__(message)


class MediaUploadError(MediaException):
    """Raised when a media file upload fails for a general reason."""
    default_message = _("The file could not be uploaded.")


class InvalidMediaTypeError(MediaException):
    """Raised when the file type is not supported or cannot be determined."""
    default_message = _("The provided file type is not supported.")


class MediaProcessingError(MediaException):
    """Raised when an error occurs during media processing (e.g., thumbnail generation)."""
    default_message = _("An error occurred while processing the media file.")
