from pathlib import Path


class ProjectInitializer:

    REQUIRED_DIRECTORIES = [
        "input",
        "output",
        "test_data"
    ]

    @staticmethod
    def initialize():

        print("\nInitializing Project...")

        for directory in ProjectInitializer.REQUIRED_DIRECTORIES:

            Path(directory).mkdir(
                parents=True,
                exist_ok=True
            )

            print(f"✓ {directory}")