from dataclasses import dataclass, field


@dataclass
class PageData:

    page_number: int

    width: float

    height: float

    words: list = field(default_factory=list)

    blocks: list = field(default_factory=list)

    images: list = field(default_factory=list)

    drawings: list = field(default_factory=list)