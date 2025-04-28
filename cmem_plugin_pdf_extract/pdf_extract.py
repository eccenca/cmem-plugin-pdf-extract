"""Extract text from PDF files"""

import re
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from io import BytesIO
from os import cpu_count

from cmem.cmempy.workspace.projects.resources import get_resources
from cmem.cmempy.workspace.projects.resources.resource import get_resource
from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities, Entity, EntityPath, EntitySchema
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.types import (
    BoolParameterType,
    IntParameterType,
    StringParameterType,
)
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access
from pdfplumber import open as pdfplumber_open
from pdfplumber.page import Page

MAX_PROCESSES_DEFAULT = cpu_count() - 1  # type: ignore[operator]


@Plugin(
    label="Extract text from PDF",
    description="",
    documentation="",
    icon=Icon(package=__package__, file_name="ic--baseline-picture-as-pdf.svg"),
    parameters=[
        PluginParameter(
            param_type=StringParameterType(),
            name="regex",
            label="File name regex filter",
            description="Regular expression for filtering resources of the project.",
        ),
        PluginParameter(
            param_type=BoolParameterType(),
            name="all_files",
            label="Output all file content as one value",
            description="Output the content of all files as one value.",
            default_value=False,
        ),
        PluginParameter(
            param_type=BoolParameterType(),
            name="strict",
            label="Strict mode",
            description="""If True, the script will raise an error on any failure during file or
            page processing. If False, it will log the error and continue, returning empty or
            error-marked results for failed items.""",
            default_value=True,
        ),
        PluginParameter(
            param_type=IntParameterType(),
            name="max_retries",
            label="Maximum number of retries",
            description="""The number of times to retry processing a file or page after a failure
            before giving up and handling it according to strict mode.""",
            default_value=3,
            advanced=True,
        ),
        PluginParameter(
            param_type=IntParameterType(),
            name="max_threads",
            label="Maximum number of threads for processing pages",
            description="""The maximum number of threads to use for processing pages within a single
            file.""",
            advanced=True,
            default_value=4,
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

    def __init__(
        self,
        regex: str,
        all_files: bool = False,
        strict: bool = True,
        max_threads: int = 4,
        max_processes: int = MAX_PROCESSES_DEFAULT,
    ) -> None:
        self.regex = regex
        self.all_files = all_files
        self.strict = strict
        self.max_threads = max_threads
        self.max_processes = max_processes

        self.input_ports = FixedNumberOfInputs([])
        self.schema = EntitySchema(type_uri="urn:extract", paths=[EntityPath("output")])
        self.output_port = FixedSchemaPort(self.schema)

    @staticmethod
    def extract_pdf_data_worker(
        filename: str, project_id: str, strict: bool, max_threads: int
    ) -> dict:
        """Extract structured PDF data (with multithreading inside)."""
        output: dict = {"metadata": {"Filename": filename}, "pages": []}
        binary_file = BytesIO(get_resource(project_id, filename))

        try:
            with pdfplumber_open(binary_file) as pdf:
                output["metadata"].update(pdf.metadata or {})  # type: ignore[attr-defined]

                with ThreadPoolExecutor(max_workers=max_threads) as executor:
                    futures = {
                        executor.submit(PdfExtract.process_page, page, i + 1): i
                        for i, page in enumerate(pdf.pages)
                    }
                    for future in as_completed(futures):
                        output["pages"].append(future.result())

        except Exception as e:
            if strict:
                raise
            output["metadata"]["error"] = str(e)
            output["pages"] = []

        return output

    @staticmethod
    def process_page(page: Page, page_number: int) -> dict:
        """Process a single PDF page and return extracted content."""
        try:
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            return {
                "page_number": page_number,
                "text": text,
                "tables": tables,
            }
        except Exception as e:
            return {"page_number": page_number, "error": str(e)}

    def get_entities(self, filenames: list) -> Entities:
        """Make entities from extracted PDF data across multiple files."""
        entities = []
        all_output = []

        with ProcessPoolExecutor(max_workers=self.max_processes) as executor:
            future_to_file = {
                executor.submit(
                    PdfExtract.extract_pdf_data_worker,
                    filename,
                    self.context.task.project_id(),
                    self.strict,
                    self.max_threads,
                ): filename
                for filename in filenames
            }

            for i, future in enumerate(as_completed(future_to_file), start=1):
                filename = future_to_file[future]
                try:
                    result = future.result()
                except Exception as e:
                    if self.strict:
                        raise
                    result = {"metadata": {"Filename": filename, "error": str(e)}, "pages": []}

                if self.all_files:
                    all_output.append(result)
                else:
                    entities.append(Entity(uri=f"urn:output_{i}", values=[[str(result)]]))

                self.log.info(f"Processed file {filename} ({i}/{len(filenames)})")
                operation_desc = "files processed" if i != 1 else "file processed"
                self.context.report.update(
                    ExecutionReport(entity_count=i, operation_desc=operation_desc)
                )

        if self.all_files:
            entities = [Entity(uri="urn:output", values=[[str(all_output)]])]

        self.log.info("Finished processing all files")

        return Entities(entities=entities, schema=self.schema)

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:  # noqa: ARG002
        """Run the workflow operator."""
        context.report.update(ExecutionReport(entity_count=0, operation_desc="files processed"))
        self.context = context
        setup_cmempy_user_access(context.user)
        filenames = [
            r["name"]
            for r in get_resources(context.task.project_id())
            if re.match(rf"{self.regex}", r["name"])
        ]
        return self.get_entities(filenames)
