# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

WORKDIR /workspace

COPY pyproject.toml ./
RUN uv venv "$UV_PROJECT_ENVIRONMENT"

ENV PATH="/opt/venv/bin:${PATH}"

FROM base AS dev
RUN uv pip install --python /opt/venv/bin/python -e ".[dev]"
COPY . .
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production
RUN uv pip install --python /opt/venv/bin/python .
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./alembic.ini
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
