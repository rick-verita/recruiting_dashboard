"""Statistics router."""

from collections import defaultdict
from datetime import date, timedelta

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.sql.expression import distinct

from email_parser.api.deps import DbSession
from email_parser.config import get_settings
from email_parser.services.openai_service import OpenAIService
from email_parser.api.schemas.statistics import (
    DailyCount,
    DailyCountBySource,
    MultiPositionApplicant,
    MultiPositionApplicantsResponse,
    PositionBreakdown,
    SourceBreakdown,
    StatusBySource,
    SummaryStats,
)
from email_parser.models.applicant import Applicant
from email_parser.models.application import (
    Application,
    ApplicationStatus,
    JobBoard,
    application_positions,
)
from email_parser.models.position import Position

router = APIRouter()


@router.get("/summary", response_model=SummaryStats)
async def get_summary_stats(db: DbSession):
    """Get overall application statistics."""
    # Total applications (application records)
    total_apps = await db.scalar(select(func.count(Application.id))) or 0

    # Total unique applicants (by name)
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

    new_count = status_counts.get(ApplicationStatus.NEW.value, 0)
    reviewed_count = total_apps - new_count
    contacted_count = (
        status_counts.get(ApplicationStatus.CONTACTED.value, 0)
        + status_counts.get(ApplicationStatus.REJECTED.value, 0)
        + status_counts.get(ApplicationStatus.HIRED.value, 0)
    )
    rejected_count = status_counts.get(ApplicationStatus.REJECTED.value, 0)
    hired_count = status_counts.get(ApplicationStatus.HIRED.value, 0)

    review_rate = round(reviewed_count / total_apps * 100, 1) if total_apps else 0.0
    contact_rate = round(contacted_count / total_apps * 100, 1) if total_apps else 0.0
    rejected_rate = round(rejected_count / total_apps * 100, 1) if total_apps else 0.0
    hire_rate = round(hired_count / total_apps * 100, 1) if total_apps else 0.0

    return SummaryStats(
        total_applications=total_apps,
        total_applicants=total_applicants,
        status_counts=status_counts,
        source_counts=source_counts,
        review_rate=review_rate,
        contact_rate=contact_rate,
        rejected_rate=rejected_rate,
        hire_rate=hire_rate,
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


@router.get("/by-position", response_model=list[PositionBreakdown])
async def get_position_breakdown(db: DbSession):
    """Get breakdown of applications by position (count of applications per position)."""
    query = (
        select(
            Position.title.label("position_title"),
            func.count(Application.id).label("count"),
        )
        .select_from(Application)
        .join(Application.positions)
        .group_by(Position.id, Position.title)
        .order_by(func.count(Application.id).desc())
    )

    result = await db.execute(query)
    rows = list(result)

    total = sum(row.count for row in rows)
    if total == 0:
        return []

    return [
        PositionBreakdown(
            position_title=row.position_title,
            count=row.count,
            percentage=round(row.count / total * 100, 1),
        )
        for row in rows
    ]


@router.get("/by-position-aggregated", response_model=list[PositionBreakdown])
async def get_position_breakdown_aggregated(db: DbSession):
    """Get applications by position with similar titles grouped via LLM."""
    query = (
        select(
            Position.title.label("position_title"),
            func.count(Application.id).label("count"),
        )
        .select_from(Application)
        .join(Application.positions)
        .group_by(Position.id, Position.title)
        .order_by(func.count(Application.id).desc())
    )
    result = await db.execute(query)
    rows = list(result)
    total = sum(row.count for row in rows)
    if total == 0:
        return []

    titles = list({row.position_title for row in rows})
    openai_service = OpenAIService(get_settings())
    title_to_group = openai_service.group_similar_positions(titles)

    aggregated: dict[str, int] = defaultdict(int)
    for row in rows:
        group = title_to_group.get(row.position_title, row.position_title)
        aggregated[group] += row.count

    sorted_groups = sorted(
        aggregated.items(),
        key=lambda x: -x[1],
    )
    return [
        PositionBreakdown(
            position_title=group,
            count=count,
            percentage=round(count / total * 100, 1),
        )
        for group, count in sorted_groups
    ]


@router.get("/multi-position-applicants", response_model=MultiPositionApplicantsResponse)
async def get_multi_position_applicants(db: DbSession):
    """Get applicants who applied to more than one position (name, positions, link)."""
    # Applicant IDs who have more than one distinct position
    multi_position_subq = (
        select(Application.applicant_id)
        .select_from(Application)
        .join(application_positions, Application.id == application_positions.c.application_id)
        .group_by(Application.applicant_id)
        .having(func.count(distinct(application_positions.c.position_id)) > 1)
    )

    # For each such applicant: first_name, last_name, comma-separated position titles, one link
    query = (
        select(
            Applicant.first_name,
            Applicant.last_name,
            func.string_agg(Position.title, ", ").label("position_titles"),
            func.max(Application.application_link).label("application_link"),
        )
        .select_from(Applicant)
        .join(Application, Application.applicant_id == Applicant.id)
        .join(application_positions, application_positions.c.application_id == Application.id)
        .join(Position, Position.id == application_positions.c.position_id)
        .where(Applicant.id.in_(multi_position_subq))
        .group_by(Applicant.id, Applicant.first_name, Applicant.last_name)
        .order_by(Applicant.last_name, Applicant.first_name)
    )

    result = await db.execute(query)
    rows = result.all()

    items = [
        MultiPositionApplicant(
            applicant_name=f"{row.first_name} {row.last_name}".strip(),
            position_titles=row.position_titles or "",
            application_link=row.application_link,
        )
        for row in rows
    ]

    return MultiPositionApplicantsResponse(total=len(items), items=items)
