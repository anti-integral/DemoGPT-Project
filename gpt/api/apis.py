from django.urls import path
from gpt.modules.register_login_view import (
    UserRegistrationView,
    UserChangePasswordView,
    UserLoginView,
    UserProfileView,
)

urlpatterns = [
    path("register", UserRegistrationView.as_view()),
    path("login", UserLoginView.as_view()),
    path("profile", UserProfileView.as_view()),
    path("change-password", UserChangePasswordView.as_view()),
]
