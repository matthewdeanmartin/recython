from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path

import recython.ai_calls as ai
from recython.config import RecythonConfig
from recython.jobs import PlannedFile, PlannedOutput, RunRequest, RunResult, SkippedFile
from recython.prompts import PromptPack, load_prompt_pack, render_prompt
from recython.tidy import extract_code_block
from recython.validation import validate_outputs


def build_run_request(
    *,
    source_root: Path,
    output_root: Path,
    style: str,
    provider: str,
    model: str,
    temperature: float,
    max_completion_tokens: int,
    exclude: list[str],
    include: list[str],
    prompt_profile: str,
    max_attempts: int,
    write_manifest: bool,
    dry_run: bool,
) -> RunRequest:
    return RunRequest(
        source_root=source_root.resolve(),
        output_root=output_root.resolve(),
        style=style,
        provider=provider,
        model=model,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        exclude=list(exclude),
        include=list(include),
        prompt_profile=prompt_profile,
        max_attempts=max_attempts,
        write_manifest=write_manifest,
        dry_run=dry_run,
    )


def _discover_python_files(source_root: Path) -> list[Path]:
    if not source_root.exists():
        raise FileNotFoundError(f"The folder '{source_root}' does not exist.")
    return sorted(path for path in source_root.rglob("*.py") if path.is_file())


def _is_match(relative_path: Path, filters: list[str]) -> bool:
    target = str(relative_path).replace("\\", "/")
    return any(fragment in target for fragment in filters)


def _planned_outputs(style: str, output_root: Path, relative_path: Path) -> tuple[list[PlannedOutput], list[str]]:
    if style == "classic":
        base_path = output_root / relative_path.parent / relative_path.stem
        return (
            [
                PlannedOutput(kind="classic_pyx", path=base_path.with_suffix(".pyx")),
                PlannedOutput(kind="classic_pxd", path=base_path.with_suffix(".pxd")),
            ],
            ["classic_pyx", "classic_pxd"],
        )
    if style == "pure":
        return ([PlannedOutput(kind="pure", path=output_root / relative_path)], ["pure"])
    raise ValueError(f"Unsupported style '{style}'.")


def plan_run(request: RunRequest) -> RunResult:
    result = RunResult(request=request)
    for source_path in _discover_python_files(request.source_root):
        result.examined_files.append(source_path)
        relative_path = source_path.relative_to(request.source_root)
        if _is_match(relative_path, request.exclude):
            result.skipped_files.append(SkippedFile(source_path=source_path, reason="excluded"))
            continue
        if request.include and not _is_match(relative_path, request.include):
            result.skipped_files.append(SkippedFile(source_path=source_path, reason="not included"))
            continue

        outputs, prompt_keys = _planned_outputs(request.style, request.output_root, relative_path)
        result.planned_files.append(
            PlannedFile(
                source_path=source_path,
                relative_path=relative_path,
                outputs=outputs,
                prompt_keys=prompt_keys,
            )
        )

    result.prompts_used = sorted({key for item in result.planned_files for key in item.prompt_keys})
    return result


def _make_artifacts_dir(request: RunRequest) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
    run_dir = request.output_root.parent / ".recython" / "runs" / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "prompts").mkdir(exist_ok=True)
    (run_dir / "responses").mkdir(exist_ok=True)
    return run_dir


def _snapshot_stem(relative_path: Path) -> str:
    return "__".join(relative_path.parts)


def _write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def _format_validation_feedback(validation_result: dict[str, object]) -> str:
    lines = []
    for item in validation_result["files"]:
        if item["ok"]:
            continue
        lines.append(f"- {item['path']} ({item['validator']}): {item['error']}")
    return "\n".join(lines)


def _render_repair_prompt(
    *,
    prompt_pack: PromptPack,
    style: str,
    source_text: str,
    previous_output: str,
    validation_result: dict[str, object],
) -> str:
    template_key = "pure" if style == "pure" else "classic_pyx"
    base_prompt = render_prompt(prompt_pack, template_key, XXXCODEXXX=source_text)
    feedback = _format_validation_feedback(validation_result)
    fence = "python" if style == "pure" else "cython"
    return (
        f"{base_prompt}\n\n"
        "The previous generated output failed validation.\n"
        "Fix the issues below and return the full corrected file only.\n\n"
        "Validation feedback:\n"
        f"{feedback}\n\n"
        "Previous generated output:\n"
        f"```{fence}\n{previous_output}\n```"
    )


def _write_run_artifacts(result: RunResult) -> None:
    if result.artifacts_dir is None:
        return

    manifest_path = result.artifacts_dir / "manifest.json"
    manifest_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    result.manifest_path = manifest_path

    report_lines = [
        "# Recython Run Report",
        "",
        f"Style: {result.request.style}",
        f"Prompt profile: {result.request.prompt_profile}",
        f"Examined files: {len(result.examined_files)}",
        f"Planned files: {len(result.planned_files)}",
        f"Written files: {len(result.written_files)}",
        f"Skipped files: {len(result.skipped_files)}",
    ]
    if result.skipped_files:
        report_lines.extend(["", "## Skipped"])
        for skipped in result.skipped_files:
            report_lines.append(f"- {skipped.source_path}: {skipped.reason}")
    report_path = result.artifacts_dir / "report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    result.report_path = report_path


