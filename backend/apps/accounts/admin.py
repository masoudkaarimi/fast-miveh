from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import OTP, Address, Profile, User, Wishlist


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'phone_number', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_phone_number_verified', 'is_email_verified', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-created_at',)
    inlines = (ProfileInline,)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'is_phone_number_verified', 'email', 'is_email_verified')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login_at', 'created_at')}),
        (_('Login Info'), {'fields': ('last_login_ip',)}),
    )

    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'password1', 'password2')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'is_email_verified', 'phone_number', 'is_phone_number_verified')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    readonly_fields = ('last_login_at', 'last_login_ip', 'created_at')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'country', 'city', 'is_default', 'is_snapshot')
    list_filter = ('is_default', 'is_snapshot', 'city', 'country')
    search_fields = ('user__username', 'city', 'country', 'state', 'zip_code', 'address_line_1', 'address_line_2')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username',)
    filter_horizontal = ('variants',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'user', 'otp_type', 'status', 'created_at', 'expires_at')
    list_filter = ('status', 'otp_type', 'created_at', 'expires_at')
    search_fields = ('recipient', 'user__username')
    readonly_fields = [f.name for f in OTP._meta.fields]

    def has_add_permission(self, request):
        """Disables the "Add" button"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disables the "Save" and "Save and continue editing" buttons"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disables the "Delete" action"""
        return False
