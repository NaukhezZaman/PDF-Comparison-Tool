import fitz

from config import (
    SOURCE_PDF,
    TARGET_PDF,
    SOURCE_JSON,
    TARGET_JSON
)

from utils import (
    save_dataclass_json,
    print_heading
)

from models.document import PDFDocument
from models.page import PageData
from models.word import Word
from models.block import Block


class PDFExtractor:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_document(self):

        print_heading(f"Reading {self.pdf_path.name}")

        document = fitz.open(self.pdf_path)

        pdf_document = PDFDocument(
            file_name=self.pdf_path.name,
            page_count=document.page_count
        )

        for page_number in range(document.page_count):

            page = document.load_page(page_number)

            page_data = self.extract_page(page, page_number + 1)

            pdf_document.pages.append(page_data)

        document.close()

        return pdf_document

    def extract_page(self, page, page_number):

        print(f"Processing Page {page_number}")

        page_data = PageData(
            page_number=page_number,
            width=page.rect.width,
            height=page.rect.height
        )

        page_data.words = self.extract_words(page)

        page_data.blocks = self.extract_blocks(page)

        page_data.images = self.extract_images(page)

        page_data.drawings = self.extract_drawings(page)

        print(
            f"   Words : {len(page_data.words)} | "
            f"Blocks : {len(page_data.blocks)} | "
            f"Images : {len(page_data.images)} | "
            f"Drawings : {len(page_data.drawings)}"
        )

        return page_data

    def extract_words(self, page):

        words = []

        extracted = page.get_text("words")

        for item in extracted:

            x0, y0, x1, y1, text, block_no, line_no, word_no = item

            words.append(
                Word(
                    text=text,
                    bbox=[x0, y0, x1, y1],
                    block=block_no,
                    line=line_no,
                    word=word_no
                )
            )

        return words

    def extract_blocks(self, page):

        blocks = []

        extracted = page.get_text("blocks")

        for index, block in enumerate(extracted):

            x0, y0, x1, y1, text, *_ = block

            text = text.strip()

            if text == "":
                continue

            blocks.append(
                Block(
                    block_no=index,
                    text=text,
                    bbox=[x0, y0, x1, y1]
                )
            )

        return blocks

    def extract_images(self, page):

        images = []

        extracted = page.get_images(full=True)

        for image in extracted:

            images.append(
                {
                    "xref": image[0],
                    "width": image[2],
                    "height": image[3],
                    "bpc": image[4],
                    "colorspace": image[5]
                }
            )

        return images

    def extract_drawings(self, page):

        drawings = []

        extracted = page.get_drawings()

        for drawing in extracted:

            drawings.append(
                {
                    "type": drawing.get("type"),
                    "rect": list(drawing.get("rect"))
                    if drawing.get("rect")
                    else None
                }
            )

        return drawings


def extract_source():

    extractor = PDFExtractor(SOURCE_PDF)

    document = extractor.extract_document()

    save_dataclass_json(document, SOURCE_JSON)

    print(f"\nSaved : {SOURCE_JSON}")


def extract_target():

    extractor = PDFExtractor(TARGET_PDF)

    document = extractor.extract_document()

    save_dataclass_json(document, TARGET_JSON)

    print(f"\nSaved : {TARGET_JSON}")