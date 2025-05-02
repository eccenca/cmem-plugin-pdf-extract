"""Tests"""

import re
import sys
from collections.abc import Generator
from contextlib import contextmanager
from io import StringIO


def validate_page_selection(page_str: str) -> None:
    """Validate the page selection string format.

    Rules:
    - No empty segments (e.g., "1,,2" is invalid)
    - Spaces only allowed:
      - At start/end (trimmed)
      - After commas (e.g., "1, 2" is allowed)
    - No spaces within numbers or ranges (e.g., "1 - 5" is invalid)
    """
    pattern = r"^\s*\d+(?:\s*-\s*\d+)?(?:\s*,\s*\d+(?:\s*-\s*\d+)?)*\s*$"
    if not re.fullmatch(pattern, page_str):
        raise ValueError("Invalid page selection format")


def parse_page_selection(page_str: str) -> list:
    """Parse a page selection string with strict spacing rules."""
    if not page_str or page_str.isspace():
        return []

    pages: list = []
    for part in [p.strip() for p in page_str.strip().split(",")]:
        if not part:
            continue  # Skip empty parts (though validator should prevent this)
        if "-" in part:
            start, end = map(int, part.split("-"))
            if start > end:
                raise ValueError(f"Invalid range: {part} (start > end)")
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    return sorted(set(pages))


@contextmanager
def get_stderr() -> Generator:
    """Get stderr"""
    stderr = StringIO()
    original_stderr = sys.stderr
    sys.stderr = stderr
    try:
        yield stderr
    finally:
        sys.stderr = original_stderr
