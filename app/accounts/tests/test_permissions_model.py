from django.core.exceptions import ValidationError
import pytest
from accounts.models import Permissions

pytestmark = pytest.mark.django_db


# -------------------- Test permission Model  --------------------


def test_create_permission_in_choice_list_should_succed():
    """Create a permission that is in choice list should succedd"""
    perm = Permissions.objects.create(name="admin")

    assert str(perm) == "admin"
    perms = Permissions.objects.all()
    assert len(perms) == 1
    assert perms[0].name == "admin"


def test_create_permission_alredy_exists_should_fail():
    """Test create an already existing permission should fail"""
    Permissions.objects.create(name="admin")
    with pytest.raises(ValidationError) as error:
        perm = Permissions.objects.create(name="admin")
    error_message = "Permissions with this Name already exists."
    assert error_message == error.value.messages[0]


def test_create_a_new_permission_not_in_choices_should_fail():
    """Test create a new permission not in choices should fail"""
    with pytest.raises((ValidationError)) as error:
        perm = Permissions.objects.create(name="admin_asd")
    error_message = "Value 'admin_asd' is not a valid choice."

    assert error_message == error.value.messages[0]
