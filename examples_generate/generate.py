from pathlib import Path

from dotenv import load_dotenv

import recython

load_dotenv()
if __name__ == "__main__":
    projects = [
        Path("../examples/src_hangman/hangman"),
        # Path("../examples/src_regex/some_regex"),
        # Path("../examples/scr_file_io/file_io"),
    ]
    for project in projects:
        recython.cythonize_classic_project(
            folder_path=project, target_folder=Path("./classic/"), never_translate=["__init__", "tests"]
        )
