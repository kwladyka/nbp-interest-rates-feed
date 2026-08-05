"""Fetching remote files over HTTP with retry for the primary source."""

from __future__ import annotations

import time
import urllib.error
import urllib.request

SOURCE_URL = "https://static.nbp.pl/dane/stopy/stopy_procentowe_archiwum.xml"
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5
TIMEOUT_SECONDS = 30


def fetch_source_xml(url: str = SOURCE_URL) -> bytes:
    """Fetch the NBP archive XML, retrying up to MAX_ATTEMPTS times total."""
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)
    raise RuntimeError(f"Failed to fetch {url} after {MAX_ATTEMPTS} attempts") from last_error


def fetch_previous_json(url: str) -> bytes | None:
    """Fetch a previously published JSON file, or None if it does not exist yet."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
