from decimal import Decimal

from nbp_feed.serialize import to_json


def test_minified_no_whitespace():
    assert to_json({"a": Decimal("1"), "b": [Decimal("2"), Decimal("3")]}) == '{"a":1,"b":[2,3]}'


def test_whole_decimal_has_no_decimal_point():
    assert to_json(Decimal("24.00")) == "24"


def test_fractional_decimal_keeps_minimal_digits():
    assert to_json(Decimal("21.50")) == "21.5"


def test_string_is_quoted_and_escaped():
    assert to_json("a\"b") == '"a\\"b"'


def test_nested_structure_matches_expected_output():
    data = {
        "lastSync": "2026-08-05",
        "rates": [
            {
                "effectiveFrom": "1998-02-26",
                "rates": {"ref": Decimal("24.00"), "lom": Decimal("27.00"), "red": Decimal("24.50")},
            }
        ],
    }

    expected = (
        '{"lastSync":"2026-08-05",'
        '"rates":[{"effectiveFrom":"1998-02-26",'
        '"rates":{"ref":24,"lom":27,"red":24.5}}]}'
    )
    assert to_json(data) == expected
