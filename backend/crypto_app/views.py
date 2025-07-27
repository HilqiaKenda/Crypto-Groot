from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from .models import User, SubscriptionPlan, Payment, UserUsageLog, Watchlist

# Dashboard view remains


def dashboard_view(request):
    return render(request, "index.html")


# User views (list only for demonstration)
class UserListView(ListView):
    model = User
    template_name = "user_list.html"


# SubscriptionPlan views
class SubscriptionPlanListView(ListView):
    model = SubscriptionPlan
    template_name = "subscriptionplan_list.html"


class SubscriptionPlanDetailView(DetailView):
    model = SubscriptionPlan
    template_name = "subscriptionplan_detail.html"


class SubscriptionPlanCreateView(CreateView):
    model = SubscriptionPlan
    fields = ["name", "price", "duration_days", "description", "is_active"]
    template_name = "subscriptionplan_form.html"
    success_url = reverse_lazy("subscriptionplan-list")


# Payment views
class PaymentListView(ListView):
    model = Payment
    template_name = "payment_list.html"


# UserUsageLog views
class UserUsageLogListView(ListView):
    model = UserUsageLog
    template_name = "userusagelog_list.html"


# Watchlist views
class WatchlistListView(ListView):
    model = Watchlist
    template_name = "watchlist_list.html"
