import datetime
import logging
import re

from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from django.utils.datastructures import MultiValueDict
from rest_framework import serializers, status

from .models import Impression, ImpressionMedia

CAMEL_CASE_REGEX = re.compile(r"(?<!^)(?=[A-Z])")

logger = logging.getLogger(__name__)


class CamelCaseMixin(serializers.Serializer):
    def _snake_to_camel(self, snake_str: str) -> str:
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {self._snake_to_camel(key): value for key, value in representation.items()}

    def to_internal_value(self, data: MultiValueDict[str, object]):
        snake_case_data = {}
        for key in data:
            t = data.getlist(key)
            value = t if isinstance(t[0], UploadedFile) else t.pop()
            # camelCase -> snake_case
            snake_key = re.sub(CAMEL_CASE_REGEX, "_", key).lower()
            snake_case_data[snake_key] = value
        return super().to_internal_value(snake_case_data)


class UnixTimestampField(serializers.IntegerField):
    def to_representation(self, value: object) -> int | None:
        if value is None:
            return None

        if isinstance(value, datetime.datetime):
            if timezone.is_naive(value):
                value = timezone.make_aware(value, datetime.UTC)
            return int(value.timestamp() * 1000)

        return super().to_representation(value)

    def to_internal_value(self, data):
        if data is None:
            return None

        try:
            timestamp = int(data) // 1000
            return datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
        except (TypeError, ValueError) as err:
            raise serializers.ValidationError("Invalid Unix timestamp (integer number of seconds).") from err


class ImpressionMediaSerializer(CamelCaseMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ImpressionMedia
        fields = ["id", "file", "is_video"]
        read_only_fields = ["id"]


class ImpressionReadSerializer(CamelCaseMixin, serializers.HyperlinkedModelSerializer):
    user_id = serializers.SerializerMethodField()
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    date = UnixTimestampField(read_only=True)
    media = ImpressionMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Impression
        fields = ["url", "id", "local_id", "user_id", "title", "description", "date", "latitude", "longitude", "media"]

    def get_user_id(self, obj):
        request = self.context.get("request")
        if request and request.user == obj.user:
            return None
        return obj.user_id


# using separate serializer for writing as DRF doesn't support writable nested serializers
class ImpressionWriteSerializer(CamelCaseMixin, serializers.HyperlinkedModelSerializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    date = UnixTimestampField(required=False, allow_null=True)
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

    def create(self, validated_data: dict[str, object]) -> Impression:
        lat = validated_data.pop("latitude")
        lng = validated_data.pop("longitude")

        date = validated_data.pop("date") if "date" in validated_data else timezone.now()
        date = date.replace(tzinfo=datetime.UTC)

        media_files: object = validated_data.pop("media", [])
        if not isinstance(media_files, list):
            logger.error(media_files)
            media_files = [media_files]

        validated_data["user"] = self.context["request"].user

        impression = Impression(**validated_data)
        impression.location = Point(lng, lat, srid=4326)
        impression.date = date
        impression.save()

        self._handle_media(impression, media_files)
        return impression

    def update(self, instance: Impression, validated_data: dict[str, object]) -> Impression:
        lat = validated_data.pop("latitude", None)
        lng = validated_data.pop("longitude", None)

        date = validated_data.pop("date") if "date" in validated_data else timezone.now()
        date = date.replace(tzinfo=datetime.UTC)

        if lat is not None and lng is not None:
            instance.location = Point(lng, lat, srid=4326)
        instance.date = date

        media_files: object = validated_data.pop("media", None)

        if media_files is not None:
            if not isinstance(media_files, list):
                media_files = [media_files]
            instance.media.all().delete()
            self._handle_media(instance, media_files)

        return super().update(instance, validated_data)

    def _handle_media(self, impression: Impression, media_files: list[object]) -> None:
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
