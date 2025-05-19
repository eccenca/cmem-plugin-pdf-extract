"""pdfplumber table extraction strategies"""
# -----------------------------------------------------------------
# Lines Strategy (Default - For PDFs with visible grid lines)
# -----------------------------------------------------------------

LINES_STRATEGY = {
    # Detection Strategies
    "vertical_strategy": "lines",  # Detect vertical cell borders
    "horizontal_strategy": "lines",  # Detect horizontal cell borders
    # Explicit Line Coordinates
    "explicit_vertical_lines": [],  # User-defined vertical lines
    "explicit_horizontal_lines": [],  # User-defined horizontal lines
    # Line Snapping
    "snap_tolerance": 3,  # Max distance to snap to a line (px)
    "snap_x_tolerance": 3,  # Horizontal snap tolerance
    "snap_y_tolerance": 3,  # Vertical snap tolerance
    # Line Joining
    "join_tolerance": 3,  # Max distance to join lines (px)
    "join_x_tolerance": 3,  # Horizontal join tolerance
    "join_y_tolerance": 3,  # Vertical join tolerance
    # Edge Processing
    "edge_min_length": 3,  # Minimum edge length to consider (px)
    # Text-Based Detection Thresholds
    "min_words_vertical": 3,  # Min words to infer vertical line
    "min_words_horizontal": 1,  # Min words to infer horizontal line
    # Intersection Handling
    "intersection_tolerance": 3,  # Max intersection distance
    "intersection_x_tolerance": 3,  # Horizontal intersection
    "intersection_y_tolerance": 3,  # Vertical intersection
    # Text Extraction Settings
    "text_settings": {
        "x_tolerance": 2,
        "y_tolerance": 2,
        "keep_blank_chars": False,
        "use_text_flow": False,
        "horizontal_ltr": True,
        "vertical_ttb": True,
        "extra_attrs": [],
    },
}

# -----------------------------------------------------------------
# Text Strategy (For borderless/whitespace-separated tables)
# -----------------------------------------------------------------
TEXT_STRATEGY = {
    # Detection Strategies
    "vertical_strategy": "text",  # Infer columns from text gaps
    "horizontal_strategy": "text",  # Infer rows from text lines
    # Explicit Line Coordinates
    "explicit_vertical_lines": [],
    "explicit_horizontal_lines": [],
    # Line Snapping (Same as default)
    "snap_tolerance": 3,
    "snap_x_tolerance": 3,
    "snap_y_tolerance": 3,
    # Line Joining (Same as default)
    "join_tolerance": 3,
    "join_x_tolerance": 3,
    "join_y_tolerance": 3,
    # Edge Processing (Same as default)
    "edge_min_length": 3,
    # Text-Based Detection Thresholds (More sensitive)
    "min_words_vertical": 1,  # Detect single-word columns
    "min_words_horizontal": 1,
    # Intersection Handling (Same as default)
    "intersection_tolerance": 3,
    "intersection_x_tolerance": 3,
    "intersection_y_tolerance": 3,
    # Text Extraction Settings (Tighter merging)
}

# -----------------------------------------------------------------
# Lattice Strategy (For machine-generated perfect grids)
# -----------------------------------------------------------------
LATTICE_STRATEGY = {
    # Detection Strategies
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    # Explicit Line Coordinates
    "explicit_vertical_lines": [],
    "explicit_horizontal_lines": [],
    # Line Snapping (Strict)
    "snap_tolerance": 1,  # Tighter snapping
    "snap_x_tolerance": 1,
    "snap_y_tolerance": 1,
    # Line Joining (Strict)
    "join_tolerance": 1,  # No gaps allowed
    "join_x_tolerance": 1,
    "join_y_tolerance": 1,
    # Edge Processing
    "edge_min_length": 5,  # Ignore short edges
    # Text-Based Detection Thresholds
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
    # Intersection Handling (Strict)
    "intersection_tolerance": 1,
    "intersection_x_tolerance": 1,
    "intersection_y_tolerance": 1,
    # Text Extraction Settings (Precise)
    "text_settings": {
        "x_tolerance": 1,
        "y_tolerance": 1,
        "keep_blank_chars": False,
        "use_text_flow": False,
        "horizontal_ltr": True,
        "vertical_ttb": True,
        "extra_attrs": [],
    },
}

# -----------------------------------------------------------------
# Sparse Strategy (For tables with minimal text content)
# -----------------------------------------------------------------
SPARSE_STRATEGY = {
    # Detection Strategies
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    # Explicit Line Coordinates
    "explicit_vertical_lines": [],
    "explicit_horizontal_lines": [],
    # Line Snapping (Same as default)
    "snap_tolerance": 3,
    "snap_x_tolerance": 3,
    "snap_y_tolerance": 3,
    # Line Joining (Same as default)
    "join_tolerance": 3,
    "join_x_tolerance": 3,
    "join_y_tolerance": 3,
    # Edge Processing (Same as default)
    "edge_min_length": 3,
    # Text-Based Detection Thresholds (Sensitive)
    "min_words_vertical": 1,
    "min_words_horizontal": 1,
    # Intersection Handling (Same as default)
    "intersection_tolerance": 3,
    "intersection_x_tolerance": 3,
    "intersection_y_tolerance": 3,
    # Text Extraction Settings (Looser merging)
}


TABLE_EXTRACTION_STRATEGIES = {
    "lines": LINES_STRATEGY,
    "text": TEXT_STRATEGY,
    "lattice": LATTICE_STRATEGY,
    "sparse": SPARSE_STRATEGY,
}

CUSTOM_TABLE_STRATEGY_DEFAULT = """# vertical_strategy: lines
# horizontal_strategy: lines
# intersection_tolerance: 5
# snap_tolerance: 3
# join_tolerance: 3
# edge_min_length: 3
# min_words_vertical: 1
# min_words_horizontal: 1
"""
