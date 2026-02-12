"""OpenAI service for parsing emails using structured outputs."""

import logging
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

from openai import OpenAI
from pydantic import BaseModel, Field

from ..config import Settings
from ..schemas.parsed_email import EmailParseResult, JobBoardSource
from ..schemas.position_grouping import PositionGroupingResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert email parser for a recruiting inbox. You must classify each email and extract structured data.

CRITICAL — Only include emails that are hiring-related:
- Set is_hiring_related=true if the email pertains to hiring, recruiting, job applications, roles, candidates, or outreach in a work/recruiting context. Be lenient: include anything that could be recruiting-related (e.g. someone mentioning a role, a recruiter message, job-board notification, application, or candidate contact). Set is_hiring_related=false only for clearly unrelated content (marketing, newsletters, purely personal, etc.).

Within hiring-related emails, two mutually exclusive categories:

1) APPLICATION (is_job_application=true, is_message=false)
   Only when the email is clearly a notification that someone submitted an official application through a job board or listing. Examples:
   - "New application from [Name] for [Position]" (ZipRecruiter, Indeed, etc.)
   - "[Name] applied to [Position]" (Handshake, Wellfound, etc.)
   - ATS notifications (Greenhouse, Lever) that state an application was submitted.
   The email must explicitly indicate that an application was submitted via the platform. Set application with first_name, last_name, source, positions, and application_link if present.

2) MESSAGE (is_job_application=false, is_message=true)
   When someone reached out but did NOT submit an official application through a board. This includes:
   - Direct emails to the company (someone emailed the recruiting inbox directly). Use source=other and message_link=null (the system will attach the email thread link for Gmail).
   - Platform messages (e.g. LinkedIn InMail, Indeed message). Use the appropriate source (linkedin, indeed, etc.).
   For platform messages, message_link is CRITICAL and must be an https URL to the platform—NEVER a mailto: link. Many platform emails have a "Reply" button that is actually mailto: (reply by email); you must IGNORE that. Instead, find the link that opens the message or conversation ON THE PLATFORM (so the user can reply there). Scan the email HTML for links that:
   (a) point to the platform domain (e.g. linkedin.com, indeed.com)—use the same domain as the platform you set in source;
   (b) are the href of a button/link like "View message", "View in LinkedIn", "See conversation", "Open in LinkedIn", "Reply on LinkedIn", "View conversation", "Message" (when it goes to the platform), or similar. Wording varies by platform; use the link that clearly opens the conversation or reply screen on that platform.
   If the only reply-related href is mailto:, do not use it—use the platform view/conversation link instead, or null if none exists. Do NOT use: mailto:, the email view in Gmail, generic login/home, or profile-only links.

3) NEITHER (is_job_application=false, is_message=false)
   Hiring-related but not clearly an application or a message (e.g. generic notification). Leave application and message null.

