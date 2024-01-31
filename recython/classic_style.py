import os
from pathlib import Path

import recython.ai_calls as ai
from recython import tidy
from recython.filesystem import get_files_and_contents, load_template

PURE_STYLE = 1
CLASSIC_STYLE = 2


def cythonize_classic_project(folder_path: Path, target_folder: Path, never_translate: list[str]) -> list[Path]:
    written = []
    for file_path, file_contents in get_files_and_contents(folder_path):
        if os.path.exists(str(file_path).replace(".py", ".pyx")):
            continue
        skip = False
        for fragment in never_translate:
            if fragment in str(file_path):
                skip = True
        if skip:
            continue
        result = cython_classic_style(file_contents, file_path, target_folder)
        written.extend(result)
    return written


def cython_classic_style(file_contents: str, file_path: Path, target_folder: Path) -> list[Path]:
    wrote_files = []
    template = load_template("cython_style_pyx.md")
    pyx_prompt = template.replace("XXXCODEXXX", file_contents)
    print(pyx_prompt)
    result = ai.completion(pyx_prompt)
    final_pyx = target_folder / file_path.parent / (file_path.stem + ".pyx")
    os.makedirs(str(final_pyx.parent), exist_ok=True)
    wrote_files.append(final_pyx)
    with open(final_pyx, "w", encoding="utf-8") as file:
        file.write(tidy.extract_code_block(result))

    # read prompt
    template = load_template("cython_style_pxd.md")
    pyx_prompt = template.replace("XXXRESULTXXX", result)

    # get and write response
    result = ai.completion(pyx_prompt)
    final_pxd = target_folder / file_path.parent / (file_path.stem + ".pxd")
    wrote_files.append(final_pxd)
    with open(str(final_pxd), "w", encoding="utf-8") as file:
        file.write(tidy.extract_code_block(result))

    return wrote_files


def run():
    folder_path = Path("./examples/src_hangman/hangman")
    target_folder = Path("./examples/src_hangman/changman")
    never_translate = [
        "__init__",
    ]
    cythonize_classic_project(folder_path, target_folder, never_translate)


if __name__ == "__main__":
    run()
