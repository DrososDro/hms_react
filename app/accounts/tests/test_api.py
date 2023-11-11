import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.request import Request

pytestmark = pytest.mark.django_db


CREATE_USER_URL = reverse("accounts:create_user")
TOKEN = reverse("accounts:token")
REFRESH_TOKEN = reverse("accounts:token_refresh")
MY_ACCOUNT = reverse("accounts:my_account")
RESET_PASS = reverse("accounts:reset_password_email")


def rev_activate(uidb, token):
    return reverse("accounts:activate", args=[uidb, token])


def rev_resset_pass(uidb, token):
    return reverse("accounts:reset_password_submit", args=[uidb, token])


client = APIClient()


# -------------------- Test create User from Api --------------------
def test_create_user_from_api_should_succeed(def_user):
    """Test Create a user from the api and
    check if he is Inactive"""

    res = client.post(CREATE_USER_URL, def_user)

    assert res.status_code == status.HTTP_201_CREATED

    user = get_user_model().objects.get(email=def_user["email"])
    assert user.check_password(def_user["password"]) is True
    assert user.is_active is False


def test_create_user_with_the_same_email_should_fail(create_user, def_user):
    """Test create a user with the same email should fail"""

    create_user(**def_user)
    res = client.post(CREATE_USER_URL, def_user)

    assert res.status_code == status.HTTP_400_BAD_REQUEST

    error_message = "user with this email address already exists."
    assert error_message == str(res.data["email"][0])


def test_create_user_with_len_pass_9_should_succed(def_user):
    """Test create user with len pass of 9 should succed"""
    def_user["password"] = "test123xp"

    res = client.post(CREATE_USER_URL, def_user)

    assert res.status_code == status.HTTP_201_CREATED
    assert res.data["email"] == def_user["email"]


def test_create_user_with_len_pass_7_should_fail(def_user):
    """Test create user with len pass of 7 should fail"""
    def_user["password"] = "test123"

    res = client.post(CREATE_USER_URL, def_user)

    assert res.status_code == status.HTTP_400_BAD_REQUEST


@patch("accounts.serializers.send_activation_mail")
def test_create_user_send_activation_email_should_call(
    patched_activation_mail, def_user
):
    """Test create user and func send activation email sould called once"""
    patched_activation_mail.return_value = True

    res = client.post(CREATE_USER_URL, def_user)

    assert res.status_code == status.HTTP_201_CREATED

    assert patched_activation_mail.call_count == 1


@patch("accounts.serializers.send_activation_mail")
def test_create_user_fail_send_email_shouldnt_call(
    patched_activation_mail,
    def_user,
    create_user,
):
    """Test create existing user should fail and email dont send"""
    create_user(**def_user)
    res = client.post(CREATE_USER_URL, def_user)

    assert res.status_code == status.HTTP_400_BAD_REQUEST
    patched_activation_mail.return_value = False

    assert patched_activation_mail.call_count == 0


# -------------------- Test activate method --------------------


def test_activate_API_call_should_succeed(
    settings,
    def_user,
    mailoutbox,
):
    """Test activate api with correct data"""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    res = client.post(CREATE_USER_URL, def_user)

    # test if the user created successfully
    assert res.status_code == status.HTTP_201_CREATED
    assert len(mailoutbox) == 1

    # take the mailbox message and convert it to activate
    mail_body = mailoutbox[0].body.split("\n")
    activation_url = [i for i in mail_body if "http://" in i][0]
    *_, uidb, token, _ = activation_url.split("/")

    # make a request to activate api
    ACTIVATE = rev_activate(uidb, token)
    res = client.post(ACTIVATE)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == "Activations Success"


def test_activate_failed():
    """Test raise value error and fail the activation"""

    ACTIVATE = rev_activate("somethin", "token")
    res = client.post(ACTIVATE)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == "Activation Fail"


# -------------------- Test reset_passowd method --------------------


def test_reset_password_submit_API_call_should_succeed(
    settings,
    def_user,
    mailoutbox,
    create_user,
):
    """Test reset passwork submit api with correct data"""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    user = create_user(**def_user)

    res = client.post(RESET_PASS, {"email": def_user["email"]})

    # test if the user created successfully
    assert res.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 1

    # take the mailbox message and convert it to activate
    mail_body = mailoutbox[0].body.split("\n")
    reset_url = [i for i in mail_body if "http://" in i][0]
    *_, uidb, token, _ = reset_url.split("/")

    # make a request to activate api
    RESET = rev_resset_pass(uidb, token)
    res = client.post(RESET, {"password": "testpasDrosos"})
    assert res.status_code == status.HTTP_200_OK
    assert res.data == "Password reset Successfully"
    user.refresh_from_db()
    assert user.check_password("testpasDrosos") is True


def test_reset_password_submit_failed():
    """Test raise value error and fail the reset password submit"""

    RESET = rev_resset_pass("somethin", "token")
    res = client.post(RESET)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == "Passowrd reset Fail"


