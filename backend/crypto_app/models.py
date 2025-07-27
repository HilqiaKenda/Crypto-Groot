from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Extend as needed, e.g. add subscription, usage, etc.
    email = models.EmailField(unique=True)
    # Add more fields as needed


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    plan = models.ForeignKey("SubscriptionPlan", on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default="pending")
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
