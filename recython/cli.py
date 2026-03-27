from __future__ import annotations

import argparse
import json
from pathlib import Path

from recython.config import apply_config_overrides, load_config, render_starter_config
from recython.engine import build_run_request, execute_run_with_pack, plan_run
from recython.jobs import RunResult
from recython.prompts import PROMPT_KEYS, list_prompt_profiles, load_prompt_pack
from recython.validation import validate_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recython",
        description="LLM-assisted Python-to-Cython harness for classic and pure-Cython workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="Run a translation pass for a source tree.")
    convert.add_argument("source", nargs="?", type=Path, help="Source package or module directory to translate.")
    convert.add_argument("output", nargs="?", type=Path, help="Destination folder for translated files.")
    convert.add_argument(
        "--style",
        choices=("classic", "pure"),
        help="Translation strategy to use.",
    )
    convert.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="TEXT",
        help="Substring filter for files that should never be translated. Repeat as needed.",
    )
    convert.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview matching Python files without calling the model.",
    )
    convert.add_argument("--include", action="append", default=[], metavar="TEXT", help="Limit work to matching files.")
    convert.add_argument("--model", help="Override the configured model for this run.")
    convert.add_argument("--prompt-profile", help="Select a bundled prompt profile.")
    convert.add_argument("--max-attempts", type=int, help="Maximum generation attempts per source file.")
    convert.add_argument("--pyproject", type=Path, help="Load configuration from a specific pyproject.toml.")
    convert.add_argument("--report-json", type=Path, help="Write the run result as JSON to this path.")
    convert.set_defaults(handler=handle_convert)

    plan = subparsers.add_parser("plan", help="Preview the files and outputs that would be touched.")
    plan.add_argument("source", nargs="?", type=Path, help="Source package or module directory to translate.")
    plan.add_argument("output", nargs="?", type=Path, help="Destination folder for translated files.")
    plan.add_argument("--style", choices=("classic", "pure"), help="Translation strategy to use.")
    plan.add_argument("--exclude", action="append", default=[], metavar="TEXT", help="Substring filter to skip files.")
    plan.add_argument("--include", action="append", default=[], metavar="TEXT", help="Limit work to matching files.")
    plan.add_argument("--prompt-profile", help="Select a bundled prompt profile.")
    plan.add_argument("--max-attempts", type=int, help="Maximum generation attempts per source file.")
    plan.add_argument("--pyproject", type=Path, help="Load configuration from a specific pyproject.toml.")
    plan.add_argument("--report-json", type=Path, help="Write the run result as JSON to this path.")
    plan.set_defaults(handler=handle_plan)

    validate = subparsers.add_parser("validate", help="Validate generated outputs.")
    validate.add_argument("target", nargs="?", type=Path, help="Output directory to validate.")
    validate.add_argument("--style", choices=("classic", "pure"), help="Translation strategy to validate.")
    validate.add_argument("--pyproject", type=Path, help="Load configuration from a specific pyproject.toml.")
    validate.add_argument("--report-json", type=Path, help="Write the validation result as JSON to this path.")
    validate.set_defaults(handler=handle_validate)

    prompts = subparsers.add_parser("prompts", help="Inspect bundled prompt templates.")
    prompts_subparsers = prompts.add_subparsers(dest="prompts_command", required=True)

    prompts_list = prompts_subparsers.add_parser("list", help="List prompt profiles and known templates.")
    prompts_list.set_defaults(handler=handle_prompts_list)

    prompts_show = prompts_subparsers.add_parser("show", help="Print a prompt template.")
    prompts_show.add_argument(
        "template",
        choices=("classic-pyx", "classic-pxd", "pure"),
        help="Template to print.",
    )
    prompts_show.add_argument("--profile", default="default", help="Prompt profile to inspect.")
    prompts_show.set_defaults(handler=handle_prompts_show)

    prompts_doctor = prompts_subparsers.add_parser("doctor", help="Validate the effective prompt pack.")
    prompts_doctor.add_argument("--profile", help="Prompt profile to validate.")
    prompts_doctor.add_argument("--pyproject", type=Path, help="Load configuration from a specific pyproject.toml.")
    prompts_doctor.set_defaults(handler=handle_prompts_doctor)

    config = subparsers.add_parser("config", help="Inspect or create recython config.")
    config_subparsers = config.add_subparsers(dest="config_command", required=True)

    config_init = config_subparsers.add_parser("init", help="Print or append a starter [tool.recython] block.")
    config_init.add_argument("--pyproject", type=Path, help="Target pyproject.toml. Defaults to ./pyproject.toml.")
    config_init.add_argument("--write", action="store_true", help="Append the starter block to the pyproject file.")
    config_init.set_defaults(handler=handle_config_init)

    return parser


