"""Plugin tests."""

import json
from ast import literal_eval
from collections import Counter
from typing import Any

import pytest
from cmem_plugin_base.dataintegration.entity import Entities, EntityPath
from cmem_plugin_base.dataintegration.typed_entities.file import (
    File,
    FileEntitySchema,
    LocalFile,
    ProjectFile,
)
from pdfplumber.utils.exceptions import PdfminerException
from yaml import YAMLError, safe_load

from cmem_plugin_pdf_extract.extraction_strategies.table_extraction_strategies import (
    TABLE_EXTRACTION_STRATEGIES,
)
from cmem_plugin_pdf_extract.extraction_strategies.text_extraction_strategies import (
    TEXT_EXTRACTION_STRATEGIES,
)
from cmem_plugin_pdf_extract.pdf_extract import PdfExtract
from cmem_plugin_pdf_extract.utils import parse_page_selection
from tests.results import (
    CUSTOM_TABLE_STRATEGY_SETTING,
    FILE_1_RESULT,
    FILE_1_RESULT_INPUT,
    FILE_2_RESULT,
    FILE_3_RESULT,
    FILE_CORRUPTED_RESULT_1,
    FILE_CORRUPTED_RESULT_2,
    FILE_PAGES_NOT_EXIST_RESULT,
    UUID4,
)
from tests.utils import TestExecutionContext, TestPluginContext

from .conftest import PROJECT_ID, TYPE_URI, TestingEnvironment


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


def test_one_entity_per_file(testing_env_valid: TestingEnvironment) -> None:
    """Test result with table strategy "lines", one entity per file"""
    plugin = testing_env_valid.extract_plugin
    entities = plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    entities.entities = sorted(entities.entities, key=lambda x: x.uri)

    assert entities.schema.paths == [EntityPath("pdf_extract_output")]
    assert entities.entities[0].uri == f"{TYPE_URI}_1"
    assert entities.entities[1].uri == f"{TYPE_URI}_2"
    assert len(entities.entities) == 2  # noqa: PLR2004
    assert literal_eval(entities.entities[0].values[0][0]) == FILE_1_RESULT
    assert literal_eval(entities.entities[1].values[0][0]) == FILE_2_RESULT


def test_one_entity(testing_env_valid: TestingEnvironment) -> None:
    """Test result with table strategy "lines", all results in one entity value"""
    plugin = testing_env_valid.extract_plugin
    plugin.all_files = "combine"
    entities = plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert entities.schema.paths == [EntityPath("pdf_extract_output")]
    assert entities.entities[0].uri == f"{TYPE_URI}_1"
    assert len(entities.entities) == 1
    assert unordered_deep_equal(
        literal_eval(entities.entities[0].values[0][0]), [FILE_1_RESULT, FILE_2_RESULT]
    )


def test_table_strategy_text(testing_env_valid: TestingEnvironment) -> None:
    """Test if table strategy "text" parameter is valid"""
    plugin = testing_env_valid.extract_plugin
    plugin.all_files = "combine"
    plugin.table_strategy = TABLE_EXTRACTION_STRATEGIES["text"]
    plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))


def test_page_selection(testing_env_page_selection: TestingEnvironment) -> None:
    """Test result with page selection"""
    plugin = testing_env_page_selection.extract_plugin
    plugin.regex = f"{UUID4}_3.pdf"
    plugin.table_strategy = TABLE_EXTRACTION_STRATEGIES["lines"]
    plugin.page_numbers = parse_page_selection("1,3-5,8-10")
    entities = plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert literal_eval(entities.entities[0].values[0][0]) == FILE_3_RESULT


def test_page_selection_not_exist(testing_env_page_selection: TestingEnvironment) -> None:
    """Test result with page selection where no pages exist"""
    plugin = testing_env_page_selection.extract_plugin
    plugin.regex = f"{UUID4}_3.pdf"
    plugin.table_strategy = TABLE_EXTRACTION_STRATEGIES["lines"]
    plugin.page_numbers = parse_page_selection("8")
    entities = plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert literal_eval(entities.entities[0].values[0][0]) == FILE_PAGES_NOT_EXIST_RESULT


def test_invalid_pdf_1(testing_env_corrupted: TestingEnvironment) -> None:
    """Test with corrupted pdf"""
    filename = f"{UUID4}_corrupted_1.pdf"

    plugin = testing_env_corrupted.extract_plugin
    plugin.regex = filename
    plugin.error_handling = "ignore"
    entities = plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert literal_eval(entities.entities[0].values[0][0]) == FILE_CORRUPTED_RESULT_1

    plugin.error_handling = "raise_on_error"

    with pytest.raises(
        PdfminerException, match=f"File {filename}: No /Root object! - Is this really a PDF?"
    ):
        plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))


def test_invalid_pdf_2(testing_env_corrupted: TestingEnvironment) -> None:
    """Test with corrupted pdf"""
    filename = f"{UUID4}_corrupted_2.pdf"
    plugin = testing_env_corrupted.extract_plugin
    plugin.regex = filename
    plugin.table_strategy = TABLE_EXTRACTION_STRATEGIES["lines"]
    entities = plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))

    assert literal_eval(entities.entities[0].values[0][0]) == FILE_CORRUPTED_RESULT_2

    plugin.error_handling = "raise_on_error_and_warning"

    with pytest.raises(
        ValueError,
        match=f"File {filename}, page 1: Text extraction error: Data-loss while decompressing "
        f"corrupted data",
    ):
        plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))


