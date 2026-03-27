from pathlib import Path

from recython.cli import main


def test_prompts_list(capsys):
    exit_code = main(["prompts", "list"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "classic-pyx" in captured.out
    assert "classic-pxd" in captured.out
    assert "pure" in captured.out


def test_convert_dry_run(capsys, tmp_path: Path):
    source = tmp_path / "pkg"
    source.mkdir()
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "module.py").write_text("print('hi')", encoding="utf-8")
    output = tmp_path / "out"

    exit_code = main(
        [
            "convert",
            str(source),
            str(output),
            "--style",
            "classic",
            "--exclude",
            "__init__",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Planned 1 file(s) for classic conversion." in captured.out
    assert "module.py" in captured.out
