"""Statistics router."""

from datetime import date, timedelta

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from email_parser.api.deps import DbSession
from email_parser.api.schemas.statistics import (
    DailyCount,
    DailyCountBySource,
    SourceBreakdown,
    StatusBySource,
    SummaryStats,
)
from email_parser.models.applicant import Applicant
from email_parser.models.application import Application, ApplicationStatus, JobBoard

router = APIRouter()


@router.get("/summary", response_model=SummaryStats)
async def get_summary_stats(db: DbSession):
    """Get overall application statistics."""
    # Total applications
    total_apps = await db.scalar(select(func.count(Application.id))) or 0

    # Total unique applicants
    total_applicants = await db.scalar(select(func.count(Applicant.id))) or 0

    # Status counts
    status_query = select(
        Application.status,
        func.count(Application.id).label("count"),
    ).group_by(Application.status)
    status_result = await db.execute(status_query)
    status_counts = {row.status.value: row.count for row in status_result}

    # Source counts
    source_query = select(
        Application.source,
        func.count(Application.id).label("count"),
    ).group_by(Application.source)
    source_result = await db.execute(source_query)
    source_counts = {row.source.value: row.count for row in source_result}

    return SummaryStats(
        total_applications=total_apps,
        total_applicants=total_applicants,
        status_counts=status_counts,
        source_counts=source_counts,
    )


@router.get("/daily", response_model=list[DailyCount])
async def get_daily_counts(
    db: DbSession,
    days: int = Query(default=30, ge=1, le=365),
):
    """Get daily application counts for the last N days."""
    start_date = date.today() - timedelta(days=days)

    query = (
        select(
            func.date(Application.application_time).label("date"),
            func.count(Application.id).label("count"),
        )
        .where(func.date(Application.application_time) >= start_date)
        .group_by(func.date(Application.application_time))
        .order_by(func.date(Application.application_time))
    )

    result = await db.execute(query)
    counts = [DailyCount(date=row.date, count=row.count) for row in result]

    # Fill in missing dates with zero counts
    date_counts = {c.date: c.count for c in counts}
    all_dates = []
    current = start_date
    today = date.today()
    while current <= today:
        all_dates.append(DailyCount(date=current, count=date_counts.get(current, 0)))
        current += timedelta(days=1)

    return all_dates


@router.get("/daily-by-source", response_model=list[DailyCountBySource])
async def get_daily_counts_by_source(
    db: DbSession,
    days: int = Query(default=30, ge=1, le=365),
):
    """Get daily application counts grouped by source for the last N days."""
    start_date = date.today() - timedelta(days=days)

    query = (
        select(
            func.date(Application.application_time).label("date"),
            Application.source,
            func.count(Application.id).label("count"),
        )
        .where(func.date(Application.application_time) >= start_date)
        .group_by(func.date(Application.application_time), Application.source)
        .order_by(func.date(Application.application_time))
    )

    result = await db.execute(query)

    # Group by date
    date_data: dict[date, dict[str, int]] = {}
    for row in result:
        if row.date not in date_data:
            date_data[row.date] = {}
        date_data[row.date][row.source.value] = row.count

    # Fill in missing dates with empty counts
    all_dates = []
    current = start_date
    today = date.today()
    while current <= today:
        counts = date_data.get(current, {})
        all_dates.append(DailyCountBySource(date=current, counts=counts))
        current += timedelta(days=1)

    return all_dates


@router.get("/by-source", response_model=list[SourceBreakdown])
async def get_source_breakdown(db: DbSession):
    """Get breakdown of applications by source."""
    query = select(
        Application.source,
        func.count(Application.id).label("count"),
    ).group_by(Application.source)

    result = await db.execute(query)
    rows = list(result)

    total = sum(row.count for row in rows)
    if total == 0:
        return []

    return [
        SourceBreakdown(
            source=row.source.value,
            count=row.count,
            percentage=round(row.count / total * 100, 1),
        )
        for row in rows
    ]


@router.get("/status-by-source", response_model=list[StatusBySource])
async def get_status_by_source(db: DbSession):
    """Get status distribution per source."""
    query = select(
        Application.source,
        Application.status,
        func.count(Application.id).label("count"),
    ).group_by(Application.source, Application.status)

    result = await db.execute(query)

    # Group by source
    source_data: dict[str, dict[str, int]] = {}
    for row in result:
        source_name = row.source.value
        if source_name not in source_data:
            source_data[source_name] = {}
        source_data[source_name][row.status.value] = row.count

    return [
        StatusBySource(source=source, status_counts=counts)
        for source, counts in source_data.items()
    ]
