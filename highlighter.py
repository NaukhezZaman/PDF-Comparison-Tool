# --------------------------------------------------
# 🟨 Yellow → Modified words
# 🟩 Green → Inserted words
# 🟥 Red → Deleted words
# --------------------------------------------------
import fitz


class PDFHighlighter:

    def highlight(self, input_pdf, output_pdf, differences, mode):

        print(f"\nOpening : {input_pdf}")

        doc = fitz.open(input_pdf)

        print(f"Pages : {len(doc)}")

        for difference in differences:

            rect = None

            # ----------------------------------------
            # Source PDF
            # ----------------------------------------

            if mode == "SOURCE":

                if difference.difference_type == "MODIFIED":

                    if difference.source_bbox is not None:
                        rect = fitz.Rect(difference.source_bbox)

                elif difference.difference_type == "DELETED":

                    if difference.source_bbox is not None:
                        rect = fitz.Rect(difference.source_bbox)

            # ----------------------------------------
            # Target PDF
            # ----------------------------------------

            elif mode == "TARGET":

                if difference.difference_type == "MODIFIED":

                    if difference.target_bbox is not None:
                        rect = fitz.Rect(difference.target_bbox)

                elif difference.difference_type == "INSERTED":

                    if difference.target_bbox is not None:
                        rect = fitz.Rect(difference.target_bbox)

            if rect is None:
                continue

            page = doc[difference.page - 1]

            highlight = page.add_highlight_annot(rect)

            # ----------------------------------------
            # Set highlight color and annotation info
            # ----------------------------------------

            if difference.difference_type == "MODIFIED":

                highlight.set_colors(stroke=(1, 1, 0))

                highlight.set_info(
                    title="PDF Comparison Tool",
                    content=(
                        f"Type   : MODIFIED\n"
                        f"Source : {difference.source_text}\n"
                        f"Target : {difference.target_text}"
                    )
                )

            elif difference.difference_type == "DELETED":

                highlight.set_colors(stroke=(1, 0, 0))

                highlight.set_info(
                    title="PDF Comparison Tool",
                    content=(
                        f"Type   : DELETED\n"
                        f"Source : {difference.source_text}"
                    )
                )

            elif difference.difference_type == "INSERTED":

                highlight.set_colors(stroke=(0, 1, 0))

                highlight.set_info(
                    title="PDF Comparison Tool",
                    content=(
                        f"Type   : INSERTED\n"
                        f"Target : {difference.target_text}"
                    )
                )

            highlight.update()

        doc.save(output_pdf)

        doc.close()

        print(f"Saved : {output_pdf}")