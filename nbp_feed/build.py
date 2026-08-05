"""Building the two JSON output structures from parsed rate entries."""

from decimal import Decimal

from nbp_feed.parse import RATE_IDS, RateEntry

STATUTORY_MARGIN = Decimal("3.5")
DEFAULT_MARGIN = Decimal("5.5")

# Statutory/max interest rates are only legally effective from this date
# onward (Art. 57 of the 2015 amendment act); see README.md "Law".
STATUTORY_EFFECTIVE_DATE = "2016-01-01"

EXT_KEY_NAMES = {
    "ref": "referenceRate",
    "lom": "lombardRate",
    "dep": "depositRate",
    "red": "billRediscountRate",
    "dys": "billDiscountRate",
}


def _with_statutory_base_entry(entries: list[RateEntry]) -> list[RateEntry]:
    """Ensure an entry exists at STATUTORY_EFFECTIVE_DATE.

    The NBP archive has no entry on that exact date (no rate change
    occurred then), but the statutory calculation is legally effective from
    that date, so a synthetic entry carrying forward the rate already in
    effect must be added.
    """
    if any(entry.effective_from == STATUTORY_EFFECTIVE_DATE for entry in entries):
        return entries

    prior_entries = [e for e in entries if e.effective_from < STATUTORY_EFFECTIVE_DATE]
    if not prior_entries:
        return entries

    base_entry = max(prior_entries, key=lambda e: e.effective_from)
    synthetic_entry = RateEntry(
        effective_from=STATUTORY_EFFECTIVE_DATE, rates=dict(base_entry.rates)
    )
    return sorted([*entries, synthetic_entry], key=lambda e: e.effective_from)


def build_basic(entries: list[RateEntry], last_sync: str) -> dict:
    return {
        "lastSync": last_sync,
        "rates": [
            {
                "effectiveFrom": entry.effective_from,
                "rates": {
                    rate_id: entry.rates[rate_id]
                    for rate_id in RATE_IDS
                    if rate_id in entry.rates
                },
            }
            for entry in entries
        ],
    }


def build_extended(entries: list[RateEntry], last_sync: str) -> dict:
    entries = _with_statutory_base_entry(entries)
    rates_list = []
    for entry in entries:
        rates = {
            EXT_KEY_NAMES[rate_id]: entry.rates[rate_id]
            for rate_id in RATE_IDS
            if rate_id in entry.rates
        }
        if entry.effective_from >= STATUTORY_EFFECTIVE_DATE:
            ref = entry.rates["ref"]
            statutory_interest_rate = ref + STATUTORY_MARGIN
            statutory_default_interest_rate = ref + DEFAULT_MARGIN
            rates["statutoryInterestRate"] = statutory_interest_rate
            rates["maxInterestRate"] = 2 * statutory_interest_rate
            rates["statutoryDefaultInterestRate"] = statutory_default_interest_rate
            rates["maxDefaultInterestRate"] = 2 * statutory_default_interest_rate
        rates_list.append({"effectiveFrom": entry.effective_from, "rates": rates})
    return {"lastSync": last_sync, "rates": rates_list}
