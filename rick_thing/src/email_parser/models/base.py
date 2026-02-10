"""SQLAlchemy base model and common utilities."""

from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Type annotations for common column patterns
intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
timestamp_created = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now()),
]
timestamp_updated = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    ),
]


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[timestamp_created]
    updated_at: Mapped[timestamp_updated]
