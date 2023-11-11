from django.contrib import admin
from accounts.models import Permissions, User
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Register your models here.
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "is_active",
        "created_at",
    )
    list_filter = ["is_active"]
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "password",
                ]
            },
        ),
        ("Personal Info", {"fields": ["email"]}),
        (
            "Permissions",
            {
                "fields": [
                    # "perms",
                    "is_admin",
                    "is_superadmin",
                    "is_active",
                    "permissions",
                ]
            },
        ),
        (
            "Info",
            {
                "fields": (
                    "created_at",
                    "edited_at",
                )
            },
        ),
    )
    readonly_fields = ["created_at", "edited_at"]
    filter_horizontal = []
    ordering = ["email"]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]


admin.site.register(User, UserAdmin)
admin.site.register(Permissions)
admin.site.unregister(Group)
