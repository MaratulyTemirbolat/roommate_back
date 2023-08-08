# Python
from typing import (
    Optional,
    Tuple,
    Any,
)

# Django
from django.contrib.admin import (
    register,
    ModelAdmin
)
from django.http.request import HttpRequest

# Project
from locations.models import (
    City,
    District,
)
from abstracts.admin import AbstractAdminIsDeleted
from abstracts.models import AbstractDateTime
from abstracts.filters import DeletedStateFilter


@register(City)
class CityAdmin(AbstractAdminIsDeleted, ModelAdmin):
    list_display: Tuple[str] = (
        "id",
        "name",
        "get_is_deleted_obj"
    )
    list_display_links: Tuple[str] = (
        "id",
        "name",
    )
    readonly_fields: Tuple[str] = (
        "get_is_deleted_obj",
        "datetime_created",
        "datetime_updated",
        "datetime_deleted",
    )
    search_fields: Tuple[str] = (
        "name",
    )
    fields: Tuple[str] = (
        "name",
        "datetime_created",
        "datetime_updated",
        "datetime_deleted",
        "get_is_deleted_obj",
    )
    list_filter: Tuple[Any] = (
        DeletedStateFilter,
    )
    save_on_top: bool = True
    save_as_continue: bool = True

    def get_is_deleted_obj(
        self,
        obj: Optional[AbstractDateTime] = None,
        obj_name: str = "Город"
    ) -> str:
        return super().get_is_deleted_obj(obj, obj_name)
    get_is_deleted_obj.short_description = "Состояние объекта"


@register(District)
class DistrictAdmin(AbstractAdminIsDeleted, ModelAdmin):
    list_display: Tuple[str] = (
        "id",
        "name",
        "city",
        "get_is_deleted_obj"
    )
    list_display_links: Tuple[str] = (
        "id",
        "name",
    )
    readonly_fields: Tuple[str] = (
        "get_is_deleted_obj",
        "datetime_created",
        "datetime_updated",
        "datetime_deleted",
    )
    search_fields: Tuple[str] = (
        "name",
    )
    fields: Tuple[str] = (
        "name",
        "city",
        "datetime_created",
        "datetime_updated",
        "datetime_deleted",
        "get_is_deleted_obj",
    )
    list_filter: Tuple[Any] = (
        "city",
        DeletedStateFilter,
    )
    list_select_related: Tuple[Any] = (
        "city",
    )
    save_on_top: bool = True
    save_as_continue: bool = True

    def get_is_deleted_obj(
        self,
        obj: Optional[AbstractDateTime] = None,
        obj_name: str = "Район"
    ) -> str:
        return super().get_is_deleted_obj(obj, obj_name)
    get_is_deleted_obj.short_description = "Состояние объекта"

    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: Optional[District] = None
    ) -> Tuple[Any]:
        if obj:
            return self.readonly_fields + (
                "city",
            )
        return self.readonly_fields
