from pathlib import Path

from recython.engine import build_run_request, execute_run
from recython.jobs import ValidationRequest


def pure_cythonize_project(folder_path: Path, target_folder: Path, never_translate: list[str]) -> list[Path]:
    request = build_run_request(
        source_root=folder_path,
        output_root=target_folder,
        style="pure",
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.0,
        max_completion_tokens=4000,
        exclude=never_translate,
        include=[],
        prompt_profile="default",
        max_attempts=1,
        maintenance_mode=False,
        baseline_manifest=None,
        write_manifest=False,
        dry_run=False,
        validation=ValidationRequest(python_compile=False),
    )
    return execute_run(request).written_files


def run():
    folder_path = Path("./examples/src_multiple_regression/multiple_regression")
    target_folder = Path("./examples/src_multiple_regression/cythonized")
    never_translate = [
        "__init__",
    ]
    pure_cythonize_project(folder_path, target_folder, never_translate)


if __name__ == "__main__":
    run()
