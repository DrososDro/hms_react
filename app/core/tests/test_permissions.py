from unittest.mock import patch, Mock
from core.perm_class import UserPermissions


@patch("core.tests.test_permissions.UserPermissions")
def test_User_permisions_called_with__call__(patched_permissions):
    """Test if the UserPermissions called with perm_list"""
    permission = UserPermissions(perm_list=["admin"])

    patched_permissions.assert_called_once_with(perm_list=["admin"])


def test_User_permisions_instance_with_perm_list():
    """Test if the UserPermissions called __call__"""
    permission = UserPermissions(perm_list=["admin"])
    perm = permission()
    assert perm is permission


def test_User_permisions_has_permissions_should_succeed():
    """test user_permissions has permission should succeed"""

    mock_request = Mock()
    mock_request.user = Mock()
    mock_request.user.is_authenticated = True
    mock_request.user.user_perms = {"admin"}
    permission = UserPermissions(perm_list=["admin"])
    perms = permission().has_permission(mock_request, None)
    assert perms is True


def test_User_permisions_has_not_permissions_should_fail():
    """test user_permissions has permission should fail"""

    mock_request = Mock()
    mock_request.user = Mock()
    mock_request.user.is_authenticated = True
    mock_request.user.user_perms = {"admin"}
    permission = UserPermissions(perm_list=["customer"])
    perms = permission().has_permission(mock_request, None)
    assert perms is False


def test_User_permisions_is_unauthenticated():
    """test user_permissions hasn't permission unauthenticated user"""

    mock_request = Mock()
    mock_request.user = Mock()
    mock_request.user.is_authenticated = False
    permission = UserPermissions(perm_list=["customer"])
    perms = permission().has_permission(mock_request, None)
    assert perms is False
