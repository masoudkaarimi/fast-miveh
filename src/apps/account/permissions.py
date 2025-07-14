from django.utils.translation import gettext_lazy as _

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    custom permission to only allow owners of an object to edit it.
    assumes the model instance has a `user` attribute.
    """
    message = _("You do not have permission to perform this action on another user's profile.")

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the profile.
        return obj.user == request.user
