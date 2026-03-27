from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
import tomllib


@dataclass(slots=True)
class ValidationConfig:
    python_compile: bool = True
    cython_compile: bool = False
    ruff: bool = True
    mypy: bool = False


@dataclass(slots=True)
class RecythonConfig:
    project_root: Path
    source: list[Path] = field(default_factory=list)
    output_root: Path = Path(".recython/build")
    style: str = "classic"
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_completion_tokens: int = 4000
    exclude: list[str] = field(default_factory=list)
    include: list[str] = field(default_factory=list)
    prompt_profile: str = "default"
    max_attempts: int = 1
    maintenance_mode: bool = False
    backup_originals: bool = False
    write_manifest: bool = True
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    prompt_paths: dict[str, str] = field(default_factory=dict)


def _find_pyproject(start_path: Path | None = None) -> Path | None:
    current = (start_path or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate_root in [current, *current.parents]:
        candidate = candidate_root / "pyproject.toml"
        if candidate.exists():
            return candidate
    return None


def _resolve_path(project_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (project_root / path).resolve()


def load_config(pyproject_path: Path | None = None, *, start_path: Path | None = None) -> RecythonConfig:
    resolved_pyproject = pyproject_path or _find_pyproject(start_path)
    project_root = resolved_pyproject.parent.resolve() if resolved_pyproject else (start_path or Path.cwd()).resolve()

    defaults = RecythonConfig(project_root=project_root)
    if resolved_pyproject is None:
        return defaults

    data = tomllib.loads(resolved_pyproject.read_text(encoding="utf-8"))
    raw_config = data.get("tool", {}).get("recython", {})
    raw_validation = raw_config.get("validation", {})
    raw_prompts = raw_config.get("prompts", {})

    return RecythonConfig(
        project_root=project_root,
        source=[_resolve_path(project_root, item) for item in raw_config.get("source", [])],
        output_root=_resolve_path(project_root, raw_config.get("output_root", str(defaults.output_root))),
        style=raw_config.get("style", defaults.style),
        provider=raw_config.get("provider", defaults.provider),
        model=raw_config.get("model", defaults.model),
        temperature=float(raw_config.get("temperature", defaults.temperature)),
        max_completion_tokens=int(raw_config.get("max_completion_tokens", defaults.max_completion_tokens)),
        exclude=list(raw_config.get("exclude", defaults.exclude)),
        include=list(raw_config.get("include", defaults.include)),
        prompt_profile=raw_config.get("prompt_profile", defaults.prompt_profile),
        max_attempts=int(raw_config.get("max_attempts", defaults.max_attempts)),
        maintenance_mode=bool(raw_config.get("maintenance_mode", defaults.maintenance_mode)),
        backup_originals=bool(raw_config.get("backup_originals", defaults.backup_originals)),
        write_manifest=bool(raw_config.get("write_manifest", defaults.write_manifest)),
        validation=ValidationConfig(
            python_compile=bool(raw_validation.get("python_compile", defaults.validation.python_compile)),
            cython_compile=bool(raw_validation.get("cython_compile", defaults.validation.cython_compile)),
            ruff=bool(raw_validation.get("ruff", defaults.validation.ruff)),
            mypy=bool(raw_validation.get("mypy", defaults.validation.mypy)),
        ),
        prompt_paths={key: value for key, value in raw_prompts.items() if isinstance(value, str)},
    )


def apply_config_overrides(config: RecythonConfig, **overrides: object) -> RecythonConfig:
    filtered = {key: value for key, value in overrides.items() if value is not None}
    return replace(config, **filtered)


def render_starter_config() -> str:
    return """
[tool.recython]
source = ["src/mypkg"]
output_root = ".recython/build"
style = "classic"
provider = "openai"
model = "gpt-4o-mini"
temperature = 0.0
max_completion_tokens = 4000
exclude = ["tests", "__init__", "migrations"]
include = []
prompt_profile = "default"
max_attempts = 1
maintenance_mode = false
backup_originals = false
write_manifest = true

[tool.recython.validation]
python_compile = true
cython_compile = false
ruff = true
mypy = false

[tool.recython.prompts]
classic_pyx = "prompts/classic_pyx.md"
classic_pxd = "prompts/classic_pxd.md"
pure = "prompts/pure.md"
""".strip()
