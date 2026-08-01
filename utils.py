import json
from dataclasses import asdict
from pathlib import Path


def save_json(data, file_path: Path):

    with open(file_path, "w", encoding="utf-8") as f:

        json.dump(data, f, indent=4, ensure_ascii=False)


def save_dataclass_json(dataclass_object, file_path: Path):

    with open(file_path, "w", encoding="utf-8") as f:

        json.dump(asdict(dataclass_object), f, indent=4, ensure_ascii=False)


def print_heading(title):

    print("\n" + "=" * 70)

    print(title)

    print("=" * 70)