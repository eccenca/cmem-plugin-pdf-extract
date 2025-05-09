"""Pytest configuration"""

from collections.abc import Generator
from contextlib import suppress
from dataclasses import dataclass
from io import BytesIO
from os import environ
from pathlib import Path

import pytest
from cmem.cmempy.workspace.projects.project import delete_project, make_new_project
from cmem.cmempy.workspace.projects.resources.resource import create_resource

from cmem_plugin_pdf_extract.pdf_extract import (
    MAX_PROCESSES_DEFAULT,
    RAISE_ON_ERROR,
    TABLE_LINES,
    PdfExtract,
)
from cmem_plugin_pdf_extract.table_extraction_strategies import CUSTOM_TABLE_STRATEGY_DEFAULT
from tests.results import UUID4

from . import __path__

PROJECT_ID = f"project_pdf_extract_plugin_test_{UUID4}"
TYPE_URI = "urn:x-eccenca:PdfExtract"


def get_env_or_skip(key: str, message: str | None = None) -> str:
    """Get environment variable or skip test."""
    value = environ.get(key, "")
    if message is None:
        message = f"Skipped because the needed environment variable '{key}' is not set."
    if value == "":
        pytest.skip(message)
    return value


@pytest.fixture
def setup_valid() -> Generator:
    """Set up Validate test"""
    with suppress(Exception):
        delete_project(PROJECT_ID)
    make_new_project(PROJECT_ID)

    with (Path(__path__[0]) / "test_1.pdf").open("rb") as f:
        create_resource(
            project_name=PROJECT_ID,
            resource_name=f"{UUID4}_1.pdf",
            file_resource=f,
            replace=True,
        )

    with (Path(__path__[0]) / "test_2.pdf").open("rb") as f:
        create_resource(
            project_name=PROJECT_ID,
            resource_name=f"{UUID4}_2.pdf",
            file_resource=f,
            replace=True,
        )

    yield

    delete_project(PROJECT_ID)


@pytest.fixture
def setup_corrupted() -> Generator:
    """Set up Validate test"""
    with suppress(Exception):
        delete_project(PROJECT_ID)
    make_new_project(PROJECT_ID)

    create_resource(
        project_name=PROJECT_ID,
        resource_name=f"{UUID4}_corrupted_1.pdf",
        file_resource=BytesIO(b""),
        replace=True,
    )

    with (Path(__path__[0]) / "test_corrupted.pdf").open("rb") as f:
        create_resource(
            project_name=PROJECT_ID,
            resource_name=f"{UUID4}_corrupted_2.pdf",
            file_resource=f,
            replace=True,
        )

    yield

    delete_project(PROJECT_ID)


@pytest.fixture
def setup_page_selection() -> Generator:
    """Set up Validate test"""
    with suppress(Exception):
        delete_project(PROJECT_ID)
    make_new_project(PROJECT_ID)

    with (Path(__path__[0]) / "test_3.pdf").open("rb") as f:
        create_resource(
            project_name=PROJECT_ID,
            resource_name=f"{UUID4}_3.pdf",
            file_resource=f,
            replace=True,
        )

    yield

    delete_project(PROJECT_ID)


@dataclass
class TestingEnvironment:
    """Testing Environment"""

    regex: str
    extract_plugin: PdfExtract


@pytest.fixture
def testing_env_valid(setup_valid: Generator) -> TestingEnvironment:
    """Provide testing environment"""
    _ = setup_valid

    regex = rf"{UUID4}_.*\.pdf"
    all_files: bool = False
    page_selection: str = ""
    error_handling: str = RAISE_ON_ERROR
    table_strategy: str = TABLE_LINES
    custom_table_strategy: str = CUSTOM_TABLE_STRATEGY_DEFAULT
    max_processes: int = MAX_PROCESSES_DEFAULT

    extract_plugin = PdfExtract(
        regex=regex,
        all_files=all_files,
        page_selection=page_selection,
        error_handling=error_handling,
        table_strategy=table_strategy,
        custom_table_strategy=custom_table_strategy,
        max_processes=max_processes,
    )
    return TestingEnvironment(
        regex=regex,
        extract_plugin=extract_plugin,
    )


@pytest.fixture
def testing_env_corrupted(setup_corrupted: Generator) -> TestingEnvironment:
    """Provide testing environment"""
    _ = setup_corrupted

    regex = rf"{UUID4}_.*\.pdf"
    all_files: bool = False
    page_selection: str = ""
    error_handling: str = RAISE_ON_ERROR
    table_strategy: str = TABLE_LINES
    custom_table_strategy: str = CUSTOM_TABLE_STRATEGY_DEFAULT
    max_processes: int = MAX_PROCESSES_DEFAULT

    extract_plugin = PdfExtract(
        regex=regex,
        all_files=all_files,
        page_selection=page_selection,
        error_handling=error_handling,
        table_strategy=table_strategy,
        custom_table_strategy=custom_table_strategy,
        max_processes=max_processes,
    )
    return TestingEnvironment(
        regex=regex,
        extract_plugin=extract_plugin,
    )


@pytest.fixture
def testing_env_page_selection(setup_page_selection: Generator) -> TestingEnvironment:
    """Provide testing environment"""
    _ = setup_page_selection

    regex = rf"{UUID4}_.*\.pdf"
    all_files: bool = False
    page_selection: str = ""
    error_handling: str = RAISE_ON_ERROR
    table_strategy: str = TABLE_LINES
    custom_table_strategy: str = CUSTOM_TABLE_STRATEGY_DEFAULT
    max_processes: int = MAX_PROCESSES_DEFAULT

    extract_plugin = PdfExtract(
        regex=regex,
        all_files=all_files,
        page_selection=page_selection,
        error_handling=error_handling,
        table_strategy=table_strategy,
        custom_table_strategy=custom_table_strategy,
        max_processes=max_processes,
    )
    return TestingEnvironment(
        regex=regex,
        extract_plugin=extract_plugin,
    )
