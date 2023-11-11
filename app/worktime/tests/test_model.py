from datetime import time, date
from django.db.utils import IntegrityError
import pytest
from worktime.models import Shift, WorkDay

pytestmark = pytest.mark.django_db
# -------------------- Test the shift model --------------------
start = time(8, 30)
end = time(16, 30)


def test_create_shift_should_succeed(create_user, def_user):
    """Create shift with correct data"""
    user = create_user(**def_user)
    payload = {"start_of_shift": start, "end_of_shift": end, "owner": user}
    shift = Shift.objects.create(**payload)

    shift.refresh_from_db()
    assert shift.start_of_shift == payload["start_of_shift"]
    assert shift.end_of_shift == payload["end_of_shift"]
    assert shift.owner == payload["owner"]
    assert str(shift) == "08:30:00-16:30:00"


def test_create_shift_without_end_of_shift_should_fail(create_user, def_user):
    """Test create shift without end of shift"""
    user = create_user(**def_user)
    payload = {"start_of_shift": start, "owner": user}
    with pytest.raises(IntegrityError) as error:
        Shift.objects.create(**payload)
    assert "null value in column" in str(error.value)


def test_create_shift_without_start_of_shift_should_fail(create_user, def_user):
    """Test create shift without end of shift"""
    user = create_user(**def_user)
    payload = {"end_of_shift": end, "owner": user}
    with pytest.raises(IntegrityError) as error:
        Shift.objects.create(**payload)
    assert "null value in column" in str(error.value)


def test_create_shift_without_owner_should_fail():
    """Create shift without owner"""
    payload = {"start_of_shift": start, "end_of_shift": end}
    with pytest.raises(IntegrityError) as error:
        Shift.objects.create(**payload)
    assert "null value in column" in str(error.value)


# -------------------- Test workDay  --------------------
start_day = time(7, 55)
end_day = time(16, 31)


def test_create_work_day(create_user, def_user):
    """Create a normal day"""
    user = create_user(**def_user)
    shift = Shift.objects.create(
        start_of_shift=start,
        end_of_shift=end,
        owner=user,
    )
    dat = date(2021, 11, 10)
    payload = {
        "start_of_work": start_day,
        "end_of_work": end_day,
        "comment": "Normal Day",
        "owner": user,
        "shift": shift,
        "date": dat,
    }
    work_day = WorkDay.objects.create(**payload)

    work_day.refresh_from_db()
    assert work_day.day == 0
    assert work_day.start_of_work == payload["start_of_work"]
    assert work_day.end_of_work == payload["end_of_work"]
    assert work_day.comment == payload["comment"]
    assert work_day.owner == payload["owner"]
    assert work_day.shift == payload["shift"]
    assert work_day.date == payload["date"]
    assert str(work_day) == str(dat)


def test_create_work_without_start_end_day_should_succeed(create_user, def_user):
    """Test create day without start end date should succeed"""
    user = create_user(**def_user)
    shift = Shift.objects.create(
        start_of_shift=start,
        end_of_shift=end,
        owner=user,
    )
    dat = date(2021, 11, 10)
    payload = {
        "comment": "Normal Day",
        "owner": user,
        "shift": shift,
        "date": dat,
    }
    work_day = WorkDay.objects.create(**payload)

    work_day.refresh_from_db()
    assert work_day.day == 0
    assert work_day.comment == payload["comment"]
    assert work_day.owner == payload["owner"]
    assert work_day.shift == payload["shift"]
    assert work_day.date == payload["date"]
    assert str(work_day) == str(dat)


def test_create_work_day_dithout_date_should_fail(create_user, def_user):
    """Test create work day withou date should fail"""
    user = create_user(**def_user)
    shift = Shift.objects.create(
        start_of_shift=start,
        end_of_shift=end,
        owner=user,
    )
    dat = date(2021, 11, 10)
    payload = {
        "start_of_work": start_day,
        "end_of_work": end_day,
        "comment": "Normal Day",
        "owner": user,
        "shift": shift,
    }
    with pytest.raises(IntegrityError) as error:
        work_day = WorkDay.objects.create(**payload)
    assert "null value in column" in str(error.value)


def test_create_work_day_without_shift_should_fail(create_user, def_user):
    user = create_user(**def_user)
    dat = date(2021, 11, 10)
    payload = {
        "start_of_work": start_day,
        "end_of_work": end_day,
        "comment": "Normal Day",
        "owner": user,
        "date": dat,
    }
    with pytest.raises(IntegrityError) as error:
        work_day = WorkDay.objects.create(**payload)
    assert "null value in column" in str(error.value)


def test_create_work_day_without_owner_should_fail(create_user, def_user):
    user = create_user(**def_user)
    shift = Shift.objects.create(
        start_of_shift=start,
        end_of_shift=end,
        owner=user,
    )
    dat = date(2021, 11, 10)
    payload = {
        "start_of_work": start_day,
        "end_of_work": end_day,
        "comment": "Normal Day",
        "shift": shift,
        "date": dat,
    }
    with pytest.raises(IntegrityError) as error:
        work_day = WorkDay.objects.create(**payload)
    assert "null value in column" in str(error.value)
