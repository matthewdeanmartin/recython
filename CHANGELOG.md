# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added `recython.config`, `recython.engine`, `recython.jobs`, and `recython.prompts` to support pyproject-driven runs, centralized planning, prompt packs, and run artifacts.
- Added `recython plan`, `recython prompts doctor`, and `recython config init` commands.
- Added machine-readable run reporting plus manifest, prompt snapshot, and response snapshot artifacts under `.recython/runs/`.
- Added validation helpers plus a `recython validate` command for Python and optional Cython output checks.

### Changed
- Changed `recython convert` to resolve defaults from `[tool.recython]` and run through the new orchestration layer.
- Changed the classic and pure translation entrypoints to delegate through the shared engine instead of calling templates and providers directly.
- Changed prompt handling so bundled profiles and custom prompt overrides are validated before execution.
- Changed generation runs to support explicit retry counts and validation-driven repair attempts.
