"""Tests"""

import logging
import re
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
    - Range start must be ≤ end (e.g., "5-2" is invalid)
    - Page numbers must be ≥ 1
    """
    pattern = r"^\s*\d+(?:\s*-\s*\d+)?(?:\s*,\s*\d+(?:\s*-\s*\d+)?)*\s*$"
    if not re.fullmatch(pattern, page_str):
        raise ValueError("Invalid page selection format")

    for part in [p.strip() for p in page_str.strip().split(",")]:
        if "-" in part:
            start_str, end_str = part.split("-")
            start, end = int(start_str), int(end_str)
            if start == 0 or end == 0:
                raise ValueError(f"Page numbers must be ≥ 1: {part}")
            if start > end:
                raise ValueError(f"Invalid range in page selection: {part} (start > end)")
        else:
            page = int(part)
            if page == 0:
                raise ValueError(f"Page numbers must be ≥ 1: {page}")


def parse_page_selection(page_str: str) -> list:
    """Parse a page selection string."""
    if not page_str or page_str.isspace():
        return []

    pages: list = []
    for part in [p.strip() for p in page_str.strip().split(",")]:
        if "-" in part:
            start, end = map(int, part.split("-"))
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    return sorted(set(pages))


@contextmanager
def capture_pdfminer_logs() -> Generator:
    """Capture pdfminer logs."""
    level = logging.WARNING
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(level)

    logger = logging.getLogger("pdfminer")
    original_level = logger.level
    logger.setLevel(level)

    logger.addHandler(handler)
    try:
        yield log_stream
    finally:
        logger.removeHandler(handler)
        logger.setLevel(original_level)
