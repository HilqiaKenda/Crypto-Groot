from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


class User(AbstractUser):
    email = models.EmailField(unique=True)
    subscription = models.ForeignKey("SubscriptionPlan", on_delete=models.CASCADE, null=True)
    subscription_start_date = models.DateTimeField(default=timezone.now)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)

    objects = CustomUserManager()
    
    def __str__(self):
        return self.username


class SubscriptionPlan(models.Model):

    COST_CHOICES = [
        (""),
    ]

    DURATION_CHOICES = [
        (""),
    ]

    free_trial = "Free Trial"
    trader_subscription = "T"
    momentum_subscription = "M"
    elite_subscription= "E"
    
    SUBSCRIPTIION_CHOICES = [
        (trader_subscription, "Trader Launchpad"),
        (momentum_subscription, "Momentum Pro"),
        (elite_subscription, "Elite Signals Club")
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Payment(models.Model):

    payment_pending = "P"
    payment_complete = "C"
    payment_failed = "F"

    PAYMENT_STATUS_CHOICES = [
        (payment_pending, 'pending'),
        (payment_complete, 'complete'),
        (payment_failed, "failed")
    ]

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    plan = models.ForeignKey("SubscriptionPlan", on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default=payment_pending)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.timestamp}"


class UserUsageLog(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"


class Watchlist(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "symbol")

    def __str__(self):
        return f"{self.user.username} - {self.symbol}"
