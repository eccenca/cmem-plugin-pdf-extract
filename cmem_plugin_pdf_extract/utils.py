"""Tests"""

import os
import re
import sys
from collections.abc import Generator
from contextlib import contextmanager
from io import StringIO
from tempfile import TemporaryFile


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


# @contextmanager
# def get_stderr() -> Generator:
#     """Get stderr"""
#     old_stderr = sys.stderr
#     try:
#         stderr = StringIO()
#         sys.stderr = stderr
#         yield stderr
#         stderr.flush()  # Ensure all output is written
#     finally:
#         sys.stderr = old_stderr


@contextmanager
def get_stderr() -> Generator:
    """Capture both Python-level and FD-level stderr."""
    stderr_fd = sys.stderr.fileno()
    saved_fd = os.dup(stderr_fd)  # Save original FD
    saved_sys_stderr = sys.stderr  # Save Python-level stderr

    with TemporaryFile(mode="w+b") as tmp:
        os.dup2(tmp.fileno(), stderr_fd)  # Redirect FD 2 to tmp
        sys.stderr = os.fdopen(tmp.fileno(), "w")  # Replace sys.stderr
        try:
            yield tmp
        finally:
            tmp.flush()
            os.dup2(saved_fd, stderr_fd)  # Restore FD 2
            sys.stderr = saved_sys_stderr  # Restore sys.stderr
            os.close(saved_fd)
