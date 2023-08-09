# Django
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import (
    path,
    include
)

urlpatterns = [
    path(settings.ADMIN_SITE_URL, admin.site.urls),
] + static(
    prefix=settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
) + static(
    prefix=settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
