from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'category', 'is_read', 'created_at')
    list_filter = ('category', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'recipient__email', 'recipient__phone_number', 'title', 'body')
    readonly_fields = [field.name for field in Notification._meta.fields]
    raw_id_fields = ('recipient',)
    actions = ('mark_as_read_action', 'mark_as_unread_action')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description=_('Mark selected notifications as read'))
    def mark_as_read_action(self, request, queryset):
        """Admin action to mark notifications as read in bulk."""
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notifications were marked as read.")

    @admin.action(description=_('Mark selected notifications as unread'))
    def mark_as_unread_action(self, request, queryset):
        """Admin action to mark notifications as unread in bulk."""
        queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{queryset.count()} notifications were marked as unread.")
