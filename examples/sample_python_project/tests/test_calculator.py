import pytest

from app.calculator import add, apply_discount, divide


def test_add():
    assert add(1, 2) == 3


def test_divide():
    assert divide(10, 2) == 5


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)


def test_apply_discount():
    assert apply_discount(100, 0.2) == 80
