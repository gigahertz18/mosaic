# Mosaic

Mosaic is a standalone, domain-agnostic AI Knowledge Platform
microservice. It lets any application ingest documents, organize them
into collections, retrieve relevant knowledge, and generate AI-powered
answers with citations. It is reusable infrastructure — not tied to any
specific business domain.

See [`docs/architecture.md`](docs/architecture.md) for the full design.

## Requirements

Only the following are required on the host:

- Docker
- Docker Compose
- Make

No local installation of Python, `uv`, PostgreSQL, Ruff, Black, or mypy
is required for normal development.

## Getting started

```bash
make build     # build the application image
make up        # start the app, PostgreSQL (pgvector), and MinIO
make migrate   # apply database migrations
make health    # curl the running health endpoint
```

Once running, the API is available at `http://localhost:8000`, with an
unversioned health check at `GET /health`.

## Development workflow

```bash
make shell            # open a shell inside the app container
make format            # check formatting (black -l 120 --check)
make format-fix        # apply formatting
make lint               # ruff
make typecheck          # mypy
make test                # full test suite
make test-unit           # unit tests only (no external dependencies)
make test-integration    # integration tests (spins up db + minio)
make coverage             # tests with coverage report (>95% target)
```

Run `make help` for the full list of targets.

## Configuration

Mosaic never uses a `.env` file. Configuration is strongly typed
(`app/core/config.py`) and supplied by the execution environment:
Docker Compose locally, GitHub Actions in CI, and the hosting platform
in staging/production. See `docker-compose.yml` for the local variable
set.

## Milestone status

- [x] Milestone 1 — project setup, Docker, configuration, logging,
      PostgreSQL, Alembic, GitHub Actions CI, health endpoint
- [ ] Milestone 2 — Collection (model, schema, repository, service,
      route, tests)
- [ ] Milestone 3 — Document (upload, storage provider)
- [ ] Milestone 4 — Chunk generation
- [ ] Milestone 5 — Embedding generation
- [ ] Milestone 6 — Similarity search
- [ ] Milestone 7 — Chat with citations
