from decimal import Decimal

from nbp_feed.numbers import format_number, parse_polish_decimal


def test_parse_polish_decimal():
    assert parse_polish_decimal("21,50") == Decimal("21.50")
    assert parse_polish_decimal("4,55") == Decimal("4.55")


def test_format_whole_number_has_no_decimal_point():
    assert format_number(Decimal("24.00")) == "24"
    assert format_number(Decimal("55.00")) == "55"


def test_format_strips_trailing_zeros():
    assert format_number(Decimal("21.50")) == "21.5"
    assert format_number(Decimal("4.55")) == "4.55"


def test_format_rounds_half_up_to_two_decimals():
    assert format_number(Decimal("2.005")) == "2.01"
