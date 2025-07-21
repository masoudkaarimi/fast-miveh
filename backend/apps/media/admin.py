from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html

from apps.media.models import Media, MediaLink


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    """Admin configuration for the Media model."""
    list_display = ('id', 'display_thumbnail', 'file', 'media_type', 'linked_object', 'created_at')
    list_filter = ('media_type',)
    search_fields = ('file', 'alt_text', 'caption')
    readonly_fields = ('linked_object',)

    def display_thumbnail(self, obj):
        """Displays a small thumbnail in the admin list view if the media is an image."""
        if obj.media_type == Media.MediaTypeChoices.IMAGE and obj.file:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.file.url)
        return "N/A"

    display_thumbnail.short_description = 'Thumbnail'

    def linked_object(self, obj):
        """Shows a link to the related object's admin page."""
        if obj.content_object:
            return format_html('<a href="{}">{}</a>', obj.content_object.get_absolute_url(), obj.content_object)
        return "Not linked"

    linked_object.short_description = 'Attached to'


class MediaLinkInline(GenericTabularInline):
    """
    An inline for managing media links on parent object admin pages (e.g., ProductAdmin).
    This allows adding/editing media directly from the product page.
    """
    model = MediaLink
    extra = 1
    fields = ('media', 'display_order', 'is_featured')
    raw_id_fields = ('media',)
    verbose_name = "Media Link"
    verbose_name_plural = "Media Links"
