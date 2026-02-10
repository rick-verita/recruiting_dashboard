"""Applications router."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select, or_, and_
from sqlalchemy.orm import selectinload

from email_parser.api.deps import DbSession
from email_parser.api.schemas.application import (
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationUpdate,
    BulkStatusUpdate,
)
from email_parser.models.applicant import Applicant
from email_parser.models.application import Application, ApplicationStatus, JobBoard
from email_parser.models.position import Position

router = APIRouter()


@router.get("", response_model=ApplicationListResponse)
async def list_applications(
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
    """Get paginated list of applications with filtering and sorting."""
    # Base query with eager loading
    query = select(Application).options(
        selectinload(Application.applicant),
        selectinload(Application.positions),
    )

    # Apply filters
    conditions = []

    # Search filter (applicant name or position)
    if search:
        search_term = f"%{search}%"
        # Subquery for position search
        position_subq = (
            select(Application.id)
            .join(Application.positions)
            .where(Position.title.ilike(search_term))
        )
        conditions.append(
            or_(
                Application.applicant.has(Applicant.first_name.ilike(search_term)),
                Application.applicant.has(Applicant.last_name.ilike(search_term)),
                Application.id.in_(position_subq),
            )
        )

    # Status filter
    if status:
        status_values = [ApplicationStatus(s) for s in status if s in [e.value for e in ApplicationStatus]]
        if status_values:
            conditions.append(Application.status.in_(status_values))

    # Source filter
    if source:
        source_values = [JobBoard(s) for s in source if s in [e.value for e in JobBoard]]
        if source_values:
            conditions.append(Application.source.in_(source_values))

    # Date range filter
    if date_from:
        conditions.append(func.date(Application.created_at) >= date_from)
    if date_to:
        conditions.append(func.date(Application.created_at) <= date_to)

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Apply sorting
    sort_column = getattr(Application, sort_by, Application.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    applications = result.scalars().unique().all()

    # Build response
    items = [ApplicationResponse.from_orm_with_computed(app) for app in applications]
    total_pages = (total + page_size - 1) // page_size

    return ApplicationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(db: DbSession, application_id: int):
    """Get a single application by ID."""
    query = (
        select(Application)
        .where(Application.id == application_id)
        .options(
            selectinload(Application.applicant),
            selectinload(Application.positions),
        )
    )
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return ApplicationResponse.from_orm_with_computed(application)


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    db: DbSession,
    application_id: int,
    update: ApplicationUpdate,
):
    """Update an application's status or comments."""
    query = (
        select(Application)
        .where(Application.id == application_id)
        .options(
            selectinload(Application.applicant),
            selectinload(Application.positions),
        )
    )
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update fields
    if update.status is not None:
        application.status = update.status
    if update.comments is not None:
        application.comments = update.comments

    await db.flush()
    await db.refresh(application)

    return ApplicationResponse.from_orm_with_computed(application)


@router.patch("/bulk/status", response_model=dict)
async def bulk_update_status(db: DbSession, update: BulkStatusUpdate):
    """Bulk update application statuses."""
    query = select(Application).where(Application.id.in_(update.ids))
    result = await db.execute(query)
    applications = result.scalars().all()

    if len(applications) != len(update.ids):
        found_ids = {app.id for app in applications}
        missing_ids = set(update.ids) - found_ids
        raise HTTPException(
            status_code=404,
            detail=f"Applications not found: {list(missing_ids)}",
        )

    for application in applications:
        application.status = update.status

    return {"updated": len(applications)}
