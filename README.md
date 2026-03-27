# recython
Use LLMs to assist in turning ordinary Python into Cython-oriented source, either as classic `.pyx`/`.pxd` output or pure-Python-with-Cython-annotations.

The project is still in active reconstruction. The current focus is a reliable single-purpose harness with a modern CLI, prompt tuning, and `pyproject.toml` driven configuration.

## Current workflows

### Classic style
Generate paired `.pyx` and `.pxd` files from Python source.

```powershell
uv run recython convert .\examples\src_hangman\hangman .\tmp\classic --style classic --exclude __init__
```

### Pure style
Generate Python files intended for Cython's pure-Python mode.

```powershell
uv run recython convert .\examples\src_hangman\hangman .\tmp\pure --style pure --exclude __init__
```

### Prompt inspection
Inspect the bundled templates before tuning or replacing them.

```powershell
uv run recython prompts list
uv run recython prompts show pure
```

## Why Cython?
- Compile Python-heavy modules for speed-sensitive paths.
- Compile for distribution and mild source obfuscation.
- Prepare code for tighter integration with C and C++ ecosystems.

## Product direction
The medium-term goal is a focused harness with two primary scenarios:

1. Initial cythonization for a module or package.
2. Maintenance cythonization for code that has drifted after upstream Python changes.

That foundation should support later TUI and Tkinter GUI frontends without forking core logic.

## Planning document
The modernization roadmap lives in [docs/modernization_plan.md](/C:/github/recython/docs/modernization_plan.md).
