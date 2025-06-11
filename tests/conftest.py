"""Pytest configuration"""

from collections.abc import Generator
from contextlib import suppress
from dataclasses import dataclass
from io import BytesIO
from os import environ
from pathlib import Path

import pytest
import yaml
from cmem.cmempy.workspace.projects.project import delete_project, make_new_project
from cmem.cmempy.workspace.projects.resources.resource import create_resource

from cmem_plugin_pdf_extract.extraction_strategies.table_extraction_strategies import (
    LINES_STRATEGY,
)
from cmem_plugin_pdf_extract.extraction_strategies.text_extraction_strategies import (
    DEFAULT_TEXT_EXTRACTION,
)
from cmem_plugin_pdf_extract.pdf_extract import (
    MAX_PROCESSES_DEFAULT,
    RAISE_ON_ERROR,
    TABLE_LINES,
    TEXT_DEFAULT,
    PdfExtract,
)
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

    __test__ = False

    regex: str
    extract_plugin: PdfExtract


def create_testing_env(generator: Generator) -> TestingEnvironment:
    """Help to create a TestingEnvironment"""
    _ = generator
    regex = rf"{UUID4}_.*\.pdf"
    extract_plugin = PdfExtract(
        regex=regex,
        all_files="no_combine",
        page_selection="",
        error_handling=RAISE_ON_ERROR,
        table_strategy=TABLE_LINES,
        text_strategy=TEXT_DEFAULT,
        custom_table_strategy="\n".join(
            f"# {_}" for _ in yaml.dump(LINES_STRATEGY).strip().splitlines()
        ),
        custom_text_strategy="\n".join(
            f"# {_}" for _ in yaml.dump(DEFAULT_TEXT_EXTRACTION).strip().splitlines()
        ),
        max_processes=MAX_PROCESSES_DEFAULT,
    )
    return TestingEnvironment(
        regex=regex,
        extract_plugin=extract_plugin,
    )


@pytest.fixture
def testing_env_valid(setup_valid: Generator) -> TestingEnvironment:
    """Provide testing environment"""
    return create_testing_env(setup_valid)


@pytest.fixture
def testing_env_corrupted(setup_corrupted: Generator) -> TestingEnvironment:
    """Provide testing environment"""
    return create_testing_env(setup_corrupted)


@pytest.fixture
def testing_env_page_selection(setup_page_selection: Generator) -> TestingEnvironment:
    """Provide testing environment"""
    return create_testing_env(setup_page_selection)
