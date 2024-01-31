import re
import shutil
import time
from pathlib import Path


def modify_python_source(file_path: Path, old_module: str, new_module: str) -> None:
    """
    Reads a Python source file, replaces imports from the old module with the new module,
    and writes the changes back to the file.

    Args:
        file_path (Path): The path to the Python source file.
        old_module (str): The old module name to replace.
        new_module (str): The new module name to use as a replacement.
    """
    if not file_path.exists() or not file_path.suffix == ".py":
        raise FileNotFoundError("The specified file does not exist or is not a .py file.")

    # Read the content of the file
    with file_path.open(mode="r", encoding="utf-8") as file:
        content = file.read()

    # Define the regex patterns and perform the replacements
    patterns = [
        (rf"from {re.escape(old_module)}", f"from {new_module}"),
        (rf"import {re.escape(old_module)}", f"import {new_module}"),
    ]
    for old, new in patterns:
        content = re.sub(old, new, content)

    # Write the modified content back to the file
    with file_path.open(mode="w", encoding="utf-8") as file:
        file.write(content)


def copy_file_if_needed(source_file: Path, target_dir: Path) -> None:
    """
    Copy a file from the source to the target directory if it's a Python (.py) file, Python Typed (.pyi) file,
    or Markdown (.md) file.

    :param source_file: Path object representing the source file.
    :param target_dir: Path object representing the target directory.
    """
    # Check if the file is a .py, .pyi, or .md file
    if source_file.suffix in [".py", ".pyi", ".md", ".typed"]:
        # Define the target file path
        target_file = target_dir / source_file.name

        # Copy the file to the target directory
        shutil.copy2(source_file, target_file)
        while not target_file.exists():
            time.sleep(0.5)
        if target_file.suffix == ".py":
            modify_python_source(target_file, "recython", "recython_pure")


def copy_files_recursively(source_dir: Path, target_dir: Path) -> None:
    """
    Recursively copy all .py, .pyi, and .md files from the source directory to the target directory.

    :param source_dir: Path object representing the source directory.
    :param target_dir: Path object representing the target directory.
    """
    # Iterate through all items in the source directory
    for item in source_dir.iterdir():
        # Skip __pycache__ directories
        if item.name == "__pycache__":
            continue
        # If the item is a directory, recursively call this function
        if item.is_dir():
            # Create a corresponding directory in the target directory
            next_target_dir = target_dir / item.name
            next_target_dir.mkdir(exist_ok=True)

            # Recurse into the subdirectory
            copy_files_recursively(item, next_target_dir)
        else:
            # If the item is a file, use copy_file_if_needed function to copy it
            copy_file_if_needed(item, target_dir)


def run() -> None:
    # Define source and target directories
    source_dir = Path("./recython")
    target_dir = Path("./recython_pure")

    # Ensure the target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)

    # Start the recursive copying process
    copy_files_recursively(source_dir, target_dir)


if __name__ == "__main__":
    run()
