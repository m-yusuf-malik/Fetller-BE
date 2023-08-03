from django.urls import path

from account.views.auth import RegisterView, LoginView
from account.views.user import UserRetrieveView, BatchView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/<str:username>", UserRetrieveView.as_view()),
    path("users/<str:username>/batch", BatchView.as_view()),
]
