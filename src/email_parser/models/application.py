"""Application model - represents a job application."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, intpk

if TYPE_CHECKING:
    from .applicant import Applicant
    from .email_record import EmailRecord
    from .position import Position


class JobBoard(str, enum.Enum):
    """Enum for job board sources."""

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


class ApplicationStatus(str, enum.Enum):
    """Enum for application status."""

    NEW = "new"
    REVIEWED = "reviewed"
    CONTACTED = "contacted"
    REJECTED = "rejected"
    HIRED = "hired"


# Association table for many-to-many relationship between applications and positions
application_positions = Table(
    "application_positions",
    Base.metadata,
    Column(
        "application_id",
        ForeignKey("applications.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "position_id",
        ForeignKey("positions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Application(Base, TimestampMixin):
    """Represents a single job application from an applicant."""

    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "applicant_id",
            "source",
            "email_record_id",
            name="uq_application_source_email",
        ),
    )

    id: Mapped[intpk]

    # Foreign keys
    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("applicants.id", ondelete="CASCADE"), index=True
    )
    email_record_id: Mapped[int] = mapped_column(
        ForeignKey("email_records.id", ondelete="CASCADE"), index=True
    )

    # Source information
    source: Mapped[JobBoard] = mapped_column(Enum(JobBoard), index=True)
    application_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Application metadata
    application_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.NEW,
        index=True,
    )

    # User-editable fields
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    applicant: Mapped["Applicant"] = relationship(
        "Applicant", back_populates="applications"
    )
    positions: Mapped[list["Position"]] = relationship(
        "Position",
        secondary=application_positions,
        back_populates="applications",
    )
    email_record: Mapped["EmailRecord"] = relationship(
        "EmailRecord",
        back_populates="applications",
    )

    def __repr__(self) -> str:
        return (
            f"<Application(id={self.id}, applicant_id={self.applicant_id}, "
            f"source={self.source.value})>"
        )
