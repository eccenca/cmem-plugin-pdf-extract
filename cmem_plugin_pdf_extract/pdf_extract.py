"""Random values workflow plugin module

Remove this and other example files after bootstrapping your project.
"""

import re
from collections.abc import Sequence
from pathlib import Path

import PyPDF2
from cmem.cmempy.workspace.projects.resources import get_all_resources
from cmem_plugin_base.dataintegration.context import ExecutionContext
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntityPath,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.types import StringParameterType
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access


def extract_pdf_text(pdf_path: str) -> str:
    """Extrahiert den Text aus einer PDF-Datei."""
    text = ""
    with Path(pdf_path).open("rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


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

    def get_entities(self, resources: list) -> Entities:
        """Extract text from PDF"""
        entities = []

        paths = [
            EntityPath(path="filename"),
            EntityPath(path="text"),
        ]

        schema = EntitySchema(type_uri="urn:row", paths=paths)

        for i, resource in enumerate(resources):
            filename = resource["name"]
            self.log.info(f"processing file {filename}")
            pdf_file = (
                Path("/data/datalake") / self.context.task.project_id() / "resources" / filename
            )
            text = extract_pdf_text(pdf_file)
            values = [
                [filename],
                [text],
            ]
            entities.append(Entity(uri=f"urn:{i + 1}", values=values))
        return Entities(entities=entities, schema=schema)

    def execute(
        self,
        inputs: Sequence[Entities],  # noqa: ARG002
        context: ExecutionContext,
    ) -> Entities:
        """Run the workflow operator."""
        self.context = context
        setup_cmempy_user_access(context.user)
        resources = [r for r in get_all_resources() if re.match(rf"{self.regex}", r["name"])]

        return self.get_entities(resources)