def _resolve_effective_request(args: argparse.Namespace):
    config = load_config(args.pyproject, start_path=Path.cwd())
    config = apply_config_overrides(
        config,
        style=getattr(args, "style", None),
        model=getattr(args, "model", None),
        prompt_profile=getattr(args, "prompt_profile", None),
        max_attempts=getattr(args, "max_attempts", None),
    )
    source = args.source or (config.source[0] if config.source else None)
    output = args.output or config.output_root
    if source is None:
        raise ValueError("A source path is required either on the CLI or in [tool.recython].source.")

    merged_exclude = list(config.exclude)
    merged_exclude.extend(getattr(args, "exclude", []))
    merged_include = list(config.include)
    merged_include.extend(getattr(args, "include", []))

    request = build_run_request(
        source_root=source,
        output_root=output,
        style=config.style,
        provider=config.provider,
        model=config.model,
        temperature=config.temperature,
        max_completion_tokens=config.max_completion_tokens,
        exclude=merged_exclude,
        include=merged_include,
        prompt_profile=config.prompt_profile,
        max_attempts=config.max_attempts,
        write_manifest=config.write_manifest,
        dry_run=getattr(args, "dry_run", False),
    )
    return config, request


def _write_report_json(path: Path | None, result: RunResult) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")


def _print_plan(result: RunResult) -> None:
    print(f"Examined {len(result.examined_files)} Python file(s).")
    print(f"Planned {len(result.planned_files)} file(s) for {result.request.style} conversion.")
    for planned in result.planned_files:
        outputs = ", ".join(str(output.path) for output in planned.outputs)
        print(f"{planned.source_path} -> {outputs}")
    if result.skipped_files:
        print("Skipped:")
        for skipped in result.skipped_files:
            print(f"{skipped.source_path} ({skipped.reason})")


def handle_convert(args: argparse.Namespace) -> int:
    config, request = _resolve_effective_request(args)
    prompt_pack = load_prompt_pack(config)
    result = execute_run_with_pack(request, prompt_pack)
    _write_report_json(args.report_json, result)

    if args.dry_run:
        _print_plan(result)
        return 0

    print(f"Wrote {len(result.written_files)} file(s) to {request.output_root}")
    for path in result.written_files:
        print(path)
    if result.manifest_path is not None:
        print(f"Manifest: {result.manifest_path}")
    return 0


def handle_plan(args: argparse.Namespace) -> int:
    _, request = _resolve_effective_request(args)
    request.dry_run = True
    result = plan_run(request)
    _write_report_json(args.report_json, result)
    _print_plan(result)
    return 0


def handle_validate(args: argparse.Namespace) -> int:
    config = load_config(args.pyproject, start_path=Path.cwd())
    config = apply_config_overrides(config, style=getattr(args, "style", None))
    target = (args.target or config.output_root).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Validation target '{target}' does not exist.")

    if config.style == "pure":
        written_files = sorted(path for path in target.rglob("*.py") if path.is_file())
    else:
        written_files = sorted(path for path in target.rglob("*") if path.is_file() and path.suffix in {".pyx", ".pxd"})

    result = validate_outputs(
        written_files,
        style=config.style,
        python_compile_enabled=config.validation.python_compile,
        cython_compile_enabled=config.validation.cython_compile,
    )
    if args.report_json is not None:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Validated {result['checked']} file result(s); failures: {result['failed']}")
    for item in result["files"]:
        status = "ok" if item["ok"] else "failed"
        print(f"{item['path']} [{item['validator']}] {status}")
        if item["error"]:
            print(item["error"])
    return 0 if result["ok"] else 1


def handle_prompts_list(_args: argparse.Namespace) -> int:
    print("Profiles:")
    for profile in list_prompt_profiles():
        print(profile)
    print("Templates:")
    for label in ("classic-pyx", "classic-pxd", "pure"):
        print(label)
    return 0


def handle_prompts_show(args: argparse.Namespace) -> int:
    config = apply_config_overrides(load_config(start_path=Path.cwd()), prompt_profile=args.profile)
    pack = load_prompt_pack(config)
    template_key = {
        "classic-pyx": "classic_pyx",
        "classic-pxd": "classic_pxd",
        "pure": "pure",
    }[args.template]
    print(pack.templates[template_key].text)
    return 0


def handle_prompts_doctor(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.pyproject, start_path=Path.cwd())
        config = apply_config_overrides(config, prompt_profile=args.profile)
        pack = load_prompt_pack(config)
    except ValueError as exc:
        print(exc)
        return 1

    print(f"Prompt pack '{pack.profile}' is valid.")
    for key in PROMPT_KEYS:
        print(f"{key}: {pack.templates[key].source}")
    return 0


def handle_config_init(args: argparse.Namespace) -> int:
    starter = render_starter_config()
    if not args.write:
        print(starter)
        return 0

    pyproject = args.pyproject or Path.cwd() / "pyproject.toml"
    existing = pyproject.read_text(encoding="utf-8") if pyproject.exists() else ""
    if "[tool.recython]" in existing:
        print(f"{pyproject} already contains a [tool.recython] section.")
        return 1

    suffix = "\n\n" if existing and not existing.endswith("\n\n") else ""
    pyproject.write_text(existing + suffix + starter + "\n", encoding="utf-8")
    print(f"Appended starter config to {pyproject}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = args.handler
    return handler(args)
