"""Messages router."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select, or_, and_
from sqlalchemy.orm import selectinload

from email_parser.api.deps import DbSession
from email_parser.api.schemas.message import (
    MessageListResponse,
    MessageResponse,
    MessageUpdate,
    MessageBulkStatusUpdate,
)
from email_parser.models.applicant import Applicant
from email_parser.models.application import ApplicationStatus, JobBoard
from email_parser.models.message import Message
from email_parser.models.position import Position

router = APIRouter()


@router.get("", response_model=MessageListResponse)
async def list_messages(
    db: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    search: Optional[str] = Query(default=None),
    status: Optional[list[str]] = Query(default=None),
    source: Optional[list[str]] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
):
    """Get paginated list of messages with filtering and sorting."""
    query = select(Message).options(
        selectinload(Message.applicant),
        selectinload(Message.positions),
    )

    conditions = []

    if search:
        search_term = f"%{search}%"
        position_subq = (
            select(Message.id)
            .join(Message.positions)
            .where(Position.title.ilike(search_term))
        )
        conditions.append(
            or_(
                Message.applicant.has(Applicant.first_name.ilike(search_term)),
                Message.applicant.has(Applicant.last_name.ilike(search_term)),
                Message.id.in_(position_subq),
            )
        )

    if status:
        status_values = [
            ApplicationStatus(s)
            for s in status
            if s in [e.value for e in ApplicationStatus]
        ]
        if status_values:
            conditions.append(Message.status.in_(status_values))

    if source:
        source_values = [
            JobBoard(s) for s in source if s in [e.value for e in JobBoard]
        ]
        if source_values:
            conditions.append(Message.source.in_(source_values))

    if date_from:
        conditions.append(func.date(Message.created_at) >= date_from)
    if date_to:
        conditions.append(func.date(Message.created_at) <= date_to)

    if conditions:
        query = query.where(and_(*conditions))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    sort_column = getattr(Message, sort_by, Message.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    messages = result.scalars().unique().all()

    items = [MessageResponse.from_orm_with_computed(m) for m in messages]
    total_pages = (total + page_size - 1) // page_size

    return MessageListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(db: DbSession, message_id: int):
    """Get a single message by ID."""
    query = (
        select(Message)
        .where(Message.id == message_id)
        .options(
            selectinload(Message.applicant),
            selectinload(Message.positions),
        )
    )
    result = await db.execute(query)
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return MessageResponse.from_orm_with_computed(message)


@router.patch("/{message_id}", response_model=MessageResponse)
async def update_message(
    db: DbSession,
    message_id: int,
    update: MessageUpdate,
):
    """Update a message's status or comments."""
    query = (
        select(Message)
        .where(Message.id == message_id)
        .options(
            selectinload(Message.applicant),
            selectinload(Message.positions),
        )
    )
    result = await db.execute(query)
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if update.status is not None:
        message.status = update.status
    if update.comments is not None:
        message.comments = update.comments

    await db.flush()
    await db.refresh(message)

    return MessageResponse.from_orm_with_computed(message)


@router.patch("/bulk/status", response_model=dict)
async def bulk_update_status(db: DbSession, update: MessageBulkStatusUpdate):
    """Bulk update message statuses."""
    query = select(Message).where(Message.id.in_(update.ids))
    result = await db.execute(query)
    messages = result.scalars().all()

    if len(messages) != len(update.ids):
        found_ids = {m.id for m in messages}
        missing_ids = set(update.ids) - found_ids
        raise HTTPException(
            status_code=404,
            detail=f"Messages not found: {list(missing_ids)}",
        )

    for message in messages:
        message.status = update.status

    return {"updated": len(messages)}