# -------------------- Test JWT Token --------------------


def test_jwt_create_token_with_is_active_user_should_succeed(
    create_user,
    def_user,
):
    """Test jwt to create token with active user  and use it shoudl succedd"""

    create_user(**def_user)

    res = client.post(TOKEN, def_user)

    assert res.status_code == status.HTTP_200_OK
    assert "access" in res.data
    assert "refresh" in res.data


def test_jwt_create_token_with_inactive_user_should_fail(
    create_user,
    def_user,
):
    """Tesg jwt with inactive user should fail"""

    create_user(**def_user, is_active=False)

    res = client.post(TOKEN, def_user)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert "access" not in res.data
    assert "refresh" not in res.data


def test_jwt_create_token_with_wrong_credentials_should_fail(
    create_user,
    def_user,
):
    """Test jwt create token with wrong credentials"""
    create_user(**def_user, is_active=False)
    def_user["password"] = "123"

    res = client.post(TOKEN, def_user)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert "access" not in res.data
    assert "refresh" not in res.data


def test_jwt_refresh_token_with_correct_credentials_should_succeed(
    def_user,
    create_user,
):
    """Test refresh token with correct credentials should succeed"""
    create_user(**def_user)

    res = client.post(TOKEN, def_user)
    refresh = res.data["refresh"]
    payload = {"refresh": refresh}

    res = client.post(REFRESH_TOKEN, payload)
    assert res.status_code == status.HTTP_200_OK
    assert "access" in res.data
    assert "refresh" not in res.data


def test_reset_passowrd_link_wrong_email_should_fail():
    """Test the reset pass api with wrong email"""
    res = client.post(RESET_PASS, {"email": "something@dontexist.com"})
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == "Give a Valid email"


def test_reset_email_with_empty_mail_should_fail():
    """Test reset email with empty email"""
    res = client.post(RESET_PASS, {"email": ""})
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == "Give a Valid email"


@patch("accounts.views.send_reset_mail")
def test_reset_email_with_corect_mail_should_succeed(
    patched_send_mail,
    def_user,
    create_user,
):
    """Test reset mail with correct mail"""
    user = create_user(**def_user)
    res = client.post(RESET_PASS, {"email": def_user["email"]})
    assert res.status_code == status.HTTP_200_OK
    assert res.data == "Reset email Sendt"
    assert patched_send_mail.call_count == 1


# -------------------- Test my account --------------------

#  ---------- Unauthorized tests  ----------


def test_my_account_unauthorized_should_fail():
    """Test get my-account with an Unauthorized user should fail"""

    res = client.get(MY_ACCOUNT)
    error_message = "Authentication credentials were not provided."
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert str(res.data["detail"]) == error_message


def test_unauthenticated_put_mathod_should_fail():
    """Test my-account put method with unauth user should fail"""
    res = client.put(MY_ACCOUNT, {"email": "something"})
    error_message = "Authentication credentials were not provided."
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert str(res.data["detail"]) == error_message


def test_unauthenticated_patch_mathod_should_fail():
    """Test my-account patch method with unauth user should fail"""
    res = client.patch(MY_ACCOUNT, {"email": "something"})
    error_message = "Authentication credentials were not provided."
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert str(res.data["detail"]) == error_message


#  ---------- Authorized tests  ----------


def test_get_my_account_should_succed(
    auth_api_client,
    def_user,
):
    """get user data for auth user"""

    res = auth_api_client.get(MY_ACCOUNT)
    assert res.status_code == status.HTTP_200_OK
    assert res.data["email"] == def_user["email"]


def test_put_method_change_email_password_should_succeed(
    auth_api_client,
):
    """Test put method update"""
    payload = {"email": "test@test.com", "password": "12345sfasgdas"}

    res = auth_api_client.put(MY_ACCOUNT, payload)

    assert res.status_code == status.HTTP_200_OK
    user = get_user_model().objects.get(id=res.data["id"])

    assert user.email == payload["email"]
    assert user.check_password(payload["password"]) is True
    assert res.data["email"] == payload["email"]
    assert "password" not in res.data


def test_patch_method_change_email_should_succeed(
    auth_api_client,
):
    """Test patch methon update email"""
    payload = {"email": "test@test.com"}

    res = auth_api_client.patch(MY_ACCOUNT, payload)

    assert res.status_code == status.HTTP_200_OK
    user = get_user_model().objects.get(id=res.data["id"])

    assert user.email == payload["email"]
    assert res.data["email"] == payload["email"]
    assert "password" not in res.data


def test_patch_method_change_password_should_succeed(
    auth_api_client,
):
    """Test patch method update pass should succeed"""
    payload = {"password": "testpassOk"}
    res = auth_api_client.patch(MY_ACCOUNT, payload)

    assert res.status_code == status.HTTP_200_OK
    user = get_user_model().objects.get(id=res.data["id"])
    assert user.check_password(payload["password"]) is True
