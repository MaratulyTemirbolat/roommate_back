# Python
from typing import (
    Tuple,
    Union,
    Dict,
    Any,
)

# Rest Framework
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRF_Request
from rest_framework.response import Response as DRF_Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

# Django
from django.db.models import (
    QuerySet,
    Manager,
)

# Project
from auths.permissions import (
    IsActiveAccount,
    IsNonDeletedUser,
)
from locations.serializers import (
    CityForeignModelSerializer,
    DistrictForeignModelSerializer,
)
from locations.models import (
    District,
    City,
)
from abstracts.handlers import DRFResponseHandler
from abstracts.mixins import ModelInstanceMixin


class CityViewSet(ModelInstanceMixin, DRFResponseHandler, ViewSet):
    """ViewSet for City model."""

    queryset: Manager = City.objects
    permission_classes: Tuple[Any] = (
        IsAuthenticated,
        IsNonDeletedUser,
        IsActiveAccount,
    )
    serializer_class: CityForeignModelSerializer = CityForeignModelSerializer

    def get_queryset(
        self,
        is_deleted: bool = False
    ) -> QuerySet[City]:
        """Get queryset with the data of City."""
        return self.queryset.get_deleted() \
            if is_deleted \
            else self.queryset.get_not_deleted()

    def list(
        self,
        request: DRF_Request,
        *args: Tuple[Any],
        **kwargs: Dict[Any, Any]
    ) -> DRF_Response:
        return self.get_drf_response(
            request=request,
            data=self.get_queryset(),
            serializer_class=CityForeignModelSerializer,
            many=True
        )

    @action(
        methods=["GET"],
        url_path="districts",
        detail=True
    )
    def get_districts(
        self,
        request: DRF_Request,
        pk: str,
        *args: Tuple[str],
        **kwargs: Dict[Any, Any]
    ) -> DRF_Response:
        city_obj: Union[City, DRF_Response] = None
        is_present: bool = False
        city_obj, is_present = self.get_obj_or_response(
            request=request,
            pk=pk,
            class_name=City,
            queryset=self.get_queryset()
        )
        if not is_present:
            return city_obj
        districts: QuerySet[District] = city_obj.districts.get_not_deleted()
        return self.get_drf_response(
            request=request,
            data=districts.select_related("city"),
            serializer_class=DistrictForeignModelSerializer,
            many=True
        )
