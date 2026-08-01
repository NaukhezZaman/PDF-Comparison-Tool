# application configuration (paths, folders, output names, etc.)
from datetime import datetime
from pathlib import Path

# ==============================
# Project Paths
# ==============================
# Instead of writing paths like: "C:/Users/Naukhez/Documents/..." everywhere,
# we define them once. If you move the project tomorrow, everything still works.

def get_report_file(source_pdf: Path, target_pdf: Path):

    timestamp = datetime.now().strftime("%d_%b_%Y_%H%M%S")

    filename = (
        f"{source_pdf.stem}_"
        f"{target_pdf.stem}_"
        f"comparison_report_"
        f"{timestamp}.xlsx"
    )

    return OUTPUT_FOLDER / filename

PROJECT_ROOT = Path(__file__).parent

INPUT_FOLDER = PROJECT_ROOT / "test_data/ignore_dashes"
OUTPUT_FOLDER = PROJECT_ROOT / "output"
TEMP_FOLDER = PROJECT_ROOT / "temp"
LOG_FOLDER = PROJECT_ROOT / "logs"

SOURCE_PDF = INPUT_FOLDER / "source_dashes.pdf"
TARGET_PDF = INPUT_FOLDER / "target_dashes.pdf"

SOURCE_JSON = TEMP_FOLDER / "source_words.json"
TARGET_JSON = TEMP_FOLDER / "target_words.json"

# ----------------------------------------------------
# Matching Configuration
# ----------------------------------------------------

MAX_MATCH_DISTANCE = 30
