"""
Serializer for the account model
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.utils import send_activation_mail


class UserSerializer(serializers.ModelSerializer):
    """Serializer fot the user Model."""

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        """Create the user with the validated_data"""
        user = get_user_model().objects.create_user(**validated_data)
        send_activation_mail(self.context["request"], user)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class ResetSerializer(serializers.Serializer):
    """Reset password email serializer"""

    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """Reset Password Submit serializer"""

    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )
