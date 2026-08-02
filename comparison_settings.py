# runtime comparison behavior

from dataclasses import dataclass


@dataclass
class ComparisonSettings:
    ignore_case: bool = False
    ignore_punctuation: bool = False
    ignore_whitespace: bool = False
    ignore_quotes: bool = False
    ignore_dashes: bool = False

    ignore_headers: bool = False
    ignore_footers: bool = False
    ignore_page_numbers: bool = False

    similarity_threshold: int = 90
    debug_matching: bool = True