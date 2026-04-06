from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models


class Impression(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, default=None, null=True, blank=True)
    description = models.TextField(max_length=2000, default=None, null=True, blank=True)
    location = PointField()  # SRID=4326 (WGS84)
    date = models.DateTimeField()

    @property
    def latitude(self) -> float:
        return self.location.y

    @property
    def longitude(self) -> float:
        return self.location.x

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["location"], name="impression_location_gist_idx"),
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
