from django.contrib.auth import get_user_model
import pytest


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
def def_user():
    """user john doe em: John.Doe@example.com pass: test*Pass1234"""
    user_dict = {
        "email": "John.Doe@example.com",
        "password": "testPass1234*",
    }
    return user_dict
