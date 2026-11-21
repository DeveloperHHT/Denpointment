"""Errors raised when a business rule is broken. The routes show the message to the user."""
from __future__ import annotations


class RuleViolation(Exception):
    """A request that is valid input but not allowed by the rules of the clinic."""

    def __init__(self, message: str, category: str = "danger") -> None:
        super().__init__(message)
        self.message = message
        self.category = category
