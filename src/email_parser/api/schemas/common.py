"""Common schemas used across the API."""

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=25, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Base response for paginated endpoints."""

    total: int
    page: int
    page_size: int
    total_pages: int
