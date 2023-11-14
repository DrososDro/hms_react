from datetime import time, date
from django.contrib.auth import get_user_model
import pytest
from rest_framework.test import APIClient

from worktime.models import Shift


@pytest.fixture
def create_user():
    def _create_user_factory(
        *, email="test@example.com", password="testPass!#$", is_active=True
    ):
        user, created = get_user_model().objects.get_or_create(
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


@pytest.fixture
def auth_api_client(create_user, def_user):
    """Api client force authenticate"""
    user = create_user(**def_user)
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def shift(create_user, def_user):
    user = create_user(**def_user)
    start = time(8, 0)
    end = time(16, 30)

    return Shift.objects.create(
        start_of_shift=start,
        end_of_shift=end,
        owner=user,
    )


@pytest.fixture
def payload_workday(shift):
    start = time(8, 0)
    end = time(16, 30)
    dat = date(2020, 10, 10)

    return {
        "day": 0,
        "start_of_work": start,
        "end_of_work": end,
        "date": dat,
        "shift": shift.id,
    }
