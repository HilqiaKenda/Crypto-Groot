# urls.py
from django.urls import path
from crypto_app.views import UserInfoView, RegisterUserView, LoginView, LogoutView, CookierefreshToken

from .api import router as api_router
from django.urls import include

urlpatterns = [
    path("users/", UserInfoView.as_view(), name="user-list"),
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", CookierefreshToken.as_view(), name="refresh"),
    path("api/", include(api_router.urls)),
]
