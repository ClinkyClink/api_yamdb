from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Права', {'fields': (
            'role',
            'is_active',
            'is_staff',
            'is_superuser')}),
        ('Персональные данные',
         {'fields': ('first_name', 'last_name', 'bio')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
