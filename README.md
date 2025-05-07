# cmem-plugin-pdf-extract

A task to extract text and tables from PDF files.

[![eccenca Corporate Memory][cmem-shield]][cmem-link][![workflow](https://github.com/eccenca/cmem-plugin-pfd-extract/actions/workflows/check.yml/badge.svg)](https://github.com/eccenca/cmem-plugin-pfd-extract/actions) [![pypi version](https://img.shields.io/pypi/v/cmem-plugin-pdf-extract)](https://pypi.org/project/cmem-plugin-pdf-extract) [![license](https://img.shields.io/pypi/l/cmem-plugin-pdf-extract)](https://pypi.org/project/cmem-plugin-pdf-extract)
[![poetry][poetry-shield]][poetry-link] [![ruff][ruff-shield]][ruff-link] [![mypy][mypy-shield]][mypy-link] [![copier][copier-shield]][copier] 


## Output format

The output is a JSON string on the path `pdf_extract_output`. The format depends on the
["Output results of all files in one value"](#all_files) parameter.

### if False:

Outputs one entity per file:

```
{
  "metadata": {
    "Filename": "sample.pdf",
    "Title": "Sample Report",
    "Author": "eccenca GmbH",
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

### if True:
Outputs one entity for all files:

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


## Parameters

**<a id="regex">File name regex filter</a>**

Regular expression used to filter the resources of the project to be processed. Only matching file names will be included in the extraction.

**<a id="all_files">Output all file content as one value</a>**

If enabled, the results of all files will be combined into a single output value. If disabled, each file result will be output in a separate entity.

**<a id="error_handling">Error Handling Mode</a>**

Specifies how errors during PDF extraction should be handled.  
- *Ignore*: Log errors and continue processing, returning empty or error-marked results.  
- *Raise on errors*: Raise an error when extraction fails.  
- *Raise on errors and warnings*: Treat any output to STDERR from the underlying PDF extraction module as an error.

**<a id="table_strategy">Table extraction strategy</a>**

Method used to detect tables in PDF pages. Available strategies include:  
- *lines*: Uses detected lines in the PDF layout to find table boundaries.  
- *text*: Relies on text alignment and spacing.  
- *custom*: Allows custom settings to be provided via the advanced parameter below.

**<a id="custom_table_strategy">Custom table extraction strategy</a>**

Defines a custom table extraction strategy using YAML syntax. Only used if "custom" is selected as the table strategy.

**<a id="max_processes">Maximum number of processes for processing files</a>**

Defines the maximum number of processes to use for concurrent file processing. By default, this is set to (number of virtual cores - 1).


## Test regular expression

Clicking the "Test regex pattern" button displays the number of files in the current project that match the regular expression
specified with the ["File name regex filter"](#parameter_doc_regex) parameter.


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
