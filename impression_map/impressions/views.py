from rest_framework import permissions, viewsets

from .models import Impression
from .serializers import ImpressionReadSerializer, ImpressionWriteSerializer


class ImpressionViewSet(viewsets.ModelViewSet):
    queryset = Impression.objects.all().order_by("user")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ImpressionWriteSerializer
        return ImpressionReadSerializer
