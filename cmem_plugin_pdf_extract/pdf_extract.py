"""Extract text from PDF files"""

import re
from collections import OrderedDict
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
from io import BytesIO
from os import cpu_count
from typing import Any

import yaml
from cmem.cmempy.workspace.projects.resources import get_resources
from cmem.cmempy.workspace.projects.resources.resource import get_resource
from cmem_plugin_base.dataintegration.context import (
    ExecutionContext,
    ExecutionReport,
    PluginContext,
)
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginAction, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities, Entity, EntityPath, EntitySchema
from cmem_plugin_base.dataintegration.parameter.choice import ChoiceParameterType
from cmem_plugin_base.dataintegration.parameter.multiline import MultilineStringParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema
from cmem_plugin_base.dataintegration.types import (
    BoolParameterType,
    IntParameterType,
    StringParameterType,
)
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access
from pdfplumber import open as pdfplumber_open
from pdfplumber.page import Page
from yaml import YAMLError, safe_load

from cmem_plugin_pdf_extract.doc import DOC
from cmem_plugin_pdf_extract.extraction_strategies.table_extraction_strategies import (
    LINES_STRATEGY,
    TABLE_EXTRACTION_STRATEGIES,
)
from cmem_plugin_pdf_extract.extraction_strategies.text_extraction_strategies import (
    DEFAULT_TEXT_EXTRACTION,
    TEXT_EXTRACTION_STRATEGIES,
)
from cmem_plugin_pdf_extract.utils import (
    capture_pdfminer_logs,
    parse_page_selection,
    validate_page_selection,
)

MAX_PROCESSES_DEFAULT = cpu_count() - 1  # type: ignore[operator]
TABLE_LINES = "lines"
TABLE_TEXT = "text"
TABLE_LATTICE = "lattice"
TABLE_SPARSE = "sparse"
TABLE_CUSTOM = "custom"
TABLE_STRATEGY_PARAMETER_CHOICES = OrderedDict(
    {
        TABLE_LINES: "Lines",
        TABLE_TEXT: "Text",
        TABLE_LATTICE: "Lattice",
        TABLE_SPARSE: "Sparse",
        TABLE_CUSTOM: "Custom",
    }
)

TEXT_DEFAULT = "default"
TEXT_RAW = "raw"
TEXT_SCANNED = "scanned"
TEXT_LAYOUT = "layout"
TEXT_CUSTOM = "custom"
TEXT_STRATEGY_PARAMETER_CHOICES = OrderedDict(
    {
        TEXT_DEFAULT: "Default",
        TEXT_RAW: "Raw",
        TEXT_SCANNED: "Scanned",
        TEXT_LAYOUT: "Layout",
        TEXT_CUSTOM: "Custom",
    }
)

IGNORE = "ignore"
RAISE_ON_ERROR = "raise_on_error"
RAISE_ON_ERROR_AND_WARNING = "raise_on_error_and_warning"
ERROR_HANDLING_PARAMETER_CHOICES = OrderedDict(
    {
        IGNORE: "Ignore",
        RAISE_ON_ERROR: "Raise on error",
        RAISE_ON_ERROR_AND_WARNING: "Raise on error and warning",
    }
)

TYPE_URI = "urn:x-eccenca:PdfExtract"


