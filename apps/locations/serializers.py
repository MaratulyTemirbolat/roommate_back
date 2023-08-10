# Python
from typing import (
    Union,
    Tuple,
)

# Rest Framework
from rest_framework.serializers import (
    ModelSerializer,
    DateTimeField,
    SerializerMethodField,
)

# Project
from locations.models import (
    District,
    City,
)
from abstracts.serializers import AbstractDateTimeSerializer


class CityForeignModelSerializer(
    AbstractDateTimeSerializer,
    ModelSerializer
):
    """CityForeignModelSerializer."""

    is_deleted: SerializerMethodField = AbstractDateTimeSerializer.is_deleted
    datetime_created: DateTimeField = \
        AbstractDateTimeSerializer.datetime_created

    class Meta:
        """Customization for the serializer."""

        model: City = City
        fields: Union[Tuple[str], str] = (
            "id",
            "name",
            "datetime_created",
            "is_deleted",
        )


class DistrictForeignModelSerializer(
    AbstractDateTimeSerializer,
    ModelSerializer
):
    """DistrictForeignModelSerializer."""

    is_deleted: SerializerMethodField = AbstractDateTimeSerializer.is_deleted
    datetime_created: DateTimeField = \
        AbstractDateTimeSerializer.datetime_created
    city: CityForeignModelSerializer = CityForeignModelSerializer()

    class Meta:
        """Customization for the serializer."""

        model: District = District
        fields: Union[Tuple[str], str] = (
            "id",
            "name",
            "city",
            "is_deleted",
            "datetime_created",
        )
