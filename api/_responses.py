from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel


class StatsRow(BaseModel):
    metrics: List[Any]
    dimensions: List[Any]


class StatsResponse(BaseModel):
    results: List[StatsRow]
    meta: dict
    query: dict


class GenericResponse(BaseModel):
    ok: bool = True
    data: Optional[Any] = None
