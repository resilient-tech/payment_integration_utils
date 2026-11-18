import frappe
from frappe import _
from frappe.twofactor import get_qr_svg_code

from payment_integration_utils.payment_integration_utils.utils.auth import Utils2FA

# the QR code carries the payer's OTP secret, so the website cache must never keep this page
no_cache = 1


def get_context(context):
    totp_uri = frappe.cache.get_value(f"{frappe.form_dict.k}{Utils2FA._OTP_URI}")
    if not totp_uri:
        frappe.throw(_("Page has expired!"), frappe.PermissionError)

    context.qrcode_svg = get_qr_svg_code(totp_uri).decode()
