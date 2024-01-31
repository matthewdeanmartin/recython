from pathlib import Path

import recython.classic_style as classic_style
import recython.pure_style as pure_style

PURE_STYLE = 1
CLASSIC_STYLE = 2


def go(folder_path: Path, target_folder: Path, cython_style: int, never_translate: list[str]):
    if cython_style == 1:
        classic_style.cythonize_classic_project(folder_path, target_folder, never_translate)
    else:
        pure_style.pure_cythonize_project(folder_path, target_folder, never_translate)


def run():
    folder_path = Path(r"E:\github\pymarc\pymarc")
    target_folder = Path("./tmp")
    never_translate = ["constants", "__init__", "exceptions", "marc8", "marc8_mapping"]
    go(folder_path, target_folder, CLASSIC_STYLE, never_translate)


if __name__ == "__main__":
    run()
