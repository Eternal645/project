import unittest

from packages.core import OrderLine, calculate_order_total, count_product_in_lines


class OrderLogicTests(unittest.TestCase):
    def test_calculate_order_total_sums_lines_and_rounds_money(self):
        lines = [
            OrderLine(product_id=1, quantity=2, unit_price=10.10),
            OrderLine(product_id=2, quantity=3, unit_price=5.555),
        ]

        self.assertEqual(calculate_order_total(lines), 36.87)

    def test_calculate_order_total_rejects_empty_order(self):
        with self.assertRaisesRegex(ValueError, "at least one line"):
            calculate_order_total([])

    def test_calculate_order_total_rejects_invalid_quantity(self):
        lines = [OrderLine(product_id=1, quantity=0, unit_price=10)]

        with self.assertRaisesRegex(ValueError, "quantity"):
            calculate_order_total(lines)

    def test_calculate_order_total_rejects_negative_price(self):
        lines = [OrderLine(product_id=1, quantity=1, unit_price=-1)]

        with self.assertRaisesRegex(ValueError, "unit_price"):
            calculate_order_total(lines)

    def test_count_product_in_lines_counts_duplicate_product_quantities(self):
        lines = [
            OrderLine(product_id=1, quantity=2, unit_price=100),
            OrderLine(product_id=2, quantity=1, unit_price=200),
            OrderLine(product_id=1, quantity=3, unit_price=100),
        ]

        self.assertEqual(count_product_in_lines(lines, 1), 5)


if __name__ == "__main__":
    unittest.main()
