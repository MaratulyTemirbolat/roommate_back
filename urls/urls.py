# Third party
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Django
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import (
    path,
    include
)

# Rest Framework
from rest_framework.routers import DefaultRouter

# Project
from apps.auths.views import CustomUserViewSet
from apps.locations.views import CityViewSet


router: DefaultRouter = DefaultRouter(trailing_slash=False)

router.register('auths/users', CustomUserViewSet)
router.register("locations/city", CityViewSet)

urlpatterns = [
    path(
        route=settings.ADMIN_SITE_URL,
        view=admin.site.urls
    ),
    path(
        route='api/token/',
        view=TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        route='api/token/refresh/',
        view=TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        route='api/token/verify/',
        view=TokenVerifyView.as_view(),
        name='token_verify'
    ),
] + static(
    prefix=settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
) + static(
    prefix=settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
) + [
    path(
        route="api/v1/",
        view=include(router.urls)
    )
]

if settings.DEBUG:
    urlpatterns += [
        path(
            route='__debug__/',
            view=include('debug_toolbar.urls')
        ),
    ]
