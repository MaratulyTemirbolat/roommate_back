# Python
from typing import Any

# Rest Framework
from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRF_Request

# Project
from auths.models import CustomUser


class IsNonDeletedUser(BasePermission):
    """IsNonDeletedUser."""

    message: str = "Вы не можете запрашивать данные, пока ваш аккаунт удалён."

    def has_permission(self, request: DRF_Request, view: Any) -> bool:
        """Handle request permissions."""
        return bool(
            request.user and
            request.user.is_authenticated and
            not request.user.datetime_deleted
        )


class IsOwnerUser(BasePermission):
    """Class for checking is the user owner of himself/herself."""

    message: str = "Вы не являетесь самим собой."

    def has_object_permission(
        self,
        request: DRF_Request,
        view: Any,
        obj: CustomUser
    ) -> bool:
        """Check whether the user is owner of himself/herself."""
        return False if obj.id != request.user.id else True
