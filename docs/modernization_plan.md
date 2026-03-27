# Recython Modernization Plan

## Mission
Recython should become a focused harness for one job: help a developer cythonize Python code with LLM assistance, either for an initial migration or for ongoing maintenance after the Python source changes.

The product should feel dependable and explicit rather than magical. That means:

- A clear CLI first.
- Predictable prompt and model configuration.
- `pyproject.toml` driven project defaults.
- Repeatable outputs and resumable runs.
- Later UI layers that wrap the same engine instead of inventing their own logic.

## Current state assessment

### Strengths worth preserving
- There is already a usable split between classic Cython output and pure-Python Cython output.
- Prompt templates are stored as editable files rather than being buried in code.
- The repo includes examples, tests, and some early documentation assets.

### Gaps and risks
- Packaging and build metadata have been moved to `uv` + `hatchling`, but the runtime/config surface still needs modernization.
- The public CLI entrypoint now has a usable scaffold, but it does not yet cover the broader command set in this plan.
- OpenAI integration was tied to older assumptions and did not expose configuration cleanly.
- The known pure-style output-shape bug has been fixed, but broader output planning is still ad hoc.
- The codebase contains duplicate or parallel packages (`recython` and `recython_pure`) that blur ownership.
- Resume strategy is still missing, even though run manifests, prompt snapshots, validation results, and a basic job model now exist.
- `pyproject.toml` can now describe translation defaults and prompt overrides, but maintenance-mode behavior is still not implemented.
- Test coverage now includes basic CLI flows, config parsing, run planning, validation, and repair retries, but it is still narrow around end-to-end orchestration and maintenance mode.

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
Prompt tuning should be treated as product surface area, not a hidden hack.

Needed capabilities:

- Named prompt profiles such as `safe`, `performance`, `minimal-diff`, and `maintenance`.
- Layered prompts: system guidance, style-specific prompt, file-context prompt, validation prompt.
- Placeholder validation so a broken custom prompt fails early.
- Optional inclusion of project-level context such as coding standards or performance goals.
- A way to capture compile failures and feed them back into a repair prompt.

### Maintenance cythonization
This is one of the most important scenarios and deserves first-class support.

Recommended flow:

1. Detect changed Python files since a git ref, manifest, or timestamp.
2. Load prior generated artifacts if they exist.
3. Provide both old Python and current Python context to the model.
4. Ask for the smallest safe update to generated output.
5. Validate the result.
6. Save a report showing generated diff, validation issues, and files needing manual review.

This mode should prefer stability over maximal optimization.

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
Even if OpenAI is the first-class provider, define a narrow provider interface now.

That interface should cover:

- Text generation.
- Structured result metadata.
- Retries and rate-limit handling.
- Request and response logging with redaction hooks.

That keeps the harness usable with Codex, Claude, or local models later without rewriting orchestration.

### Run artifacts
Each run should write a machine-readable manifest under a hidden working folder such as `.recython/runs/<timestamp>/`.

Recommended artifacts:

- `manifest.json`
- `prompts/`
- `responses/`
- `outputs/`
- `validation.json`
- `report.md`

This is critical for resume, debugging, and maintenance mode.

## Delivery phases

### Phase 0: Foundation cleanup
- [x] Finish moving the repo to `uv` + `hatchling`.
- [x] Replace placeholder CLI with a stable command structure.
- [ ] Remove or clearly quarantine dead helper scripts.
- [x] Normalize package metadata and dependency groups.
- [ ] Fix obvious path and output bugs.

### Phase 4: Maintenance mode
- Add baseline manifest support.
- Detect changed upstream files.
- Generate minimal-diff updates for affected outputs.
- Add reporting geared toward reviewing regenerated code.

### Phase 5: UI shells
- Build a TUI over the existing engine for local operator workflows.
- Build a Tkinter GUI for broader accessibility.
- Keep both as thin frontends over the same job APIs and config model.

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

### This pass
- [x] Move packaging to `hatchling` with `uv` dependency groups.
- [x] Replace the CLI stub with a usable command scaffold.
- [x] Fix the pure output path bug.
- [x] Write and check in a comprehensive modernization plan.

### Next pass
- Clean up or delete obsolete helper scripts once replacements exist.

## Success criteria
The project is on the right path when:

- A new user can run one documented `uv run recython ...` command and get predictable output.
- A project can store repeatable defaults in `pyproject.toml`.
- A failed generation can be inspected, resumed, and repaired.
- Maintenance cythonization is a supported path rather than a manual workaround.
- Future TUI and Tkinter layers reuse the same engine cleanly.
