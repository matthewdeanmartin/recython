import json
from pathlib import Path
from unittest.mock import patch

from recython.cli import main
from recython.config import RecythonConfig
from recython.engine import build_run_request, execute_run_with_pack, plan_run
from recython.prompts import load_prompt_pack


def test_plan_run_filters_and_maps_outputs(tmp_path: Path):
    source = tmp_path / "pkg"
    source.mkdir()
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "service.py").write_text("print('hi')", encoding="utf-8")
    (source / "worker.py").write_text("print('bye')", encoding="utf-8")

    request = build_run_request(
        source_root=source,
        output_root=tmp_path / "out",
        style="classic",
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.0,
        max_completion_tokens=4000,
        exclude=["__init__"],
        include=["service"],
        prompt_profile="default",
        max_attempts=1,
        write_manifest=False,
        dry_run=True,
    )

    result = plan_run(request)

    assert len(result.examined_files) == 3
    assert len(result.planned_files) == 1
    assert result.planned_files[0].relative_path == Path("service.py")
    assert [output.path.name for output in result.planned_files[0].outputs] == ["service.pyx", "service.pxd"]
    assert {item.reason for item in result.skipped_files} == {"excluded", "not included"}


def test_execute_run_writes_manifest_and_prompt_snapshots(tmp_path: Path):
    source = tmp_path / "pkg"
    source.mkdir()
    (source / "module.py").write_text("print('hi')", encoding="utf-8")

    request = build_run_request(
        source_root=source,
        output_root=tmp_path / "out",
        style="pure",
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.0,
        max_completion_tokens=4000,
        exclude=[],
        include=[],
        prompt_profile="default",
        max_attempts=1,
        write_manifest=True,
        dry_run=False,
    )
    pack = load_prompt_pack(RecythonConfig(project_root=tmp_path))

    with patch("recython.ai_calls.completion", return_value="```python\nprint('converted')\n```"):
        result = execute_run_with_pack(request, pack)

    output_file = tmp_path / "out" / "module.py"
    assert output_file.read_text(encoding="utf-8") == "print('converted')"
    assert result.manifest_path is not None
    assert result.report_path is not None
    assert result.artifacts_dir is not None
    assert any(path.name.endswith(".pure.md") for path in (result.artifacts_dir / "prompts").iterdir())
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["written_files"] == [str(output_file)]
    assert manifest["validation_results"]["ok"] is True


def test_plan_command_uses_pyproject_defaults(tmp_path: Path, capsys):
    source = tmp_path / "src" / "pkg"
    source.mkdir(parents=True)
    (source / "module.py").write_text("print('hi')", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.recython]
source = ["src/pkg"]
output_root = "build/out"
style = "pure"
exclude = []
include = []
prompt_profile = "default"
""".strip(),
        encoding="utf-8",
    )
    report_path = tmp_path / "plan.json"

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        exit_code = main(["plan", "--report-json", str(report_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Planned 1 file(s) for pure conversion." in captured.out
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["request"]["style"] == "pure"


def test_execute_run_retries_after_validation_failure(tmp_path: Path):
    source = tmp_path / "pkg"
    source.mkdir()
    (source / "module.py").write_text("print('hi')", encoding="utf-8")

    request = build_run_request(
        source_root=source,
        output_root=tmp_path / "out",
        style="pure",
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.0,
        max_completion_tokens=4000,
        exclude=[],
        include=[],
        prompt_profile="default",
        max_attempts=2,
        write_manifest=False,
        dry_run=False,
    )
    pack = load_prompt_pack(RecythonConfig(project_root=tmp_path))

    responses = [
        "```python\ndef broken(:\n```",
        "```python\nprint('fixed')\n```",
    ]
    with patch("recython.ai_calls.completion", side_effect=responses) as completion:
        result = execute_run_with_pack(request, pack)

    output_file = tmp_path / "out" / "module.py"
    assert output_file.read_text(encoding="utf-8") == "print('fixed')"
    assert completion.call_count == 2
    attempts = result.validation_results["attempts"][str(source / "module.py")]
    assert len(attempts) == 2
    assert result.validation_results["ok"] is True


def test_prompts_doctor_reports_invalid_custom_prompt(tmp_path: Path, capsys):
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "pure.md").write_text("missing placeholder", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.recython]

[tool.recython.prompts]
pure = "prompts/pure.md"
""".strip(),
        encoding="utf-8",
    )

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        exit_code = main(["prompts", "doctor"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "missing placeholders" in captured.out


def test_validate_command_reports_python_syntax_errors(tmp_path: Path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.recython]
output_root = "out"
style = "pure"

[tool.recython.validation]
python_compile = true
cython_compile = false
""".strip(),
        encoding="utf-8",
    )

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        exit_code = main(["validate"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "failures: 1" in captured.out
