"""Message schemas for API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from email_parser.models.application import ApplicationStatus, JobBoard


class PositionResponse(BaseModel):
    """Position in a message response."""

    id: int
    title: str

    class Config:
        from_attributes = True


class ApplicantResponse(BaseModel):
    """Applicant in a message response."""

    id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Single message response."""

    id: int
    applicant: ApplicantResponse
    applicant_name: str = ""
    positions: list[PositionResponse]
    position_titles: str = ""
    source: JobBoard
    status: ApplicationStatus
    comments: Optional[str] = None
    email: Optional[str] = None  # sender_email for direct email
    message_link: Optional[str] = None  # link to view message on platform
    received_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_computed(cls, obj) -> "MessageResponse":
        """Create response with computed fields."""
        applicant_name = f"{obj.applicant.first_name} {obj.applicant.last_name}"
        position_titles = ", ".join(p.title for p in obj.positions)
        return cls(
            id=obj.id,
            applicant=ApplicantResponse.model_validate(obj.applicant),
            applicant_name=applicant_name,
            positions=[PositionResponse.model_validate(p) for p in obj.positions],
            position_titles=position_titles,
            source=obj.source,
            status=obj.status,
            comments=obj.comments,
            email=obj.sender_email,
            message_link=obj.message_link,
            received_at=obj.received_at,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


class MessageListResponse(BaseModel):
    """Paginated list of messages."""

    items: list[MessageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageUpdate(BaseModel):
    """Request to update a message."""

    status: Optional[ApplicationStatus] = None
    comments: Optional[str] = Field(default=None, max_length=10000)


class MessageBulkStatusUpdate(BaseModel):
    """Request to bulk update message statuses."""

    ids: list[int] = Field(..., min_length=1, max_length=100)
    status: ApplicationStatus
