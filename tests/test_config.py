from pathlib import Path

from recython.config import load_config


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
