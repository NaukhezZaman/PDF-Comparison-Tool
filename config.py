from pathlib import Path

# ==============================
# Project Paths
# ==============================
# Instead of writing paths like: "C:/Users/Naukhez/Documents/..." everywhere,
# we define them once. If you move the project tomorrow, everything still works.

PROJECT_ROOT = Path(__file__).parent

INPUT_FOLDER = PROJECT_ROOT / "input"
OUTPUT_FOLDER = PROJECT_ROOT / "output"
TEMP_FOLDER = PROJECT_ROOT / "temp"
LOG_FOLDER = PROJECT_ROOT / "logs"

SOURCE_PDF = INPUT_FOLDER / "source.pdf"
TARGET_PDF = INPUT_FOLDER / "target_deleted.pdf"

SOURCE_JSON = TEMP_FOLDER / "source_words.json"
TARGET_JSON = TEMP_FOLDER / "target_words.json"

# ----------------------------------------------------
# Matching Configuration
# ----------------------------------------------------

MAX_MATCH_DISTANCE = 30