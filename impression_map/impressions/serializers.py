from django.contrib.gis.geos import Point
from rest_framework import serializers

from .models import Impression


class ImpressionSerializer(serializers.HyperlinkedModelSerializer):
    latitude_write = serializers.FloatField(write_only=True, required=True)
    longitude_write = serializers.FloatField(write_only=True, required=True)

    class Meta:
        model = Impression
        fields = [
            "url",
            "title",
            "description",
            "latitude",
            "longitude",
            "latitude_write",
            "longitude_write",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["url", "created_at", "updated_at"]

    def create(self, validated_data):
        lat = validated_data.pop("latitude_write")
        lng = validated_data.pop("longitude_write")

        validated_data["user"] = self.context["request"].user

        impression = Impression(**validated_data)
        impression.location = Point(lng, lat, srid=4326)
        impression.save()
        return impression

    def update(self, instance, validated_data):
        lat = validated_data.pop("latitude_write", None)
        lng = validated_data.pop("longitude_write", None)

        if lat is not None and lng is not None:
            instance.location = Point(lng, lat, srid=4326)

        return super().update(instance, validated_data)
