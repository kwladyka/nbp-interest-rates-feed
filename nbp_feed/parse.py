"""Parsing of the NBP interest rates archive XML."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from decimal import Decimal

from nbp_feed.numbers import parse_polish_decimal

# Order matters: it defines the key order in generated output.
RATE_IDS = ("ref", "lom", "dep", "red", "dys")


@dataclass(frozen=True)
class RateEntry:
    effective_from: str
    rates: dict[str, Decimal]


def parse_archive(xml_bytes: bytes) -> list[RateEntry]:
    """Parse the NBP archive XML into a list of RateEntry, sorted by date."""
    root = ET.fromstring(xml_bytes)
    entries = []
    for pozycje in root.findall("pozycje"):
        effective_from = pozycje.attrib["obowiazuje_od"]
        rates: dict[str, Decimal] = {}
        for pozycja in pozycje.findall("pozycja"):
            rate_id = pozycja.attrib["id"]
            if rate_id not in RATE_IDS:
                continue
            rates[rate_id] = parse_polish_decimal(pozycja.attrib["oprocentowanie"])
        if "ref" not in rates:
            raise ValueError(
                f"Entry effective from {effective_from} is missing the reference rate"
            )
        entries.append(RateEntry(effective_from=effective_from, rates=rates))
    entries.sort(key=lambda entry: entry.effective_from)
    return entries
