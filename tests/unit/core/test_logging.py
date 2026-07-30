"""Unit tests for app.core.logging."""

from __future__ import annotations

import logging

from app.core.config import LoggingSettings
from app.core.logging import configure_logging, get_logger


def test_configure_logging_sets_root_level() -> None:
    configure_logging(LoggingSettings(level="WARNING", json_format=True))

    assert logging.getLogger().level == logging.WARNING


def test_configure_logging_is_idempotent() -> None:
    configure_logging(LoggingSettings(level="INFO", json_format=True))
    configure_logging(LoggingSettings(level="INFO", json_format=True))

    # A second call must not accumulate duplicate handlers.
    assert len(logging.getLogger().handlers) == 1


def test_get_logger_returns_bound_logger_with_name() -> None:
    configure_logging(LoggingSettings(level="INFO", json_format=True))
    logger = get_logger("test.module")

    # structlog wraps the stdlib logger; smoke-test that logging doesn't raise.
    logger.info("hello", extra_field="value")
