from django.core.management.base import BaseCommand
from crypto_app.models import SubscriptionPlan


class Command(BaseCommand):
    help = "Create default subscription plans"

    def handle(self, *args, **options):
        plans = [
            {
                "name": "Free",
                "price": 0.0,
                "duration_days": 7,
                "description": "Free trial plan",
            },
            {
                "name": "Basic",
                "price": 9.99,
                "duration_days": 30,
                "description": "Basic monthly plan",
            },
            {
                "name": "Pro",
                "price": 99.99,
                "duration_days": 365,
                "description": "Pro annual plan",
            },
        ]
        for plan in plans:
            obj, created = SubscriptionPlan.objects.get_or_create(
                name=plan["name"],
                defaults={
                    "price": plan["price"],
                    "duration_days": plan["duration_days"],
                    "description": plan["description"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created plan: {obj.name}"))
            else:
                self.stdout.write(f"Plan already exists: {obj.name}")
