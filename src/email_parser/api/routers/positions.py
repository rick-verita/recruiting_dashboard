"""Positions router."""

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from email_parser.api.deps import DbSession
from email_parser.models.position import Position

router = APIRouter()


class PositionListItem(BaseModel):
    """Position list item response."""

    id: int
    title: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[PositionListItem])
async def list_positions(db: DbSession, active_only: bool = False):
    """Get list of positions for filter dropdown."""
    query = select(Position).order_by(Position.title)
    if active_only:
        query = query.where(Position.is_active == True)

    result = await db.execute(query)
    positions = result.scalars().all()

    return [PositionListItem.model_validate(p) for p in positions]
