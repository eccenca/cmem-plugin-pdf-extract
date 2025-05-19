"""pdfplumber text extraction strategies"""

# =================================================================
# Text Extraction Presets (All parameters explicitly defined)
# =================================================================

# -----------------------------------------------------------------
# Default Extraction (Balanced for most digital PDFs)
# -----------------------------------------------------------------

DEFAULT_TEXT_EXTRACTION = {
    # Text Merging
    "x_tolerance": 1,  # Horizontal merge threshold (px)
    "y_tolerance": 1,  # Vertical merge threshold (px)
    # Spatial Analysis
    "x_density": 7.25,  # Characters per inch (horizontal)
    "y_density": 13,  # Characters per inch (vertical)
    # Layout Control
    "layout": False,  # Disable advanced layout analysis
    # "layout_bbox": None,  # No bounding box restriction  # noqa: ERA001
    "layout_width": None,
    "layout_height": None,
    "layout_x0": None,
    "layout_x1": None,
    "layout_y0": None,
    "layout_y1": None,
    # Text Handling
    "keep_blank_chars": False,  # Discard empty chars
    "use_text_flow": False,  # Physical text order
    "horizontal_ltr": True,  # Left-to-right reading
    "vertical_ttb": True,  # Top-to-bottom reading
    # Metadata
    "extra_attrs": [],  # No extra attributes
    "split_at_punctuation": False,
}

# -----------------------------------------------------------------
# Scanned PDFs (Aggressive text merging for OCR'd documents)
# -----------------------------------------------------------------
SCANNED_TEXT_EXTRACTION = {
    # Text Merging (Looser thresholds)
    "x_tolerance": 3,  # Wider horizontal merging
    "y_tolerance": 3,  # Wider vertical merging
    # Spatial Analysis (Same as default)
    "x_density": 7.25,
    "y_density": 13,
    # Layout Control (Same as default)
    "layout": False,
    "layout_bbox": None,
    "layout_width": None,
    "layout_height": None,
    "layout_x0": None,
    "layout_x1": None,
    "layout_y0": None,
    "layout_y1": None,
    # Text Handling
    "keep_blank_chars": True,  # Preserve whitespace
    "use_text_flow": False,  # Physical order
    "horizontal_ltr": True,
    "vertical_ttb": True,
    # Metadata
    "extra_attrs": [],
    "split_at_punctuation": False,
}

# -----------------------------------------------------------------
# Layout-Aware Extraction (For complex/multi-column documents)
# -----------------------------------------------------------------
LAYOUT_AWARE_EXTRACTION = {
    # Text Merging (Precise)
    "x_tolerance": 1,
    "y_tolerance": 1,
    # Spatial Analysis (Same as default)
    "x_density": 7.25,
    "y_density": 13,
    # Layout Control (Enabled)
    "layout": True,  # Enable layout analysis
    "layout_bbox": None,
    "layout_width": None,
    "layout_height": None,
    "layout_x0": None,
    "layout_x1": None,
    "layout_y0": None,
    "layout_y1": None,
    # Text Handling
    "keep_blank_chars": False,
    "use_text_flow": True,  # Logical reading order
    "horizontal_ltr": True,
    "vertical_ttb": True,
    # Metadata
    "extra_attrs": ["fontname", "size"],  # Capture font data
    "split_at_punctuation": True,  # Split at punctuation
}

# -----------------------------------------------------------------
# Raw Extraction (No merging, for debugging text positions)
# -----------------------------------------------------------------
RAW_TEXT_EXTRACTION = {
    # Text Merging (Disabled)
    "x_tolerance": 0,  # No horizontal merging
    "y_tolerance": 0,  # No vertical merging
    # Spatial Analysis (Same as default)
    "x_density": 7.25,
    "y_density": 13,
    # Layout Control (Same as default)
    "layout": False,
    "layout_bbox": None,
    "layout_width": None,
    "layout_height": None,
    "layout_x0": None,
    "layout_x1": None,
    "layout_y0": None,
    "layout_y1": None,
    # Text Handling
    "keep_blank_chars": True,  # Keep all whitespace
    "use_text_flow": False,  # Physical order
    "horizontal_ltr": True,
    "vertical_ttb": True,
    # Metadata
    "extra_attrs": [],
    "split_at_punctuation": False,
}

TEXT_EXTRACTION_STRATEGIES = {
    "default": DEFAULT_TEXT_EXTRACTION,
    "raw": RAW_TEXT_EXTRACTION,
    "scanned": SCANNED_TEXT_EXTRACTION,
    "layout": LAYOUT_AWARE_EXTRACTION,
}
