from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import Throttled
from rest_framework.throttling import ScopedRateThrottle as BaseScopedRateThrottle


class APIThrottled(Throttled):
    """
    Custom Throttled exception with a localized and more informative message.
    Inherits from DRF's base Throttled exception.
    """
    default_detail = _("Too many requests.")

    def __init__(self, wait=None, detail=None, code=None):
        if detail is None and wait is not None:
            detail = _("Request was throttled. Expected available in %(seconds)d seconds.") % {'seconds': int(wait)}

        super().__init__(detail=detail, wait=wait, code=code)


class ScopedRateThrottle(BaseScopedRateThrottle):
    """A custom scoped rate throttle that raises our custom APIThrottled exception."""

    def throttle_failure(self):
        """Overrides the default behavior to raise our custom exception class."""
        wait = self.wait()
        raise APIThrottled(wait=wait)
