from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from account.models import User, OTPToken


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'date_joined',
                    'is_superuser', 'is_staff', 'name')
    search_fields = ('email', 'username')
    readonly_fields = ('id', 'date_joined', 'last_login',
                       'is_superuser', 'is_staff','is_email_verified')
    list_filter = ()
    filter_horizontal = ()
    fieldsets = ()


class OTPTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'expiry_time')

admin.site.register(User, UserAdmin)
admin.site.register(OTPToken, OTPTokenAdmin)
