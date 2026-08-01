from dataclasses import dataclass


@dataclass
class Block:
    block_no: int
    text: str
    bbox: list