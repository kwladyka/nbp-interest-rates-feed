from decimal import Decimal

from nbp_feed.build import build_basic, build_extended
from nbp_feed.parse import RateEntry

EARLY_ENTRY = RateEntry(
    effective_from="1998-02-26",
    rates={"ref": Decimal("24"), "lom": Decimal("27"), "red": Decimal("24.5")},
)

MODERN_ENTRY = RateEntry(
    effective_from="2010-01-01",
    rates={
        "ref": Decimal("3.5"),
        "lom": Decimal("5"),
        "dep": Decimal("2"),
        "red": Decimal("3.75"),
        "dys": Decimal("4"),
    },
)

PRE_LAW_ENTRY = RateEntry(
    effective_from="2015-03-05",
    rates={
        "ref": Decimal("1.5"),
        "lom": Decimal("2.5"),
        "dep": Decimal("0.5"),
        "red": Decimal("1.75"),
    },
)

POST_LAW_ENTRY = RateEntry(
    effective_from="2020-03-18",
    rates={
        "ref": Decimal("1"),
        "lom": Decimal("1.5"),
        "dep": Decimal("0.5"),
        "red": Decimal("1.05"),
        "dys": Decimal("1.1"),
    },
)

EXACT_LAW_DATE_ENTRY = RateEntry(
    effective_from="2016-01-01",
    rates={"ref": Decimal("1.5"), "lom": Decimal("2.5"), "red": Decimal("1.75")},
)


def test_build_basic_keeps_source_field_names_and_order():
    result = build_basic([EARLY_ENTRY], "2026-08-05")

    assert result == {
        "lastSync": "2026-08-05",
        "rates": [
            {
                "effectiveFrom": "1998-02-26",
                "rates": {
                    "ref": Decimal("24"),
                    "lom": Decimal("27"),
                    "red": Decimal("24.5"),
                },
            }
        ],
    }


def test_build_basic_does_not_add_synthetic_entry():
    # The 2016-01-01 synthetic entry is only added to the extended output.
    result = build_basic([PRE_LAW_ENTRY], "2026-08-05")

    assert [entry["effectiveFrom"] for entry in result["rates"]] == ["2015-03-05"]


def test_build_extended_renames_fields_and_omits_statutory_before_law_date():
    result = build_extended([EARLY_ENTRY], "2026-08-05")

    rates = result["rates"][0]["rates"]
    assert rates["referenceRate"] == Decimal("24")
    assert rates["lombardRate"] == Decimal("27")
    assert rates["billRediscountRate"] == Decimal("24.5")
    assert "depositRate" not in rates
    assert "billDiscountRate" not in rates
    # 1998-02-26 is before the law's 2016-01-01 effective date, so no
    # statutory/max fields should be computed.
    assert "statutoryInterestRate" not in rates
    assert "maxInterestRate" not in rates
    assert "statutoryDefaultInterestRate" not in rates
    assert "maxDefaultInterestRate" not in rates


def test_build_extended_omits_statutory_for_modern_entry_before_law_date():
    result = build_extended([MODERN_ENTRY], "2026-08-05")

    rates = result["rates"][0]["rates"]
    assert rates == {
        "referenceRate": Decimal("3.5"),
        "lombardRate": Decimal("5"),
        "depositRate": Decimal("2"),
        "billRediscountRate": Decimal("3.75"),
        "billDiscountRate": Decimal("4"),
    }


def test_build_extended_computes_statutory_on_exact_law_date():
    result = build_extended([EXACT_LAW_DATE_ENTRY], "2026-08-05")

    rates = result["rates"][0]["rates"]
    # README example: ref=1.5 -> statutory_interest=5, max_interest=10,
    # statutory_default=7, max_default=14
    assert rates["statutoryInterestRate"] == Decimal("5")
    assert rates["maxInterestRate"] == Decimal("10.00")
    assert rates["statutoryDefaultInterestRate"] == Decimal("7")
    assert rates["maxDefaultInterestRate"] == Decimal("14.00")


def test_build_extended_computes_statutory_after_law_date():
    result = build_extended([PRE_LAW_ENTRY, POST_LAW_ENTRY], "2026-08-05")

    post_entry = next(e for e in result["rates"] if e["effectiveFrom"] == "2020-03-18")
    # README example: ref=1 -> statutory_interest=4.5, max_interest=9,
    # statutory_default=6.5, max_default=13
    assert post_entry["rates"]["statutoryInterestRate"] == Decimal("4.5")
    assert post_entry["rates"]["maxInterestRate"] == Decimal("9.00")
    assert post_entry["rates"]["statutoryDefaultInterestRate"] == Decimal("6.5")
    assert post_entry["rates"]["maxDefaultInterestRate"] == Decimal("13.00")


def test_build_extended_inserts_synthetic_entry_for_law_date():
    result = build_extended([PRE_LAW_ENTRY, POST_LAW_ENTRY], "2026-08-05")

    dates = [entry["effectiveFrom"] for entry in result["rates"]]
    assert dates == ["2015-03-05", "2016-01-01", "2020-03-18"]

    synthetic = next(e for e in result["rates"] if e["effectiveFrom"] == "2016-01-01")
    # Carries forward the rate in effect on 2016-01-01 (from 2015-03-05).
    assert synthetic["rates"]["referenceRate"] == Decimal("1.5")
    assert synthetic["rates"]["lombardRate"] == Decimal("2.5")
    assert synthetic["rates"]["billRediscountRate"] == Decimal("1.75")
    # README example: ref=1.5 -> statutory_interest=5, max_interest=10,
    # statutory_default=7, max_default=14
    assert synthetic["rates"]["statutoryInterestRate"] == Decimal("5")
    assert synthetic["rates"]["maxInterestRate"] == Decimal("10.00")
    assert synthetic["rates"]["statutoryDefaultInterestRate"] == Decimal("7")
    assert synthetic["rates"]["maxDefaultInterestRate"] == Decimal("14.00")


def test_build_extended_does_not_duplicate_existing_entry_on_law_date():
    result = build_extended([EXACT_LAW_DATE_ENTRY], "2026-08-05")

    dates = [entry["effectiveFrom"] for entry in result["rates"]]
    assert dates == ["2016-01-01"]


def test_build_extended_skips_synthetic_entry_when_no_prior_data():
    # If all known entries are already on/after the law date, there is no
    # earlier rate to carry forward, so no synthetic entry is added.
    result = build_extended([POST_LAW_ENTRY], "2026-08-05")

    dates = [entry["effectiveFrom"] for entry in result["rates"]]
    assert dates == ["2020-03-18"]
