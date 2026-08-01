import math
import string

from loader import PDFLoader
from config import (
    SOURCE_JSON,
    TARGET_JSON,
    MAX_MATCH_DISTANCE
)

from models.match import Match
from models.difference import Difference
from rapidfuzz import fuzz
from comparison_settings import ComparisonSettings

class PDFMatcher:

    def __init__(self):

        self.source = None
        self.target = None
        self.settings = ComparisonSettings()

    def normalize_text(self, text):

        normalized_text = text

        if self.settings.ignore_case:
            normalized_text = self.normalize_case(normalized_text)

        if self.settings.ignore_quotes:
            normalized_text = self.normalize_quotes(normalized_text)

        if self.settings.ignore_dashes:
            normalized_text = self.normalize_dashes(normalized_text)

        if self.settings.ignore_punctuation:
            normalized_text = self.normalize_punctuation(normalized_text)

        if self.settings.ignore_whitespace:
            normalized_text = self.normalize_whitespace(normalized_text)

        return normalized_text

    def normalize_case(self, text):

        return text.lower()

    def normalize_punctuation(self, text):

        normalized_text = ""

        for index, char in enumerate(text):

            # Keep apostrophes
            if char == "'":
                normalized_text += char
                continue

            # Keep decimal points between digits
            if (
                    char == "."
                    and index > 0
                    and index < len(text) - 1
                    and text[index - 1].isdigit()
                    and text[index + 1].isdigit()
            ):
                normalized_text += char
                continue

            # Skip punctuation
            if char in string.punctuation:
                continue

            normalized_text += char

        return normalized_text

    def normalize_whitespace(self, text):

        return " ".join(text.split())

    def normalize_quotes(self, text):

        quote_mapping = {

            "“": '"',
            "”": '"',

            "‘": "'",
            "’": "'"
        }

        normalized_text = ""

        for char in text:
            normalized_text += quote_mapping.get(char, char)

        return normalized_text

    def normalize_dashes(self, text):

        dash_mapping = {

            "‐": "-",
            "-": "-",
            "–": "-",
            "—": "-",
            "−": "-"
        }

        normalized_text = ""

        for char in text:
            normalized_text += dash_mapping.get(char, char)

        return normalized_text

    def calculate_similarity(self, source_text, target_text):

        source_text = self.normalize_text(source_text)
        target_text = self.normalize_text(target_text)

        return fuzz.ratio(source_text, target_text)

    def calculate_confidence(self, similarity, distance):

        distance_score = max(0, 100 - (distance * 3))

        confidence = (similarity + distance_score) / 2

        return round(confidence, 2)

    # --------------------------------------------------------

    def load_documents(self):

        self.source = PDFLoader(SOURCE_JSON).load()

        self.target = PDFLoader(TARGET_JSON).load()

        print("\nJSON loaded successfully.")

    # --------------------------------------------------------

    @staticmethod
    def get_center(bbox):

        x0, y0, x1, y1 = bbox

        return (
            (x0 + x1) / 2,
            (y0 + y1) / 2
        )

    # --------------------------------------------------------

    def distance(self, bbox1, bbox2):

        x1, y1 = self.get_center(bbox1)

        x2, y2 = self.get_center(bbox2)

        return math.sqrt(
            (x1 - x2) ** 2 +
            (y1 - y2) ** 2
        )

    # --------------------------------------------------------

    def match_page(self, source_page, target_page):

        matches = []

        target_words = target_page["words"]

        # Keeps track of which target words are already matched
        matched_target_indices = set()

        # Enumerate gives us both the index and the word
        for source_index, source_word in enumerate(source_page["words"]):

            nearest = None
            nearest_distance = float("inf")
            nearest_target_index = None

            # Iterate through target words with their index
            for target_index, target_word in enumerate(target_words):

                # Skip target words that are already matched
                if target_index in matched_target_indices:
                    continue

                d = self.distance(
                    source_word["bbox"],
                    target_word["bbox"]
                )

                if d < nearest_distance:
                    nearest_distance = d
                    nearest = target_word
                    nearest_target_index = target_index

            # Accept the match only if it is within the threshold
            if (
                    nearest_target_index is not None
                    and nearest_distance <= MAX_MATCH_DISTANCE
            ):

                matched_target_indices.add(nearest_target_index)

            else:

                nearest = None
                nearest_target_index = None
                nearest_distance = float("inf")

            similarity = 0
            confidence = 0

            if nearest is not None:
                similarity = self.calculate_similarity(
                    source_word["text"],
                    nearest["text"]
                )

                confidence = self.calculate_confidence(
                    similarity,
                    nearest_distance
                )

            matches.append(
                Match(
                    page=source_page["page_number"],
                    source_index=source_index,
                    target_index=nearest_target_index,
                    source_word=source_word,
                    target_word=nearest,
                    distance=nearest_distance,
                    similarity=similarity,
                    confidence=confidence
                )
            )

        return matches

    # --------------------------------------------------------

    def match_documents(self, settings=None):
        if settings is not None:
            self.settings = settings
        all_matches = []

        for source_page, target_page in zip(
                self.source["pages"],
                self.target["pages"]
        ):
            page_matches = self.match_page(
                source_page,
                target_page
            )

            all_matches.extend(page_matches)

        return all_matches
    # --------------------------------------------------------

    def print_match_metrics(self, matches):

        print("\nMatch Metrics")
        print("-" * 90)

        for match in matches:

            if match.target_word is None:
                print(
                    f"DELETED CANDIDATE : {match.source_word['text']}"
                )

                continue

            if match.source_word["text"] != match.target_word["text"]:
                print(
                    f"{match.source_word['text']:20}"
                    f" -> "
                    f"{match.target_word['text']:20}"
                    f"| Distance = {match.distance:6.2f}"
                    f"| Similarity = {match.similarity:6.2f}"
                )
        # -------------------------------------------------------

    def detect_differences(self, matches):

        differences = []

        same = 0
        modified = 0
        inserted = 0
        deleted = 0

        # Track matched target words page-wise
        matched_targets = {}

        for match in matches:

            page = match.page

            if page not in matched_targets:
                matched_targets[page] = set()

            if match.target_index is not None:
                matched_targets[page].add(match.target_index)

            source_text = match.source_word["text"]

            # -----------------------------
            # Deleted Word
            # -----------------------------
            if match.target_word is None:
                deleted += 1

                differences.append(

                    Difference(

                        page=match.page,

                        block=match.source_word["block"],

                        line=match.source_word["line"],

                        word=match.source_word["word"],

                        difference_type="DELETED",

                        source_text=source_text,

                        target_text="",

                        source_bbox=match.source_word["bbox"],

                        target_bbox=None,

                        distance=0
                    )
                )

                continue

            target_text = match.target_word["text"]

            # -----------------------------
            # Normalize both texts
            # -----------------------------
            normalized_source = self.normalize_text(source_text)
            normalized_target = self.normalize_text(target_text)

            # -----------------------------
            # Same Word
            # -----------------------------
            if normalized_source == normalized_target:
                same += 1
                continue

            # -----------------------------
            # Modified Word
            # -----------------------------
            modified += 1

            differences.append(

                Difference(

                    page=page,

                    block=match.source_word["block"],

                    line=match.source_word["line"],

                    word=match.source_word["word"],

                    difference_type="MODIFIED",

                    source_text=source_text,

                    target_text=target_text,

                    source_bbox=match.source_word["bbox"],

                    target_bbox=match.target_word["bbox"],

                    distance=match.distance
                )

            )

        # ------------------------------------------------------
        # Detect inserted words
        # ------------------------------------------------------

        for target_page in self.target["pages"]:

            page_number = target_page["page_number"]

            matched = matched_targets.get(page_number, set())

            for target_index, target_word in enumerate(target_page["words"]):

                if target_index in matched:
                    continue

                inserted += 1

                differences.append(

                    Difference(

                        page=page_number,

                        block=target_word["block"],

                        line=target_word["line"],

                        word=target_word["word"],

                        difference_type="INSERTED",

                        source_text="",

                        target_text=target_word["text"],

                        source_bbox=None,

                        target_bbox=target_word["bbox"],

                        distance=0
                    )

                )

        differences.sort(
            key=lambda diff: (
                diff.page,
                diff.block,
                diff.line,
                diff.word
            )
        )

        print("\nComparison Summary")
        print("-" * 40)
        print(f"Same Words      : {same}")
        print(f"Modified Words  : {modified}")
        print(f"Inserted Words  : {inserted}")
        print(f"Deleted Words   : {deleted}")
        print("-" * 40)

        return differences
    # --------------------------------------------------------

    def print_differences(self, differences):

        print("\nDetected Differences\n")

        for diff in differences:

            if diff.difference_type == "MODIFIED":

                print(
                    f"[MODIFIED] "
                    f"{diff.source_text}"
                    f" ---> "
                    f"{diff.target_text}"
                    f" | Page={diff.page}"
                    f" Block={diff.block}"
                    f" Line={diff.line}"
                    f" Word={diff.word}"
                )

            elif diff.difference_type == "INSERTED":

                print(
                    f"[INSERTED] "
                    f"{diff.target_text}"
                    f" | Page={diff.page}"
                    f" Block={diff.block}"
                    f" Line={diff.line}"
                    f" Word={diff.word}"
                )

            elif diff.difference_type == "DELETED":

                print(
                    f"[DELETED] "
                    f"{diff.source_text}"
                    f" | Page={diff.page}"
                    f" Block={diff.block}"
                    f" Line={diff.line}"
                    f" Word={diff.word}"
                )

