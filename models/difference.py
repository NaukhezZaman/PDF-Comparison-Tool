from dataclasses import dataclass


@dataclass
class Difference:

    page: int

    block: int

    line: int

    word: int

    difference_type: str

    source_text: str

    target_text: str

    source_bbox: list | None

    target_bbox: list | None

    distance: float