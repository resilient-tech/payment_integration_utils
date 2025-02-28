import re
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from payment_integration_utils.payment_integration_utils.utils.validation import (
    validate_ifsc_code,
    validate_payment_mode,
)


class TestUtils(FrappeTestCase):
    @patch("requests.get")
    def test_ifsc_code(self, mock_get):
        IN_VALID_CODE = "SBK0000001"

        # Mock a failed response
        mock_get.return_value.status_code = 404
        self.assertFalse(validate_ifsc_code(IN_VALID_CODE))

        # Mock a successful response
        mock_get.return_value.status_code = 200
        self.assertTrue(validate_ifsc_code("HDFC0000314"))

        # Test throwing an exception
        mock_get.return_value.status_code = 404
        self.assertRaisesRegex(
            frappe.exceptions.ValidationError,
            re.compile(rf"Invalid IFSC Code:.*{IN_VALID_CODE}.*"),
            validate_ifsc_code,
            IN_VALID_CODE,
            throw=True,
        )

    def test_payment_mode(self):
        valid_modes = ["NEFT", "IMPS", "RTGS", "UPI", "Link"]

        for mode in valid_modes:
            self.assertTrue(validate_payment_mode(mode))

        IN_VALID_MODE = "Crypto"
        self.assertFalse(validate_payment_mode(IN_VALID_MODE))

        # Test throwing an exception
        self.assertRaisesRegex(
            frappe.exceptions.ValidationError,
            re.compile(r"Invalid Payment Mode:.* Must be one of:.*"),
            validate_payment_mode,
            IN_VALID_MODE,
            throw=True,
        )
