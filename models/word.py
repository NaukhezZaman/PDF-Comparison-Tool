from dataclasses import dataclass


@dataclass
class Word:
    text: str
    bbox: list
    block: int
    line: int
    word: int