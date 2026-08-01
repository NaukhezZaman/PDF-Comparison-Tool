from openpyxl import Workbook


class ReportGenerator:

    def __init__(self):
        pass

    def generate_report(self, output_file, source_file, target_file, differences):

        workbook = Workbook()

        summary_sheet = workbook.active
        summary_sheet.title = "Summary"

        difference_sheet = workbook.create_sheet(title="Differences")

        self._populate_summary_sheet(
            summary_sheet,
            source_file,
            target_file,
            differences
        )

        self._populate_difference_sheet(
            difference_sheet,
            differences
        )

        workbook.save(output_file)

        print(f"Excel report generated successfully: {output_file}")

    def _populate_summary_sheet(self, summary_sheet, source_file, target_file, differences):

        modified = 0
        deleted = 0
        inserted = 0

        for difference in differences:

            if difference.difference_type == "MODIFIED":
                modified += 1

            elif difference.difference_type == "DELETED":
                deleted += 1

            elif difference.difference_type == "INSERTED":
                inserted += 1

        summary_sheet.append(["Metric", "Value"])
        summary_sheet.append(["Source File", source_file])
        summary_sheet.append(["Target File", target_file])
        summary_sheet.append(["Total Differences", len(differences)])
        summary_sheet.append(["Modified", modified])
        summary_sheet.append(["Deleted", deleted])
        summary_sheet.append(["Inserted", inserted])

    def _populate_difference_sheet(self, difference_sheet, differences):

        difference_sheet.append([
            "Page",
            "Type",
            "Source",
            "Target",
            "Block",
            "Line",
            "Word"
        ])

        for difference in differences:
            difference_sheet.append([
                difference.page,
                difference.difference_type,
                difference.source_text,
                difference.target_text,
                difference.block,
                difference.line,
                difference.word
            ])