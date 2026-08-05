"""Minified JSON serialization with exact control over number formatting.

The stdlib json module renders whole floats as "55.0" and cannot render a
Decimal directly, so this module walks the structure itself and only
delegates to json.dumps for string escaping.
"""

import json
from decimal import Decimal

from nbp_feed.numbers import format_number


def to_json(value) -> str:
    if isinstance(value, dict):
        items = ",".join(f"{to_json(key)}:{to_json(val)}" for key, val in value.items())
        return "{" + items + "}"
    if isinstance(value, list):
        return "[" + ",".join(to_json(item) for item in value) + "]"
    if isinstance(value, Decimal):
        return format_number(value)
    if isinstance(value, str):
        return json.dumps(value)
    raise TypeError(f"Unsupported type for JSON serialization: {type(value)!r}")
