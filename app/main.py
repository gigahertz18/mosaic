"""FastAPI application factory.

The application is built through :func:`create_app` rather than as a
module-level object. Building ``Settings`` eagerly at import time would
break any tooling that imports this module without the full environment
configured (linters, mypy, doc generators). Run with::

    uvicorn app.main:create_app --factory
"""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    """Build and return a configured :class:`FastAPI` application instance."""
    settings = get_settings()
    configure_logging(settings.logging)

    app = FastAPI(title=settings.app_name, debug=settings.debug)
    # Health is intentionally unversioned: infrastructure probes (Docker,
    # Kubernetes, load balancers) expect a stable, un-prefixed path.
    app.include_router(health_router)

    return app
