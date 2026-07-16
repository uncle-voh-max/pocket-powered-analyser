FROM mcr.microsoft.com/devcontainers/python:3.12

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv jupyter ipykernel

# Pre-install project dependencies globally so they're available immediately
RUN pip install --no-cache-dir \
    langgraph>=0.3.0 \
    langchain>=0.3.0 \
    langchain-openai>=0.3.0 \
    langchain-community>=0.3.0 \
    langchain-ollama>=1.0.0 \
    langgraph-checkpoint>=2.0.0 \
    pydantic>=2.0.0 \
    pydantic-settings>=2.0.0 \
    httpx>=0.27.0 \
    fastapi>=0.115.0 \
    uvicorn>=0.30.0 \
    typer>=0.12.0 \
    structlog>=24.0.0 \
    tenacity>=9.0.0 \
    python-dotenv>=1.0.0 \
    trafilatura>=1.8.0 \
    beautifulsoup4>=4.12.0 \
    lxml>=5.0.0 \
    aiosqlite>=0.20.0 \
    prometheus-client>=0.20.0 \
    opentelemetry-api>=1.25.0 \
    opentelemetry-sdk>=1.25.0 \
    rich>=13.0.0 \
    pyyaml>=6.0.0 \
    orjson>=3.10.0
