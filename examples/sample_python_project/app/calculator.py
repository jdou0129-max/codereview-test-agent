from __future__ import annotations


def add(a: float, b: float) -> float:
    return a + b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("b must not be zero")
    return a / b


def apply_discount(price: float, discount: float) -> float:
    """Return final price after discount.

    discount is expected to be between 0 and 1.
    """
    if price < 0:
        raise ValueError("price must not be negative")
    if discount < 0 or discount > 1:
        raise ValueError("discount must be between 0 and 1")
    return round(price * (1 - discount), 2)
