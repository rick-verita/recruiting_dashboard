"""Database service for persisting parsed application data."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..config import Settings
from ..models.applicant import Applicant
from ..models.application import Application, ApplicationStatus, JobBoard
from ..models.email_record import EmailProcessingStatus, EmailRecord
from ..models.message import Message
from ..models.position import Position
from ..schemas.parsed_email import EmailParseResult, JobBoardSource, ParsedMessage

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations."""

    def __init__(self, settings: Settings):
        self.settings = settings
        # Convert postgresql:// to postgresql+asyncpg://
        db_url = settings.database_url
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        self.engine = create_async_engine(
            db_url,
            echo=settings.debug,
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_or_create_applicant(
        self,
        session: AsyncSession,
        first_name: str,
        last_name: str,
    ) -> Applicant:
        """
        Get existing applicant by name or create new one.
        """
        result = await session.execute(
            select(Applicant).where(
                Applicant.first_name == first_name,
                Applicant.last_name == last_name,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        applicant = Applicant(
            first_name=first_name,
            last_name=last_name,
        )
        session.add(applicant)
        return applicant

    async def get_or_create_position(
        self,
        session: AsyncSession,
        title: str,
    ) -> Position:
        """Get existing position by title or create new one."""
        normalized_title = title.strip()

        result = await session.execute(
            select(Position).where(Position.title == normalized_title)
        )
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        position = Position(title=normalized_title, is_active=True)
        session.add(position)
        return position

    async def is_email_processed(
        self,
        session: AsyncSession,
        gmail_message_id: str,
    ) -> bool:
        """Check if email has already been processed."""
        result = await session.execute(
            select(EmailRecord).where(
                EmailRecord.gmail_message_id == gmail_message_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def create_email_record(
        self,
        session: AsyncSession,
        gmail_message_id: str,
        gmail_thread_id: str,
        subject: Optional[str],
        sender: Optional[str],
        received_at: Optional[datetime],
        raw_body: Optional[str] = None,
    ) -> EmailRecord:
        """Create a record of a processed email."""
        email_record = EmailRecord(
            gmail_message_id=gmail_message_id,
            gmail_thread_id=gmail_thread_id,
            subject=subject,
            sender=sender,
            received_at=received_at,
            raw_body=raw_body[:10000] if raw_body else None,
            processing_status=EmailProcessingStatus.PENDING,
        )
        session.add(email_record)
        return email_record

    async def save_parsed_application(
        self,
        session: AsyncSession,
        email_record: EmailRecord,
        parse_result: EmailParseResult,
    ) -> Optional[Application]:
        """
        Save parsed application data to database.

        Returns:
            Created Application or None if not a job application
        """
        if not parse_result.is_job_application or not parse_result.application:
            email_record.processing_status = EmailProcessingStatus.SKIPPED
            email_record.processed_at = datetime.now(timezone.utc)
            return None

        app_data = parse_result.application

        # Get or create applicant
        applicant = await self.get_or_create_applicant(
            session,
            first_name=app_data.first_name,
            last_name=app_data.last_name,
        )
        await session.flush()

        # Map schema JobBoardSource to model JobBoard
        source = JobBoard(app_data.source.value)

        # Get or create positions
        positions = []
        for pos_title in app_data.positions:
            position = await self.get_or_create_position(session, pos_title)
            positions.append(position)

        # application_time = when the notification email was received (from Gmail Date header), not any date in the body
        application_time = email_record.received_at
        if application_time is None:
            application_time = datetime.now(timezone.utc)

        # Create application
        application = Application(
            applicant_id=applicant.id,
            email_record_id=email_record.id,
            source=source,
            application_link=app_data.application_link,
            application_time=application_time,
            status=ApplicationStatus.NEW,
        )
        application.positions = positions
        session.add(application)

        # Update email record
        email_record.processing_status = EmailProcessingStatus.PROCESSED
        email_record.processed_at = datetime.now(timezone.utc)

        return application

    async def save_parsed_message(
        self,
        session: AsyncSession,
        email_record: EmailRecord,
        parse_result: EmailParseResult,
    ) -> Optional[Message]:
        """
        Save parsed message data (direct email or job-board message) to database.

        Returns:
            Created Message or None if not a message
        """
        if not parse_result.is_message or not parse_result.message:
            return None

        msg_data: ParsedMessage = parse_result.message

        applicant = await self.get_or_create_applicant(
            session,
            first_name=msg_data.first_name,
            last_name=msg_data.last_name,
        )
        await session.flush()

        source = JobBoard(msg_data.source.value)
        positions = []
        for pos_title in msg_data.positions:
            position = await self.get_or_create_position(session, pos_title)
            positions.append(position)

        received_at = email_record.received_at or datetime.now(timezone.utc)
        sender_email = email_record.sender  # For direct email; null for platform messages is ok

        message = Message(
            applicant_id=applicant.id,
            email_record_id=email_record.id,
            source=source,
            message_link=msg_data.message_link,
            sender_email=sender_email,
            received_at=received_at,
            status=ApplicationStatus.NEW,
        )
        message.positions = positions
        session.add(message)

        email_record.processing_status = EmailProcessingStatus.PROCESSED
        email_record.processed_at = datetime.now(timezone.utc)

        return message
