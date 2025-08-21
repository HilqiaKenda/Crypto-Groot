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
                "description": "Free 7-day trial with limited access to indicators and assets.",
            },
            {
                "name": "Basic Access",
                "price": 9.99,
                "duration_days": 30,
                "description": "Ideal for casual traders. Access to real-time charts and up to 2 indicators for 3 assets.",
            },
            {
                "name": "Trader Launchpad",
                "price": 24.99,
                "duration_days": 90,
                "description": "Perfect for beginners or short-term traders. Features: Real-time charts, limited indicators, up to 5 tradable assets.",
            },
            {
                "name": "Momentum Pro",
                "price": 54.99,
                "duration_days": 180,
                "description": "For growing traders needing deeper insight. Advanced indicators, 10+ tracked assets, strategy alerts.",
            },
            {
                "name": "Elite Signals Club",
                "price": 99.99,
                "duration_days": 365,
                "description": "Full access for professional traders. All indicators, unlimited assets, AI signals, and priority support.",
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
