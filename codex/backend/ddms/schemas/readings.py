from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ReadingOut(BaseModel):
    timestamp: datetime = Field(description="UTC timestamp of the reading")
    value: float = Field(description="Measured value")

    model_config = {"from_attributes": True}

