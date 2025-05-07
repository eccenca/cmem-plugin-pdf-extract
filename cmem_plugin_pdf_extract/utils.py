"""Tests"""

import os
import re
import sys
import warnings
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
#     stderr = StringIO()
#     original_stderr = sys.stderr
#     sys.stderr = stderr
#     try:
#         yield stderr
#     finally:
#         sys.stderr = original_stderr


@contextmanager
def get_stderr() -> Generator:
    """Capture ALL stderr output while handling __stderr__ properly"""
    stderr_fd = sys.stderr.fileno()
    saved_fd = os.dup(stderr_fd)
    saved_sys_stderr = sys.stderr

    with TemporaryFile(mode="w+b") as tmp:
        # Redirect at FD level
        os.dup2(tmp.fileno(), stderr_fd)

        # Create new stderr handle
        new_stderr = open(tmp.fileno(), "w", buffering=1)  # noqa: SIM115 PTH123
        sys.stderr = new_stderr

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                if hasattr(sys, "__stderr__"):
                    # Temporarily shadow __stderr__ without modifying it
                    original_stderr = sys.__stderr__
                    sys.__stderr__ = new_stderr

            yield tmp
        finally:
            # Restore original state
            tmp.flush()
            os.fsync(tmp.fileno())
            os.dup2(saved_fd, stderr_fd)
            os.close(saved_fd)
            sys.stderr = saved_sys_stderr
            if hasattr(sys, "__stderr__"):
                sys.__stderr__ = original_stderr
