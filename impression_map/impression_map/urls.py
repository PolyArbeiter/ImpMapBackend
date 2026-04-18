from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from impressions.views import UserImpressionViewSet

from . import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/impressions/", include("impressions.urls")),
    # access impressions by (user_id, local_id)
    path("api/v1/users/<int:user_id>/impressions/", UserImpressionViewSet.as_view({"get": "list"})),
    path(
        "api/v1/impressions/users/<int:user_id>/impressions/<int:local_id>/",
        UserImpressionViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
    ),
]

if settings.DEBUG:
    # nginx is better for production
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
