"""OpenAI service for parsing emails using structured outputs."""

import logging

from openai import OpenAI

from ..config import Settings
from ..schemas.parsed_email import EmailParseResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert email parser specializing in job application notification emails.

Your task is to analyze emails received at a recruiting inbox and extract structured information about job applications.

Common job board notification formats you'll encounter:
- ZipRecruiter: "New Application from [Name] for [Position]"
- Handshake: "[Name] applied to [Position]"
- Wellfound (AngelList): "New applicant for [Position]"
- Indeed: "New Application: [Position] - [Name]"
- Welcome to the Jungle: "New application for [Position]"
- LinkedIn: "New applicant for [Position]"
- Greenhouse/Lever: Various ATS notification formats

Extract ALL relevant information from the email:
- First name and last name of the applicant
- The job board/source the application came from
- The position(s) they applied for
- Any link to view the full application (if present in the email)

Important notes:
- If only a full name is given, intelligently split into first and last name
- The application_link may not be present - that's okay, set it to null
- For positions, extract the exact position title as stated in the email
- If the email is not a job application notification (e.g., marketing, newsletter), set is_job_application to false"""


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
                    confidence=0.0,
                    application=None,
                )

            return result

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
