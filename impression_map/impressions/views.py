from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.mixins import DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.serializers import Serializer

from .models import Impression
from .serializers import ImpressionReadSerializer, ImpressionWriteSerializer


# /api/v1/impressions/users/<user_id>/impressions/<local_id>
class UserImpressionViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, viewsets.GenericViewSet):
    def get_object(self) -> Impression:
        local_id = self.kwargs.get("local_id")
        user_id = self.kwargs.get("user_id")

        queryset = Impression.objects.filter(user_id=user_id)
        obj = get_object_or_404(queryset, local_id=local_id, user_id=user_id)

        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ImpressionWriteSerializer
        return ImpressionReadSerializer


class ImpressionViewSet(viewsets.ModelViewSet):
    queryset = Impression.objects.all().order_by("user")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self)  -> Serializer:
        if self.action in ("create", "update", "partial_update"):
            return ImpressionWriteSerializer
        return ImpressionReadSerializer
