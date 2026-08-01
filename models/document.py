from dataclasses import dataclass, field


@dataclass
class PDFDocument:

    file_name: str

    page_count: int

    pages: list = field(default_factory=list)