def execute_run(request: RunRequest) -> RunResult:
    prompt_pack = load_prompt_pack(
        RecythonConfig(project_root=request.source_root, prompt_profile=request.prompt_profile)
    )
    return execute_run_with_pack(request, prompt_pack)


def execute_run_with_pack(request: RunRequest, prompt_pack: PromptPack) -> RunResult:
    if request.provider != "openai":
        raise ValueError(f"Unsupported provider '{request.provider}'.")

    result = plan_run(request)
    if request.write_manifest:
        result.artifacts_dir = _make_artifacts_dir(request)

    if request.dry_run:
        _write_run_artifacts(result)
        return result

    validation_summary = {
        "ok": True,
        "checked": 0,
        "failed": 0,
        "files": [],
        "attempts": {},
    }

    for planned in result.planned_files:
        source_text = planned.source_path.read_text(encoding="utf-8")
        snapshot_prefix = _snapshot_stem(planned.relative_path)
        attempts: list[dict[str, object]] = []
        final_outputs: list[Path] = []
        file_validation = {"ok": True, "checked": 0, "failed": 0, "files": []}
        pyx_contents = ""
        pure_contents = ""

        for attempt_index in range(1, request.max_attempts + 1):
            if request.style == "classic":
                if attempt_index == 1:
                    pyx_prompt = render_prompt(prompt_pack, "classic_pyx", XXXCODEXXX=source_text)
                else:
                    pyx_prompt = _render_repair_prompt(
                        prompt_pack=prompt_pack,
                        style=request.style,
                        source_text=source_text,
                        previous_output=pyx_contents,
                        validation_result=file_validation,
                    )
                pyx_response = ai.completion(
                    pyx_prompt,
                    model=request.model,
                    max_completion_tokens=request.max_completion_tokens,
                    temperature=request.temperature,
                )
                pyx_contents = extract_code_block(pyx_response)
                pyx_output = planned.outputs[0].path
                _write_text(pyx_output, pyx_contents)

                pxd_prompt = render_prompt(prompt_pack, "classic_pxd", XXXRESULTXXX=pyx_response)
                pxd_response = ai.completion(
                    pxd_prompt,
                    model=request.model,
                    max_completion_tokens=request.max_completion_tokens,
                    temperature=request.temperature,
                )
                pxd_contents = extract_code_block(pxd_response)
                pxd_output = planned.outputs[1].path
                _write_text(pxd_output, pxd_contents)
                final_outputs = [pyx_output, pxd_output]

                if result.artifacts_dir is not None:
                    suffix = f".attempt{attempt_index}"
                    _write_text(
                        result.artifacts_dir / "prompts" / f"{snapshot_prefix}{suffix}.classic_pyx.md",
                        pyx_prompt,
                    )
                    _write_text(
                        result.artifacts_dir / "prompts" / f"{snapshot_prefix}{suffix}.classic_pxd.md",
                        pxd_prompt,
                    )
                    _write_text(
                        result.artifacts_dir / "responses" / f"{snapshot_prefix}{suffix}.classic_pyx.txt",
                        pyx_response,
                    )
                    _write_text(
                        result.artifacts_dir / "responses" / f"{snapshot_prefix}{suffix}.classic_pxd.txt",
                        pxd_response,
                    )
            else:
                if attempt_index == 1:
                    pure_prompt = render_prompt(prompt_pack, "pure", XXXCODEXXX=source_text)
                else:
                    pure_prompt = _render_repair_prompt(
                        prompt_pack=prompt_pack,
                        style=request.style,
                        source_text=source_text,
                        previous_output=pure_contents,
                        validation_result=file_validation,
                    )
                pure_response = ai.completion(
                    pure_prompt,
                    model=request.model,
                    max_completion_tokens=request.max_completion_tokens,
                    temperature=request.temperature,
                )
                pure_contents = extract_code_block(pure_response)
                pure_output = planned.outputs[0].path
                _write_text(pure_output, pure_contents)
                final_outputs = [pure_output]

                if result.artifacts_dir is not None:
                    suffix = f".attempt{attempt_index}"
                    _write_text(result.artifacts_dir / "prompts" / f"{snapshot_prefix}{suffix}.pure.md", pure_prompt)
                    _write_text(
                        result.artifacts_dir / "responses" / f"{snapshot_prefix}{suffix}.pure.txt",
                        pure_response,
                    )

            file_validation = validate_outputs(
                final_outputs,
                style=request.style,
                python_compile_enabled=request.style == "pure",
                cython_compile_enabled=request.style == "classic",
            )
            attempts.append(
                {
                    "attempt": attempt_index,
                    "ok": file_validation["ok"],
                    "failed": file_validation["failed"],
                }
            )
            if file_validation["ok"]:
                break

        result.written_files.extend(final_outputs)
        validation_summary["checked"] += int(file_validation["checked"])
        validation_summary["failed"] += int(file_validation["failed"])
        validation_summary["files"].extend(file_validation["files"])
        validation_summary["attempts"][str(planned.source_path)] = attempts
        if not file_validation["ok"]:
            validation_summary["ok"] = False

    result.validation_results = validation_summary

    _write_run_artifacts(result)
    return result
