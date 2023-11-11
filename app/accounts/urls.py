from django.urls import path
from accounts import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


app_name = "accounts"
urlpatterns = [
    path(
        "create-user/",
        views.CreateUserView.as_view(),
        name="create_user",
    ),
    path(
        "activate/<str:uidb64>/<str:token>/",
        views.ActivateEmail.as_view(),
        name="activate",
    ),
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("my-account/", views.MyAccountView.as_view(), name="my_account"),
    path(
        "reset-password-email",
        views.ResetPassword.as_view(),
        name="reset_password_email",
    ),
    path(
        "reset-password-submit/<str:uidb64>/<str:token>/",
        views.ResetPasswordSubmit.as_view(),
        name="reset_password_submit",
    ),
]
