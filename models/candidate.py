from dataclasses import dataclass

@dataclass
class Candidate:
    source_word: dict
    target_index: int
    target_word: dict

    distance: float

    similarity: float = 0
    confidence: float = 0

    # NEW
    source_index: int = -1
    reading_order_score: float = 0
    line_score: int = 0

    selected: bool = False

    def __repr__(self):
        return (
            f"Candidate("
            f"source='{self.source_word['text']}', "
            f"target='{self.target_word['text']}', "
            f"distance={self.distance:.2f}, "
            f"similarity={self.similarity:.2f}, "
            f"confidence={self.confidence:.2f}, "
            f"source_index={self.source_index}, "
            f"target_index={self.target_index}, "
            f"reading_order={self.reading_order_score:.2f}, "
            f"source_line={self.source_word['line']}, "
            f"target_line={self.target_word['line']}, "
            f"line_score={self.line_score}, "
            f"selected={self.selected}"
            f")"
        )