from datetime import timedelta
import pytest
from unittest.mock import patch
from accounts.tasks import delete_inactivate_emails


@patch("accounts.tasks.call_command")
def test_delete_inactive_mail_should_succeed(patched_command):
    assert patched_command.call_count == 0
    delete_inactivate_emails()
    assert patched_command.call_count == 2
    patched_command.assert_any_call("wait_for_db")
    patched_command.assert_called_with("delete_inactive_mails")


@pytest.mark.django_db
@patch("accounts.signals.delete_inactivate_emails.apply_async")
def test_delete_inactive_mail_signal_call(
    patched_delete_mails,
    def_user,
    create_user,
):
    """Test if the signal call the comand to delete emails"""
    patched_delete_mails.return_value = True
    user = create_user(**def_user)

    patched_delete_mails.assert_called_once_with(
        eta=user.created_at + timedelta(minutes=61),
    )
