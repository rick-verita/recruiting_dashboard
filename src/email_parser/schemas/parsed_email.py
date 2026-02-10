"""Pydantic schemas for OpenAI structured output parsing."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobBoardSource(str, Enum):
    """Job board source extracted from email."""

    ZIPRECRUITER = "ziprecruiter"
    HANDSHAKE = "handshake"
    WELLFOUND = "wellfound"
    INDEED = "indeed"
    LINKEDIN = "linkedin"
    WELCOME_TO_THE_JUNGLE = "welcome_to_the_jungle"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    OTHER = "other"
    UNKNOWN = "unknown"


class ParsedApplication(BaseModel):
    """Parsed job application data from email."""

    first_name: str = Field(..., description="Applicant's first name")
    last_name: str = Field(..., description="Applicant's last name")
    source: JobBoardSource = Field(
        ..., description="The job board or platform the application came from"
    )
    positions: list[str] = Field(
        ...,
        description="List of position titles the applicant applied for",
        min_length=1,
    )
    application_link: Optional[str] = Field(
        None,
        description="Link to view the full application (may not be available)",
    )


class EmailParseResult(BaseModel):
    """Result of parsing an email for job application data."""

    is_job_application: bool = Field(
        ...,
        description="Whether this email is a job application notification",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the parsing (0-1)",
    )
    application: Optional[ParsedApplication] = Field(
        None,
        description="Parsed application data (null if not a job application email)",
    )
