from rest_framework.permissions import BasePermission


class UserPermissions(BasePermission):
    def __init__(self, perm_list: list = []) -> None:
        self.perm_list = perm_list

    def __call__(self):
        return self

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            for i in request.user.user_perms:
                if i in self.perm_list:
                    return True

                return False

        return False
