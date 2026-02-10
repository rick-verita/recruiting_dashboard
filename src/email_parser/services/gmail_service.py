"""Gmail API service for fetching and managing emails."""

import base64
import logging
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build

from ..config import Settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailService:
    """Service for interacting with Gmail API."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._service: Optional[Resource] = None
        self._credentials: Optional[Credentials] = None

    def _get_credentials(self) -> Credentials:
        """Get or refresh OAuth2 credentials."""
        if self._credentials and self._credentials.valid:
            return self._credentials

        if (
            self._credentials
            and self._credentials.expired
            and self._credentials.refresh_token
        ):
            self._credentials.refresh(Request())
        else:
            creds_dict = {
                "token": None,
                "refresh_token": self.settings.gmail_refresh_token.get_secret_value(),
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": self.settings.gmail_client_id,
                "client_secret": self.settings.gmail_client_secret.get_secret_value(),
                "scopes": SCOPES,
            }
            self._credentials = Credentials.from_authorized_user_info(
                creds_dict, SCOPES
            )

            if not self._credentials.valid:
                if (
                    self._credentials.expired
                    and self._credentials.refresh_token
                ):
                    self._credentials.refresh(Request())

        return self._credentials

    @property
    def service(self) -> Resource:
        """Get Gmail API service instance."""
        if self._service is None:
            creds = self._get_credentials()
            self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def list_all_messages(self, max_results: int = 500) -> list[dict]:
        """
        List all messages in inbox (for initial sync).

        Args:
            max_results: Maximum number of messages to return

        Returns:
            List of message metadata
        """
        messages = []
        page_token = None

        while len(messages) < max_results:
            response = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=min(100, max_results - len(messages)),
                    labelIds=["INBOX"],
                    pageToken=page_token,
                )
                .execute()
            )

            batch = response.get("messages", [])
            messages.extend(batch)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        logger.info(f"Found {len(messages)} messages in inbox")
        return messages

    def list_unprocessed_messages(self, max_results: int = 50) -> list[dict]:
        """
        List messages that haven't been processed yet.

        Args:
            max_results: Maximum number of messages to return

        Returns:
            List of message metadata
        """
        # Get recent inbox messages - we filter by database record, not Gmail label
        # This is more reliable than label-based filtering
        response = (
            self.service.users()
            .messages()
            .list(
                userId="me",
                maxResults=max_results,
                labelIds=["INBOX"],
            )
            .execute()
        )

        messages = response.get("messages", [])
        logger.info(f"Found {len(messages)} messages to check")
        return messages

    def get_message(self, message_id: str) -> dict:
        """
        Get full message content by ID.

        Args:
            message_id: Gmail message ID

        Returns:
            Full message data including headers and body
        """
        message = (
            self.service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",
            )
            .execute()
        )
        return message

    def extract_email_data(self, message: dict) -> dict:
        """
        Extract useful data from a Gmail message.

        Args:
            message: Full Gmail message object

        Returns:
            Dictionary with extracted email data
        """
        headers = {
            h["name"].lower(): h["value"]
            for h in message["payload"]["headers"]
        }

        body = self._extract_body(message["payload"])

        received_at = None
        if "date" in headers:
            try:
                received_at = parsedate_to_datetime(headers["date"])
            except Exception:
                pass

        return {
            "message_id": message["id"],
            "thread_id": message["threadId"],
            "subject": headers.get("subject", ""),
            "sender": headers.get("from", ""),
            "received_at": received_at,
            "body_text": body.get("text", ""),
            "body_html": body.get("html", ""),
        }

    def _extract_body(self, payload: dict) -> dict:
        """Extract text and HTML body from message payload."""
        body = {"text": "", "html": ""}

        if "parts" in payload:
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain" and "data" in part.get("body", {}):
                    body["text"] = base64.urlsafe_b64decode(
                        part["body"]["data"]
                    ).decode("utf-8", errors="ignore")
                elif mime_type == "text/html" and "data" in part.get("body", {}):
                    body["html"] = base64.urlsafe_b64decode(
                        part["body"]["data"]
                    ).decode("utf-8", errors="ignore")
                elif "parts" in part:
                    nested = self._extract_body(part)
                    body["text"] = body["text"] or nested["text"]
                    body["html"] = body["html"] or nested["html"]
        elif "body" in payload and "data" in payload["body"]:
            data = base64.urlsafe_b64decode(payload["body"]["data"]).decode(
                "utf-8", errors="ignore"
            )
            if payload.get("mimeType") == "text/html":
                body["html"] = data
            else:
                body["text"] = data

        return body

    def add_label(self, message_id: str, label_name: str) -> None:
        """Add a label to mark email as processed."""
        labels = self.service.users().labels().list(userId="me").execute()
        label_id = None

        for label in labels.get("labels", []):
            if label["name"] == label_name:
                label_id = label["id"]
                break

        if not label_id:
            new_label = (
                self.service.users()
                .labels()
                .create(
                    userId="me",
                    body={
                        "name": label_name,
                        "messageListVisibility": "show",
                        "labelListVisibility": "labelShow",
                    },
                )
                .execute()
            )
            label_id = new_label["id"]

        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [label_id]},
        ).execute()