@Plugin(
    label="Extract from PDF files",
    description="Extract text and tables from PDF files",
    documentation=DOC,
    icon=Icon(package=__package__, file_name="pdf-extract.svg"),
    actions=[
        PluginAction(
            name="test_regex",
            label="Preview files",
            description="Preview all of the PDF files that have been found.",
        )
    ],
    parameters=[
        PluginParameter(
            param_type=StringParameterType(),
            name="regex",
            label="File name regex filter",
            description="Regular expression for filtering resources of the project. If this "
            "parameter is set, the input port will be closed and project "
            "files will be compared against the regular expression.",
            advanced=True,
            default_value="",
        ),
        PluginParameter(
            param_type=BoolParameterType(),
            name="all_files",
            label="Combine the results from all files into a single value",
            description="""If enabled, the results of all files will be combined into a single
            output value. If disabled, each file result will be output in a separate entity.""",
            default_value=False,
        ),
        PluginParameter(
            param_type=StringParameterType(),
            name="page_selection",
            label="Page selection",
            description="""Comma-separated page numbers or ranges (e.g., 1,2-5,7) for page
            selection. Files that do not contain any of the specified pages will return
            empty results with the information logged. If no page selection is specified, all pages
            will be processed.""",
            default_value="",
        ),
        PluginParameter(
            param_type=ChoiceParameterType(ERROR_HANDLING_PARAMETER_CHOICES),
            name="error_handling",
            label="Error Handling Mode",
            description="""The mode in which errors during the extraction are handled. If set to
            "Ignore", it will log errors and continue, returning empty or error-marked results
            for files. When "Raise on errors and warnings" is selected, any warning from the
            underlying PDF extraction module when extracting text and tables from pages is
            treated as an error if empty results are returned.""",
            default_value=RAISE_ON_ERROR,
        ),
        PluginParameter(
            param_type=ChoiceParameterType(TEXT_STRATEGY_PARAMETER_CHOICES),
            name="text_strategy",
            label="Text extraction strategy",
            description="""Specifies how text is extracted from a PDF page.
            Options include "raw", "layout", and others, each interpreting character positions and
            formatting differently to control how text is grouped and ordered.""",
            default_value=TEXT_DEFAULT,
        ),
        PluginParameter(
            param_type=ChoiceParameterType(TABLE_STRATEGY_PARAMETER_CHOICES),
            name="table_strategy",
            label="Table extraction strategy",
            description="""Specifies the method used to detect tables in the PDF page. Options
            include "lines" and "text", each using different cues (such as  lines or text alignment)
            to find tables. If "Custom" is selected, a custom setting needs to defined under
            advanced options.""",
            default_value=TABLE_LINES,
        ),
        PluginParameter(
            param_type=MultilineStringParameterType(),
            name="custom_text_strategy",
            description="Custom text extraction strategy in YAML format.",
            advanced=True,
        ),
        PluginParameter(
            param_type=MultilineStringParameterType(),
            name="custom_table_strategy",
            label="Custom table extraction strategy",
            description="Custom table extraction strategy in YAML format.",
            advanced=True,
        ),
        PluginParameter(
            param_type=IntParameterType(),
            name="max_processes",
            label="Maximum number of processes for processing files",
            description="""The maximum number of processes to use for processing multiple files
            concurrently. The default is (number of virtual cores)-1.""",
            advanced=True,
            default_value=MAX_PROCESSES_DEFAULT,
        ),
    ],
)
class PdfExtract(WorkflowPlugin):
    """PDF Extract plugin."""

    def __init__(  # noqa: PLR0913
        self,
        regex: str,
        all_files: bool = False,
        page_selection: str = "",
        error_handling: str = RAISE_ON_ERROR,
        table_strategy: str = TABLE_LINES,
        text_strategy: str = TEXT_DEFAULT,
        custom_table_strategy: str = "\n".join(
            f"# {_}" for _ in yaml.dump(LINES_STRATEGY).strip().splitlines()
        ),
        custom_text_strategy: str = "\n".join(
            f"# {_}" for _ in yaml.dump(DEFAULT_TEXT_EXTRACTION).strip().splitlines()
        ),
        max_processes: int = MAX_PROCESSES_DEFAULT,
    ) -> None:
        if page_selection:
            validate_page_selection(page_selection)
        self.page_numbers = parse_page_selection(page_selection)
        self.table_strategy: dict[Any, Any]
        self.set_table_strategy(custom_table_strategy, table_strategy)

        self.text_strategy: dict[Any, Any]
        self.set_text_strategy(custom_text_strategy, text_strategy)

        if error_handling not in ERROR_HANDLING_PARAMETER_CHOICES:
            raise ValueError(f"Invalid error handling mode: {error_handling}")
        self.error_handling = error_handling

        self.regex = rf"{regex}"
        self.all_files = all_files
        self.max_processes = max_processes
        self.schema = EntitySchema(type_uri=TYPE_URI, paths=[EntityPath("pdf_extract_output")])
        self.input_ports = (
            FixedNumberOfInputs([FixedSchemaPort(schema=FileEntitySchema())])
            if not self.regex
            else FixedNumberOfInputs([])
        )
        self.output_port = FixedSchemaPort(self.schema)

    def set_text_strategy(self, custom_text_strategy: str, text_strategy: str) -> None:
        """Set text strategy to be used in extraction"""
        if text_strategy not in TEXT_STRATEGY_PARAMETER_CHOICES:
            raise ValueError(f"Invalid text strategy: {text_strategy}")
        if text_strategy == TEXT_CUSTOM:
            cleaned_string = "\n".join(
                [
                    line
                    for line in custom_text_strategy.splitlines()
                    if not line.strip().startswith("#") and line.strip() != ""
                ]
            ).strip()
            if not cleaned_string:
                raise ValueError("No custom text strategy defined")
            try:
                self.text_strategy = safe_load(cleaned_string)
            except YAMLError as e:
                raise YAMLError(f"Invalid custom text strategy: {e}") from e
        else:
            self.text_strategy = TEXT_EXTRACTION_STRATEGIES[text_strategy]

    def set_table_strategy(self, custom_table_strategy: str, table_strategy: str) -> None:
        """Set table strategy to be used in extraction"""
        if table_strategy not in TABLE_STRATEGY_PARAMETER_CHOICES:
            raise ValueError(f"Invalid table strategy: {table_strategy}")
        if table_strategy == TABLE_CUSTOM:
            cleaned_string = "\n".join(
                [
                    line
                    for line in custom_table_strategy.splitlines()
                    if not line.strip().startswith("#") and line.strip() != ""
                ]
            ).strip()
            if not cleaned_string:
                raise ValueError("No custom table strategy defined")
            try:
                self.table_strategy = safe_load(cleaned_string)
            except YAMLError as e:
                raise YAMLError(f"Invalid custom table strategy: {e}") from e
        else:
            self.table_strategy = TABLE_EXTRACTION_STRATEGIES[table_strategy]

    def test_regex(self, context: PluginContext) -> str:
        """Plugin Action to test the regex pattern against existing files"""
        output = ["No regular expression was given!"]
        if self.regex != "":
            setup_cmempy_user_access(context.user)
            files_found = self.get_file_list(context.project_id)
            output = [
                f"{len(files_found)} file{'' if len(files_found) == 1 else 's'} found matching "
                f"the regular expression in the project files."
            ]
            output.extend(f"- {file}" for file in files_found)
        output.append(
            "\nThe preview does not show results from input ports as they are usually "
            "not available before the execution"
        )
        return "\n".join(output)

    @staticmethod
    def extract_pdf_data_worker(  # noqa: PLR0913
        filename: str,
        page_numbers: list,
        project_id: str,
        table_settings: dict,
        text_settings: dict,
        error_handling: str,
        file_origin: str,
    ) -> dict:
        """Extract structured PDF data (sequential processing)."""
        output: dict = {"metadata": {"Filename": filename}, "pages": []}
        binary_file: str | BytesIO
        if file_origin == "Local":
            binary_file = filename
        else:
            binary_file = BytesIO(get_resource(project_id, filename))
        page_number = None
        try:
            with pdfplumber_open(binary_file) as pdf:
                output["metadata"].update(pdf.metadata or {})
                valid_page_numbers = (
                    [_ for _ in page_numbers if _ <= len(pdf.pages)]
                    if page_numbers
                    else range(1, len(pdf.pages) + 1)
                )
                invalid_page_numbers = list(set(page_numbers) - set(valid_page_numbers))
                for page_number in valid_page_numbers:
                    try:
                        page_data = PdfExtract.process_page(
                            pdf.pages[page_number - 1],
                            page_number,
                            table_settings,
                            text_settings,
                            error_handling,
                        )
                        output["pages"].append(page_data)
                    except Exception as e:
                        if error_handling != IGNORE:
                            raise
                        output["pages"].append({"page_number": page_number, "error": str(e)})
                for page_number in invalid_page_numbers:
                    output["pages"].append(
                        {"page_number": page_number, "error": "page does not exist"}
                    )

        except Exception as e:
            if error_handling != IGNORE:
                if page_number is not None:
                    msg = f"File {filename}, page {page_number}: {e}"
                else:
                    msg = f"File {filename}: {e}"
                raise type(e)(msg) from e
            output["metadata"]["error"] = str(e)

        return output

    @staticmethod
    def process_page(
        page: Page, page_number: int, table_settings: dict, text_settings: dict, error_handling: str
    ) -> dict:
        """Process a single PDF page and return extracted content."""
        text_warning = None
        table_warning = None
        stderr_warning = None
        try:
            with capture_pdfminer_logs() as stderr:
                text = page.extract_text(**text_settings) or ""
            stderr_output = stderr.getvalue().strip()
            if not text and stderr_output:
                text_warning = f"Text extraction error: {stderr_output}"

            with capture_pdfminer_logs() as stderr:
                tables = page.extract_tables(table_settings) or []
            stderr_output = stderr.getvalue().strip()
            if not tables and stderr_output:
                table_warning = f"Table extraction error: {stderr_output}"

            if text_warning or table_warning:
                stderr_warning = (
                    f"{text_warning}, {table_warning}"
                    if text_warning and table_warning
                    else text_warning or table_warning
                )

        except Exception as e:
            if error_handling != IGNORE:
                raise
            return {"page_number": page_number, "error": str(e)}

        if stderr_warning:
            if error_handling == RAISE_ON_ERROR_AND_WARNING:
                raise ValueError(stderr_warning)
            return {
                "page_number": page_number,
                "text": text,
                "tables": tables,
                "error": stderr_warning,
            }
        return {
            "page_number": page_number,
            "text": text,
            "tables": tables,
        }

    def get_entities(self, filenames: list, file_origins: list) -> Entities:
        """Make entities from extracted PDF data across multiple files."""
        entities = []
        all_output = []

        with ProcessPoolExecutor(max_workers=self.max_processes) as executor:
            future_to_file = {
                executor.submit(
                    PdfExtract.extract_pdf_data_worker,
                    filename,
                    self.page_numbers,
                    self.context.task.project_id(),
                    self.table_strategy,
                    self.text_strategy,
                    self.error_handling,
                    file_origin,
                ): filename
                for filename, file_origin in zip(filenames, file_origins)
            }

            for i, future in enumerate(as_completed(future_to_file), start=1):
                filename = future_to_file[future]
                try:
                    if self.context.workflow.status() == "Canceling":
                        return Entities(entities=entities, schema=self.schema)
                except AttributeError:
                    pass
                try:
                    result = future.result()
                except Exception as e:
                    if self.error_handling != IGNORE:
                        raise
                    result = {"metadata": {"Filename": filename, "error": str(e)}, "pages": []}

                if self.all_files:
                    all_output.append(result)
                else:
                    entities.append(Entity(uri=f"{TYPE_URI}_{i}", values=[[str(result)]]))

                self.log.info(f"Processed file {filename} ({i}/{len(filenames)})")
                self.context.report.update(
                    ExecutionReport(
                        entity_count=i,
                        operation_desc=f"file{'' if i == 1 else 's'} processed",
                    )
                )

        if self.all_files:
            entities = [Entity(uri=f"{TYPE_URI}_1", values=[[str(all_output)]])]

        self.log.info("Finished processing all files")

        return Entities(entities=entities, schema=self.schema)

    def get_file_list(self, project_id: str) -> list:
        """Get file list using regex pattern"""
        return [r["name"] for r in get_resources(project_id) if re.fullmatch(self.regex, r["name"])]

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:
        """Run the workflow operator."""
        context.report.update(ExecutionReport(entity_count=0, operation_desc="files processed"))
        self.context = context

        if len(inputs) != 0:
            setup_cmempy_user_access(context.user)
            filenames = []
            filetypes = []
            for entity in inputs[0].entities:
                file = FileEntitySchema().from_entity(entity=entity)
                filenames.append(file.path)
                filetypes.append(file.file_type)
            return self.get_entities(filenames, filetypes)

        setup_cmempy_user_access(context.user)
        filenames = self.get_file_list(context.task.project_id())
        if not filenames:
            raise FileNotFoundError("No matching files found")
        return self.get_entities(filenames, "Project")
