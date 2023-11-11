"""Test the user model"""
import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from accounts.models import Permissions


pytestmark = pytest.mark.django_db


# -------------------- Test user Model--------------------
def test_create_user_with_email_should_succed(def_user) -> None:
    """Create a user and test if saved in db"""
    user = get_user_model().objects.create_user(**def_user)
    all_user = get_user_model().objects.all()
    assert len(all_user) == 1


@pytest.mark.parametrize(
    "given,expected",
    [
        ("TesT@ExaMpLe.com", "TesT@example.com"),
        ("test1@ExamPle.CoM", "test1@example.com"),
    ],
)
def test_user_normalize_email_should_succed(
    def_user,
    given,
    expected,
) -> None:
    """create user and test normalize email"""
    user = get_user_model().objects.create_user(
        email=given,
        password=def_user.get("password"),
    )
    assert user.email == expected


def test_str_should_return_email(create_user, def_user) -> None:
    """test str method should return mail"""
    user = create_user(**def_user)

    assert str(user) == def_user.get("email")


def test_user_create_without_mail_should_fail(create_user) -> None:
    """Creating a user without email"""
    with pytest.raises(ValueError) as e:
        create_user(
            email=None,
            password="pass",
        )

    assert str(e.value) == "User must have an email address"


def test_create_superuser_with_email_successfull(create_superuser):
    """
    test create_superuser function with
    email,  password,
    to return the user and save the
    model to the db
    """

    create_superuser
    user = get_user_model().objects.get(email="xaos@xaos.com")

    assert user.email == "xaos@xaos.com"
    assert user.check_password("passWord")
    assert user.is_active is True
    assert user.is_admin is True
    assert user.is_superadmin is True
    assert user.is_staff is True


def test_has_perm_should_return_is_admin_should_succeed(
    def_user,
    create_user,
) -> None:
    """Test the has_perm method to return is admin"""
    user = create_user(**def_user)
    assert user.has_perm(user) is False
    user.is_admin = True
    user.save()
    assert user.has_perm(user) is True


def test_unique_of_email_should_fail(def_user, create_user) -> None:
    """Test the unique email"""
    user = create_user(**def_user)

    with pytest.raises(IntegrityError) as e:
        fail_user = create_user(**def_user)
    assert isinstance(e.value, IntegrityError)
    assert "duplicate key value violates unique constraint" in str(e.value)


def test_has_module_perm_should_return_is_admin_should_succeed(
    def_user,
    create_user,
) -> None:
    """Test user if has_module_perms method to return is admin"""
    user = create_user(**def_user)
    assert user.has_module_perms(user) is False
    user.is_admin = True
    user.save()
    assert user.has_module_perms(user) is True


def test_user_add_permissions_should_succed(create_superuser):
    """Test add permissions to one user should succedd"""
    admin = create_superuser
    created_perm = Permissions.objects.create(name="admin")
    assert admin.permissions.count() == 0
    admin.permissions.add(created_perm)
    assert admin.permissions.count() == 1
    perm = admin.permissions.all()[0]
    assert perm == created_perm


def test_user_permissions_should_return_a_set_of_permissions(create_superuser):
    """Test add permissions to one user should succedd"""
    admin = create_superuser
    admin_perm = Permissions.objects.create(name="admin")
    customer_perm = Permissions.objects.create(name="customer")
    admin.permissions.add(admin_perm)
    admin.permissions.add(customer_perm)

    assert "admin" in admin.user_perms
    assert "customer" in admin.user_perms
