# urls.py
from django.urls import path, re_path
from crypto_app.views import (
    PaymentView,
    SubscriptionPlanView,
    UserInfoView, 
    RegisterUserView, 
    LoginView, 
    LogoutView, 
    CookierefreshToken,
    UserUsageLogView, 
    WatchlistView
)

from django.urls import include
from . import consumers


urlpatterns = [
    # Auth
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", CookierefreshToken.as_view(), name="refresh"),
    path("user-info/", UserInfoView.as_view(), name="user-info"),
    
    # services
    path("payment/", PaymentView.as_view(), name="payment"),
    path("subscription/", SubscriptionPlanView.as_view(), name="subscription"),
    path("watch-list/", WatchlistView.as_view(), name="watchlist"),
    path("usage-log/", UserUsageLogView.as_view(), name="usage-log"),
]

websocket_urlpatterns = [
    re_path(r"ws/socket-server/", consumers.DashConsumer.as_asgi())
]
