from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models


class Impression(models.Model):
    local_id = models.BigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, default=None, null=False, blank=False)
    description = models.TextField(max_length=2000, default=None, null=False, blank=False)
    location = PointField()  # SRID=4326 (WGS84)
    date = models.DateTimeField(null=True)

    @property
    def latitude(self) -> float:
        return self.location.y

    @property
    def longitude(self) -> float:
        return self.location.x

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="local_id is unique in user's pool",
                fields=["user_id", "local_id"],
            ),
        ]

    def __str__(self) -> str:
        return self.title or f"Impression {self.id}"


class ImpressionMedia(models.Model):
    impression = models.ForeignKey(Impression, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="impressions/%Y/%m/%d/")
    is_video = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Media"

    def __str__(self) -> str:
        return f"Media for Impression {self.impression_id}"
