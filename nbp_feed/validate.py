"""Validation of generated output: structural schema and "no regressions" check."""

from __future__ import annotations

import re

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Statutory/max interest rates are only legally effective from this date
# onward; see README.md "Law" and nbp_feed.build.STATUTORY_EFFECTIVE_DATE.
STATUTORY_EFFECTIVE_DATE = "2016-01-01"

BASIC_RATE_KEYS = {"ref", "lom", "dep", "red", "dys"}
EXT_STATUTORY_KEYS = {
    "statutoryInterestRate",
    "maxInterestRate",
    "statutoryDefaultInterestRate",
    "maxDefaultInterestRate",
}
EXT_RATE_KEYS = {
    "referenceRate",
    "lombardRate",
    "depositRate",
    "billRediscountRate",
    "billDiscountRate",
} | EXT_STATUTORY_KEYS
BASIC_REQUIRED_KEYS = {"ref"}
EXT_REQUIRED_KEYS = {"referenceRate"}


def validate_output_schema(data: dict, *, extended: bool) -> None:
    """Validate the structure of a generated output file.

    Raises ValueError with a descriptive message if the data does not match
    the schema described in README.md.
    """
    if not isinstance(data, dict) or set(data.keys()) != {"lastSync", "rates"}:
        raise ValueError(f"Unexpected top-level keys: {sorted(data.keys())}")

    if not isinstance(data["lastSync"], str) or not DATE_RE.match(data["lastSync"]):
        raise ValueError(f"Invalid lastSync: {data['lastSync']!r}")

    rates = data["rates"]
    if not isinstance(rates, list) or not rates:
        raise ValueError("rates must be a non-empty list")

    allowed_keys = EXT_RATE_KEYS if extended else BASIC_RATE_KEYS
    required_keys = EXT_REQUIRED_KEYS if extended else BASIC_REQUIRED_KEYS

    previous_date = None
    for entry in rates:
        if not isinstance(entry, dict) or set(entry.keys()) != {"effectiveFrom", "rates"}:
            raise ValueError(f"Unexpected entry keys: {sorted(entry.keys())}")

        effective_from = entry["effectiveFrom"]
        if not isinstance(effective_from, str) or not DATE_RE.match(effective_from):
            raise ValueError(f"Invalid effectiveFrom: {effective_from!r}")
        if previous_date is not None and effective_from <= previous_date:
            raise ValueError(f"rates entries are not strictly increasing at {effective_from}")
        previous_date = effective_from

        entry_rates = entry["rates"]
        if not isinstance(entry_rates, dict):
            raise ValueError(f"rates for {effective_from} must be an object")

        keys = set(entry_rates.keys())
        if not keys.issubset(allowed_keys):
            raise ValueError(
                f"Unexpected rate keys for {effective_from}: {sorted(keys - allowed_keys)}"
            )

        entry_required_keys = set(required_keys)
        if extended:
            if effective_from >= STATUTORY_EFFECTIVE_DATE:
                entry_required_keys |= EXT_STATUTORY_KEYS
            elif keys & EXT_STATUTORY_KEYS:
                raise ValueError(
                    f"Statutory rate keys present before {STATUTORY_EFFECTIVE_DATE} "
                    f"for {effective_from}: {sorted(keys & EXT_STATUTORY_KEYS)}"
                )
        if not entry_required_keys.issubset(keys):
            raise ValueError(
                f"Missing required rate keys for {effective_from}: "
                f"{sorted(entry_required_keys - keys)}"
            )

        for key, value in entry_rates.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"Rate {key} for {effective_from} must be a number, got {value!r}")


def assert_is_superset(previous: dict | None, new: dict) -> None:
    """Ensure `new` contains every entry from `previous` unchanged.

    `new` may contain additional entries with dates not present in
    `previous`, but it must not omit or modify any existing entry.
    """
    if previous is None:
        return

    new_by_date = {entry["effectiveFrom"]: entry["rates"] for entry in new["rates"]}
    for entry in previous["rates"]:
        date = entry["effectiveFrom"]
        if date not in new_by_date:
            raise ValueError(f"Entry for {date} present in previous output is missing in new output")
        if new_by_date[date] != entry["rates"]:
            raise ValueError(f"Rate values for {date} changed between previous and new output")
