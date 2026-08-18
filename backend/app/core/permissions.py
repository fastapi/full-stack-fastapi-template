# Central RBAC permission definitions and role-to-permission mapping.
import uuid
from enum import StrEnum

from app.models import User, UserRole


class Permission(StrEnum):
    USERS_LIST = "users:list"
    USERS_CREATE = "users:create"
    USERS_UPDATE_ANY = "users:update_any"
    USERS_DELETE = "users:delete"
    METRICS_VIEW = "metrics:view"
    PROFILE_UPDATE_SELF = "profile:update_self"
    SETTINGS_GLOBAL = "settings:global"
    ITEMS_LIST_ANY = "items:list_any"
    ITEMS_MANAGE_ANY = "items:manage_any"


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


def user_is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


def user_can_manage_item(user: User, owner_id: uuid.UUID) -> bool:
    if user_has_permission(user, Permission.ITEMS_MANAGE_ANY):
        return True
    return owner_id == user.id
