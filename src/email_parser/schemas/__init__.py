"""Pydantic schemas for data validation."""

from .parsed_email import (
    JobBoardSource,
    ParsedApplication,
    EmailParseResult,
)

__all__ = [
    "JobBoardSource",
    "ParsedApplication",
    "EmailParseResult",
]
