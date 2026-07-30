# Mosaic Architecture

Mosaic is a standalone, domain-agnostic microservice that lets any
application ingest documents, organize them into collections, retrieve
relevant knowledge, and generate AI-powered answers. It is reusable
infrastructure, not a demo tied to a specific business domain.

## Layering

Every feature follows the same request flow:

```
Client -> FastAPI Route -> Service -> Repository / Provider -> Database / External System
```

- **Routes** (`app/api/routes`) handle HTTP only: request validation,
  response shaping, and translating domain exceptions
  (`app.core.exceptions`) into HTTP responses. They never contain
  business logic and never call providers directly.
- **Services** (`app/services`) own all business logic. They coordinate
  repositories and providers and never know about HTTP.
- **Repositories** (`app/repositories`) own persistence — reading and
  writing ORM models. No business logic lives here.
- **Providers** (`app/providers`) wrap external systems only: object
  storage, embeddings, chat completion, and the vector store. Providers
  are introduced only when an external dependency actually exists;
  interfaces are added only once multiple implementations are realistic
  (e.g. swapping OpenAI for Anthropic, or pgvector for Qdrant).

## Domain model

The core domain is intentionally small and domain-agnostic:

- **Collection** — a named grouping of documents.
- **Document** — a single ingested file, tracked through a lifecycle
  (`pending -> processing -> ready` / `failed`).
- **Chunk** — a segment of text extracted from a document.
- **Embedding** — a vector representation of a chunk, stored via
  pgvector.

All primary keys are UUIDs; all timestamps are UTC.

## Configuration

Configuration is centralized in `app.core.config` and is strongly typed
(`Settings`, `DatabaseSettings`, `ObjectStorageSettings`,
`LoggingSettings`). `app.core.config` is the only module allowed to read
`os.environ`. No `.env` file and no `python-dotenv` are used anywhere:

- **Local development** — values come from `docker-compose.yml`.
- **CI** — values come from the GitHub Actions workflow environment.
- **Staging/Production** — values come from the hosting platform's
  environment/secrets manager.
- **Tests** — construct `Settings` explicitly (see `tests/conftest.py`);
  they never depend on the process environment.

`Settings` is immutable (`frozen`) and hashable, so it is cached once
per process (`get_settings`) and injected everywhere else via FastAPI's
dependency injection rather than read from ad hoc.

## Logging

Structured logging (`app.core.logging`) is built on `structlog`, wired
into the stdlib `logging` module so both first-party and third-party
log records share one JSON (or console, in local dev) output format.

## Database & migrations

PostgreSQL with the `pgvector` extension is the only supported
datastore. SQLAlchemy 2.x async is used for the application; Alembic
drives migrations using a synchronous connection
(`DatabaseSettings.sync_dsn`). Migrations are written by hand rather
than blindly trusting autogeneration, and the pgvector extension is
created explicitly in the first migration.

## Running everything

The project is designed to require only Docker, Docker Compose, and
Make on the host:

```
make build   # build the app image
make up      # start app + postgres + minio
make migrate # apply migrations
make test    # run the full test suite
make lint    # ruff
make format  # black --check
make typecheck # mypy
```

See the `Makefile` for the full list of targets (`make help`).

## What's deliberately not here yet

Per the milestone plan, document upload, chunking, embedding generation,
similarity search, and chat-with-citations are introduced in later
milestones, one vertical slice at a time. No placeholder code,
speculative abstractions, or event buses have been added ahead of need.
