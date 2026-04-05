from django.urls import include, path
from rest_framework import routers

from .views import ImpressionViewSet

router = routers.DefaultRouter()

router.register(prefix=r"impressions", viewset=ImpressionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
