"""Main entry point for the email parser application."""

import asyncio
import logging
import sys

from .config import get_settings
from .services.database_service import DatabaseService
from .services.gmail_service import GmailService
from .services.openai_service import OpenAIService
from .workers.email_processor import EmailProcessor

logger = logging.getLogger(__name__)


class EmailParserApp:
    """Main application class."""

    def __init__(self):
        self.settings = get_settings()
        self.running = False
        self.initial_sync_done = False
        self._shutdown_event = asyncio.Event()

        # Initialize services
        self.gmail_service = GmailService(self.settings)
        self.openai_service = OpenAIService(self.settings)
        self.db_service = DatabaseService(self.settings)
        self.processor = EmailProcessor(
            gmail_service=self.gmail_service,
            openai_service=self.openai_service,
            db_service=self.db_service,
        )

    def setup_logging(self):
        """Configure logging."""
        logging.basicConfig(
            level=getattr(logging, self.settings.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
            ],
        )

    async def initial_sync(self):
        """Process all historical emails on first launch."""
        logger.info("Starting initial sync - processing all historical emails...")
        count = await self.processor.process_all_messages()
        logger.info(f"Initial sync complete. Processed {count} emails.")
        self.initial_sync_done = True

    async def polling_loop(self):
        """Main polling loop for checking new emails."""
        while self.running:
            try:
                logger.debug("Checking for new emails...")
                count = await self.processor.process_new_messages()
                if count > 0:
                    logger.info(f"Processed {count} new emails")

            except Exception as e:
                logger.error(f"Error in polling loop: {e}")

            # Use wait with timeout so we can check running flag
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.settings.polling_interval_seconds,
                )
                # If we get here, shutdown was requested
                break
            except asyncio.TimeoutError:
                # Normal timeout, continue polling
                pass

    async def run(self):
        """Run the application."""
        self.setup_logging()
        logger.info("Starting Email Parser Application")
        logger.info(f"Polling interval: {self.settings.polling_interval_seconds}s")
        logger.info("Press Ctrl+C to stop")

        self.running = True

        # Initial sync - process all historical emails
        await self.initial_sync()

        # Start polling loop
        logger.info("Starting polling loop...")
        await self.polling_loop()

        logger.info("Email Parser Application stopped.")

    def stop(self):
        """Stop the application."""
        logger.info("Shutting down...")
        self.running = False
        self._shutdown_event.set()


def main():
    """Entry point."""
    app = EmailParserApp()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        app.stop()
        print("\nStopped.")


if __name__ == "__main__":
    main()
