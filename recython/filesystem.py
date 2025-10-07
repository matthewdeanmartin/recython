from pathlib import Path

from recython.benchmark_utils import CaptureOutput as capture_output


def get_files_and_contents(folder_path: Path) -> list[tuple[Path, str]]:
    # Ensure the folder path exists
    if not folder_path.exists():
        raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")
    items = []
    # Iterate over all items in the folder, including subfolders
    for item in folder_path.glob("**/*"):
        if item.is_file() and item.suffix == ".py":
            # If it's a file, yield its path and contents
            with open(item, encoding="utf-8") as file:
                # cython can't handle yield?
                # yield item, file.read()
                items.append((item, file.read()))
    return items


def rename_file_add_suffix(current_path: Path, suffix="_old") -> Path | None:
    if not current_path.is_file():
        print(f"The path {current_path} does not exist or is not a file.")
        return None

    # Get the parent directory, base name, and extension of the current file
    parent_dir = current_path.parent
    base_name = current_path.stem
    extension = current_path.suffix

    # Create the new file name by adding the suffix before the extension
    new_name = f"{base_name}{suffix}{extension}"

    # Create a new Path object with the new name in the same directory
    new_path = parent_dir / new_name

    # Rename the file
    try:
        current_path.rename(new_path)
        print(f"File renamed to {new_path}")
        return new_path
    except Exception as e:
        print(f"An error occurred while renaming the file: {e}")
        return None


def load_template(template_name: str) -> str:
    path_to_template = Path(__file__).parent / template_name
    with open(str(path_to_template), encoding="utf-8") as file:
        template = file.read()
    return template


def run():
    with capture_output() as _captured:
        "__file__"
        folder_path = Path(".") / "recython"
        for file_path, file_contents in get_files_and_contents(folder_path):
            print(f"File: {file_path}")
            print(f"Contents:\n{file_contents}\n")


if __name__ == "__main__":
    run()
