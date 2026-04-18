from datetime import UTC, datetime, timedelta
from random import randint
from typing import Any

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.files import File
from django.core.management.base import BaseCommand

from impression_map.settings import BASE_DIR
from impressions.models import Impression, ImpressionMedia

EXAMPLE_MEDIA_ROOT = BASE_DIR / "media-example"


class Command(BaseCommand):
    help = "Creates superuser, 2 regular users and 8 Impression objects."

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(self.style.SUCCESS("Starting database population..."))

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(username="admin", password="admin")
            self.stdout.write(self.style.SUCCESS("Superuser created: admin:admin"))
        else:
            self.stdout.write(self.style.WARNING("Superuser admin already exists"))

        users_data = [
            {"username": "user1", "password": "user123"},
            {"username": "user2", "password": "user123"},
        ]

        users: list[User] = []

        for data in users_data:
            if not User.objects.filter(username=data["username"]).exists():
                user = User.objects.create_user(**data)
                users.append(user)
                self.stdout.write(self.style.SUCCESS(f"User created: {data['username']}"))
            else:
                user = User.objects.get(username=data["username"])
                users.append(user)
                self.stdout.write(self.style.WARNING(f"User {data['username']} already exists"))

        now = datetime.now(tz=UTC)

        impressions_data = [
            {
                "local_id": 12,
                "user": users[0],
                "title": "Between-Riversburg",
                "description": "Beautiful place in the middle of nowhere.",
                "longitude": 53.689715,
                "latitude": 88.138630,
                "date": datetime(day=10, month=8, year=2021),
                "add_media": True,
            },
            {
                "local_id": 13,
                "user": users[0],
                "title": "Gorky Park",
                "description": "Great place for walks, sports and picnics.",
                "longitude": 37.6012,
                "latitude": 55.7285,
                "date": now + self._gen_rand_timedelta(),
            },
            {
                "local_id": 11,
                "user": users[1],
                "title": "Hermitage",
                "description": "One of the largest museums in the world.",
                "longitude": 30.3139,
                "latitude": 59.9398,
                "date": now + self._gen_rand_timedelta(),
            },
            {
                "local_id": 12,
                "user": users[1],
                "title": "Sochi Beach",
                "description": "Sea, sun and palm trees.",
                "longitude": 39.7231,
                "latitude": 43.5855,
                "date": now + self._gen_rand_timedelta(),
            },
            {
                "local_id": 1,
                "user": users[0],
                "title": "Baikal Lake",
                "description": "The deepest lake on the planet.",
                "longitude": 104.9000,
                "latitude": 51.8500,
                "date": now + self._gen_rand_timedelta(),
            },
            {
                "local_id": 2,
                "user": users[1],
                "title": "Ruskeala",
                "description": "Marble canyon with stunning views.",
                "longitude": 30.3667,
                "latitude": 61.9500,
                "date": now + self._gen_rand_timedelta(),
            },
            {
                "local_id": 3,
                "user": users[0],
                "title": "Vladivostok Bridge",
                "description": "Beautiful view of the Golden Bridge.",
                "longitude": 131.8855,
                "latitude": 43.1155,
                "date": now + self._gen_rand_timedelta(),
            },
            {
                "local_id": 4,
                "user": users[1],
                "title": "Altai Mountains",
                "description": "Mountains, rivers and clean air.",
                "longitude": 86.0000,
                "latitude": 51.4000,
                "date": now + self._gen_rand_timedelta(),
            },
        ]

        for data in impressions_data:
            point = Point(data["longitude"], data["latitude"], srid=4326)

            impression = Impression.objects.create(
                local_id=data["local_id"],
                user=data["user"],
                title=data["title"],
                description=data["description"],
                date=data["date"],
                location=point,
            )

            if data.get("add_media"):
                self._add_example_media(impression)

        self.stdout.write(self.style.SUCCESS(f"Created {len(impressions_data)} Impression objects"))
        self.stdout.write(self.style.SUCCESS("Database population completed successfully."))

    def _gen_rand_timedelta(self) -> timedelta:
        return timedelta(days=randint(-2000, 0), seconds=randint(0, 24 * 60 * 60))

    def _add_example_media(self, impression: Impression) -> None:
        try:
            with open(EXAMPLE_MEDIA_ROOT / "example.jpg", "rb") as f:
                ImpressionMedia.objects.create(
                    impression=impression,
                    file=File(f, name="example.jpg"),
                    is_video=False,
                )
            with open(EXAMPLE_MEDIA_ROOT / "example.mp4", "rb") as f:
                ImpressionMedia.objects.create(
                    impression=impression,
                    file=File(f, name="example.mp4"),
                    is_video=True,
                )

            self.stdout.write(self.style.SUCCESS(f"Added media to Impression: {impression.title}"))
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING("example.jpg or example.mp4 not found."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error adding media: {e}"))
