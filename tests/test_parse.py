from decimal import Decimal
from pathlib import Path

import pytest

from nbp_feed.parse import parse_archive

FIXTURE = Path(__file__).parent / "fixtures" / "sample_archive.xml"


def test_parses_and_sorts_by_effective_from():
    entries = parse_archive(FIXTURE.read_bytes())

    assert [e.effective_from for e in entries] == [
        "1998-02-26",
        "1998-04-23",
        "1998-05-21",
        "2025-10-09",
    ]


def test_parses_polish_decimal_rates():
    entries = parse_archive(FIXTURE.read_bytes())

    first = entries[0]
    assert first.rates == {
        "ref": Decimal("24.00"),
        "lom": Decimal("27.00"),
        "red": Decimal("24.50"),
    }


def test_later_entry_includes_deposit_and_discount_rates():
    entries = parse_archive(FIXTURE.read_bytes())

    last = entries[-1]
    assert last.effective_from == "2025-10-09"
    assert last.rates == {
        "ref": Decimal("4.50"),
        "lom": Decimal("5.00"),
        "dep": Decimal("4.00"),
        "red": Decimal("4.55"),
        "dys": Decimal("4.60"),
    }


def test_missing_reference_rate_is_rejected():
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <stopy_procentowe_archiwum>
        <pozycje obowiazuje_od="1998-02-26">
            <pozycja id="lom" oprocentowanie="27,00" />
        </pozycje>
    </stopy_procentowe_archiwum>
    """
    with pytest.raises(ValueError):
        parse_archive(xml)
