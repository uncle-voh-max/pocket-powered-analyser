# Contributing

Thanks for your interest in Pocket Powered Analyser.

## Pull requests

- Keep changes focused. One PR per feature, refactor, or bug fix.
- Write tests for every non-trivial addition. Run the full suite before opening:

  ```bash
  uv sync --extra dev
  uv run pytest -v
  ```

- Run the linter and type checker on changed files:

  ```bash
  uv run ruff check src/
  uv run mypy src/
  ```

- Follow the existing code style:
  - 100-character line length
  - Double quotes for strings
  - Typed Pydantic models at system boundaries
  - Async IO for network-bound operations
  - All external calls must have timeouts, retries, structured errors, and tests
  - Never hide partial failures

## Adding a source adapter

1. Create `src/research_agent/adapters/<source>.py`
2. Implement `BaseSearchAdapter` with `search_for_query()` and `fetch()`
3. Register in `_get_adapter()` in `graph/nodes.py`
4. Add a graph node in `graph/nodes.py` + register in `graph/workflow.py`
5. Add mock data in `adapters/mock.py`
6. Write tests in `tests/unit/test_adapters.py`

See `docs/architecture.md` for the full extension guide.

## Code of conduct

Be respectful, constructive, and professional. This is a staff-engineering-grade project — assume good intent, review with care, and hold each other to a high bar.
