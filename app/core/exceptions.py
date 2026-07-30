"""Domain-specific exceptions.

Services raise these instead of HTTP exceptions. Routes are responsible
for translating them into the appropriate HTTP response.
"""

from __future__ import annotations


class MosaicError(Exception):
    """Base class for all domain errors raised by the application."""


class NotFoundError(MosaicError):
    """Raised when a requested resource does not exist."""


class ValidationError(MosaicError):
    """Raised when a business rule is violated."""
