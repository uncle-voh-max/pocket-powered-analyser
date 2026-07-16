FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
    git curl build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "research_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
