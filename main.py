from extractor import extract_source, extract_target
from matcher import PDFMatcher
from highlighter import PDFHighlighter
from config import SOURCE_PDF, TARGET_PDF, OUTPUT_FOLDER

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



if __name__ == "__main__":
    main()