"""
Test the commands
"""
from datetime import timedelta
from django.contrib.auth import get_user_model
import pytest
from django.db.utils import OperationalError
from django.core.management import call_command

from psycopg.errors import OperationalError as psycopgError

from unittest.mock import patch

pytestmark = pytest.mark.django_db


# -------------------- Test the command wait for db --------------------


@patch("core.management.commands.wait_for_db.Command.check")
def test_wait_for_db_should_success(patched_ceck):
    """Test the command wait for db should succed"""
    patched_ceck.return_value = True
    call_command("wait_for_db")
    patched_ceck.assert_called_once_with(databases=["default"])


@patch("core.management.commands.wait_for_db.Command.check")
@patch("time.sleep")
def test_wait_for_db_5_errors_should_succed_after(
    patched_sleep,
    patched_check,
):
    """
    Check command wait for db with 5 errors,
    the 6th time should succedd
    """
    error_list = [psycopgError] * 3 + [OperationalError] * 2 + [True]
    patched_check.side_effect = error_list

    call_command("wait_for_db")
    assert patched_check.call_count == 6
    assert patched_check.called_with(databases=["default"])


# --------------- Test the command delete_inactive_mails ---------------
@patch("core.management.commands.delete_inactive_mails.timedelta")
def test_delete_inactive_mails_created_1_hour_ago_should_succeed(
    patched_timedelta, create_user, def_user
):
    """Test delete inactive mails that created one hour ago"""
    patched_timedelta.return_value = timedelta(minutes=-60)

    user = create_user(**def_user, is_active=False)
    assert get_user_model().objects.filter(email=user.email).exists() is True
    call_command("delete_inactive_mails")
    assert get_user_model().objects.filter(email=user.email).exists() is False


@patch("core.management.commands.delete_inactive_mails.timedelta")
def test_delete_inactive_mails_created_59_minutes_ago_should_fail(
    patched_timedelta, create_user, def_user
):
    """Test delete inactive mails that created one hour ago"""
    patched_timedelta.return_value = timedelta(minutes=1)

    user = create_user(**def_user, is_active=False)
    assert get_user_model().objects.filter(email=user.email).exists() is True
    call_command("delete_inactive_mails")
    assert get_user_model().objects.filter(email=user.email).exists() is True


@patch("core.management.commands.delete_inactive_mails.timedelta")
def test_delete_inactive_mails_created_1_hour_ago_active_user_should_fail(
    patched_timedelta, create_user, def_user
):
    """
    Test delete inactive mails that created one hour ago with active user
    should fail
    """
    patched_timedelta.return_value = timedelta(minutes=-60)

    user = create_user(**def_user)
    assert get_user_model().objects.filter(email=user.email).exists() is True
    call_command("delete_inactive_mails")
    assert get_user_model().objects.filter(email=user.email).exists() is True
