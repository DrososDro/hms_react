from django.contrib.auth import get_user_model
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def create_user():
    def _create_user_factory(*, email, password, is_active=True):
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        if is_active:
            user.is_active = True

        user.save()
        return user

    return _create_user_factory


@pytest.fixture
def create_superuser():
    user = get_user_model().objects.create_superuser(
        email="xaos@xaos.com",
        password="passWord",
    )
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def def_user():
    """user john doe em: John.Doe@example.com pass: test*Pass1234"""
    user_dict = {
        "email": "John.Doe@example.com",
        "password": "testPass1234*",
    }
    return user_dict


@pytest.fixture
def auth_api_client(create_user, def_user):
    """Api client force authenticate"""
    user = create_user(**def_user)
    client = APIClient()
    client.force_authenticate(user)
    return client
