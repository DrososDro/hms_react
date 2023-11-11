from datetime import time
from django.db.utils import IntegrityError
import pytest
from worktime.models import Shift

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
