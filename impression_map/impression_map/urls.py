from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/impressions/", include("impressions.urls")),
    # path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

if settings.DEBUG:
    # nginx is better for production
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
