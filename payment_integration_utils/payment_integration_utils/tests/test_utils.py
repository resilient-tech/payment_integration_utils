from frappe.tests.utils import FrappeTestCase

from payment_integration_utils.payment_integration_utils.utils import *


class TestUtils(FrappeTestCase):
    def test_conversion(self):
        # (100, 10000) => 100 Rupees = 10000 Paisa
        data = [
            (100, 10000),
            (100.0, 10000),
            (100.5, 10050),
            (0.5, 50),
            (79.9, 7990),
            (0, 0),
        ]
        for rupees, paisa in data:
            self.assertEqual(rupees_to_paisa(rupees), paisa)
            self.assertEqual(paisa_to_rupees(paisa), rupees)

    def test_to_hyphenated(self):
        self.assertEqual(to_hyphenated("Hello World"), "Hello-World")
        self.assertEqual(to_hyphenated("Hello World!"), "Hello-World-")
