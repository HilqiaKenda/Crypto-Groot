from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from crypto_app.models import UserUsageLog


class Command(BaseCommand):
    help = "Log a user action to UserUsageLog"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("action", type=str)
        parser.add_argument("--details", type=str, default="")

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        action = options["action"]
        details = options["details"]
        user = User.objects.filter(username=username).first()
        if not user:
            self.stdout.write(self.style.ERROR(f"User '{username}' does not exist."))
            return
        log = UserUsageLog.objects.create(user=user, action=action, details=details)
        self.stdout.write(
            self.style.SUCCESS(
                f"Logged action '{action}' for user '{username}' at {log.timestamp}"
            )
        )
