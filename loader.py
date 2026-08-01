import json


class PDFLoader:

    def __init__(self, json_file):
        self.json_file = json_file

    def load(self):

        with open(self.json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def print_summary(self):

        data = self.load()

        print("\n-----------------------------------------")
        print(f"File : {data['file_name']}")
        print(f"Pages : {data['page_count']}")
        print("-----------------------------------------")

        total_words = 0
        total_blocks = 0

        for page in data["pages"]:

            word_count = len(page["words"])
            block_count = len(page["blocks"])

            total_words += word_count
            total_blocks += block_count

            print(
                f"Page {page['page_number']} : "
                f"Words = {word_count} | "
                f"Blocks = {block_count}"
            )

        print("-----------------------------------------")
        print(f"Total Words : {total_words}")
        print(f"Total Blocks : {total_blocks}")
        print("-----------------------------------------")

        return data