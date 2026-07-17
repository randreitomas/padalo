from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedRead(APIModel):
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(APIModel, Generic[T]):
    items: list[T]
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


Money = Decimal
