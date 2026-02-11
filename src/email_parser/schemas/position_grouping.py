"""Schema for LLM-based position title grouping."""

from pydantic import BaseModel, Field


class PositionMapping(BaseModel):
    """Maps one position title to a canonical group name."""

    original_title: str = Field(..., description="The position title as stored")
    group_name: str = Field(..., description="Canonical group name for similar positions")


class PositionGroupingResult(BaseModel):
    """Result of grouping similar position titles."""

    mappings: list[PositionMapping] = Field(
        ...,
        description="One mapping per input title; group_name may repeat for similar titles",
    )
