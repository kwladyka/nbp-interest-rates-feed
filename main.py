"""Fetch the NBP interest rates archive and build the feed output files.

On success, writes to build/:
  - stopy_procentowe_archiwum.xml (the original source file, verbatim)
  - nbp-interest-rates.json
  - nbp-interest-rates-ext.json

If fetching the source file fails after retries, exits with a non-zero
status and writes nothing, so any already-published output is left
untouched (the workflow simply stops before the publish step).
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from nbp_feed.build import build_basic, build_extended
from nbp_feed.fetch import SOURCE_URL, fetch_source_xml
from nbp_feed.parse import parse_archive
from nbp_feed.serialize import to_json

BUILD_DIR = Path("build")

XML_OUTPUT_NAME = "stopy_procentowe_archiwum.xml"
BASIC_OUTPUT_NAME = "nbp-interest-rates.json"
EXT_OUTPUT_NAME = "nbp-interest-rates-ext.json"


def current_warsaw_date() -> str:
    return datetime.now(ZoneInfo("Europe/Warsaw")).date().isoformat()


def main() -> int:
    try:
        xml_bytes = fetch_source_xml(SOURCE_URL)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    entries = parse_archive(xml_bytes)
    last_sync = current_warsaw_date()

    basic = build_basic(entries, last_sync)
    extended = build_extended(entries, last_sync)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / XML_OUTPUT_NAME).write_bytes(xml_bytes)
    (BUILD_DIR / BASIC_OUTPUT_NAME).write_text(to_json(basic), encoding="utf-8")
    (BUILD_DIR / EXT_OUTPUT_NAME).write_text(to_json(extended), encoding="utf-8")

    print(f"Wrote output to {BUILD_DIR}/ (lastSync={last_sync}, entries={len(entries)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
