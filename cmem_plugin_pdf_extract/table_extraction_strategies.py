"""pdfplumber table extraction strategies"""

LINES_STRATEGY = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "intersection_tolerance": 5,
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 1,
    "min_words_horizontal": 1,
}

TEXT_STRATEGY = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    "intersection_tolerance": 5,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 1,
    "min_words_horizontal": 1,
}


TABLE_EXTRACTION_STRATEGIES = {
    "lines": LINES_STRATEGY,
    "text": TEXT_STRATEGY,
}

CUSTOM_TABLE_STRATEGY_DEFAULT = """# {
#     "vertical_strategy": "lines",
#     "horizontal_strategy": "lines",
#     "intersection_tolerance": 5,
#     "snap_tolerance": 3,
#     "join_tolerance": 3,
#     "edge_min_length": 3,
#     "min_words_vertical": 1,
#     "min_words_horizontal": 1
# }"""
