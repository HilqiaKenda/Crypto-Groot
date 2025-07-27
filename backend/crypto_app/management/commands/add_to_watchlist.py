from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from crypto_app.models import Watchlist


class Command(BaseCommand):
    help = "Add a symbol to a user's watchlist"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("symbol", type=str)

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        symbol = options["symbol"]
        user = User.objects.filter(username=username).first()
        if not user:
            self.stdout.write(self.style.ERROR(f"User '{username}' does not exist."))
            return
        obj, created = Watchlist.objects.get_or_create(user=user, symbol=symbol)
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Added {symbol} to {username}'s watchlist.")
            )
        else:
            self.stdout.write(f"{symbol} is already in {username}'s watchlist.")
