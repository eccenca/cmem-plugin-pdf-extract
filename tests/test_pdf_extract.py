"""Plugin tests."""

import json
from ast import literal_eval
from collections import Counter
from collections.abc import Generator
from contextlib import suppress
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from cmem.cmempy.workspace.projects.project import delete_project, make_new_project
from cmem.cmempy.workspace.projects.resources.resource import create_resource
from cmem_plugin_base.dataintegration.entity import EntityPath
from pdfplumber.utils.exceptions import PdfminerException
from yaml import YAMLError, safe_load

from cmem_plugin_pdf_extract.pdf_extract import PdfExtract
from tests.results import (
    CUSTOM_TABLE_STRATEGY_SETTING,
    FILE_1_RESULT,
    FILE_2_RESULT,
    FILE_CORRUPTED_RESULT_1,
    FILE_CORRUPTED_RESULT_2,
    UUID4,
)
from tests.utils import TestExecutionContext

from . import __path__

PROJECT_ID = f"project_pdf_extract_plugin_test_{UUID4}"
TYPE_URI = "urn:x-eccenca:PdfExtract"


def normalise(item: Any) -> Any:  # noqa: ANN401
    """Normalise item"""
    if isinstance(item, dict):
        return json.dumps(item, sort_keys=True)
    if isinstance(item, list):
        return json.dumps(sorted([normalise(i) for i in item]))
    return item


def unordered_deep_equal(list1: list, list2: list) -> bool:
    """Compare unordered list of objects"""
    norm1 = [normalise(item) for item in list1]
    norm2 = [normalise(item) for item in list2]
    return Counter(norm1) == Counter(norm2)


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


@pytest.mark.usefixtures("setup_valid")
def test_one_entity_per_file() -> None:
    """Test result with table strategy "lines", one entity per file"""
    entities = PdfExtract(
        regex=rf"^{UUID4}_.*\.pdf$",
        table_strategy="lines",
    ).execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert entities.schema.paths == [EntityPath("pdf_extract_output")]
    assert entities.entities[0].uri == f"{TYPE_URI}_1"
    assert entities.entities[1].uri == f"{TYPE_URI}_2"
    assert len(entities.entities) == 2  # noqa: PLR2004
    assert literal_eval(entities.entities[0].values[0][0]) == FILE_1_RESULT
    assert literal_eval(entities.entities[1].values[0][0]) == FILE_2_RESULT


@pytest.mark.usefixtures("setup_valid")
def test_one_entity() -> None:
    """Test result with table strategy "lines", all results in one entity value"""
    entities = PdfExtract(
        regex=rf"^{UUID4}_.*\.pdf$",
        all_files=True,
        table_strategy="lines",
    ).execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert entities.schema.paths == [EntityPath("pdf_extract_output")]
    assert entities.entities[0].uri == f"{TYPE_URI}_1"
    assert len(entities.entities) == 1
    assert unordered_deep_equal(
        literal_eval(entities.entities[0].values[0][0]), [FILE_1_RESULT, FILE_2_RESULT]
    )


@pytest.mark.usefixtures("setup_valid")
def test_table_strategy_text() -> None:
    """Test if table strategy "text" parameter is valid"""
    PdfExtract(
        regex=rf"^{UUID4}_.*\.pdf$",
        all_files=True,
        table_strategy="text",
    ).execute(inputs=[], context=TestExecutionContext(PROJECT_ID))


@pytest.mark.usefixtures("setup_corrupted")
def test_invalid_pdf_1() -> None:
    """Test with corrupted pdf"""
    filename = f"{UUID4}_corrupted_1.pdf"
    entities = PdfExtract(
        regex=filename,
        table_strategy="lines",
        error_handling="ignore",
    ).execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert literal_eval(entities.entities[0].values[0][0]) == FILE_CORRUPTED_RESULT_1

    with pytest.raises(
        PdfminerException, match=f"File {filename}: No /Root object! - Is this really a PDF?"
    ):
        PdfExtract(
            regex=filename,
            table_strategy="lines",
        ).execute(inputs=[], context=TestExecutionContext(PROJECT_ID))


@pytest.mark.usefixtures("setup_corrupted")
def test_invalid_pdf_2() -> None:
    """Test with corrupted pdf"""
    filename = f"{UUID4}_corrupted_2.pdf"
    entities = PdfExtract(
        regex=filename,
        table_strategy="lines",
        error_handling="raise_on_error",
    ).execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert literal_eval(entities.entities[0].values[0][0]) == FILE_CORRUPTED_RESULT_2

    with pytest.raises(
        ValueError,
        match=f"File {filename}, page 1: Text extraction error: Data-loss while decompressing "
        f"corrupted data",
    ):
        PdfExtract(
            regex=filename,
            table_strategy="lines",
            error_handling="raise_on_error_and_warning",
        ).execute(inputs=[], context=TestExecutionContext(PROJECT_ID))


def test_custom_table_strategy_parameter() -> None:
    """Test custom table extraction strategy parameter"""
    plugin = PdfExtract(
        regex="test",
        table_strategy="custom",
        custom_table_strategy=CUSTOM_TABLE_STRATEGY_SETTING,
    )
    assert plugin.table_strategy == safe_load(CUSTOM_TABLE_STRATEGY_SETTING)

    with pytest.raises(ValueError, match="No custom table strategy defined"):
        PdfExtract(
            regex="test",
            table_strategy="custom",
        )

    with pytest.raises(YAMLError, match="Invalid custom table strategy"):
        PdfExtract(
            regex="test",
            table_strategy="custom",
            custom_table_strategy=CUSTOM_TABLE_STRATEGY_SETTING + "this:should:fail",
        )
