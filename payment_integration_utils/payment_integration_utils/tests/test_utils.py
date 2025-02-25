from frappe.tests.utils import FrappeTestCase

from payment_integration_utils.payment_integration_utils.utils import *


class TestUtils(FrappeTestCase):
    def test_start_of_day_epoch(self):
        self.assertEqual(get_start_of_day_epoch("2024-05-30"), 1717007400)

    def test_end_of_day_epoch(self):
        self.assertEqual(get_end_of_day_epoch("2024-05-30"), 1717093799)
