from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Category(StrEnum):
    meeting = "meeting"
    note = "note"
    instruction = "instruction"
    other = "other"


class Transcription(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    text: str
    created_at: datetime
    source_metadata: dict[str, str] = Field(default_factory=dict)


class Classification(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    suggested_title: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
