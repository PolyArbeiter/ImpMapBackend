from rest_framework import permissions, viewsets

from .models import Impression
from .serializers import ImpressionSerializer


class ImpressionViewSet(viewsets.ModelViewSet):
    queryset = Impression.objects.all().order_by("user")
    serializer_class = ImpressionSerializer
    permission_classes = [permissions.IsAuthenticated]
