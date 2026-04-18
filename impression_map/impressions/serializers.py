import re
from datetime import datetime
from typing import Any

from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers, status

from .models import Impression, ImpressionMedia

CAMEL_CASE_REGEX = re.compile(r"(?<!^)(?=[A-Z])")


class CamelCaseMixin(serializers.Serializer):
    def _snake_to_camel(self, snake_str: str) -> str:
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {self._snake_to_camel(key): value for key, value in representation.items()}

    def to_internal_value(self, data):
        snake_case_data = {}
        for key, value in data.items():
            # camelCase -> snake_case
            snake_key = re.sub(CAMEL_CASE_REGEX, "_", key).lower()
            snake_case_data[snake_key] = value
        return super().to_internal_value(snake_case_data)


class ImpressionMediaSerializer(CamelCaseMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ImpressionMedia
        fields = ["id", "file", "is_video"]
        read_only_fields = ["id"]


class ImpressionReadSerializer(CamelCaseMixin, serializers.HyperlinkedModelSerializer):
    user_id = serializers.SerializerMethodField()
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M", read_only=True)
    media = ImpressionMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Impression
        fields = ["id", "local_id", "user_id", "url", "title", "description", "date", "latitude", "longitude", "media"]

    def get_user_id(self, obj):
        request = self.context.get("request")
        if request and request.user == obj.user:
            return None
        return obj.user_id


# using separate serializer for writing as DRF doesn't support writable nested serializers
class ImpressionWriteSerializer(CamelCaseMixin, serializers.HyperlinkedModelSerializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    date = serializers.DateTimeField(
        required=False,
        format="%Y-%m-%dT%H:%M",
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
    )
    media = serializers.ListField(
        required=False,
        child=serializers.FileField(),
        allow_empty=True,
        max_length=10,
        write_only=True,
    )

    class Meta:
        model = Impression
        fields = ["url", "local_id", "title", "description", "date", "latitude", "longitude", "media"]

    def create(self, validated_data: dict[str, Any]) -> Impression:
        lat = validated_data.pop("latitude")
        lng = validated_data.pop("longitude")
        date = validated_data.pop("date") if "date" in validated_data else datetime.now()
        media_files: list[Any] = validated_data.pop("media", [])

        validated_data["user"] = self.context["request"].user

        impression = Impression(**validated_data)
        impression.location = Point(lng, lat, srid=4326)
        impression.date = date
        impression.save()

        self._handle_media(impression, media_files)
        return impression

    def update(self, instance: Impression, validated_data: dict[str, Any]) -> Impression:
        lat = validated_data.pop("latitude", None)
        lng = validated_data.pop("longitude", None)
        date = validated_data.pop("date") if "date" in validated_data else datetime.now()

        if lat is not None and lng is not None:
            instance.location = Point(lng, lat, srid=4326)
        instance.date = date

        instance = super().update(instance, validated_data)

        media_files: list[Any] = validated_data.get("media")
        if media_files is not None:
            instance.media.all().delete()
            self._handle_media(instance, media_files)

        return instance

    def _handle_media(self, impression: Impression, media_files: list[Any]) -> None:
        media_objects: list[ImpressionMedia] = []

        for file in media_files:
            if not isinstance(file, UploadedFile):
                continue

            content_type = file.content_type or ""

            if content_type == "image/jpeg":
                is_video = False
            elif content_type == "video/mp4":
                is_video = True
            else:
                raise serializers.ValidationError(
                    {"media": f"Unsupported file type: {content_type}. Only JPEG and MP4 are allowed."},
                    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                )

            media_objects.append(ImpressionMedia(impression=impression, file=file, is_video=is_video))

        if media_objects:
            ImpressionMedia.objects.bulk_create(media_objects)
