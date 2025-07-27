from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from crypto_app.models import SubscriptionPlan, Payment


class Command(BaseCommand):
    help = "Create a superuser and assign a subscription plan"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("email", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("--plan", type=str, default="Pro")

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        email = options["email"]
        password = options["password"]
        plan_name = options["plan"]

        user, created = User.objects.get_or_create(
            username=username, email=email, is_superuser=True, is_staff=True
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {username}"))
        else:
            self.stdout.write(f"Superuser already exists: {username}")

        plan = SubscriptionPlan.objects.filter(name=plan_name).first()
        if plan:
            Payment.objects.get_or_create(
                user=user, plan=plan, amount=plan.price, status="completed"
            )
            self.stdout.write(
                self.style.SUCCESS(f"Assigned plan '{plan_name}' to {username}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Plan '{plan_name}' does not exist. No plan assigned."
                )
            )
