# urls.py

from django.urls import path
from crypto_app.views import (
    UserListView,
    SubscriptionPlanListView,
    SubscriptionPlanDetailView,
    SubscriptionPlanCreateView,
    PaymentListView,
    UserUsageLogListView,
    WatchlistListView,
)
from .api import router as api_router
from django.urls import include

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("plans/", SubscriptionPlanListView.as_view(), name="subscriptionplan-list"),
    path(
        "plans/<int:pk>/",
        SubscriptionPlanDetailView.as_view(),
        name="subscriptionplan-detail",
    ),
    path(
        "plans/create/",
        SubscriptionPlanCreateView.as_view(),
        name="subscriptionplan-create",
    ),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path("usage-logs/", UserUsageLogListView.as_view(), name="userusagelog-list"),
    path("watchlist/", WatchlistListView.as_view(), name="watchlist-list"),
    path("api/", include(api_router.urls)),
]
