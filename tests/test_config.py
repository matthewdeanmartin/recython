from pathlib import Path

from recython.config import load_config
from recython.prompts import load_prompt_pack


def test_load_config_from_pyproject(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.recython]
source = ["src/pkg"]
output_root = ".recython/out"
style = "pure"
model = "gpt-4.1-mini"
exclude = ["tests"]
include = ["service"]
prompt_profile = "maintenance"
max_attempts = 3
write_manifest = false

[tool.recython.validation]
ruff = false

[tool.recython.prompts]
pure = "prompts/pure.md"
""".strip(),
        encoding="utf-8",
    )

    config = load_config(pyproject)

    assert config.project_root == tmp_path.resolve()
    assert config.source == [(tmp_path / "src/pkg").resolve()]
    assert config.output_root == (tmp_path / ".recython/out").resolve()
    assert config.style == "pure"
    assert config.model == "gpt-4.1-mini"
    assert config.exclude == ["tests"]
    assert config.include == ["service"]
    assert config.prompt_profile == "maintenance"
    assert config.max_attempts == 3
    assert config.write_manifest is False
    assert config.validation.ruff is False
    assert config.prompt_paths["pure"] == "prompts/pure.md"


def test_prompt_profile_changes_loaded_prompt_text(tmp_path: Path):
    config = load_config(start_path=tmp_path)
    default_pack = load_prompt_pack(config)
    safe_pack = load_prompt_pack(config.__class__(project_root=config.project_root, prompt_profile="safe"))

    assert default_pack.templates["pure"].text != safe_pack.templates["pure"].text
    assert "Prefer correctness and readability" in safe_pack.templates["pure"].text
