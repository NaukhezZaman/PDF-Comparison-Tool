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
from models.candidate import Candidate

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

    def filter_candidates(self, candidates):

        valid_candidates = []

        for candidate in candidates:

            if candidate.similarity >= self.settings.similarity_threshold:
                valid_candidates.append(candidate)

        return valid_candidates

    def rank_candidates(self, candidates):

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda c: (
                c.confidence,
                c.line_score,
                c.reading_order_score,
                c.similarity,
                -c.distance
            )
        )

    def get_best_candidate(self, candidates):

        if not candidates:
            return None

        valid_candidates = self.filter_candidates(candidates)

        if not valid_candidates:
            return None

        return self.rank_candidates(valid_candidates)

    # --------------------------------------------------------

    def load_documents(self):

        self.source = PDFLoader(SOURCE_JSON).load()

        self.target = PDFLoader(TARGET_JSON).load()

        print("\nJSON loaded successfully.")

    # -------------------------------------------------------
    def debug_print(self, *args, **kwargs):

        if getattr(self.settings, "debug_matching", True):
            print(*args, **kwargs)
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

    def get_candidates(self, source_word, target_words, matched_target_indices ):

        candidates = []

        for target_index, target_word in enumerate(target_words):

            # Skip already matched words
            if target_index in matched_target_indices:
                continue

            d = self.distance(
                source_word["bbox"],
                target_word["bbox"]
            )

            if d <= MAX_MATCH_DISTANCE:
                candidates.append(

                    Candidate(
                        source_word=source_word,
                        target_index=target_index,
                        target_word=target_word,
                        distance=d
                    )

                )

        return candidates

    # ---------------------------------------------------------

    def score_candidates(self, candidates):

        for candidate in candidates:
            candidate.similarity = self.calculate_similarity(
                candidate.source_word["text"],
                candidate.target_word["text"]
            )

            candidate.confidence = self.calculate_confidence(
                candidate.similarity,
                candidate.distance
            )
            reading_difference = abs(
                candidate.source_index -
                candidate.target_index
            )

            candidate.reading_order_score = max(
                0,
                100 - reading_difference
            )
            source_line = candidate.source_word["line"]
            target_line = candidate.target_word["line"]

            candidate.line_score = (
                100 if source_line == target_line else 0
            )

    # --------------------------------------------------------
    def collect_page_candidates(self, source_page, target_page):

        pending_matches = []
        all_candidates = []

        target_words = target_page["words"]

        # Empty set because we want ALL possible candidates
        matched_target_indices = set()

        for source_index, source_word in enumerate(source_page["words"]):

            candidates = self.get_candidates(
                source_word,
                target_words,
                matched_target_indices
            )

            for candidate in candidates:
                candidate.source_index = source_index

            self.score_candidates(candidates)

            all_candidates.extend(candidates)

            pending_matches.append({
                "source_index": source_index,
                "source_word": source_word,
                "candidates": candidates
            })

            # Debug Output (same as before)
            if candidates:

                self.debug_print(
                    f"\nSource : {source_word['text']} "
                    f"(Index={source_index}, "
                    f"Line={source_word['line']}, "
                    f"Block={source_word['block']})"
                )

                for candidate in candidates:
                    self.debug_print(candidate)

        return pending_matches, all_candidates
    # --------------------------------------------------------

    def match_page(self, source_page, target_page):

        # ---------------------------------------------------------
        # PASS 1 : Collect every possible candidate
        # ---------------------------------------------------------

        pending_matches, all_candidates = self.collect_page_candidates(
            source_page,
            target_page
        )

        matches = []

        self.debug_print(f"\nTotal Page Candidates : {len(all_candidates)}")

        valid_candidates = self.filter_candidates(all_candidates)

        self.debug_print(f"Valid Candidates      : {len(valid_candidates)}")

        sorted_candidates = sorted(
            valid_candidates,
            key=lambda c: (
                c.confidence,
                c.line_score,
                c.reading_order_score,
                c.similarity,
                -c.distance
            ),
            reverse=True
        )

        accepted_candidates = self.assign_matches_globally(
            sorted_candidates
        )

        accepted_lookup = {}

        for candidate in accepted_candidates:
            accepted_lookup[id(candidate.source_word)] = candidate

        self.debug_print(f"\nAccepted Lookup Size : {len(accepted_lookup)}")

        self.debug_print("\nTop Ranked Candidates")

        for candidate in sorted_candidates[:10]:
            self.debug_print(candidate)

        # ---------------------------------------------------------
        # PASS 2 : Build Match objects
        # ---------------------------------------------------------

        matched_target_indices = set()

        for item in pending_matches:

            source_index = item["source_index"]
            source_word = item["source_word"]

            best_candidate = accepted_lookup.get(id(source_word))

            if best_candidate is None:
                matches.append(
                    Match(
                        page=source_page["page_number"],
                        source_index=source_index,
                        source_word=source_word,
                        target_word=None,
                        target_index=None,
                        distance=0,
                        similarity=0,
                        confidence=0
                    )
                )

                continue

            matched_target_indices.add(best_candidate.target_index)

            matches.append(
                Match(
                    page=source_page["page_number"],
                    source_index=source_index,
                    source_word=source_word,
                    target_word=best_candidate.target_word,
                    target_index=best_candidate.target_index,
                    distance=best_candidate.distance,
                    similarity=best_candidate.similarity,
                    confidence=best_candidate.confidence
                )
            )

        return matches

    # -------------------------------------------------------

    def assign_matches_globally(self, sorted_candidates):

        matched_sources = set()
        matched_targets = set()

        accepted_candidates = []

        for candidate in sorted_candidates:

            source_id = id(candidate.source_word)
            target_id = id(candidate.target_word)

            if source_id in matched_sources:
                continue

            if target_id in matched_targets:
                continue

            matched_sources.add(source_id)
            matched_targets.add(target_id)

            candidate.selected = True

            accepted_candidates.append(candidate)

        self.debug_print("\nGlobally Accepted Candidates")
        self.debug_print("-" * 80)

        for candidate in accepted_candidates:
            self.debug_print(candidate)

        return accepted_candidates
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

