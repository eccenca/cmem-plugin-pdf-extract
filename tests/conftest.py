"""Pytest configuration"""

import os
from collections.abc import Generator
from contextlib import suppress
from dataclasses import dataclass
from os import environ
from pathlib import Path

import pytest
import yaml
from cmem_client.client import Client
from cmem_client.models.project import Project
from cmem_client.repositories.protocols.import_item import ImportConflictPolicy
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema, ProjectFile
from cmem_plugin_base.testing import TestExecutionContext, TestPluginContext, TestSystemContext

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


def project_file_entities(names: list[str]) -> Entities:
    """Wrap project resource names as a FileEntitySchema Entities input."""
    schema = FileEntitySchema()
    entities = [schema.to_entity(ProjectFile(path=name, mime="application/pdf")) for name in names]
    return Entities(entities=entities, schema=schema)


def get_env_or_skip(key: str, message: str | None = None) -> str:
    """Get environment variable or skip test."""
    value = environ.get(key, "")
    if message is None:
        message = f"Skipped because the needed environment variable '{key}' is not set."
    if value == "":
        pytest.skip(message)
    return value


def get_test_client() -> Client:
    """Get test client."""
    test_execution_context = TestExecutionContext()
    test_execution_context.system = TestSystemContext(
        cmem_base_uri=str(os.getenv("CMEM_BASE_URI")),
        di_api_endpoint=str(os.getenv("CMEM_BASE_URI")) + "/dataintegration",
        dp_api_endpoint=str(os.getenv("CMEM_BASE_URI")) + "/dataplatform",
    )
    test_plugin_context = TestPluginContext()
    test_plugin_context.system = TestSystemContext(
        cmem_base_uri=str(os.getenv("CMEM_BASE_URI")),
        di_api_endpoint=str(os.getenv("CMEM_BASE_URI")) + "/dataintegration",
        dp_api_endpoint=str(os.getenv("CMEM_BASE_URI")) + "/dataplatform",
    )
    return Client.from_context(test_execution_context)


@pytest.fixture
def setup_valid() -> Generator:
    """Set up Validate test"""
    client = get_test_client()
    with suppress(Exception):
        client.projects.delete_item(PROJECT_ID)
    client.projects.create_item(Project(name=PROJECT_ID))

    path = Path(__path__[0]) / "test_1.pdf"
    key = f"{PROJECT_ID}:{UUID4}_1.pdf"
    client.files.import_item(path=path, key=key, on_conflict=ImportConflictPolicy.REPLACE)

    path = Path(__path__[0]) / "test_2.pdf"
    key = f"{PROJECT_ID}:{UUID4}_2.pdf"
    client.files.import_item(path=path, key=key, on_conflict=ImportConflictPolicy.REPLACE)

    yield

    client.projects.delete_item(PROJECT_ID)


@pytest.fixture
def setup_corrupted() -> Generator:
    """Set up Validate test"""
    client = get_test_client()
    with suppress(Exception):
        client.projects.delete_item(PROJECT_ID)
    client.projects.create_item(Project(name=PROJECT_ID))

    path = Path(__path__[0]) / "test_corrupted_1.pdf"
    key = f"{PROJECT_ID}:{UUID4}_corrupted_1.pdf"
    client.files.import_item(path=path, key=key, on_conflict=ImportConflictPolicy.REPLACE)

    path = Path(__path__[0]) / "test_corrupted.pdf"
    key = f"{PROJECT_ID}:{UUID4}_corrupted_2.pdf"
    client.files.import_item(path=path, key=key, on_conflict=ImportConflictPolicy.REPLACE)

    yield

    client.projects.delete_item(PROJECT_ID)


@pytest.fixture
def setup_page_selection() -> Generator:
    """Set up Validate test"""
    client = get_test_client()
    with suppress(Exception):
        client.projects.delete_item(PROJECT_ID)
    client.projects.create_item(Project(name=PROJECT_ID))

    path = Path(__path__[0]) / "test_3.pdf"
    key = f"{PROJECT_ID}:{UUID4}_3.pdf"
    client.files.import_item(path=path, key=key, on_conflict=ImportConflictPolicy.REPLACE)

    yield

    client.projects.delete_item(PROJECT_ID)


@pytest.fixture
def setup_umlauts() -> Generator:
    """Set up Validate test"""
    client = get_test_client()
    with suppress(Exception):
        client.projects.delete_item(PROJECT_ID)
    client.projects.create_item(Project(name=PROJECT_ID))

    path = Path(__path__[0]) / "test_with_umlauts_äöü.pdf"
    key = f"{PROJECT_ID}:{UUID4}_with_umlauts_äöü.pdf"
    client.files.import_item(path=path, key=key, on_conflict=ImportConflictPolicy.REPLACE)

    yield

    client.projects.delete_item(PROJECT_ID)


@dataclass
class TestingEnvironment:
    """Testing Environment"""

    __test__ = False

    extract_plugin: PdfExtract

    test_execution_context: TestExecutionContext


def create_testing_env(generator: Generator) -> TestingEnvironment:
    """Help to create a TestingEnvironment"""
    _ = generator
    extract_plugin = PdfExtract(
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
    test_execution_context = TestExecutionContext(PROJECT_ID)

    return TestingEnvironment(
        extract_plugin=extract_plugin,
        test_execution_context=test_execution_context,
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


@pytest.fixture
def testing_env_umlauts(setup_umlauts: Generator) -> TestingEnvironment:
    """Provide testing environment"""
    return create_testing_env(setup_umlauts)
