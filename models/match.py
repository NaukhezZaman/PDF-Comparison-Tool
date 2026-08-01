from dataclasses import dataclass


@dataclass
class Match:

    page: int

    source_index: int

    target_index: int

    source_word: dict

    target_word: dict

    distance: float

    similarity: float

    confidence: float