from django.test import TestCase
from .models import User, SubscriptionPlan, Payment, UserUsageLog, Watchlist
from django.utils import timezone

# Create your tests here.


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, "test@example.com")


class SubscriptionPlanModelTest(TestCase):
    def test_create_plan(self):
        plan = SubscriptionPlan.objects.create(name="Pro", price=10.0, duration_days=30)
        self.assertEqual(SubscriptionPlan.objects.count(), 1)
        self.assertEqual(plan.name, "Pro")


class PaymentModelTest(TestCase):
    def test_create_payment(self):
        user = User.objects.create_user(
            username="payuser", email="pay@example.com", password="testpass"
        )
        plan = SubscriptionPlan.objects.create(name="Basic", price=5.0, duration_days=7)
        payment = Payment.objects.create(
            user=user, plan=plan, amount=5.0, status="completed"
        )
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(payment.status, "completed")


class UserUsageLogModelTest(TestCase):
    def test_create_usage_log(self):
        user = User.objects.create_user(
            username="loguser", email="log@example.com", password="testpass"
        )
        log = UserUsageLog.objects.create(
            user=user, action="login", details="User logged in"
        )
        self.assertEqual(UserUsageLog.objects.count(), 1)
        self.assertEqual(log.action, "login")


class WatchlistModelTest(TestCase):
    def test_create_watchlist(self):
        user = User.objects.create_user(
            username="watchuser", email="watch@example.com", password="testpass"
        )
        watch = Watchlist.objects.create(user=user, symbol="BTCUSDT")
        self.assertEqual(Watchlist.objects.count(), 1)
        self.assertEqual(watch.symbol, "BTCUSDT")
