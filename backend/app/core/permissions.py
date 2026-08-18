# Central RBAC permission definitions and role-to-permission mapping.
from enum import Enum

from app.models import User, UserRole


class Permission(str, Enum):
    USERS_LIST = "users:list"
    USERS_CREATE = "users:create"
    USERS_UPDATE_ANY = "users:update_any"
    USERS_DELETE = "users:delete"
    METRICS_VIEW = "metrics:view"
    PROFILE_UPDATE_SELF = "profile:update_self"
    SETTINGS_GLOBAL = "settings:global"


ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.ADMIN: frozenset(Permission),
    UserRole.MANAGER: frozenset(
        {
            Permission.USERS_LIST,
            Permission.METRICS_VIEW,
            Permission.PROFILE_UPDATE_SELF,
        }
    ),
    UserRole.MEMBER: frozenset({Permission.PROFILE_UPDATE_SELF}),
}


def user_has_permission(user: User, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(user.role, frozenset())
