# Agent Workflow Notes

## Use `uv run`
Always run project tools through `uv run` or the `make` targets that wrap `uv run`.

Why this matters:

- It uses the project's locked environment instead of whatever happens to be on system Python.
- It keeps global Python packages clean.
- It makes local runs, CI, and agent runs behave the same way.

Examples:

- `uv run pytest -q`
- `uv run ruff check recython tests`
- `make check-llm`

## Human targets vs `*-llm` targets
The `Makefile` has two families of jobs.

Human-oriented jobs:

- `make format`
- `make lint`
- `make test`
- `make check`

These are the fuller commands for deliberate development passes. They may run more checks and may rewrite files when that is the target's purpose.

LLM-oriented jobs:

- `make lint-llm`
- `make test-llm`
- `make check-llm`

These are designed for tight repair loops:

- They are terse by default.
- They do not reformat or auto-fix files.
- They are intended to minimize noisy output and token usage.

## Recommended loop
For fast agent or pair-programming passes:

1. `make check-llm`
2. Fix the reported issues.
3. Re-run `make check-llm`

Before a broader handoff or release-quality pass:

1. `make format`
2. `make check`

## Dependency setup
If the environment is missing dependencies or the lock file changed, run:

- `make sync`

If dependencies changed intentionally and the lock file needs to be refreshed, run:

- `make lock`
