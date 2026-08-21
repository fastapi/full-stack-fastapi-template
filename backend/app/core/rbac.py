from app.models import User

# Role slugs. This is the single source of truth for what roles exist and
# what they grant — see ROLE_PERMISSIONS below.
ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_MEMBER = "member"

ROLE_SLUGS = [ROLE_ADMIN, ROLE_MANAGER, ROLE_MEMBER]

# Permission codes
PERMISSION_USERS_LIST = "users:list"
PERMISSION_USERS_CREATE = "users:create"
PERMISSION_USERS_MANAGE = "users:manage"
PERMISSION_METRICS_VIEW = "metrics:view"
# Catch-all for the remaining admin-only surfaces (item access across all
# owners, transactional-email test/preview endpoints) and the permission
# that blocks self-deletion. Kept as one code rather than four narrow ones
# because only `admin` has ever held any of them.
PERMISSION_SYSTEM_ADMIN = "system:admin"

PERMISSION_CODES = [
    PERMISSION_USERS_LIST,
    PERMISSION_USERS_CREATE,
    PERMISSION_USERS_MANAGE,
    PERMISSION_METRICS_VIEW,
    PERMISSION_SYSTEM_ADMIN,
]

# Permission codes granted to each seeded role. Adding a role is one entry
# here (plus a matching seed-data row); adding a permission is one constant
# above plus wiring it into the roles that should have it here.
ROLE_PERMISSIONS: dict[str, list[str]] = {
    ROLE_ADMIN: PERMISSION_CODES,
    ROLE_MANAGER: [PERMISSION_USERS_LIST, PERMISSION_METRICS_VIEW],
    ROLE_MEMBER: [],
}


def get_permission_codes(user: User) -> list[str]:
    return [permission.code for permission in user.role.permissions]


def has_permission(user: User, code: str) -> bool:
    return code in get_permission_codes(user)
