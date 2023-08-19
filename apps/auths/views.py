# Python
from typing import (
    Tuple,
    Optional,
    Union,
    List,
    Dict,
    Any,
)

# Third party
from rest_framework_simplejwt.tokens import RefreshToken

# Rest Framework
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRF_Request
from rest_framework.response import Response as DRF_Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.decorators import action
from rest_framework.status import (
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)

# Django
from django.db.models import (
    QuerySet,
    Manager,
    Max,
)
from django.contrib.auth import login

# Project
from auths.models import CustomUser
from auths.serializers import (
    CustomUserBaseSerializer,
    CustomUserListSerializer,
    CustomUserDetailSerializer,
    CreateCustomUserSerializer,
)
from auths.permissions import (
    IsNonDeletedUser,
    IsOwnerUser,
    IsActiveAccount,
)
from auths.utils import get_valid_request_data
from locations.models import District
from abstracts.handlers import DRFResponseHandler
from abstracts.mixins import ModelInstanceMixin
from abstracts.paginators import AbstractPageNumberPaginator
from abstracts.tools import get_filled_params_dict


class CustomUserViewSet(ModelInstanceMixin, DRFResponseHandler, ViewSet):
    """ViewSet for CustomUser model."""

    queryset: Manager = CustomUser.objects
    permission_classes: Tuple[Any] = (IsNonDeletedUser, IsActiveAccount,)
    serializer_class: CustomUserBaseSerializer = CustomUserBaseSerializer
    __user_list_params: Tuple[str] = ("gender",)
    __location_list_params: Tuple[str] = ("city",)

    def get_queryset(
        self,
        is_deleted: bool = False,
        is_active_account: bool = True
    ) -> QuerySet[CustomUser]:
        """Get deleted/non-deleted queryset with CustUser instances."""
        return self.queryset.get_deleted().filter(
            is_active_account=is_active_account
        ) if is_deleted \
            else self.queryset.get_not_deleted().filter(
                is_active_account=is_active_account
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
            ""
        ).split(",")
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
        reqest: DRF_Request,
        **query_params: Dict[str, Any]
    ) -> QuerySet[CustomUser]:
        """Get queryset by filtering through the query_params."""
        user_dict_params: Dict[str, Any] = get_filled_params_dict(
            req_params=self.__user_list_params,
            **query_params
        )

        final_budjet: int = int(query_params.get(
            "month_budjet",
            CustomUser.objects.get_not_deleted().filter(
                is_active=True
            ).aggregate(Max('month_budjet')).get("month_budjet__max", 0)
        )) if not query_params.get("upper_budjet", False) \
            else int(
                query_params.get(
                    "month_budjet",
                    CustomUser.objects.get_not_deleted().filter(
                        is_active=True
                    ).aggregate(Max('month_budjet')).get(
                        "month_budjet__max",
                        0
                    ) * 1.2
                )
            )
        district_ids: Tuple[int] = self.__get_district_ids(**query_params)
        user_queryset: QuerySet[CustomUser] = CustomUser.objects.filter(
            **user_dict_params,
            month_budjet__lte=final_budjet,
            districts__in=district_ids,
            is_active_account=True,
        ).exclude(
            id=reqest.user.id
        ).prefetch_related(
            "districts",
            "districts__city",
        ).order_by("-datetime_created").distinct()
        if user_queryset.count() == 0:
            user_queryset = CustomUser.objects.filter(
                **user_dict_params,
                month_budjet__lte=int(final_budjet*1.2),
                districts__in=district_ids,
                is_active_account=True
            ).exclude(
                id=reqest.user.id
            ).prefetch_related(
                "districts",
                "districts__city",
            ).order_by("-datetime_created").distinct()
        return user_queryset

    def list(
        self,
        request: DRF_Request,
        *args: Tuple[Any],
        **kwargs: Dict[Any, Any],
    ) -> DRF_Response:
        """Handle GET-request to provide list of users."""
        validated_params: Dict[str, Any] = get_valid_request_data(
            request_data=request.query_params,
            single_keys=(
                "gender", "month_budjet",
                "city", "districts",
            )
        )
        response: DRF_Response = self.get_drf_response(
            request=request,
            data=self.get_params_queryset(
                reqest=request,
                # **request.query_params
                **validated_params
            ),
            serializer_class=CustomUserListSerializer,
            many=True,
            paginator=AbstractPageNumberPaginator(),
        )
        return response

    def retrieve(
        self,
        request: DRF_Request,
        pk: str,
        *args: Tuple[Any],
        **kwargs: Dict[str, Any]
    ) -> DRF_Response:
        """Handle GET-request with provided ID to get user."""
        obj: Optional[CustomUser] = self.get_queryset_instance(
            class_name=CustomUser,
            queryset=self.get_queryset().prefetch_related(
                "districts",
                "districts__city",
            ),
            pk=pk
        )
        if not obj:
            return DRF_Response(
                data={
                    "response": f"Пользователь с ID: {pk} не найден или удалён"
                },
                status=HTTP_404_NOT_FOUND
            )
        return self.get_drf_response(
            request=request,
            data=obj,
            serializer_class=CustomUserDetailSerializer
        )

    @action(
        methods=["POST"],
        url_path="add_districts",
        detail=False,
        permission_classes=(IsAuthenticated, IsNonDeletedUser,)
    )
    def add_districts(
        self,
        request: DRF_Request,
        *args: Tuple[str],
        **kwargs: Dict[str, Any]
    ) -> DRF_Response:
        """Handle POST-request for adding districts to the user."""
        districts: List[str] = request.data.get(
            "districts",
            ""
        ).split(",")
        if len(districts) == 0:
            return DRF_Response(
                data={
                    "response": "Извините, но вы не предоставили "
                    "список районов"
                },
                status=HTTP_400_BAD_REQUEST
            )
        request.user.districts.clear()
        request.user.districts.add(
            *list(District.objects.filter(id__in=districts))
        )
        return DRF_Response(
            data={
                "response": "Выбранные вами районы успешно добавлены",
            },
            status=HTTP_200_OK
        )

    @action(
        methods=["POST"],
        url_path="register_user",
        detail=False,
        permission_classes=(AllowAny,)
    )
    def register_user(
        self,
        request: DRF_Request,
        *args: Tuple[str],
        **kwargs: Dict[str, Any]
    ) -> DRF_Response:
        """Handle POST-request to register new user with provided data."""
        is_superuser: bool = bool(
            request.data.get("is_superuser", False)
        )
        is_staff: bool = True if is_superuser else False
        if is_superuser and not request.user.is_superuser:
            return DRF_Response(
                data={
                    "response": [
                        {
                            "permission": "Вы не админ, "
                            "чтобы создать супер пользователя"
                        }
                    ]
                },
                status=HTTP_403_FORBIDDEN
            )
        resulted_data: Dict[str, Any] = get_valid_request_data(
            request_data=request.data.copy(),
            single_keys=CustomUser.SINGLE_FIELDS
        )
        photo_url: Optional[str] = request.data.get(
            "photo_url",
            None
        )
        serializer: CreateCustomUserSerializer = CreateCustomUserSerializer(
            data=resulted_data
        )
        new_password: Optional[str] = resulted_data.get("password", None)
        if not new_password or not isinstance(new_password, str):
            return DRF_Response(
                data={
                    "password": "Пароль обязан быть в формате строки"
                },
                status=HTTP_400_BAD_REQUEST
            )
        valid: bool = serializer.is_valid()
        if valid:
            new_cust_user: CustomUser = CustomUser(
                **resulted_data,
                is_staff=is_staff
            )
            if photo_url:
                new_cust_user.save_remote_image(
                    image_url=photo_url
                )
            new_cust_user.set_password(new_password)
            new_cust_user.save()
            login(
                request=request,
                user=new_cust_user
            )
            self.add_districts(
                request=request,
                *args,
                **kwargs
            )
            refresh_token: RefreshToken = RefreshToken.for_user(
                user=new_cust_user
            )
            response: DRF_Response = self.retrieve(
                request=request,
                pk=new_cust_user.id,
                *args,
                **kwargs
            )
            response.data.setdefault("refresh", str(refresh_token))
            response.data.setdefault("access", str(refresh_token.access_token))
            return response
        return DRF_Response(
            data=serializer.errors,
            status=HTTP_400_BAD_REQUEST
        )

    @action(
        methods=["POST"],
        detail=False,
        url_path="login",
        url_name="login",
        permission_classes=(AllowAny,)
    )
    def login(
        self,
        request: DRF_Request,
        *args: Tuple[Any],
        **kwargs: Dict[str, Any]
    ) -> DRF_Response:
        """Handle POST-request to login the already existed user."""

        if request.user.is_authenticated:
            return DRF_Response(
                data={
                    "response": "Вы уже авторизованы!"
                },
                status=HTTP_403_FORBIDDEN
            )
        phone_email_telegram: str = request.data.get("login_data", "")
        password: str = request.data.get("password", "")
        if not phone_email_telegram or not password or \
                not isinstance(phone_email_telegram, str) or \
                not isinstance(password, str):
            return DRF_Response(
                data={
                    "response": "Данные должны быть предоставлены строками"
                },
                status=HTTP_400_BAD_REQUEST
            )

        custom_user: Optional[CustomUser] = \
            CustomUser.objects.get_by_email_phone_telegram(
                phone_email_telegram=phone_email_telegram
            )
        if not custom_user:
            return DRF_Response(
                data={
                    "response": "Пользователя с такими данными не найден"
                },
                status=HTTP_404_NOT_FOUND
            )
        same_passwords: bool = custom_user.check_password(
            raw_password=password
        )
        if not same_passwords:
            return DRF_Response(
                data={"response": "Вы ввели неправильный пароль"},
                status=HTTP_403_FORBIDDEN
            )
        if custom_user.datetime_deleted:
            return DRF_Response(
                data={"response": "Извините, но ваше пользователь удалён"},
                status=HTTP_403_FORBIDDEN
            )
        login(
            request=request,
            user=custom_user
        )
        refresh_token: RefreshToken = RefreshToken.for_user(user=custom_user)
        det_ser: CustomUserDetailSerializer = CustomUserDetailSerializer(
            instance=custom_user,
            many=False
        )
        resulted_data: dict[str, Any] = det_ser.data.copy()
        resulted_data.setdefault("refresh", str(refresh_token))
        resulted_data.setdefault("access", str(refresh_token.access_token))
        response: DRF_Response = DRF_Response(
            data=resulted_data,
            status=HTTP_200_OK
        )
        return response

    @action(
        methods=["PATCH"],
        detail=False,
        url_path="deactivate",
        url_name="deactivate",
        permission_classes=(
            IsAuthenticated,
            IsNonDeletedUser,
            IsActiveAccount,
            IsOwnerUser,
        )
    )
    def deactivate_user(
        self,
        request: DRF_Request,
        *args: Tuple[Any],
        **kwargs: Dict[str, Any]
    ) -> DRF_Response:
        """Handle PATCH request to deactivate already logged in user."""
        obj_resp: Union[CustomUser, DRF_Response]
        is_existed: bool = False
        obj_resp, is_existed = self.get_obj_or_response(
            request=request,
            pk=request.user.id,
            class_name=CustomUser,
            queryset=self.queryset.get_not_deleted()
        )
        if not is_existed:
            return obj_resp
        self.check_object_permissions(request=request, obj=obj_resp)
        if not obj_resp.is_active_account:
            return DRF_Response(
                data={
                    "response": "Ваш аккаунт уже итак деактивирован."
                },
                status=HTTP_403_FORBIDDEN
            )
        obj_resp.deactivate()
        return DRF_Response(
            data={
                "response": "Ваш аккаунт успешно деактивирован"
            },
            status=HTTP_200_OK
        )

    @action(
        methods=["PATCH"],
        detail=False,
        url_path="activate",
        url_name="activate",
        permission_classes=(
            IsAuthenticated,
            IsNonDeletedUser,
            IsOwnerUser,
        )
    )
    def activate_user(
        self,
        request: DRF_Request,
        *args: Tuple[Any],
        **kwargs: Dict[str, Any]
    ) -> DRF_Response:
        """Handle PATCH request to activate already logged in user."""
        obj_resp: Union[CustomUser, DRF_Response]
        is_existed: bool = False
        obj_resp, is_existed = self.get_obj_or_response(
            request=request,
            pk=request.user.id,
            class_name=CustomUser,
            queryset=self.queryset.get_not_deleted()
        )
        if not is_existed:
            return obj_resp
        self.check_object_permissions(request=request, obj=obj_resp)
        if obj_resp.is_active_account:
            return DRF_Response(
                data={
                    "response": "Ваш аккаунт уже итак активирован."
                },
                status=HTTP_403_FORBIDDEN
            )
        obj_resp.activate()
        return DRF_Response(
            data={
                "response": "Ваш аккаунт успешно активирован"
            },
            status=HTTP_200_OK
        )

    @action(
        methods=["GET"],
        url_path="personal_account",
        detail=False,
        permission_classes=(
            IsAuthenticated,
            IsNonDeletedUser,
            IsActiveAccount,
        )
    )
    def get_personal_account(
        self,
        request: DRF_Request,
        *args: Tuple[Any],
        **kwargs: Dict[Any, Any]
    ) -> DRF_Response:
        """Handle GET-request to obtain user's personal data."""
        return self.retrieve(
            request=request,
            pk=request.user.id,
            *args,
            **kwargs
        )

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="confirm_account",
        url_name="confirm_account",
        permission_classes=(
            IsAdminUser,
            IsNonDeletedUser,
            IsActiveAccount
        )
    )
    def confirm_account(
        self,
        request: DRF_Request,
        pk: str,
        *args: Tuple[Any],
        **kwargs: Dict[str, Any]
    ) -> None:
        """Confirm user's account."""
        found_user: Optional[CustomUser] = self.get_queryset_instance(
            class_name=CustomUser,
            queryset=self.get_queryset(),
            pk=pk
        )
        if not found_user:
            return DRF_Response(
                data={
                    "detail": "Пользователь не найден. Возможные причины: "
                    "1. Аккаунт удалён"
                    "2. Аккаунт является неактивным"
                    "3. Пользователь не зарегестрирован"
                },
                status=HTTP_404_NOT_FOUND
            )
        if found_user.is_confirmed_account:
            return DRF_Response(
                data={
                    "detail": "Ваш аккаунт итак подтвержден. Нет "
                    "необходимости делать это снова."
                },
                status=HTTP_400_BAD_REQUEST
            )
        found_user.confirm_account()
        return DRF_Response(
            data={
                "detail": f"Аккаунт пользователя {found_user.first_name} "
                "успешно подтвержден :) Приятного поиска будущих соседей",
                "data": {
                    "telegram_id": found_user.telegram_user_id
                },
            }
        )
