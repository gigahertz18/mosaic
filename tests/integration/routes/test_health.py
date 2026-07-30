"""Integration tests for GET /health."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.health import router as health_router
from app.core.config import Settings, get_settings


def _build_test_app(settings: Settings) -> FastAPI:
    app = FastAPI()
    app.include_router(health_router)
    app.dependency_overrides[get_settings] = lambda: settings
    return app


def test_health_returns_200_with_expected_body(test_settings: Settings) -> None:
    app = _build_test_app(test_settings)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "status": "ok",
        "app_name": test_settings.app_name,
        "environment": test_settings.environment.value,
    }


def test_health_reflects_configured_app_name(test_settings: Settings) -> None:
    custom_settings = test_settings.model_copy(update={"app_name": "mosaic-custom"})
    app = _build_test_app(custom_settings)
    client = TestClient(app)

    response = client.get("/health")

    assert response.json()["app_name"] == "mosaic-custom"


def test_health_rejects_post(test_settings: Settings) -> None:
    app = _build_test_app(test_settings)
    client = TestClient(app)

    response = client.post("/health")

    assert response.status_code == 405
