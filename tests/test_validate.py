import copy

import pytest

from nbp_feed.validate import assert_is_superset, validate_output_schema

VALID_BASIC = {
    "lastSync": "2026-08-05",
    "rates": [
        {"effectiveFrom": "1998-02-26", "rates": {"ref": 24, "lom": 27, "red": 24.5}},
        {"effectiveFrom": "1998-04-23", "rates": {"ref": 23, "lom": 27, "red": 24.5}},
    ],
}

VALID_EXT = {
    "lastSync": "2026-08-05",
    "rates": [
        {
            "effectiveFrom": "1998-02-26",
            "rates": {
                "referenceRate": 24,
                "lombardRate": 27,
                "billRediscountRate": 24.5,
            },
        },
        {
            "effectiveFrom": "2016-01-01",
            "rates": {
                "referenceRate": 1.5,
                "lombardRate": 2.5,
                "billRediscountRate": 1.75,
                "statutoryInterestRate": 5,
                "maxInterestRate": 10,
                "statutoryDefaultInterestRate": 7,
                "maxDefaultInterestRate": 14,
            },
        },
    ],
}


def test_valid_basic_schema_passes():
    validate_output_schema(VALID_BASIC, extended=False)


def test_valid_extended_schema_passes():
    validate_output_schema(VALID_EXT, extended=True)


def test_rejects_unexpected_top_level_key():
    data = copy.deepcopy(VALID_BASIC)
    data["extra"] = "nope"
    with pytest.raises(ValueError):
        validate_output_schema(data, extended=False)


def test_rejects_bad_last_sync_format():
    data = copy.deepcopy(VALID_BASIC)
    data["lastSync"] = "05-08-2026"
    with pytest.raises(ValueError):
        validate_output_schema(data, extended=False)


def test_rejects_non_increasing_dates():
    data = copy.deepcopy(VALID_BASIC)
    data["rates"][1]["effectiveFrom"] = "1998-01-01"
    with pytest.raises(ValueError):
        validate_output_schema(data, extended=False)


def test_rejects_extended_keys_in_basic_schema():
    data = copy.deepcopy(VALID_BASIC)
    data["rates"][0]["rates"]["maxInterestRate"] = 55
    with pytest.raises(ValueError):
        validate_output_schema(data, extended=False)


def test_rejects_missing_required_key():
    data = copy.deepcopy(VALID_EXT)
    del data["rates"][1]["rates"]["maxDefaultInterestRate"]
    with pytest.raises(ValueError):
        validate_output_schema(data, extended=True)


def test_rejects_missing_statutory_interest_rate_on_or_after_law_date():
    data = copy.deepcopy(VALID_EXT)
    del data["rates"][1]["rates"]["statutoryInterestRate"]
    with pytest.raises(ValueError):
        validate_output_schema(data, extended=True)


def test_rejects_statutory_interest_rate_before_law_date():
    data = copy.deepcopy(VALID_EXT)
    data["rates"][0]["rates"]["statutoryInterestRate"] = 27.5
    with pytest.raises(ValueError):
        validate_output_schema(data, extended=True)


def test_accepts_entry_without_statutory_fields_before_law_date():
    data = copy.deepcopy(VALID_EXT)
    del data["rates"][1]
    validate_output_schema(data, extended=True)


def test_superset_passes_when_previous_is_none():
    assert_is_superset(None, VALID_BASIC)


def test_superset_passes_when_new_only_adds_entries():
    previous = copy.deepcopy(VALID_BASIC)
    new = copy.deepcopy(VALID_BASIC)
    new["rates"].append(
        {"effectiveFrom": "1998-05-21", "rates": {"ref": 21.5, "lom": 26, "red": 23.5}}
    )
    assert_is_superset(previous, new)


def test_superset_fails_when_existing_value_changed():
    previous = copy.deepcopy(VALID_BASIC)
    new = copy.deepcopy(VALID_BASIC)
    new["rates"][0]["rates"]["ref"] = 99
    with pytest.raises(ValueError):
        assert_is_superset(previous, new)


def test_superset_fails_when_existing_entry_removed():
    previous = copy.deepcopy(VALID_BASIC)
    new = copy.deepcopy(VALID_BASIC)
    new["rates"].pop()
    with pytest.raises(ValueError):
        assert_is_superset(previous, new)
