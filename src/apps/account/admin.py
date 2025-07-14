from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from apps.account.models import User, Profile, OTP


class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = _('Profile')
    fk_name = 'user'
    fields = ('avatar', 'gender', 'birthdate', 'national_code')


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_select_related = ('profile',)
    list_display = (
        'phone_number',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'is_phone_number_verified'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('phone_number', 'email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal Info'), {'fields': ('username', 'first_name', 'last_name', 'email')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Verification Status'), {'fields': ('is_phone_number_verified', 'is_email_verified')}),
        (_('Important dates'), {'fields': ('last_login_ip', 'last_login_at', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('last_login_at','last_login_ip', 'created_at', 'updated_at')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipient',
        'type',
        'status',
        'code',
        'created_at',
        'expires_at',
        'attempts'
    )
    list_filter = ('status', 'type', 'created_at')
    search_fields = ('recipient', 'user__phone_number', 'user__email')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        """Hook to make all fields read-only."""
        # This makes all fields read-only, preventing any edits from the admin.
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        """Prevent manual creation of OTPs from the admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of OTPs from the admin for audit purposes."""
        return False
