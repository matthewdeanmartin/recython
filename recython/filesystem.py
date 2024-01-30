from pathlib import Path


def get_files_and_contents(folder_path):
    folder_path = Path(folder_path)

    # Ensure the folder path exists
    if not folder_path.exists():
        raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")

    # Iterate over all items in the folder, including subfolders
    for item in folder_path.glob("**/*"):
        if item.is_file() and item.suffix == ".py":
            # If it's a file, yield its path and contents
            with open(item, encoding="utf-8") as file:
                yield item, file.read()


def rename_file_add_suffix(current_path, suffix="_old"):
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


# Example usage:
# current_file_path = Path('/path/to/your/file.py')
# new_file_path = rename_file_add_suffix(current_file_path)


if __name__ == "__main__":
    # Example usage:
    folder_path = r"E:\github\pymarc\pymarc"
    for file_path, file_contents in get_files_and_contents(folder_path):
        print(f"File: {file_path}")
        print(f"Contents:\n{file_contents}\n")
