from django.contrib.auth import get_user_model
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import time
from worktime.serializers import ShiftSerializer

from worktime.models import Shift


pytestmark = pytest.mark.django_db

SHIFT_URL = reverse("worktime:shift-list")


def shift_url_details(id):
    return reverse("worktime:shift-detail", args=[id])


# -------------------- Unauthenticated Tests --------------------


def test_get_shift_unauth_should_fail():
    """Test get method wihtout auth user"""
    client = APIClient()
    res = client.get(SHIFT_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_shift_details_unauth_should_fail(def_user, create_user):
    """Test get details method wihtout auth user"""
    user = create_user(**def_user)
    shift = Shift.objects.create(
        start_of_shift="08:30",
        end_of_shift="16:30",
        owner=user,
    )

    client = APIClient()
    res = client.get(shift_url_details(shift.id))
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_post_shift_unauth_should_fail():
    """Test post method wihtout auth user"""
    client = APIClient()
    res = client.post(SHIFT_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_shift_unauth_should_fail():
    """Test delete method wihtout auth user"""
    client = APIClient()
    res = client.delete(SHIFT_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


# -------------------- Authenticated Tests --------------------

start_shift = time(8, 30)
end_shift = time(16, 30)


def test_create_shift_should_succed(create_user, auth_api_client):
    """TEst create shift for user"""
    user = create_user()
    payload = {
        "start_of_shift": start_shift,
        "end_of_shift": end_shift,
    }
    res = auth_api_client.post(SHIFT_URL, payload)
    ser_data = ShiftSerializer(payload)
    assert res.status_code == status.HTTP_201_CREATED
    assert ser_data.data["start_of_shift"] == res.data["start_of_shift"]
    assert ser_data.data["end_of_shift"] == res.data["end_of_shift"]


def test_create_shift_diferent_user(
    create_user,
    auth_api_client,
):
    """Test create same shift for 2 users"""
    user1 = create_user()
    user2 = get_user_model().objects.get(email__icontains="John.doe")
    payload = {
        "start_of_shift": start_shift,
        "end_of_shift": end_shift,
    }
    res = auth_api_client.post(SHIFT_URL, payload)
    assert res.status_code == status.HTTP_201_CREATED
    payload["owner"] = user2
    res = auth_api_client.post(SHIFT_URL, payload)
    assert res.status_code == status.HTTP_201_CREATED

    shifts = Shift.objects.all()
    assert len(shifts) == 2
    assert Shift.objects.filter(owner=user2).exists() is True
    assert Shift.objects.filter(owner=user1).exists() is False


def test_get_shift_list_with_differnt_user_should_fail(create_user, auth_api_client):
    user = create_user()
    payload = {
        "start_of_shift": start_shift,
        "end_of_shift": end_shift,
        "owner": user,
    }

    for i in range(3):
        Shift.objects.create(**payload)

    res = auth_api_client.get(SHIFT_URL)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 0


def test_get_shift_list(auth_api_client):
    user = get_user_model().objects.get(email__icontains="John.doe")
    payload = {
        "start_of_shift": start_shift,
        "end_of_shift": end_shift,
        "owner": user,
    }

    for i in range(3):
        Shift.objects.create(**payload)

    res = auth_api_client.get(SHIFT_URL)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 3


def test_get_shift_details(auth_api_client):
    user = get_user_model().objects.get(email__icontains="John.doe")
    payload = {
        "start_of_shift": start_shift,
        "end_of_shift": end_shift,
        "owner": user,
    }

    shift = Shift.objects.create(**payload)

    res = auth_api_client.get(shift_url_details(shift.id))
    assert res.status_code == status.HTTP_200_OK
    assert res.data == ShiftSerializer(shift).data


def test_delete_shift(auth_api_client):
    user = get_user_model().objects.get(email__icontains="John.doe")
    payload = {
        "start_of_shift": start_shift,
        "end_of_shift": end_shift,
        "owner": user,
    }

    for i in range(3):
        shift = Shift.objects.create(**payload)

    res = auth_api_client.get(SHIFT_URL)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 3
    del_item = auth_api_client.delete(shift_url_details(shift.id))
    assert del_item.status_code == status.HTTP_204_NO_CONTENT
    res = auth_api_client.get(SHIFT_URL)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 2
