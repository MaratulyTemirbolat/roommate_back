# Python
from typing import (
    Sequence,
    Tuple,
    Union,
    Any,
    Optional,
)

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http.request import HttpRequest
from django.utils.safestring import mark_safe

# Project
from auths.models import CustomUser
from abstracts.filters import DeletedStateFilter
from abstracts.admin import AbstractAdminIsDeleted


@admin.register(CustomUser)
class CustomUserAdmin(AbstractAdminIsDeleted, UserAdmin):
    """CustomUser setting on Django admin site."""

    ordering: tuple[str] = ("-datetime_updated", "-id")
    list_display: tuple[str] = (
        "id",
        "email",
        "phone",
        "first_name",
        "telegram_username",
        "gender",
        "month_budjet",
        "is_active",
        "is_staff",
        "is_superuser",
        "get_photo",
        "get_is_deleted",
    )
    list_display_links: Sequence[str] = (
        "id",
        "email",
        "phone",
    )
    readonly_fields: tuple[str] = (
        "get_photo",
        "get_is_deleted",
        "datetime_deleted",
        "datetime_created",
        "datetime_updated",
    )
    search_fields: Sequence[str] = (
        "id",
        "email",
        "first_name",
        "phone",
        "telegram_username",
    )
    list_filter: tuple[str, Any] = (
        "is_active",
        "is_staff",
        "is_superuser",
        "gender",
        DeletedStateFilter,
    )
    filter_horizontal: tuple[str] = ("districts",)
    fieldsets: tuple[tuple[Union[str, dict[str, Any]]]] = (
        (
            "Личная информация",
            {
                "fields": (
                    "first_name",
                    ("email", "telegram_username", "phone"),
                    "telegram_user_id",
                    "gender",
                    "photo",
                    "get_photo",
                )
            }
        ),
        (
            "Предпочтения по жилью",
            {
                "fields": (
                    "month_budjet",
                    "districts",
                    "comment",
                )
            }
        ),
        (
            "Разрешения (Доступы)",
            {
                "fields": (
                    ("is_superuser", "is_staff",),
                    "is_active_account",
                    "is_active",
                    "user_permissions",
                )
            }
        ),
        (
            "Данные времени",
            {
                "fields": (
                    "datetime_created",
                    "datetime_updated",
                    "datetime_deleted",
                    "get_is_deleted",
                )
            }
        )
    )
    add_fieldsets: tuple[tuple] = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone",
                    "first_name",
                    "telegram_username",
                    "gender",
                    "is_active",
                    "month_budjet",
                    "comment",
                    "photo",
                    "districts",
                    "is_staff",
                    "is_superuser",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    save_on_top: bool = True
    list_per_page: int = 20

    def get_is_deleted(self, obj: Optional[CustomUser] = None) -> str:
        """Get is deleted state of object."""
        return self.get_is_deleted_obj(obj=obj, obj_name="Пользователь")
    get_is_deleted.short_description = "Состояние"

    def get_photo(
        self,
        obj: Optional[CustomUser],
        width: int = 100
    ) -> str:
        """Get img photo."""
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="{width}">')
    get_photo.short_description = "Фото"
    get_photo.empty_value_display = "No photo uploaded"

    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: Optional[CustomUser] = None
    ) -> Tuple[str]:
        """Get readonly fields as obj is created."""
        if obj:
            return self.readonly_fields + (
                "email",
                "phone",
                "first_name",
                "gender",
                "is_active",
                "is_staff",
                "photo",
                "is_superuser",
                "telegram_user_id",
                "telegram_username",
            )
        return self.readonly_fields
