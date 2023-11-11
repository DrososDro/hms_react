"""
Tests for the email in utils
"""
from unittest.mock import patch, Mock
from django.urls import reverse
from django.views.decorators.debug import HttpRequest
import pytest
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db
request = HttpRequest()


CREATE_USER_URL = reverse("accounts:create_user")
RESET_PASS = reverse("accounts:reset_password_email")
client = APIClient()


def uidb_mock(*args, **kwargs):
    return "uidb64"


@patch("accounts.utils.get_current_site")
@patch("accounts.utils.urlsafe_base64_encode", side_effect=uidb_mock)
@patch("accounts.utils.default_token_generator.make_token")
def test_send_creation_email_should_succeed(
    patched_token,
    patched_uidb,
    patched_site,
    mailoutbox,
    settings,
    def_user,
):
    """Test send creation email with correct data"""
    patched_site.return_value.domain = "xaos"
    patched_token.return_value = "token"
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

    mail_subject = "Activate account for Our Site"
    site = "http://xaos/activate/uidb64/token/"

    assert len(mailoutbox) == 0
    res = client.post(CREATE_USER_URL, def_user)

    assert res.status_code == status.HTTP_201_CREATED
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == mail_subject
    assert site in str(mailoutbox[0].body)


@patch("accounts.utils.get_current_site")
@patch("accounts.utils.urlsafe_base64_encode", side_effect=uidb_mock)
@patch("accounts.utils.default_token_generator.make_token")
def test_send_reset_email_should_succeed(
    patched_token,
    patched_uidb,
    patched_site,
    mailoutbox,
    settings,
    def_user,
    create_user,
):
    """Test send creation email with correct data"""
    patched_site.return_value.domain = "xaos"
    patched_token.return_value = "token"
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    user = create_user(**def_user)

    mail_subject = "Reset password"
    site = "http://xaos/reset/uidb64/token/"

    assert len(mailoutbox) == 0
    res = client.post(RESET_PASS, {"email": user.email})
    assert res.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == mail_subject
    assert site in str(mailoutbox[0].body)
