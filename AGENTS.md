# Research Agent — Implementation Guide

## Architecture

See `docs/architecture.md` for the full architecture documentation, graph flow, and extension points.

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
