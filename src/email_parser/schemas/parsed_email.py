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


class ParsedMessage(BaseModel):
    """Parsed message data (direct email or job-board message, not an application)."""

    first_name: str = Field(..., description="Sender's or message author's first name")
    last_name: str = Field(..., description="Sender's or message author's last name")
    source: JobBoardSource = Field(
        ...,
        description="Where the message came from (e.g. linkedin for InMail, or 'other' for direct email)",
    )
    positions: list[str] = Field(
        default_factory=list,
        description="Position titles mentioned or relevant to the message (may be empty)",
    )
    message_link: Optional[str] = Field(
        None,
        description="For platform messages only: an https URL that opens the message/conversation on the platform (e.g. linkedin.com, indeed.com) so the user can reply there. NEVER use a mailto: link—many Reply buttons are mailto; ignore those and use the link that opens the platform (e.g. 'View in LinkedIn', 'See conversation'). For direct email (source=other): leave null.",
    )


class EmailParseResult(BaseModel):
    """Result of parsing an email for job application data."""

    is_hiring_related: bool = Field(
        ...,
        description="True if the email pertains to hiring, recruiting, job applications, or roles in any way. Be lenient: include outreach, role mentions, recruiter/candidate contact, job boards, etc. False only for clearly unrelated content (e.g. marketing, newsletters, purely personal).",
    )
    is_job_application: bool = Field(
        ...,
        description="True only when this email is clearly a notification that someone submitted an official application through a job board/listing (e.g. 'New application from X for Y'). Not true for direct emails or job-board messages (e.g. LinkedIn InMail).",
    )
    is_message: bool = Field(
        ...,
        description="True when this is a direct email from a person or a message via a job board (e.g. LinkedIn message) that is NOT an application—i.e. someone reached out or messaged but did not submit an official application.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the parsing (0-1)",
    )
    application: Optional[ParsedApplication] = Field(
        None,
        description="Parsed application data (set only when is_job_application is true)",
    )
    message: Optional[ParsedMessage] = Field(
        None,
        description="Parsed message data (set when is_message is true)",
    )
