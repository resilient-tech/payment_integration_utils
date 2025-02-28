import frappe
from frappe import get_system_settings

from payment_integration_utils.payment_integration_utils.utils.auth import AUTH_METHOD


def execute():
    otp_issuer = get_system_settings("otp_issuer_name")

    # update system settings
    frappe.db.set_single_value(
        "System Settings",
        {
            "payment_authentication_method": AUTH_METHOD.OTP_APP.value,
            "payment_otp_issuer_name": otp_issuer,
        },
    )

    # set default values
    frappe.db.set_default("payment_authentication_method", AUTH_METHOD.OTP_APP.value)
    frappe.db.set_default("payment_otp_issuer_name", otp_issuer)
