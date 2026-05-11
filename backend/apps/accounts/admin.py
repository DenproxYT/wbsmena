from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "phone_number", "pvz_address", "role", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Доп. поля PVZ", {"fields": ("phone_number", "pvz_address", "is_intern", "role")} ),
    )
