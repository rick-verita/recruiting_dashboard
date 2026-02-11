"""OpenAI service for parsing emails using structured outputs."""

import logging

from openai import OpenAI

from ..config import Settings
from ..schemas.parsed_email import EmailParseResult
from ..schemas.position_grouping import PositionGroupingResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert email parser for a recruiting inbox. You must classify each email and extract structured data.

CRITICAL — Two mutually exclusive categories:

1) APPLICATION (is_job_application=true, is_message=false)
   Only when the email is clearly a notification that someone submitted an official application through a job board or listing. Examples:
   - "New application from [Name] for [Position]" (ZipRecruiter, Indeed, etc.)
   - "[Name] applied to [Position]" (Handshake, Wellfound, etc.)
   - ATS notifications (Greenhouse, Lever) that state an application was submitted.
   The email must explicitly indicate that an application was submitted via the platform. Set application with first_name, last_name, source, positions, and application_link if present.

2) MESSAGE (is_job_application=false, is_message=true)
   When someone reached out but did NOT submit an official application through a board. This includes:
   - Direct emails to the company (someone emailed the recruiting inbox directly).
   - Job-board or platform messages that are just messages (e.g. LinkedIn InMail, a message on a board), not "application submitted" notifications.
   For messages: set message with first_name, last_name, source (use "other" for direct email, or e.g. "linkedin" if it's a LinkedIn message), positions (any role mentioned, can be empty), and message_link only if the email contains a URL to view the message on the platform (e.g. LinkedIn message link). Do not set message_link for direct emails.

3) NEITHER (is_job_application=false, is_message=false)
   Marketing, newsletters, or unrelated emails. Leave application and message null.

Extraction rules:
- First/last name: split intelligently if only full name is given.
- For applications: extract the exact position title(s) from the notification; include application_link from href in HTML when present. For Handshake, if there is no "view application" link, use the "View all applicants" or "log in to your account" button href as application_link.
- For messages: if it's a direct email, source=other and message_link=null. If it's a platform message (e.g. LinkedIn), set source accordingly and set message_link to any URL in the email that opens the message on that platform."""


class OpenAIService:
    """Service for parsing emails using OpenAI."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key.get_secret_value())
        self.model = settings.openai_model

    def parse_email(
        self,
        subject: str,
        body: str,
        sender: str,
    ) -> EmailParseResult:
        """
        Parse an email to extract job application data.

        Args:
            subject: Email subject line
            body: Email body (text or HTML)
            sender: Email sender address

        Returns:
            Parsed email result with application data
        """
        # Truncate very long emails
        truncated_body = body[:1000000] if len(body) > 1000000 else body

        user_message = f"""Parse the following email to extract job application information:

SENDER: {sender}

SUBJECT: {subject}

BODY:
{truncated_body}
"""

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                response_format=EmailParseResult,
            )

            result = response.choices[0].message.parsed

            if result is None:
                logger.warning("OpenAI returned unparseable response")
                return EmailParseResult(
                    is_job_application=False,
                    is_message=False,
                    confidence=0.0,
                    application=None,
                    message=None,
                )

            return result

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise

    def group_similar_positions(self, titles: list[str]) -> dict[str, str]:
        """
        Use the LLM to group similar position titles into canonical names.
        Returns a mapping from each original title to its group name.
        """
        if not titles:
            return {}

        user_message = """Group the following job position titles. Many are repetitive or similar (e.g. "Software Engineer", "SWE", "Software Developer").
For each title, choose a canonical group name that best represents it. Put similar roles in the same group (same group_name).
Return one mapping per input title. Use the exact original_title as given. Keep group_name concise (e.g. "Software Engineer", "Data Scientist").

Position titles:
"""
        user_message += "\n".join(f"- {t}" for t in titles)

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You output a list of mappings: each input position title (original_title) is mapped to a canonical group_name. Similar titles must get the same group_name.",
                    },
                    {"role": "user", "content": user_message},
                ],
                response_format=PositionGroupingResult,
            )
            result = response.choices[0].message.parsed
            if result is None:
                return {t: t for t in titles}
            return {m.original_title: m.group_name for m in result.mappings}
        except Exception as e:
            logger.warning(f"Position grouping failed: {e}, using titles as-is")
            return {t: t for t in titles}
