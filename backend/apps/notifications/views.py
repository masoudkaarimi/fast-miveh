from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.notifications.services import NotificationService


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """A viewset for viewing and managing notifications for the authenticated user."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_read']

    def get_queryset(self):
        return Notification.objects.for_user(self.request.user)

    @action(detail=False, methods=['post'], url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        """Marks all of the user's unread notifications as read."""
        service = NotificationService(recipient=request.user)
        service.mark_all_as_read()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        """Marks a single notification as read."""
        notification = self.get_object()
        service = NotificationService(recipient=request.user)
        service.mark_as_read(notification)
        return Response(status=status.HTTP_204_NO_CONTENT)
