A task to extract text and tables from PDF files.

## Output format

The output is a JSON string on the path `pdf_extract_output`. The format depends on the
["Output results of all files in one value"](#parameter_doc_all_files) parameter.

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

**<a id="parameter_doc_regex">File name regex filter</a>**

Regular expression used to filter the resources of the project to be processed. Only matching file names will be included in the extraction.

**<a id="page_selection">Page selection</a>**

Comma-separated page numbers or ranges (e.g., 1,2-5,7) for page selection. Files that do not contain any of the specified pages will return
empty results with the information logged. If no page selection is specified, all pages will be processed.

**<a id="parameter_doc_all_files">Output all file content as one value</a>**

If enabled, the results of all files will be combined into a single output value. If disabled, each file result will be output in a separate entity.

**<a id="parameter_doc_error_handling">Error Handling Mode</a>**

Specifies how errors during PDF extraction should be handled.  
- *Ignore*: Log errors and continue processing, returning empty or error-marked results.  
- *Raise on errors*: Raise an error when extraction fails.  
- *Raise on errors and warnings*: Treat any output to STDERR from the underlying PDF extraction module as an error.

**<a id="parameter_doc_table_strategy">Table extraction strategy</a>**

Method used to detect tables in PDF pages. Available strategies include:  
- *lines*: Uses detected lines in the PDF layout to find table boundaries.  
- *text*: Relies on text alignment and spacing.  
- *custom*: Allows custom settings to be provided via the advanced parameter below.

**<a id="parameter_doc_custom_table_strategy">Custom table extraction strategy</a>**

Defines a custom table extraction strategy using YAML syntax. Only used if "custom" is selected as the table strategy.

**<a id="parameter_doc_max_processes">Maximum number of processes for processing files</a>**

Defines the maximum number of processes to use for concurrent file processing. By default, this is set to (number of virtual cores - 1).
