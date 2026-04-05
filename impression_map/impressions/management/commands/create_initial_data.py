from typing import Any

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from impressions.models import Impression


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

        impressions_data = [
            {
                "user": users[0],
                "title": "Red Square",
                "description": "Beautiful place in the center of Moscow.",
                "longitude": 37.6216,
                "latitude": 55.7539,
                "onServer": True,
            },
            {
                "user": users[0],
                "title": "Gorky Park",
                "description": "Great place for walks, sports and picnics.",
                "longitude": 37.6012,
                "latitude": 55.7285,
                "onServer": False,
            },
            {
                "user": users[1],
                "title": "Hermitage",
                "description": "One of the largest museums in the world.",
                "longitude": 30.3139,
                "latitude": 59.9398,
                "onServer": False,
            },
            {
                "user": users[1],
                "title": "Sochi Beach",
                "description": "Sea, sun and palm trees.",
                "longitude": 39.7231,
                "latitude": 43.5855,
                "onServer": True,
            },
            {
                "user": users[0],
                "title": "Baikal Lake",
                "description": "The deepest lake on the planet.",
                "longitude": 104.9000,
                "latitude": 51.8500,
                "onServer": True,
            },
            {
                "user": users[1],
                "title": "Ruskeala",
                "description": "Marble canyon with stunning views.",
                "longitude": 30.3667,
                "latitude": 61.9500,
                "onServer": False,
            },
            {
                "user": users[0],
                "title": "Vladivostok Bridge",
                "description": "Beautiful view of the Golden Bridge.",
                "longitude": 131.8855,
                "latitude": 43.1155,
                "onServer": True,
            },
            {
                "user": users[1],
                "title": "Altai Mountains",
                "description": "Mountains, rivers and clean air.",
                "longitude": 86.0000,
                "latitude": 51.4000,
                "onServer": True,
            },
        ]

        for data in impressions_data:
            point = Point(data["longitude"], data["latitude"], srid=4326)

            Impression.objects.create(
                user=data["user"],
                title=data["title"],
                description=data["description"],
                location=point,
            )

        self.stdout.write(self.style.SUCCESS(f"Created {len(impressions_data)} Impression objects"))
        self.stdout.write(self.style.SUCCESS("Database population completed successfully."))
