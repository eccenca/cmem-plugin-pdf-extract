"""doc"""

from pathlib import Path

with (Path(__path__[0]) / "pdf_extract_doc.md").open("r", encoding="utf-8") as f:
    DOC = f.read()