def test_custom_table_strategy_parameter() -> None:
    """Test custom table extraction strategy parameter"""
    plugin = PdfExtract(
        regex="test",
        table_strategy="custom",
        custom_table_strategy=CUSTOM_TABLE_STRATEGY_SETTING,
    )
    assert plugin.table_strategy == safe_load(CUSTOM_TABLE_STRATEGY_SETTING)

    with pytest.raises(ValueError, match="No custom table strategy defined"):
        PdfExtract(regex="test", table_strategy="custom")

    with pytest.raises(YAMLError, match="Invalid custom table strategy"):
        PdfExtract(
            regex="test",
            table_strategy="custom",
            custom_table_strategy=CUSTOM_TABLE_STRATEGY_SETTING + "this:should:fail",
        )


def test_invalid_page_selection_format() -> None:
    """Test page selection parsing."""
    with pytest.raises(ValueError, match="Invalid page selection format"):
        PdfExtract(regex="test", page_selection="invalid")

    with pytest.raises(ValueError, match=r"Invalid range in page selection: 2-1 \(start > end\)"):
        PdfExtract(regex="test", page_selection="2-1")

    with pytest.raises(ValueError, match=r"Page numbers must be ≥ 1: 0"):
        PdfExtract(regex="test", page_selection="0,1")

    with pytest.raises(ValueError, match=r"Page numbers must be ≥ 1: 0"):
        PdfExtract(regex="test", page_selection="5,0-2")


def test_regex_plugin_action(testing_env_valid: TestingEnvironment) -> None:
    """Test plugin action"""
    result = testing_env_valid.extract_plugin.test_regex(TestPluginContext(PROJECT_ID))
    assert (
        result
        == """2 files found matching the regular expression in the project files.
- c394802542bd4c9990cca50d3104e6a0_1.pdf
- c394802542bd4c9990cca50d3104e6a0_2.pdf

The preview does not show results from input ports as they are usually not available before the execution"""  # noqa: E501
    )


def test_input_port_pdf(testing_env_valid: TestingEnvironment) -> None:
    """Test input via input port"""
    schema = FileEntitySchema()
    files = [LocalFile(path="tests/test_1.pdf", mime="application/pdf")]
    entities = [schema.to_entity(file) for file in files]
    input_entities = Entities(entities=entities, schema=schema)

    plugin = testing_env_valid.extract_plugin
    plugin.regex = "tests/test_1.pdf"

    results = plugin.execute(inputs=[input_entities], context=TestExecutionContext())

    assert literal_eval(results.entities[0].values[0][0]) == FILE_1_RESULT_INPUT


def test_text_extraction_strategies(testing_env_valid: TestingEnvironment) -> None:
    """Test all combinations of text- and table-strategies"""
    text_strategies = ["default", "raw", "layout", "scanned"]
    table_strategies = ["lines", "sparse", "lattice", "text"]

    plugin = testing_env_valid.extract_plugin

    for text_strategy in text_strategies:
        for table_strategy in table_strategies:
            plugin.table_strategy = TABLE_EXTRACTION_STRATEGIES[table_strategy]
            plugin.text_strategy = TEXT_EXTRACTION_STRATEGIES[text_strategy]
            result = plugin.execute(inputs=[], context=TestExecutionContext(PROJECT_ID))
            assert len(list(result.entities)) > 0


def test_wrong_text_extraction() -> None:
    """Test invalid text strategy"""
    wrong_text_strategy = "wrong"
    with pytest.raises(ValueError, match=f"Invalid text strategy: {wrong_text_strategy}"):
        PdfExtract(regex="test", text_strategy=wrong_text_strategy)


def test_wrong_file_type(testing_env_valid: TestingEnvironment) -> None:
    """Test for wrong filetype of the FileEntitySchema"""
    schema = FileEntitySchema()
    files = [File(path="tests/test_1.pdf", file_type="unsupported", mime="application/pdf")]
    entities = [schema.to_entity(file) for file in files]
    input_entities = Entities(entities=entities, schema=schema)

    plugin = testing_env_valid.extract_plugin
    with pytest.raises(ValueError, match=r"^File 'tests/test_1.pdf' has unexpected type"):
        plugin.execute(inputs=[input_entities], context=TestExecutionContext())


def test_input_project_file(testing_env_valid: TestingEnvironment) -> None:
    """Test execution with Project type files as input"""
    schema = FileEntitySchema()
    files = [File(path=f"{UUID4}_1.pdf", file_type="Project", mime="application/pdf")]
    entities = [schema.to_entity(file) for file in files]
    input_entities = Entities(entities=entities, schema=schema)

    plugin = testing_env_valid.extract_plugin
    results = plugin.execute(inputs=[input_entities], context=TestExecutionContext(PROJECT_ID))

    assert len(list(results.entities)) == 1


def test_different_file_type_inputs(testing_env_valid: TestingEnvironment) -> None:
    """Test execution with inputs from different file types: Project and Local"""
    schema = FileEntitySchema()
    files = []
    file_project = ProjectFile(path=f"{UUID4}_1.pdf", mime="application/pdf")
    file_local = LocalFile(path="tests/test_1.pdf", mime="application/pdf")
    files.append(file_project)
    files.append(file_local)
    entities = [schema.to_entity(file) for file in files]
    input_entities = Entities(entities=entities, schema=schema)

    plugin = testing_env_valid.extract_plugin
    result = plugin.execute(inputs=[input_entities], context=TestExecutionContext(PROJECT_ID))
    assert len(list(result.entities)) == len(files)