Extraction rules:
- First/last name: split intelligently if only full name is given.
- For applications: extract the exact position title(s) from the notification; include application_link from href in HTML when present. For Handshake, if there is no "view application" link, use the "View all applicants" or "log in to your account" button href as application_link.
- For messages: direct email → source=other, message_link=null. Platform message → source=linkedin/indeed/etc. and message_link = an https URL to the platform that opens the message/conversation (never mailto:). Prefer links from buttons like "View in [Platform]", "See conversation", "View message" when the Reply button is mailto:."""


class PlatformMessageLinkSelection(BaseModel):
    """Structured output for choosing the best platform message link."""

    message_link: str | None = Field(
        None,
        description="Best URL that opens the message thread/conversation on the platform (not mailto).",
    )


class AnchorHrefExtractor(HTMLParser):
    """Extract href + visible text from anchor tags."""

    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._current_text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = None
        for key, value in attrs:
            if key.lower() == "href" and value:
                href = value.strip()
                break
        self._current_href = href
        self._current_text_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None and data:
            self._current_text_parts.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a":
            return
        if self._current_href:
            text = " ".join(t for t in self._current_text_parts if t).strip()
            self.links.append((self._current_href, text))
        self._current_href = None
        self._current_text_parts = []


class OpenAIService:
    """Service for parsing emails using OpenAI."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key.get_secret_value())
        self.model = settings.openai_model

    def _extract_link_candidates(self, body: str, max_links: int = 120) -> list[tuple[str, str]]:
        """Extract candidate href + label pairs from HTML body."""
        parser = AnchorHrefExtractor()
        try:
            parser.feed(body)
        except Exception:
            return []

        # Include any href attributes across all tags (some email buttons are not plain <a> tags).
        href_pattern = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
        regex_links: list[tuple[str, str]] = []
        for m in href_pattern.finditer(body):
            href = (m.group(1) or "").strip()
            if not href:
                continue
            # Nearby context helps link scoring when visible anchor text is absent.
            start = max(0, m.start() - 80)
            end = min(len(body), m.end() + 80)
            context = body[start:end].replace("\n", " ").replace("\r", " ").strip()
            regex_links.append((href, context))

        combined = parser.links + regex_links

        deduped: list[tuple[str, str]] = []
        seen: set[str] = set()
        for href, text in combined:
            key = href.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append((href.strip(), text.strip()))
            if len(deduped) >= max_links:
                break
        return deduped

    @staticmethod
    def _is_http_link(link: str | None) -> bool:
        if not link:
            return False
        value = link.strip().lower()
        return value.startswith("http://") or value.startswith("https://")

    @staticmethod
    def _source_domains(source: JobBoardSource) -> tuple[str, ...]:
        domain_map: dict[JobBoardSource, tuple[str, ...]] = {
            JobBoardSource.LINKEDIN: ("linkedin.com", "lnkd.in"),
            JobBoardSource.INDEED: ("indeed.com",),
            JobBoardSource.ZIPRECRUITER: ("ziprecruiter.com",),
            JobBoardSource.HANDSHAKE: ("joinhandshake.com", "handshake.com"),
            JobBoardSource.WELLFOUND: ("wellfound.com", "angel.co"),
            JobBoardSource.WELCOME_TO_THE_JUNGLE: ("welcometothejungle.com",),
            JobBoardSource.GREENHOUSE: ("greenhouse.io",),
            JobBoardSource.LEVER: ("lever.co",),
            JobBoardSource.OTHER: (),
            JobBoardSource.UNKNOWN: (),
        }
        return domain_map.get(source, ())

    def _score_platform_link(self, source: JobBoardSource, href: str, text: str) -> int:
        """Heuristic fallback scorer for platform conversation links."""
        if not self._is_http_link(href):
            return -100

        parsed = urlparse(href)
        host = (parsed.netloc or "").lower()
        path = (parsed.path or "").lower()
        href_lower = href.lower()
        text_lower = (text or "").lower()
        score = 0

        source_domains = self._source_domains(source)
        if source_domains and any(d in host for d in source_domains):
            score += 70
        elif source != JobBoardSource.UNKNOWN:
            score -= 20

        positive_tokens = (
            "message",
            "messaging",
            "inmail",
            "inbox",
            "thread",
            "conversation",
            "reply",
            "comm/talent/inbox",
            "comm/messaging",
        )
        if any(tok in href_lower or tok in path for tok in positive_tokens):
            score += 35
        if any(tok in text_lower for tok in ("reply", "message", "conversation", "view")):
            score += 12

        negative_tokens = ("feed", "home", "login", "signup", "unsubscribe", "profile", "help")
        if any(tok in href_lower for tok in negative_tokens):
            score -= 45

        return score

    def _choose_platform_message_link_with_llm(
        self,
        source: JobBoardSource,
        subject: str,
        sender: str,
        current_link: str | None,
        candidates: list[tuple[str, str]],
    ) -> str | None:
        """Use a focused LLM step to select the best platform conversation link."""
        if not candidates:
            return None

        candidates_text = "\n".join(
            f"- href: {href}\n  text: {text or '<no-visible-text>'}"
            for href, text in candidates
        )

        user_message = f"""Select the best message link for a platform message email.

SOURCE: {source.value}
SENDER: {sender}
SUBJECT: {subject}
CURRENT_PARSED_LINK: {current_link}

Candidate links from email HTML:
{candidates_text}
"""

        system_message = """Choose the URL that opens the message/conversation/reply screen ON THE PLATFORM.
Rules:
- Output one field: message_link.
- message_link MUST be http/https, never mailto.
- Prefer source domain match (e.g. linkedin.com for linkedin).
- Prefer URLs that indicate message/inbox/thread/conversation/reply.
- Reject generic feed/home/login/profile/help/unsubscribe links.
- If no suitable platform conversation URL exists, return null."""

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                response_format=PlatformMessageLinkSelection,
            )
            parsed = response.choices[0].message.parsed
            if parsed is None:
                return None
            return parsed.message_link
        except Exception as e:
            logger.warning(f"Platform message-link selection failed: {e}")
            return None

    def _refine_platform_message_link(
        self,
        source: JobBoardSource,
        subject: str,
        sender: str,
        body: str,
        current_link: str | None,
    ) -> str | None:
        """Refine platform message link so it lands on platform conversation view."""
        candidates = self._extract_link_candidates(body)

        # Start from the original parser result and only replace if we find a clearly better link.
        best_href: str | None = current_link if self._is_http_link(current_link) else None
        best_score = (
            self._score_platform_link(source, current_link or "", "")
            if self._is_http_link(current_link)
            else -10_000
        )

        # LLM proposal over explicit candidate hrefs/text.
        chosen = self._choose_platform_message_link_with_llm(
            source=source,
            subject=subject,
            sender=sender,
            current_link=current_link,
            candidates=candidates,
        )
        if self._is_http_link(chosen):
            chosen_score = self._score_platform_link(source, chosen, "")
            if chosen_score > best_score:
                best_href = chosen
                best_score = chosen_score

        # Deterministic scoring across all candidates.
        for href, text in candidates:
            score = self._score_platform_link(source, href, text)
            if score > best_score:
                best_score = score
                best_href = href

        if best_href and best_score > 0 and self._is_http_link(best_href):
            return best_href
        return current_link if self._is_http_link(current_link) else None

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
                    is_hiring_related=False,
                    is_job_application=False,
                    is_message=False,
                    confidence=0.0,
                    application=None,
                    message=None,
                )

            # Platform messages: run a focused link selection pass so Contact opens
            # the platform conversation/reply screen instead of mailto or generic URLs.
            if (
                result.is_message
                and result.message is not None
                and result.message.source not in (JobBoardSource.OTHER, JobBoardSource.UNKNOWN)
            ):
                refined_link = self._refine_platform_message_link(
                    source=result.message.source,
                    subject=subject,
                    sender=sender,
                    body=truncated_body,
                    current_link=result.message.message_link,
                )
                result.message.message_link = refined_link

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
