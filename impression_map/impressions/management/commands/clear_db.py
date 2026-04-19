from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Removes non-superuser users and all related objects"

    def handle(self, *args: Any, **options: Any) -> None:
        User.objects.filter(is_superuser=False).delete()
