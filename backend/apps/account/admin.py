# apps/account/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Address, Wishlist, OTP


# This allows the Profile to be edited directly within the User admin page
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Combines default User admin with custom fields and the Profile inline
    list_display = ('username', 'phone_number', 'email', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-created_at',)
    inlines = (ProfileInline,)

    # Adding custom fields to the admin view
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('phone_number', 'is_phone_number_verified', 'is_email_verified')}),
        ('Login Info', {'fields': ('last_login_at', 'last_login_ip')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'email')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    # Optimized for performance and usability
    list_display = ('id', 'user', 'title', 'city', 'country', 'is_default', 'is_snapshot')
    list_filter = ('is_default', 'is_snapshot', 'country', 'city')
    search_fields = ('user__username', 'city', 'state', 'zip_code', 'address_line_1')
    # Use raw_id_fields for better performance on ForeignKey fields with many related objects
    raw_id_fields = ('user',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    # Provides a better UI for the ManyToMany relationship
    list_display = ('id', 'user',)
    search_fields = ('user__username',)
    # Use filter_horizontal for a user-friendly way to manage ManyToMany fields
    filter_horizontal = ('products',)
    raw_id_fields = ('user',)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    # A secure, read-only view for debugging OTP records
    list_display = ('recipient', 'user', 'type', 'status', 'created_at', 'expires_at')
    list_filter = ('status', 'type')
    search_fields = ('recipient', 'user__username')
    # Make all fields read-only to prevent accidental changes
    readonly_fields = [f.name for f in OTP._meta.fields]

    def has_add_permission(self, request):
        # Disables the "Add" button
        return False

    def has_change_permission(self, request, obj=None):
        # Disables the "Save" and "Save and continue editing" buttons
        return False

    def has_delete_permission(self, request, obj=None):
        # Disables the "Delete" action
        return False
