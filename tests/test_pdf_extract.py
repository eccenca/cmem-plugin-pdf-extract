"""Plugin tests."""

import json
from ast import literal_eval
from collections import Counter
from collections.abc import Generator
from contextlib import suppress
from pathlib import Path

import pytest
from cmem.cmempy.workspace.projects.project import delete_project, make_new_project
from cmem.cmempy.workspace.projects.resources.resource import (
    create_resource,
)
from cmem_plugin_base.dataintegration.entity import EntityPath

from cmem_plugin_pdf_extract.pdf_extract import MAX_PROCESSES_DEFAULT, PdfExtract
from tests.results import FILE_1_RESULT, FILE_2_RESULT, UUID4
from tests.utils import TestExecutionContext

from . import __path__

PROJECT_ID = f"project_{UUID4}"
TYPE_URI = "urn:x-eccenca:PdfExtract"


def normalize(item):
    if isinstance(item, dict):
        return json.dumps(item, sort_keys=True)
    if isinstance(item, list):
        return json.dumps(sorted([normalize(i) for i in item]))
    return item


def unordered_deep_equal(list1, list2):
    norm1 = [normalize(item) for item in list1]
    norm2 = [normalize(item) for item in list2]
    return Counter(norm1) == Counter(norm2)


@pytest.fixture
def setup() -> Generator:
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


@pytest.mark.usefixtures("setup")
def test_one_entities() -> None:
    """Test result with one entity per file"""
    entities = PdfExtract(
        regex=rf"^{UUID4}_.*\.pdf$",
        all_files=False,
        strict=True,
        table_strategy="lines",
        max_processes=MAX_PROCESSES_DEFAULT,
    ).execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert entities.schema.paths == [EntityPath("pdf_extract_output")]
    assert entities.entities[0].uri == f"{TYPE_URI}_1"
    assert entities.entities[1].uri == f"{TYPE_URI}_2"
    assert len(entities.entities) == 2
    assert literal_eval(entities.entities[0].values[0][0]) == FILE_1_RESULT
    assert literal_eval(entities.entities[1].values[0][0]) == FILE_2_RESULT


@pytest.mark.usefixtures("setup")
def test_one_entity() -> None:
    """Test result with all results in one entity value"""
    entities = PdfExtract(
        regex=rf"^{UUID4}_.*\.pdf$",
        all_files=True,
        strict=True,
        table_strategy="lines",
        max_processes=MAX_PROCESSES_DEFAULT,
    ).execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert entities.schema.paths == [EntityPath("pdf_extract_output")]
    assert entities.entities[0].uri == f"{TYPE_URI}_1"
    assert len(entities.entities) == 1
    assert unordered_deep_equal(
        literal_eval(entities.entities[0].values[0][0]), [FILE_1_RESULT, FILE_2_RESULT]
    )
