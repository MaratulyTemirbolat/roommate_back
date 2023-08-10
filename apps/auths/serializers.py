# Python
from typing import (
    Tuple,
    Union,
)

# Rest Framework
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    DateTimeField,
)

# Project
from auths.models import CustomUser
from abstracts.serializers import AbstractDateTimeSerializer
from locations.serializers import DistrictForeignModelSerializer


class CustomUserBaseSerializer(AbstractDateTimeSerializer, ModelSerializer):
    """CustomUserBaseSerializer."""

    datetime_created: DateTimeField = \
        AbstractDateTimeSerializer.datetime_created
    is_deleted: SerializerMethodField = AbstractDateTimeSerializer.is_deleted

    class Meta:
        """Customization of the serializer."""

        model: CustomUser = CustomUser
        fields: Union[Tuple[str], str] = "__all__"


class CustomUserListSerializer(CustomUserBaseSerializer):
    """Serializer for listing the custom users."""

    districts: DistrictForeignModelSerializer = DistrictForeignModelSerializer(
        many=True
    )

    class Meta:
        """Customization for the serializer."""

        model: CustomUser = CustomUser
        fields: Union[Tuple[str], str] = (
            "id",
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
            "is_superuser",
            "last_login",
            "is_deleted",
            "datetime_created",
        )


class CustomUserDetailSerializer(CustomUserBaseSerializer):
    """CustomUserDetailSerializer."""

    districts: DistrictForeignModelSerializer = DistrictForeignModelSerializer(
        many=True
    )

    class Meta:
        """Customization for the serializer."""

        model: CustomUser = CustomUser
        fields: Union[Tuple[str], str] = (
            "id",
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
            "is_superuser",
            "last_login",
            "is_deleted",
            "datetime_created",
        )


class CreateCustomUserSerializer(CustomUserBaseSerializer):
    """CreateCustomUserSerializer."""

    class Meta:
        """Customization of the Serializer."""

        model: CustomUser = CustomUser
        fields: tuple[str] = (
            "email",
            "phone",
            "first_name",
            "telegram_username",
            "gender",
            "month_budjet",
            "password",
        )
