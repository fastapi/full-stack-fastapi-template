from enum import Enum

MAX_USERS_PER_PAGE = 100


class UserType(str, Enum):
    NORMAL = "normal"  # self-registered via the signup page
    COMPANY = "company"  # created by an admin for a company account
    ADMIN = "admin"  # platform administrator
