from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models


class Impression(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, default="Untitled")
    description = models.TextField(max_length=2000, default="No description.")
    location = PointField()  # SRID=4326 (WGS84)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x

    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["location"], name="impression_location_gist_idx"),
        ]
