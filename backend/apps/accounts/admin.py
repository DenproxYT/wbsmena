from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    model = User

    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'phone_number', 'pvz_address', 'role', 'is_active', 'is_staff',
    )
    list_filter = ('role', 'is_intern', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'pvz_address')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'email')}),
        ('ПВЗ и роль', {
            'fields': ('phone_number', 'pvz_address', 'role', 'is_intern', 'must_change_credentials'),
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
                'first_name', 'last_name', 'email',
                'phone_number', 'pvz_address', 'role',
                'is_active', 'is_staff',
            ),
        }),
    )
