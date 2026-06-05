"""Reusable order calculations and validation rules."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class OrderLine:
    product_id: int
    quantity: int
    unit_price: float


def calculate_order_total(lines: list[OrderLine]) -> float:
    """Return rounded total amount for order lines."""
    validate_order_lines(lines)
    total = sum(
        Decimal(str(line.unit_price)) * Decimal(line.quantity)
        for line in lines
    )
    return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def validate_order_lines(lines: list[OrderLine]) -> None:
    """Validate order lines before saving an order."""
    if not lines:
        raise ValueError("order must contain at least one line")

    for line in lines:
        if line.product_id <= 0:
            raise ValueError("product_id must be positive")
        if line.quantity <= 0:
            raise ValueError("quantity must be positive")
        if line.unit_price < 0:
            raise ValueError("unit_price must be non-negative")


def count_product_in_lines(lines: list[OrderLine], product_id: int) -> int:
    """Return total quantity of a product already present in order lines."""
    return sum(line.quantity for line in lines if line.product_id == product_id)
