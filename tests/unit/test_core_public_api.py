import unittest

import packages.core as core


class CorePublicApiTests(unittest.TestCase):
    def test_public_api_can_calculate_total(self):
        lines = [core.OrderLine(product_id=1, quantity=2, unit_price=15000)]

        self.assertEqual(core.calculate_order_total(lines), 30000.0)


if __name__ == "__main__":
    unittest.main()
