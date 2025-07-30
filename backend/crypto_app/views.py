from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView
)
from django.urls import reverse_lazy
from .models import User, SubscriptionPlan, Payment, UserUsageLog, Watchlist


# User views (list only for demonstration)
class UserListView(ListView):
    model = User


# SubscriptionPlan views
class SubscriptionPlanListView(ListView):
    model = SubscriptionPlan


class SubscriptionPlanDetailView(DetailView):
    model = SubscriptionPlan


class SubscriptionPlanCreateView(CreateView):
    model = SubscriptionPlan
    fields = ["name", "price", "duration_days", "description", "is_active"]
    success_url = reverse_lazy("subscriptionplan-list")


# Payment views
class PaymentListView(ListView):
    model = Payment


# UserUsageLog views
class UserUsageLogListView(ListView):
    model = UserUsageLog


# Watchlist views
class WatchlistListView(ListView):
    model = Watchlist
