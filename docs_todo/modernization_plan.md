# Recython Modernization Plan

## Mission
Recython should become a focused harness for one job: help a developer cythonize Python code with LLM assistance, either for an initial migration or for ongoing maintenance after the Python source changes.

The product should feel dependable and explicit rather than magical. That means:

- A clear CLI first.
- Predictable prompt and model configuration.
- `pyproject.toml` driven project defaults.
- Repeatable outputs and resumable runs.
- Later UI layers that wrap the same engine instead of inventing their own logic.

## Current state

### Strengths
- There is already a usable split between classic Cython output and pure-Python Cython output.
- Prompt templates are stored as editable files rather than being buried in code.
- The repo includes examples, tests, and some early documentation assets.

### Remaining gaps
- The codebase still carries duplicate or parallel packages (`recython` and `recython_pure`) that blur ownership.
- Resume support is still missing, even though runs now persist manifests, source snapshots, prompt snapshots, response snapshots, validation results, and maintenance metadata.
- Maintenance mode exists, but it is still manifest-based rather than git-ref or timestamp aware.
- Validation currently focuses on syntax and Cython parser checks; richer compile, lint, and type-check feedback is still missing.
- The CLI covers the core workflows, but `resume` and a richer reporting surface are still open.
- Test coverage now includes config parsing, planning, validation, repair retries, and maintenance baselines, but end-to-end fixture coverage is still modest.

## Target product shape

### Core engine
Build a single orchestration layer that accepts:

- Source root or explicit file list.
- Output mode: `classic`, `pure`, or later `compile-only`.
- LLM provider and model configuration.
- Prompt profile.
- Include and exclude rules.
- Maintenance context such as baseline generated files and diff strategy.

The engine should produce a run result containing:

- Files examined.
- Files skipped and why.
- Prompts used.
- Raw LLM responses.
- Written outputs.
- Validation results.
- Compile or syntax feedback where available.

### CLI
The CLI should become the primary interface and support both one-shot and iterative work.

Recommended commands:

1. `recython convert`
   Convert a module, package, or explicit file set.
2. `recython maintain`
   Re-run cythonization against changed Python sources while preserving hand-edited generated files where possible.
3. `recython prompts list`
   Show available bundled prompt packs.
4. `recython prompts show`
   Print the effective prompt template.
5. `recython prompts doctor`
   Validate placeholders and prompt pack completeness.
6. `recython config init`
   Write a starter `[tool.recython]` config block.
7. `recython plan`
   Preview which files, prompts, and outputs would be touched.
8. `recython validate`
   Run syntax and compile-oriented checks over generated outputs.
9. `recython resume`
   Continue an interrupted run from saved state.
10. `recython report`
   Summarize what changed and what still needs human review.

### Config model
Add a first-class `[tool.recython]` block in `pyproject.toml`.

Recommended initial schema:

```toml
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
maintenance_mode = false
backup_originals = false
write_manifest = true

[tool.recython.validation]
python_compile = true
cython_compile = false
ruff = true
mypy = false

[tool.recython.prompts]
system = "prompts/system.md"
classic_pyx = "prompts/classic_pyx.md"
classic_pxd = "prompts/classic_pxd.md"
pure = "prompts/pure.md"
```

Design rules:

- CLI flags override config.
- Config overrides package defaults.
- Missing config should not block basic usage.
- Prompt paths should allow local overrides without editing package files.

### Prompt tuning
Prompt tuning is product surface area, not a hidden hack.

Current direction:

- Named prompt profiles such as `safe`, `performance`, `minimal-diff`, and `maintenance`.
- Layered prompts: system guidance, style-specific prompt, file-context prompt, validation prompt.
- Placeholder validation so a broken custom prompt fails early.
- Optional inclusion of project-level context such as coding standards or performance goals.
- A way to capture compile failures and feed them back into a repair prompt.

### Maintenance cythonization
Maintenance mode now has a first usable shape:

1. Compare current Python source hashes to a baseline manifest.
2. Skip unchanged files.
3. Provide old source, current source, and previous generated output to the model.
4. Ask for the smallest safe update to generated output.
5. Validate the result and retry with targeted repair context when needed.
6. Save a report showing changed files, unchanged files, regenerated outputs, and manual-review candidates.

The next step is broadening change detection beyond manifest-to-manifest comparison.

## Architecture direction

### Suggested package layout
Move toward a structure like this:

```text
recython/
  cli.py
  config.py
  engine.py
  jobs.py
  prompts.py
  providers/
    openai.py
  strategies/
    classic.py
    pure.py
  validation/
    compile.py
    lint.py
  ui/
    tui/
    tkinter/
```

Guiding principle:

- Providers talk to LLM APIs.
- Strategies know how to translate a file in a given style.
- The engine coordinates runs.
- UI layers call the engine, never the provider directly.

### Provider abstraction
OpenAI is still the first-class provider, but the orchestration layer should keep moving toward a narrow provider interface that covers:

- Text generation.
- Structured result metadata.
- Retries and rate-limit handling.
- Request and response logging with redaction hooks.

That keeps the harness usable with Codex, Claude, or local models later without rewriting orchestration.

### Run artifacts
Runs now write machine-readable manifests under `.recython/runs/<timestamp>/` with prompt snapshots, response snapshots, validation data, source snapshots, and `report.md`.

The main missing artifact work is resume-specific state and a cleaner operator-facing report surface.

## Delivery phases

### Phase 0: Foundation cleanup
- [x] Finish moving the repo to `uv` + `hatchling`.
- [x] Replace placeholder CLI with a stable command structure.
- [ ] Remove or clearly quarantine dead helper scripts.
- [x] Normalize package metadata and dependency groups.
- [ ] Fix obvious path and output bugs.

### Phase 5: UI shells
- Build a TUI over the existing engine for local operator workflows.
- Build a Tkinter GUI for broader accessibility.
- Keep both as thin frontends over the same job APIs and config model.

### Cross-cutting cleanup
- Remove or clearly quarantine dead helper scripts.
- Consolidate duplicate package ownership between `recython` and `recython_pure`.
- Add resume support over existing run artifacts.
- Improve reporting and validation depth without bloating the CLI.

## Testing strategy

### Unit tests
- CLI argument parsing.
- Config loading and precedence.
- Prompt template resolution.
- File filtering and mapping.
- Output path planning.

### Integration tests
- Classic conversion flow with mocked provider responses.
- Pure conversion flow with mocked provider responses.
- Maintenance mode against a small fixture repo.
- Manifest and report generation.

### Golden tests
- Snapshot prompt rendering.
- Snapshot generated output mapping for representative projects.

### Tooling checks
- `uv run pytest`
- `uv run ruff check .`
- `uv run black --check .`
- Optional later: `uv run mypy recython`

## Immediate backlog

- Clean up or delete obsolete helper scripts once replacements exist.
- Add resume support on top of saved manifests and artifacts.
- Expand maintenance-mode detection beyond baseline-manifest comparison.
- Add richer validation and reporting for review-heavy workflows.

## Success criteria
The project is on the right path when:

- A new user can run one documented `uv run recython ...` command and get predictable output.
- A project can store repeatable defaults in `pyproject.toml`.
- A failed generation can be inspected, resumed, and repaired.
- Maintenance cythonization is a supported path rather than a manual workaround.
- Future TUI and Tkinter layers reuse the same engine cleanly.
