"""Email processor worker for handling Gmail messages."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.email_record import EmailProcessingStatus, EmailRecord
from ..services.database_service import DatabaseService
from ..services.gmail_service import GmailService
from ..services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class EmailProcessor:
    """Processes emails from Gmail and stores parsed data."""

    def __init__(
        self,
        gmail_service: GmailService,
        openai_service: OpenAIService,
        db_service: DatabaseService,
    ):
        self.gmail = gmail_service
        self.openai = openai_service
        self.db = db_service

    async def process_message(
        self,
        message_id: str,
        session: AsyncSession,
    ) -> Optional[EmailRecord]:
        """
        Process a single Gmail message.

        Args:
            message_id: Gmail message ID
            session: Database session

        Returns:
            EmailRecord if processed, None if skipped (already processed)
        """
        # Check if already processed
        if await self.db.is_email_processed(session, message_id):
            logger.debug(f"Message {message_id} already processed, skipping")
            return None

        # Fetch full message
        try:
            message = self.gmail.get_message(message_id)
            email_data = self.gmail.extract_email_data(message)
        except Exception as e:
            logger.error(f"Failed to fetch message {message_id}: {e}")
            raise

        # Create email record
        email_record = await self.db.create_email_record(
            session=session,
            gmail_message_id=email_data["message_id"],
            gmail_thread_id=email_data["thread_id"],
            subject=email_data["subject"],
            sender=email_data["sender"],
            received_at=email_data["received_at"],
            raw_body=email_data["body_text"] or email_data["body_html"],
        )
        await session.flush()

        # Parse with OpenAI
        try:
            body = email_data["body_text"] or email_data["body_html"]
            if not body:
                logger.warning(f"Message {message_id} has no body content")
                email_record.processing_status = EmailProcessingStatus.SKIPPED
                email_record.processing_error = "No body content"
                email_record.processed_at = datetime.now(timezone.utc)
                return email_record

            parse_result = self.openai.parse_email(
                subject=email_data["subject"],
                body=body,
                sender=email_data["sender"],
            )

            logger.info(
                f"Parsed email {message_id}: "
                f"is_job_application={parse_result.is_job_application}, "
                f"confidence={parse_result.confidence}"
            )

            # Save to database
            application = await self.db.save_parsed_application(
                session=session,
                email_record=email_record,
                parse_result=parse_result,
            )

            if application:
                logger.info(
                    f"Created application {application.id} for "
                    f"{parse_result.application.first_name} "
                    f"{parse_result.application.last_name}"
                )

            # Add processed label in Gmail
            try:
                self.gmail.add_label(
                    message_id,
                    self.gmail.settings.gmail_processed_label,
                )
            except Exception as e:
                logger.warning(
                    f"Failed to add label to message {message_id}: {e}"
                )

            return email_record

        except Exception as e:
            logger.error(f"Failed to parse message {message_id}: {e}")
            email_record.processing_status = EmailProcessingStatus.FAILED
            email_record.processing_error = str(e)
            email_record.processed_at = datetime.now(timezone.utc)
            raise

    async def process_all_messages(self) -> int:
        """
        Process all messages in inbox (for initial sync).

        Returns:
            Number of messages processed
        """
        messages = self.gmail.list_all_messages()
        return await self._process_messages(messages)

    async def process_new_messages(self) -> int:
        """
        Process unprocessed messages.

        Returns:
            Number of messages processed
        """
        messages = self.gmail.list_unprocessed_messages()
        return await self._process_messages(messages)

    async def _process_messages(self, messages: list[dict]) -> int:
        """
        Process a list of messages.

        Args:
            messages: List of message metadata dicts

        Returns:
            Number of messages successfully processed
        """
        processed_count = 0

        for msg in messages:
            msg_id = msg.get("id")
            if not msg_id:
                continue

            async with self.db.async_session() as session:
                try:
                    result = await self.process_message(msg_id, session)
                    await session.commit()
                    if result:
                        processed_count += 1
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Error processing message {msg_id}: {e}")
                    # Continue with other messages

        return processed_count
