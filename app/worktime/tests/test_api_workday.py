from datetime import time
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from worktime.serializers import WorkDayDetailsSerializer, WorkDaySerializer

from worktime.models import WorkDay


WORKDAY_URL = reverse("worktime:workday-list")
CALCULATOR_URL = reverse("worktime:work_calc")


def workday_url_details(id):
    return reverse("worktime:workday-detail", args=[id])


pytestmark = pytest.mark.django_db


# -------------------- Unauth api tests --------------------


def test_get_unauth_workday_should_fail() -> None:
    """Test get unauth workday shoulf fail"""

    client = APIClient()
    res = client.get(WORKDAY_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_post_unauth_workday_should_fail() -> None:
    """Test post unauth workday shoulf fail"""

    client = APIClient()
    res = client.post(WORKDAY_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_unauth_details_should_fail() -> None:
    """Test get details unauth user should fail"""
    client = APIClient()
    res = client.get(workday_url_details("something"))
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_unauth_details_should_fail() -> None:
    """Test get details unauth user should fail"""
    client = APIClient()
    res = client.delete(workday_url_details("something"))
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


# -------------------- Auth api tests --------------------


def test_get_workday_list_should_succeed(auth_api_client, payload_workday):
    req = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert req.status_code == status.HTTP_201_CREATED

    res = auth_api_client.get(WORKDAY_URL)
    assert res.status_code == status.HTTP_200_OK
    for i in ["day", "start_of_work", "end_of_work", "id", "date"]:
        assert i in res.data[0]


def test_get_details_should_succeed(auth_api_client, payload_workday):
    """Test get details from work time"""
    req = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert req.status_code == status.HTTP_201_CREATED

    res = auth_api_client.get(workday_url_details(req.data["id"]))
    assert res.status_code == status.HTTP_200_OK
    assert res.data == req.data


def test_delete_details_should_succeed(auth_api_client, payload_workday):
    """Test delete details from work time"""
    req = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert req.status_code == status.HTTP_201_CREATED

    res = auth_api_client.delete(workday_url_details(req.data["id"]))
    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_post_workday_should_succeed(payload_workday, auth_api_client):
    """Test create workday"""
    res = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert res.status_code == status.HTTP_201_CREATED
    day = WorkDay.objects.get(id=res.data["id"])
    assert res.data == WorkDayDetailsSerializer(day).data
    for i in [
        "day",
        "start_of_work",
        "end_of_work",
        "id",
        "date",
        "comment",
        "shift",
    ]:
        assert i in res.data


def test_post_workday_without_shift_should_fail(
    auth_api_client,
    payload_workday,
):
    """Test create workday without shift should fail"""
    payload_workday.pop("shift")
    res = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_post_normal_day_without_start_time_should_fail(
    auth_api_client, payload_workday
):
    """Test post normal day without start time"""
    payload_workday["start_of_work"] = ""
    res = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    message = "Normal day should have (start of work) and (end of work)"
    assert str(res.data["non_field_errors"][0]) == message


def test_post_normal_day_without_end_time_should_fail(
    auth_api_client,
    payload_workday,
):
    """Test post normal day without end time"""
    payload_workday["end_of_work"] = ""
    res = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    message = "Normal day should have (start of work) and (end of work)"
    assert str(res.data["non_field_errors"][0]) == message


def test_post_job_travel_should_succeed(auth_api_client, payload_workday):
    """Test post job travel"""
    payload_workday["day"] = 5
    res = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data["end_of_work"] is None


def test_post_job_travel_without_start_day_shoudl_fail(
    payload_workday, auth_api_client
):
    """Test post job travel without start time should fail"""
    payload_workday["day"] = 5
    payload_workday["start_of_work"] = ""
    res = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    message = "start of work mustn't be empty"
    assert str(res.data["non_field_errors"][0]) == message


def test_create_same_user_same_dates_should_fail(
    auth_api_client,
    payload_workday,
):
    """Test create 2 same dates with the same user should fail"""
    res = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert res.status_code == status.HTTP_201_CREATED
    res = auth_api_client.post(WORKDAY_URL, payload_workday)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        res.data.get("non_field_errors")[0]
        == "Please Select another Date This already exists"
    )


def test_data_from_view_shold_succeed(
    auth_api_client,
    payload_workday,
):
    """Test the calculator"""
    req = auth_api_client.post(WORKDAY_URL, payload_workday)
    payload = {
        "from_date": payload_workday["date"],
        "to_date": payload_workday["date"],
    }

    res = auth_api_client.post(CALCULATOR_URL, payload)
    data = {
        "late_for_work": 0,
        "overtime": 0,
        "early_leave": 0,
        "workdays": 1,
        "weekend": 0,
        "times_off": 0,
        "sick_leaves": 0,
        "publick_holidays": 0,
        "job_travel": 0,
    }
    assert res.data == data


def test_data_late_for_work_from_view_should_succeed(
    auth_api_client,
    payload_workday,
):
    """Test the calculator"""
    payload_workday["start_of_work"] = time(8, 11)
    req = auth_api_client.post(WORKDAY_URL, payload_workday)
    payload = {
        "from_date": payload_workday["date"],
        "to_date": payload_workday["date"],
    }

    res = auth_api_client.post(CALCULATOR_URL, payload)
    data = {
        "late_for_work": 11,
        "overtime": 0,
        "early_leave": 0,
        "workdays": 1,
        "weekend": 0,
        "times_off": 0,
        "sick_leaves": 0,
        "publick_holidays": 0,
        "job_travel": 0,
    }
    assert res.data == data


def test_data_overtime_from_view_should_succeed(
    auth_api_client,
    payload_workday,
):
    """Test the calculator"""
    payload_workday["end_of_work"] = time(16, 50)
    req = auth_api_client.post(WORKDAY_URL, payload_workday)
    payload = {
        "from_date": payload_workday["date"],
        "to_date": payload_workday["date"],
    }

    res = auth_api_client.post(CALCULATOR_URL, payload)
    data = {
        "late_for_work": 0,
        "overtime": 20,
        "early_leave": 0,
        "workdays": 1,
        "weekend": 0,
        "times_off": 0,
        "sick_leaves": 0,
        "publick_holidays": 0,
        "job_travel": 0,
    }
    assert res.data == data


def test_data_early_leave_from_view_should_succeed(
    auth_api_client,
    payload_workday,
):
    """Test the calculator"""
    payload_workday["end_of_work"] = time(16, 00)
    req = auth_api_client.post(WORKDAY_URL, payload_workday)
    payload = {
        "from_date": payload_workday["date"],
        "to_date": payload_workday["date"],
    }

    res = auth_api_client.post(CALCULATOR_URL, payload)
    data = {
        "late_for_work": 0,
        "overtime": 0,
        "early_leave": -30,
        "workdays": 1,
        "weekend": 0,
        "times_off": 0,
        "sick_leaves": 0,
        "publick_holidays": 0,
        "job_travel": 0,
    }
    assert res.data == data
