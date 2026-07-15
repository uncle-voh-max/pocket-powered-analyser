

# Research Agent — Implementation Guide

## Architecture

See `docs/architecture.md` for the full architecture documentation, graph flow, and extension points.


## Engineering principles:
- Prefer simple, explicit architecture over clever abstractions.
- Use typed Pydantic models at system boundaries.
- Keep source adapters pluggable.
- All external calls must have timeouts, retries, structured errors, and tests.
- Never hide partial failures.
- Never fabricate citations or evidence.
- Treat social media and Reddit as anecdotal unless corroborated.
- Prefer async IO for network-bound source collection.
- Keep LLM calls behind interfaces so models/providers can be swapped.
- All generated reports must distinguish facts, claims, opinions, uncertainty, and limitations.
- No secrets in code, logs, fixtures, or docs.
- Add tests for every non-trivial module.
- Use uv, ruff, mypy/pyright, pytest, and pytest-asyncio.
- Write code that a staff engineer would be comfortable operating in production.

## Quick Start

```bash
cp .env.example .env
# Add OPENAI_API_KEY to .env
uv sync
uv run python -m research_agent.cli run "What is the impact of AI safety?"
```

## Adding a New Source Adapter

1. Create `src/research_agent/adapters/<source>.py`
2. Implement `BaseSearchAdapter` with `search_for_query()` and `fetch()`
3. Register in `_get_adapter()` in `src/research_agent/graph/nodes.py`
4. Add a graph node in `graph/nodes.py` + register in `graph/workflow.py`
5. Add mock data in `adapters/mock.py`
6. Write tests in `tests/unit/test_adapters.py`

## Key Interfaces

- `BaseSearchAdapter`: All source adapters implement this
- `Repository`: Storage backends implement this
- `ResearchState`: Single graph state flows through all nodes

## Testing

```bash
pytest -v -m "not slow"
pytest -v
```
