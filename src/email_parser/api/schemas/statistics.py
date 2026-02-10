"""Statistics schemas for API."""

from datetime import date

from pydantic import BaseModel

from email_parser.models.application import ApplicationStatus, JobBoard


class SummaryStats(BaseModel):
    """Overall application statistics."""

    total_applications: int
    total_applicants: int
    status_counts: dict[str, int]
    source_counts: dict[str, int]


class DailyCount(BaseModel):
    """Daily application count."""

    date: date
    count: int


class SourceBreakdown(BaseModel):
    """Breakdown of applications by source."""

    source: str
    count: int
    percentage: float


class StatusBySource(BaseModel):
    """Status distribution per source."""

    source: str
    status_counts: dict[str, int]


class DailyCountBySource(BaseModel):
    """Daily application count broken down by source."""

    date: date
    counts: dict[str, int]
