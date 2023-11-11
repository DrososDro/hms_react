import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


# -------------------- Test admin panel --------------------
def test_users_list(client, create_superuser):
    """Test that users are listed on page."""
    admin = create_superuser
    client.force_login(admin)

    url = reverse("admin:accounts_user_changelist")
    res = client.get(url)

    assert admin.email in res.content.decode("utf-8")


def test_edit_user_page(client, create_superuser):
    """Test that edit user page works."""
    admin = create_superuser
    client.force_login(admin)
    url = reverse("admin:accounts_user_change", args=[admin.id])
    res = client.get(url)

    assert res.status_code == 200


def test_create_user_page(client, create_superuser):
    """Test the create user page works."""
    admin = create_superuser
    client.force_login(admin)
    url = reverse("admin:accounts_user_add")
    res = client.get(url)
    assert res.status_code == 200


def test_users_list_for_permissions(
    client,
    create_superuser,
    create_user,
    def_user,
):
    """
    Test that users are listed on page
    with email, is_active,created_at
    """
    url = reverse("admin:accounts_user_changelist")
    admin = create_superuser
    user = create_user(**def_user)
    client.force_login(admin)
    res = client.get(url)

    content = res.content.decode("utf-8")
    assert user.email in content
    assert "is_active" in content
    assert "is_admin" not in content
    assert "is_superadmin" not in content
    assert "created_at" in content
    assert "permissions" in content
