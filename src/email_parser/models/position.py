"""Position model - represents a job position being recruited for."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, intpk

if TYPE_CHECKING:
    from .application import Application


class Position(Base, TimestampMixin):
    """Represents a job position being recruited for."""

    __tablename__ = "positions"

    id: Mapped[intpk]
    title: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    applications: Mapped[list["Application"]] = relationship(
        "Application",
        secondary="application_positions",
        back_populates="positions",
    )

    def __repr__(self) -> str:
        return f"<Position(id={self.id}, title='{self.title}')>"
