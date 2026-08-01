from extractor import extract_source, extract_target
from matcher import PDFMatcher
from highlighter import PDFHighlighter
from config import SOURCE_PDF, TARGET_PDF, OUTPUT_FOLDER
from report_generator import ReportGenerator
from config import REPORT_FILE

def main():

    print("\nPDF Comparison Tool")

    print("\nSTEP 1")

    extract_source()

    extract_target()

    print("\nSTEP 2")

    matcher = PDFMatcher()

    matcher.load_documents()

    print("\nSTEP 3")

    matches = matcher.match_documents()
    matcher.print_match_metrics(matches)

    print("\nSTEP 4")

    differences = matcher.detect_differences(matches)
    matcher.print_differences(differences)

    highlighter = PDFHighlighter()
    highlighter.highlight(
        SOURCE_PDF,
        OUTPUT_FOLDER / "source_highlighted.pdf",
        differences,
        "SOURCE"
    )

    highlighter.highlight(
        TARGET_PDF,
        OUTPUT_FOLDER / "target_highlighted.pdf",
        differences,
        "TARGET"
    )

    report_generator = ReportGenerator()

    report_generator.generate_report(
        REPORT_FILE,
        SOURCE_PDF.name,
        TARGET_PDF.name,
        differences
    )

if __name__ == "__main__":
    main()