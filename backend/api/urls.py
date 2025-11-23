from django.urls import path
from .views import (
    RegistrationView,
    LoginView,
    ForgotPasswordView,
    ResetPasswordView,
    PromoteUserView,
    UserProfileView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", UserProfileView.as_view(), name="me"),
    path("forgotPassword/", ForgotPasswordView.as_view(), name="forgotPassword"),
    path("resetPassword/", ResetPasswordView.as_view(), name="resetPassword"),
    path("promote-user/", PromoteUserView.as_view(), name="promote-user"),
]