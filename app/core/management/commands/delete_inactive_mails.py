from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    def handle(self, *args, **options):
        accounts = get_user_model().objects.filter(is_active=False)
        if accounts:
            for user in accounts:
                if timezone.now() >= user.created_at + timedelta(minutes=60):
                    user.delete()
