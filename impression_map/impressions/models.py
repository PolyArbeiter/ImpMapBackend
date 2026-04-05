from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models


class Impression(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, default=None, null=True, blank=True)
    description = models.TextField(max_length=2000, default=None, null=True, blank=True)
    onServer = models.BooleanField(default=True)
    location = PointField()  # SRID=4326 (WGS84)
    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["location"], name="impression_location_gist_idx"),
        ]
