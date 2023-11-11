import time
from django.core.management.base import BaseCommand
from psycopg.errors import OperationalError as PsycopgError
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Check ig the db is ready to start connection with db"""

    help = "check if the db is ready to start connection with db"

    def handle(self, *args, **options):
        db_ready = False

        self.stdout.write("w8 for db")
        while db_ready is False:
            try:
                self.check(databases=["default"])
                db_ready = True
            except (PsycopgError, OperationalError):
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("db is available"))
