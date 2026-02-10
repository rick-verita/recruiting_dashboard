"""EmailRecord model - tracks processed emails."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, intpk

if TYPE_CHECKING:
    from .application import Application


class EmailProcessingStatus(str, enum.Enum):
    """Enum for email processing status."""

    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"  # Not a job application email


class EmailRecord(Base, TimestampMixin):
    """Tracks processed emails to prevent re-processing."""

    __tablename__ = "email_records"

    id: Mapped[intpk]

    # Gmail identifiers
    gmail_message_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True
    )
    gmail_thread_id: Mapped[str] = mapped_column(String(255), index=True)

    # Email metadata
    subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sender: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Processing status
    processing_status: Mapped[EmailProcessingStatus] = mapped_column(
        Enum(EmailProcessingStatus),
        default=EmailProcessingStatus.PENDING,
        index=True,
    )
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Raw content for debugging
    raw_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="email_record",
    )

    def __repr__(self) -> str:
        return (
            f"<EmailRecord(id={self.id}, gmail_id='{self.gmail_message_id}', "
            f"status={self.processing_status.value})>"
        )
