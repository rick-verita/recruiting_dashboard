"""Message model - represents a direct email or job-board message (not an application)."""

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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .application import ApplicationStatus, JobBoard
from .base import Base, TimestampMixin, intpk

if TYPE_CHECKING:
    from .applicant import Applicant
    from .email_record import EmailRecord
    from .position import Position


# Association table for many-to-many between messages and positions
message_positions = Table(
    "message_positions",
    Base.metadata,
    Column(
        "message_id",
        ForeignKey("messages.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "position_id",
        ForeignKey("positions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Message(Base, TimestampMixin):
    """Represents a message (direct email or job-board message) that is not an application."""

    __tablename__ = "messages"

    id: Mapped[intpk]

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("applicants.id", ondelete="CASCADE"), index=True
    )
    email_record_id: Mapped[int] = mapped_column(
        ForeignKey("email_records.id", ondelete="CASCADE"), index=True
    )

    source: Mapped[JobBoard] = mapped_column(Enum(JobBoard), index=True)
    message_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sender_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.NEW,
        index=True,
    )
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    applicant: Mapped["Applicant"] = relationship(
        "Applicant", back_populates="messages"
    )
    positions: Mapped[list["Position"]] = relationship(
        "Position",
        secondary=message_positions,
        back_populates="messages",
    )
    email_record: Mapped["EmailRecord"] = relationship(
        "EmailRecord",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return (
            f"<Message(id={self.id}, applicant_id={self.applicant_id}, "
            f"source={self.source})>"
        )
