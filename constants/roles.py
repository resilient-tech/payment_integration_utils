from frappe.permissions import ADMIN_ROLE, ALL_USER_ROLE

from constants.enums import BaseEnum


class ROLE_PROFILE(BaseEnum):
    """
    Common roles for online payments related doctypes.
    """

    BANK_ACC_MANAGER = "Bank Account Manager"
    BANK_ACC_USER = "Bank Account User"

    PAYMENT_AUTHORIZER = "Online Payments Authorizer"


class PERMISSION_LEVEL(BaseEnum):
    """
    Common permission levels for online payments related doctypes.
    """

    ZERO = 0  #   base and default
    SEVEN = 7  # specific to payment and security


class DEFAULT_ROLE_PROFILE(BaseEnum):
    """
    Roles defined in Frappe and ERPNext.
    """

    ALL = ALL_USER_ROLE
    ADMIN = ADMIN_ROLE
    SYSTEM_MANAGER = "System Manager"


PERMISSIONS = {
    "Manager": [
        "select",
        "read",
        "create",
        "write",
        "delete",
        "email",
        "submit",
        "cancel",
        "amend",
    ],
    "User": ["select", "read", "create", "write"],
    "Basic": ["select", "read"],
}


ROLES = [
    ## Bank ##
    {
        "doctype": "Bank",
        "role_name": ROLE_PROFILE.BANK_ACC_MANAGER.value,
        "permlevels": PERMISSION_LEVEL.ZERO.value,
        "permissions": PERMISSIONS["User"],
    },
    {
        "doctype": "Bank",
        "role_name": ROLE_PROFILE.BANK_ACC_USER.value,
        "permlevels": PERMISSION_LEVEL.ZERO.value,
        "permissions": PERMISSIONS["Basic"],
    },
    ## Bank Account ##
    {
        "doctype": "Bank Account",
        "role_name": ROLE_PROFILE.BANK_ACC_MANAGER.value,
        "permlevels": [PERMISSION_LEVEL.ZERO.value, PERMISSION_LEVEL.SEVEN.value],
        "permissions": PERMISSIONS["Manager"],
    },
    {
        "doctype": "Bank Account",
        "role_name": ROLE_PROFILE.BANK_ACC_USER.value,
        "permlevels": PERMISSION_LEVEL.ZERO.value,
        "permissions": PERMISSIONS["User"],
    },
    ## Payment Entry ##
    {
        "doctype": "Payment Entry",
        "role_name": ROLE_PROFILE.PAYMENT_AUTHORIZER.value,
        "permlevels": [PERMISSION_LEVEL.ZERO.value, PERMISSION_LEVEL.SEVEN.value],
        "permissions": PERMISSIONS["Manager"],
    },
]
