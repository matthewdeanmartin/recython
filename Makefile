PYTHON := uv run python
UV_RUN := uv run
PACKAGE := recython
TEST_DIRS := tests

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make sync         - install/update project dependencies with uv"
	@echo "  make lock         - refresh uv.lock"
	@echo "  make format       - apply repo formatting for humans"
	@echo "  make lint         - full lint pass"
	@echo "  make test         - full pytest run"
	@echo "  make check        - human-oriented full verification"
	@echo "  make lint-llm     - terse lint pass without rewriting files"
	@echo "  make test-llm     - terse pytest pass"
	@echo "  make check-llm    - token-efficient verification for agent loops"
	@echo "  make clean        - remove local caches and generated artifacts"

.PHONY: sync
sync:
	$(UV_RUN) uv sync --dev

.PHONY: lock
lock:
	$(UV_RUN) uv lock

.PHONY: format
format:
	$(UV_RUN) ruff check . --fix
	$(UV_RUN) black .

.PHONY: lint
lint:
	$(UV_RUN) ruff check .
	$(UV_RUN) black --check .
	$(UV_RUN) mypy $(PACKAGE)

.PHONY: lint-llm
lint-llm:
	$(UV_RUN) ruff check $(PACKAGE) $(TEST_DIRS)

.PHONY: test
test:
	$(UV_RUN) pytest

.PHONY: test-llm
test-llm:
	$(UV_RUN) pytest -q

.PHONY: check
check: lint test

.PHONY: check-llm
check-llm: lint-llm test-llm

.PHONY: prompts
prompts:
	$(UV_RUN) recython prompts list

.PHONY: clean
clean:
	$(PYTHON) -c "from pathlib import Path; import shutil; targets=[Path('.pytest_cache'), Path('.mypy_cache'), Path('.ruff_cache'), Path('htmlcov'), Path('dist'), Path('build')]; [shutil.rmtree(path, ignore_errors=True) for path in targets]; [path.unlink() for path in (Path('.coverage'),) if path.exists()];"
