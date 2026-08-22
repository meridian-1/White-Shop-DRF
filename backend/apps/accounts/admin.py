from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = (
        "full_name",
        "street_address",
        "city",
        "postal_code",
        "country",
        "is_default",
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ["-created_at"]
    list_display = ("email", "is_email_verified", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_email_verified")
    search_fields = ("email", "phone_number")
    readonly_fields = ("created_at", "updated_at")
    inlines = [AddressInline]

    fieldsets = (
        (None, {"fields": ("password",)}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone_number")}),
        (
            _("Status"),
            {"fields": ("is_email_verified", "is_active", "is_staff", "is_superuser")},
        ),
        (_("Permissions"), {"fields": ("groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "city", "country", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("full_name", "user__email", "city", "postal_code")
