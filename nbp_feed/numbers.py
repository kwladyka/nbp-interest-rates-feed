"""Decimal parsing/formatting helpers for rate values."""

from decimal import ROUND_HALF_UP, Decimal


def parse_polish_decimal(value: str) -> Decimal:
    """Parse a Polish-formatted decimal ("21,50") into a Decimal."""
    return Decimal(value.replace(",", "."))


def format_number(value: Decimal) -> str:
    """Render a Decimal as the shortest exact decimal string.

    Whole numbers are rendered without a decimal point (e.g. "55" not
    "55.00") and trailing zeros are stripped, matching the output format
    shown in README.md.
    """
    quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if quantized == quantized.to_integral_value():
        return str(int(quantized))
    text = format(quantized, "f")
    return text.rstrip("0").rstrip(".")
