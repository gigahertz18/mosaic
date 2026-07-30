"""Unit tests for app.core.exceptions."""

from __future__ import annotations

import pytest

from app.core.exceptions import MosaicError, NotFoundError, ValidationError


def test_not_found_error_is_a_mosaic_error() -> None:
    with pytest.raises(MosaicError):
        raise NotFoundError("collection not found")


def test_validation_error_is_a_mosaic_error() -> None:
    with pytest.raises(MosaicError):
        raise ValidationError("name must not be empty")


def test_errors_carry_their_message() -> None:
    error = NotFoundError("document 123 not found")
    assert str(error) == "document 123 not found"
