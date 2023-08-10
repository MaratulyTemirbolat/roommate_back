# Python
from typing import Any

# Rest Framework
from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRF_Request


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
