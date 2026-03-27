from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

from recython.classic_style import cythonize_classic_project
from recython.filesystem import get_files_and_contents, load_template
from recython.pure_style import pure_cythonize_project

Converter = Callable[[Path, Path, list[str]], list[Path]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recython",
        description="LLM-assisted Python-to-Cython harness for classic and pure-Cython workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="Run a translation pass for a source tree.")
    convert.add_argument("source", type=Path, help="Source package or module directory to translate.")
    convert.add_argument("output", type=Path, help="Destination folder for translated files.")
    convert.add_argument(
        "--style",
        choices=("classic", "pure"),
        default="classic",
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
    convert.set_defaults(handler=handle_convert)

    prompts = subparsers.add_parser("prompts", help="Inspect bundled prompt templates.")
    prompts_subparsers = prompts.add_subparsers(dest="prompts_command", required=True)

    prompts_list = prompts_subparsers.add_parser("list", help="List known prompt templates.")
    prompts_list.set_defaults(handler=handle_prompts_list)

    prompts_show = prompts_subparsers.add_parser("show", help="Print a prompt template.")
    prompts_show.add_argument(
        "template",
        choices=("classic-pyx", "classic-pxd", "pure"),
        help="Template to print.",
    )
    prompts_show.set_defaults(handler=handle_prompts_show)

    return parser


def handle_convert(args: argparse.Namespace) -> int:
    source = args.source.resolve()
    output = args.output.resolve()
    excludes = list(args.exclude)

    if args.dry_run:
        matches = [
            path
            for path, _contents in get_files_and_contents(source)
            if not any(fragment in str(path) for fragment in excludes)
        ]
        print(f"Matched {len(matches)} Python files for {args.style} conversion:")
        for path in matches:
            print(path)
        return 0

    converter: Converter = (
        cythonize_classic_project if args.style == "classic" else pure_cythonize_project
    )
    written = converter(source, output, excludes)
    print(f"Wrote {len(written)} file(s) to {output}")
    for path in written:
        print(path)
    return 0


def handle_prompts_list(_args: argparse.Namespace) -> int:
    for label in ("classic-pyx", "classic-pxd", "pure"):
        print(label)
    return 0


def handle_prompts_show(args: argparse.Namespace) -> int:
    template_name = {
        "classic-pyx": "cython_style_pyx.md",
        "classic-pxd": "cython_style_pxd.md",
        "pure": "cython_pure_python_style.md",
    }[args.template]
    print(load_template(template_name))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = args.handler
    return handler(args)
