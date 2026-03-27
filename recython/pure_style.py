import os
from pathlib import Path

import recython.ai_calls as ai
from recython import tidy
from recython.filesystem import get_files_and_contents, load_template

PURE_STYLE = 1
CLASSIC_STYLE = 2


def pure_cythonize_project(folder_path: Path, target_folder: Path, never_translate: list[str]) -> list[Path]:
    written = []
    for file_path, file_contents in get_files_and_contents(folder_path):
        skip = False
        for fragment in never_translate:
            if fragment in str(file_path):
                skip = True
        if skip:
            continue
        # another skip list for DONE
        relative_path = file_path.relative_to(folder_path)
        result = cython_pure_style(file_contents, relative_path, target_folder)
        written.extend(result)
    return written


def cython_pure_style(file_contents: str, file_path: Path, target_folder: Path) -> list[Path]:
    template = load_template("cython_pure_python_style.md")
    pure_prompt = template.replace("XXXCODEXXX", file_contents)
    result = ai.completion(pure_prompt)

    final_py = target_folder / file_path
    os.makedirs(final_py.parent, exist_ok=True)
    if final_py == file_path:
        raise TypeError("Cannot overwrite the original file")
    with open(final_py, "w", encoding="utf-8") as file:
        file.write(tidy.extract_code_block(result))
    return [final_py]


def run():
    folder_path = Path("./examples/src_hangman/hangman")
    target_folder = Path("./examples/src_hangman/changman")
    never_translate = [
        "__init__",
    ]
    pure_cythonize_project(folder_path, target_folder, never_translate)


if __name__ == "__main__":
    run()
