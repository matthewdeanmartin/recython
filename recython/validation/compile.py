from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from Cython.Compiler.Main import CompilationOptions, compile_single, default_options


def _success_result(path: Path, validator: str) -> dict[str, object]:
    return {
        "path": str(path),
        "validator": validator,
        "ok": True,
        "error": None,
    }


def _failure_result(path: Path, validator: str, error: Exception) -> dict[str, object]:
    return {
        "path": str(path),
        "validator": validator,
        "ok": False,
        "error": str(error),
    }


def validate_python_file(path: Path) -> dict[str, object]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return _failure_result(path, "python_compile", exc)
    return _success_result(path, "python_compile")


def validate_cython_file(path: Path) -> dict[str, object]:
    try:
        with TemporaryDirectory() as temp_dir:
            options_template = deepcopy(default_options)
            output_file = str(Path(temp_dir) / f"{path.stem}.c")
            options = CompilationOptions(options_template, output_file=output_file)
            module_name = ".".join(path.with_suffix("").parts[-3:]).replace("-", "_")
            result = compile_single(str(path), options, module_name)
            if getattr(result, "num_errors", 0):
                raise ValueError(f"Cython reported {result.num_errors} error(s).")
    except Exception as exc:  # pragma: no cover - library-specific exception tree
        return _failure_result(path, "cython_compile", exc)
    return _success_result(path, "cython_compile")


def validate_outputs(
    written_files: list[Path],
    *,
    style: str,
    python_compile_enabled: bool,
    cython_compile_enabled: bool,
) -> dict[str, object]:
    file_results: list[dict[str, object]] = []

    for path in written_files:
        if python_compile_enabled and path.suffix == ".py":
            file_results.append(validate_python_file(path))
        if cython_compile_enabled and style == "classic" and path.suffix in {".pyx", ".pxd"}:
            file_results.append(validate_cython_file(path))

    failed = [item for item in file_results if not item["ok"]]
    return {
        "ok": not failed,
        "checked": len(file_results),
        "failed": len(failed),
        "files": file_results,
    }
