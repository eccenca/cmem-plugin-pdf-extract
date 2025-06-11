A task to extract text and tables from PDF files.

## Output format

The output is a JSON string on the path `pdf_extract_output`. The format depends on the
["Combine the results from all files into a single value"](#parameter_doc_all_files) parameter.


### Output one entity/value per file

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


### Output one entity/value for all files

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

## Input format

This task can either work with project files when a regular expression is being used or with
entities coming from another task or dataset. 
The input must be file entities following the [FileEntitySchema](https://github.com/eccenca/cmem-plugin-base/blob/main/cmem_plugin_base/dataintegration/typed_entities/file.py).
If a regular expression is set, the input ports will close and no connection will be possible.


## Parameters

**<a id="parameter_doc_regex">File name regex filter</a>**

Regular expression used to filter the resources of the project to be processed. Only matching file names will be included in the extraction.

**<a id="page_selection">Page selection</a>**

Comma-separated page numbers or ranges (e.g., 1,2-5,7) for page selection. Files that do not contain any of the specified pages will return
empty results with the information logged. If no page selection is specified, all pages will be processed.

**<a id="parameter_doc_all_files">Combine the results from all files into a single value</a>**

If set to "Combine", the results of all files will be combined into a single output value. If set to "Don't combine", each file result will be output in a separate entity.

**<a id="parameter_doc_error_handling">Error Handling Mode</a>**

Specifies how errors during PDF extraction should be handled.  
- *Ignore*: Log errors and continue processing, returning empty or error-marked results.  
- *Raise on errors*: Raise an error when extraction fails.  
- *Raise on errors and warnings*: Treat any warning from the underlying PDF extraction module (pdfplumber) when extracting text and tables from pages as an error if empty results are returned.

**<a id="parameter_doc_table_strategy">Table extraction strategy</a>**

Method used to detect tables in PDF pages. For further explanation click [here](https://github.com/jsvine/pdfplumber/blob/stable/README.md#extracting-tables).

Available strategies include:  
- *lines*: Uses detected lines in the PDF layout to find table boundaries.  
- *text*: Relies on text alignment and spacing.
- *lattice*: Best for machine-generated perfect grids.
- *sparse*: Best for tables with minimal text content.
- *custom*: Allows custom settings to be provided via the advanced parameter below.

**<a id="parameter_doc_custom_table_strategy">Custom table extraction strategy</a>**

Defines a custom table extraction strategy using YAML syntax. Only used if "custom" is selected as the table strategy.

**<a id="parameter_doc_text_strategy">Text extraction strategy</a>**

Method used to extract text in PDF pages. For further explanation click [here](https://github.com/jsvine/pdfplumber/blob/stable/README.md#extracting-text). 

Available strategies include:
- *default*: Balanced for most digital PDFs.
- *raw*: Extract the PDFs with no merging of text fragments.
- *scanned*: Best for scanned PDFs as it merges text more agressively.
- *layout*: Layout-aware extraction for complex/multi-column documents

**<a id="parameter_doc_max_processes">Maximum number of processes for processing files</a>**

Defines the maximum number of processes to use for concurrent file processing. By default, this is set to (number of virtual cores - 1).


## Test regular expression

Clicking the "Test regex pattern" button displays the files in the current project that match the regular expression
specified with the ["File name regex filter"](#parameter_doc_regex) parameter.
This does not display the files if there is another dataset or task connected to the input
as the entities are not known before execution.
