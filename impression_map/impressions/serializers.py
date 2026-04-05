from django.contrib.gis.geos import Point
from rest_framework import serializers

from .models import Impression


class ImpressionSerializer(serializers.HyperlinkedModelSerializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)

    class Meta:
        model = Impression
        fields = [
            "url",
            "title",
            "description",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["url"]

    def create(self, validated_data):
        lat = validated_data.pop("latitude")
        lng = validated_data.pop("longitude")

        validated_data["user"] = self.context["request"].user

        impression = Impression(**validated_data)
        impression.location = Point(lng, lat, srid=4326)
        impression.save()
        return impression

    def update(self, instance, validated_data):
        lat = validated_data.pop("latitude", None)
        lng = validated_data.pop("longitude", None)

        if lat is not None and lng is not None:
            instance.location = Point(lng, lat, srid=4326)

        return super().update(instance, validated_data)
