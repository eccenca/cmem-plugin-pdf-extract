# cmem-plugin-pdf-extract

Extract text from PDF files

[![eccenca Corporate Memory][cmem-shield]][cmem-link][![workflow](https://github.com/eccenca/cmem-plugin-pfd-extract/actions/workflows/check.yml/badge.svg)](https://github.com/eccenca/cmem-plugin-pfd-extract/actions) [![pypi version](https://img.shields.io/pypi/v/cmem-plugin-pdf-extract)](https://pypi.org/project/cmem-plugin-pdf-extract) [![license](https://img.shields.io/pypi/l/cmem-plugin-pdf-extract)](https://pypi.org/project/cmem-plugin-pdf-extract)
[![poetry][poetry-shield]][poetry-link] [![ruff][ruff-shield]][ruff-link] [![mypy][mypy-shield]][mypy-link] [![copier][copier-shield]][copier] 



### all_files = False:

Outputs entities with the extracted data from each file on the path `output` as string in the format of a JSON object:

```
{
  "metadata": {
    "Filename": "sample.pdf",
    "Title": "Sample Report",
    "Author": "ACME Inc.",
    ...
  },
  "pages": [
    {
      "page_number": 1,
      "text": "This is digital text from the PDF.",
      "tables": [...]
    },
    {
      "page_number": 2,
      "text": "",
      "tables": []
    },
    ...
  ]
}
```

### all_files = True:
Outputs one entoty with the extracted data from all files the path `output` as string in the format of a JSON object:

```
[
    {
        "metadata": {"Filename": "file1.pdf", ...},
        "pages": [...]
    },
    {
        "metadata": {"Filename": "file2.pdf", ...},
        "pages": [...]
    },
    ...
]
```

## Development

- Run [task](https://taskfile.dev/) to see all major development tasks.
- Use [pre-commit](https://pre-commit.com/) to avoid errors before commit.
- This repository was created with [this copier template](https://github.com/eccenca/cmem-plugin-template).

[cmem-link]: https://documentation.eccenca.com
[cmem-shield]: https://img.shields.io/endpoint?url=https://dev.documentation.eccenca.com/badge.json
[poetry-link]: https://python-poetry.org/
[poetry-shield]: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json
[ruff-link]: https://docs.astral.sh/ruff/
[ruff-shield]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&label=Code%20Style
[mypy-link]: https://mypy-lang.org/
[mypy-shield]: https://www.mypy-lang.org/static/mypy_badge.svg
[copier]: https://copier.readthedocs.io/
[copier-shield]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json
