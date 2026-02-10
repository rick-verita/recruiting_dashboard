"""Applicant model - represents a job applicant."""

from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, intpk

if TYPE_CHECKING:
    from .application import Application


class Applicant(Base, TimestampMixin):
    """Represents a job applicant (deduplicated by name)."""

    __tablename__ = "applicants"
    __table_args__ = (
        UniqueConstraint("first_name", "last_name", name="uq_applicant_name"),
    )

    id: Mapped[intpk]
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))

    # Relationships
    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="applicant",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Applicant(id={self.id}, name='{self.first_name} {self.last_name}')>"
