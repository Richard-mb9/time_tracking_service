from typing import List

from fastapi import Depends

from application.exceptions import AccessDeniedError

from .current_user import CurrentUser


class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
        self.resource, self.action = required_permission.split(":")

    async def __call__(self, current_user: CurrentUser) -> None:
        if self._has_permission(current_user.roles):
            return

        raise AccessDeniedError("Access denied")

    def _has_permission(self, user_permissions: List[str]) -> bool:
        for permission in user_permissions:
            if permission == "*":
                return True

            if ":" not in permission:
                continue

            resource, action = permission.split(":")

            if resource == "*":
                return True

            if resource == self.resource and action == "*":
                return True

            if resource == self.resource and action == self.action:
                return True

        return False


def require_role(permission: str):
    return Depends(PermissionChecker(permission))
