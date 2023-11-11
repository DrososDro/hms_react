from django.contrib.auth import get_user_model
from django.contrib.auth.forms import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status, views
from accounts.serializers import (
    UserSerializer,
    ResetSerializer,
    ResetPasswordSerializer,
)
from rest_framework.response import Response
from accounts.models import Permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.utils import send_reset_mail


class CreateUserView(generics.CreateAPIView):
    """
    Create the user Here.
    Please put a valid email and check your mails for
    the validation email
    """

    serializer_class = UserSerializer


class ActivateEmail(views.APIView):
    """Activate Email address and take the basic Permission."""

    serializer_class = None

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            get_user_model().DoesNotExist,
        ):
            user = None
        if user is not None and default_token_generator.check_token(
            user,
            token,
        ):
            user.is_active = True
            user.save()
            perm, created = Permissions.objects.get_or_create(name="customer")
            user.permissions.add(perm)

            return Response(data="Activations Success")
        else:
            return Response(
                data="Activation Fail",
                status=status.HTTP_400_BAD_REQUEST,
            )


class MyAccountView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrive and return the authenticated user."""

        return self.request.user


class ResetPassword(views.APIView):
    """Reset password, 1st step email validation that exists"""

    serializer_class = ResetSerializer

    def post(self, request):
        email = request.data.get("email", None)
        try:
            user = get_user_model().objects.get(
                email__iexact=email,
                is_active=True,
            )
        except get_user_model().DoesNotExist:
            return Response(
                data="Give a Valid email",
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            send_reset_mail(request, user)

            return Response(
                data="Reset email Sendt",
            )


class ResetPasswordSubmit(views.APIView):
    """Reset Password set Password view"""

    serializer_class = ResetPasswordSerializer

    def post(self, request, uidb64, token):
        password = request.data.get("password", None)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            get_user_model().DoesNotExist,
        ):
            user = None

        if (
            user is not None
            and password is not None
            and default_token_generator.check_token(
                user,
                token,
            )
        ):
            user.set_password(password)
            user.save()

            return Response(data="Password reset Successfully")
        else:
            return Response(
                data="Passowrd reset Fail",
                status=status.HTTP_400_BAD_REQUEST,
            )
