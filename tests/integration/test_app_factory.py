"""Integration tests for the create_app application factory."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def _configured_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOSAIC_ENVIRONMENT", "test")
    monkeypatch.setenv("MOSAIC_DB_HOST", "db")
    monkeypatch.setenv("MOSAIC_DB_USER", "mosaic")
    monkeypatch.setenv("MOSAIC_DB_PASSWORD", "mosaic")
    monkeypatch.setenv("MOSAIC_DB_NAME", "mosaic")
    monkeypatch.setenv("MOSAIC_STORAGE_ENDPOINT", "minio:9000")
    monkeypatch.setenv("MOSAIC_STORAGE_ACCESS_KEY", "mosaic")
    monkeypatch.setenv("MOSAIC_STORAGE_SECRET_KEY", "mosaic123")
    monkeypatch.setenv("MOSAIC_LOG_JSON", "false")


def test_create_app_builds_app_and_serves_health(_configured_env: None) -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["environment"] == "test"


def test_create_app_does_not_require_import_time_environment() -> None:
    """Importing app.main must never construct Settings eagerly."""
    import importlib

    import app.main as main_module

    importlib.reload(main_module)  # succeeds even with no env vars set
