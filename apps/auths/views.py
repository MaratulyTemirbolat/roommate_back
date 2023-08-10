# Python
from typing import (
    Tuple,
    List,
    Dict,
    Any,
)

# Rest Framework
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRF_Request
from rest_framework.response import Response as DRF_Response
from rest_framework.permissions import AllowAny

# Django
from django.db.models import (
    QuerySet,
    Manager,
    Max,    
)

# Project
from auths.models import CustomUser
from auths.serializers import (
    CustomUserBaseSerializer,
    CustomUserListSerializer,
)
from locations.models import District
from abstracts.handlers import DRFResponseHandler
from abstracts.mixins import ModelInstanceMixin
from abstracts.paginators import AbstractPageNumberPaginator
from abstracts.tools import get_filled_params_dict


class CustomUserViewSet(ModelInstanceMixin, DRFResponseHandler, ViewSet):
    """Serializer for CustomUser model."""

    queryset: Manager = CustomUser.objects
    permission_classes: Tuple[Any] = (AllowAny,)
    serializer_class: CustomUserBaseSerializer = CustomUserBaseSerializer
    __user_list_params: Tuple[str] = ("gender",)
    __location_list_params: Tuple[str] = ("city",)

    def get_queryset(self, is_deleted: bool = False) -> QuerySet[CustomUser]:
        """Get deleted/non-deleted queryset with CustUser instances."""
        return self.queryset.get_deleted().filter(is_active=True) \
            if is_deleted else self.queryset.get_not_deleted().filter(
                is_active=True
            )

    def __get_district_ids(
        self,
        **query_params: Dict[str, Any]
    ) -> Tuple[int]:
        """Get queryset for district through the query_params."""
        location_dict_params: Dict[str, Any] = get_filled_params_dict(
            req_params=self.__location_list_params,
            **query_params
        )
        req_districts: List[str] = query_params.get(
            "districts",
            [""]
        )[0].split(",")
        district_ids: Tuple[int] = tuple((
            District.objects.filter(
                **location_dict_params,
                id__in=req_districts
            ) if req_districts[0] else District.objects.filter(
                **location_dict_params
                )
        ).values_list("id", flat=True))
        return district_ids

    def get_params_queryset(
        self,
        **query_params: Dict[str, Any]
    ) -> QuerySet[CustomUser]:
        """Get queryset by filtering through the query_params."""
        user_dict_params: Dict[str, Any] = get_filled_params_dict(
            req_params=self.__user_list_params,
            **query_params
        )

        final_budjet: int = int(query_params.get(
            "month_budjet",
            [CustomUser.objects.get_not_deleted().filter(
                is_active=True
            ).aggregate(Max('month_budjet')).get("month_budjet__max", 0)]
        )[0]) if not query_params.get("upper_budjet", False) \
            else int(
                query_params.get(
                    "month_budjet",
                    [CustomUser.objects.get_not_deleted().filter(
                        is_active=True
                    ).aggregate(Max('month_budjet')).get(
                        "month_budjet__max",
                        0
                    ) * 1.2]
                )[0]
            )

        district_ids: Tuple[int] = self.__get_district_ids(**query_params)
        user_queryset: QuerySet[CustomUser] = CustomUser.objects.filter(
            **user_dict_params,
            month_budjet__lte=final_budjet,
            districts__in=district_ids
        ).prefetch_related(
            "districts",
            "districts__city",
        )
        return user_queryset

    def list(
        self,
        request: DRF_Request,
        *args: Tuple[Any],
        **kwargs: Dict[Any, Any],
    ) -> DRF_Response:
        """Handle GET-request to provide list of users."""
        response: DRF_Response = self.get_drf_response(
            request=request,
            data=self.get_params_queryset(**request.query_params),
            serializer_class=CustomUserListSerializer,
            many=True,
            paginator=AbstractPageNumberPaginator(),
        )
        return response
