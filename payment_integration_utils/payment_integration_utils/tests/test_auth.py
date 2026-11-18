import re
from unittest.mock import patch
from urllib.parse import parse_qsl, urlparse

import frappe
import pyotp
from frappe.tests.utils import FrappeTestCase
from frappe.twofactor import clear_default, get_qr_svg_code
from frappe.utils import set_request
from frappe.website.serve import get_response_content

from payment_integration_utils.payment_integration_utils.utils.auth import (
    Trigger2FA,
    Utils2FA,
)


class TestAuth(FrappeTestCase):
    def test_emailed_link_shows_otp_app_qr_code(self):
        user = "payer@example.com"
        if not frappe.db.exists("User", user):
            frappe.get_doc(
                {
                    "doctype": "User",
                    "email": user,
                    "first_name": "Payer",
                    "send_welcome_email": 0,
                }
            ).insert()
        clear_default(Utils2FA.get_otp_login_key(user))

        with self.set_user(user), patch("frappe.sendmail") as sendmail:
            Trigger2FA(["PE-TEST-0001"]).send_otp()

        message = sendmail.call_args.kwargs["message"]
        link = urlparse(re.search(r"href='(.+?)'", message)[1])
        set_request(method="GET", path=link.path, query_string=link.query)

        with (
            self.set_user("Guest"),
            patch.dict(frappe.local.form_dict, parse_qsl(link.query)),
        ):
            html = get_response_content(link.path)

        totp_uri = pyotp.TOTP(Utils2FA.get_otp_secret(user)).provisioning_uri(
            name=user, issuer_name=Utils2FA.get_otp_issuer()
        )
        self.assertIn(get_qr_svg_code(totp_uri).decode(), html)
