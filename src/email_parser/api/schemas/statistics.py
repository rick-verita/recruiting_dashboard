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
    review_rate: float = 0.0
    contact_rate: float = 0.0
    rejected_rate: float = 0.0
    hire_rate: float = 0.0


class MultiPositionApplicant(BaseModel):
    """Applicant who applied to more than one position."""

    applicant_name: str
    position_titles: str  # comma-separated
    application_link: str | None


class MultiPositionApplicantsResponse(BaseModel):
    """Response for applicants who applied to multiple positions."""

    total: int
    items: list[MultiPositionApplicant]


class PositionBreakdown(BaseModel):
    """Breakdown of applications by position."""

    position_title: str
    count: int
    percentage: float


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
