"""Validate freshly built output files before they are published.

Run after main.py. For each output file:
  1. Validate its structure against the expected schema.
  2. Compare it against the currently published version on GitHub Pages
     (if any) and fail if any existing rate entry was removed or changed.

Exits with a non-zero status (and prints the reason) on any failure, which
stops the workflow before the publish step.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from nbp_feed.fetch import fetch_previous_json
from nbp_feed.validate import assert_is_superset, validate_output_schema

BUILD_DIR = Path("build")

CHECKS = [
    (
        "nbp-interest-rates.json",
        "https://kwladyka.github.io/nbp-interest-rates-feed/nbp-interest-rates.json",
        False,
    ),
    (
        "nbp-interest-rates-ext.json",
        "https://kwladyka.github.io/nbp-interest-rates-feed/nbp-interest-rates-ext.json",
        True,
    ),
]


def main() -> int:
    for filename, url, extended in CHECKS:
        new_data = json.loads((BUILD_DIR / filename).read_text(encoding="utf-8"))

        try:
            validate_output_schema(new_data, extended=extended)
        except ValueError as exc:
            print(f"ERROR: {filename} failed schema validation: {exc}", file=sys.stderr)
            return 1

        previous_bytes = fetch_previous_json(url)
        previous_data = json.loads(previous_bytes) if previous_bytes is not None else None

        try:
            assert_is_superset(previous_data, new_data)
        except ValueError as exc:
            print(f"ERROR: {filename} failed regression check: {exc}", file=sys.stderr)
            return 1

        print(f"OK: {filename}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
