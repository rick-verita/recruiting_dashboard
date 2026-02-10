"""Application schemas for API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from email_parser.models.application import ApplicationStatus, JobBoard


class PositionResponse(BaseModel):
    """Position in an application response."""

    id: int
    title: str

    class Config:
        from_attributes = True


class ApplicantResponse(BaseModel):
    """Applicant in an application response."""

    id: int
    first_name: str
    last_name: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    """Single application response."""

    id: int
    applicant: ApplicantResponse
    applicant_name: str = ""
    positions: list[PositionResponse]
    position_titles: str = ""
    source: JobBoard
    status: ApplicationStatus
    comments: Optional[str] = None
    application_link: Optional[str] = None
    application_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_computed(cls, obj) -> "ApplicationResponse":
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
            application_link=obj.application_link,
            application_time=obj.application_time,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


class ApplicationListResponse(BaseModel):
    """Paginated list of applications."""

    items: list[ApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ApplicationUpdate(BaseModel):
    """Request to update an application."""

    status: Optional[ApplicationStatus] = None
    comments: Optional[str] = Field(default=None, max_length=10000)


class BulkStatusUpdate(BaseModel):
    """Request to bulk update application statuses."""

    ids: list[int] = Field(..., min_length=1, max_length=100)
    status: ApplicationStatus
