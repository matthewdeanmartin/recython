from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ValidationRequest:
    python_compile: bool = True
    cython_compile: bool = False
    ruff: bool = True
    mypy: bool = False


def _json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


@dataclass(slots=True)
class PlannedOutput:
    kind: str
    path: Path


@dataclass(slots=True)
class PlannedFile:
    source_path: Path
    relative_path: Path
    outputs: list[PlannedOutput]
    prompt_keys: list[str]


@dataclass(slots=True)
class SkippedFile:
    source_path: Path
    reason: str


@dataclass(slots=True)
class RunRequest:
    source_root: Path
    output_root: Path
    style: str
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_completion_tokens: int = 4000
    exclude: list[str] = field(default_factory=list)
    include: list[str] = field(default_factory=list)
    prompt_profile: str = "default"
    max_attempts: int = 1
    maintenance_mode: bool = False
    baseline_manifest: Path | None = None
    write_manifest: bool = True
    dry_run: bool = False
    validation: ValidationRequest = field(default_factory=ValidationRequest)

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass(slots=True)
class RunResult:
    request: RunRequest
    examined_files: list[Path] = field(default_factory=list)
    planned_files: list[PlannedFile] = field(default_factory=list)
    skipped_files: list[SkippedFile] = field(default_factory=list)
    written_files: list[Path] = field(default_factory=list)
    prompts_used: list[str] = field(default_factory=list)
    validation_results: dict[str, Any] = field(default_factory=dict)
    source_snapshot: dict[str, str] = field(default_factory=dict)
    source_contents: dict[str, str] = field(default_factory=dict)
    generated_outputs: dict[str, dict[str, str]] = field(default_factory=dict)
    maintenance_summary: dict[str, Any] = field(default_factory=dict)
    artifacts_dir: Path | None = None
    manifest_path: Path | None = None
    report_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))
