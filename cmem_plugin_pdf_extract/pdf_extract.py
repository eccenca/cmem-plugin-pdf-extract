"""Extract text from PDF files"""

import re
from collections.abc import Sequence

from cmem.cmempy.workspace.projects.resources import get_resources
from cmem_plugin_base.dataintegration.context import ExecutionContext
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities, Entity, EntityPath, EntitySchema
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.types import StringParameterType
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access
from pymupdf import open as pymupdf_open


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
    ],
)
class PdfExtract(WorkflowPlugin):
    """PDF Extract plugin"""

    def __init__(self, regex: str) -> None:
        self.regex = regex

    def get_entities(self, filenames: list) -> Entities:
        """Extract text from PDF"""
        entities = []
        paths = [EntityPath(path="filename"), EntityPath(path="text")]
        schema = EntitySchema(type_uri="urn:entity", paths=paths)
        for i, filename in enumerate(filenames):
            self.log.info(f"processing file {filename}")
            pdf_path = f"/data/datalake/{self.context.task.project_id()}/resources/{filename}"
            pdf_file = pymupdf_open(pdf_path)
            text_list = [page.get_text() for page in pdf_file]
            text = "\n".join(text_list)
            values = [[filename], [text]]
            entities.append(Entity(uri=f"urn:{i + 1}", values=values))
        return Entities(entities=entities, schema=schema)

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:  # noqa: ARG002
        """Run the workflow operator."""
        self.context = context
        setup_cmempy_user_access(context.user)
        filenames = [
            r["name"]
            for r in get_resources(context.task.project_id())
            if re.match(rf"{self.regex}", r["name"])
        ]
        return self.get_entities(filenames)
