from __future__ import annotations

from typing import Any, List, Literal, Optional, Tuple, TypedDict

# ----------
# Type aliases
# ----------
Metric = str  # e.g. "visitors", "pageviews", "bounce_rate", etc.
Dimension = str  # e.g. "visit:country_name", "event:page", "time:day", etc.

Direction = Literal["asc", "desc"]
OrderByItem = Tuple[str, Direction]  # (dimension_or_metric, direction)
OrderBy = List[OrderByItem]

Filter = List[Any]  # Simple or logical filters as per API docs


class IncludeOptions(TypedDict, total=False):
    imports: bool
    time_labels: bool
    total_rows: bool


class Pagination(TypedDict, total=False):
    limit: int
    offset: int


class StatsQuery(TypedDict, total=False):
    site_id: str  # REQUIRED
    metrics: List[Metric]  # REQUIRED
    date_range: Any  # REQUIRED: string or [start, end] ISO8601 strings
    dimensions: List[Dimension]
    filters: List[Filter]
    order_by: OrderBy
    include: IncludeOptions
    pagination: Pagination


# ---------
# Responses
# ---------
class QueryResultRow(TypedDict):
    metrics: List[Any]
    dimensions: List[Any]


class StatsResponse(TypedDict):
    results: List[QueryResultRow]
    meta: dict
    query: dict


# ---------
# Events API
# ---------
class EventPayload(TypedDict, total=False):
    domain: str
    name: str
    url: str
    referrer: Optional[str]
    props: Optional[dict]
    revenue: Optional[dict]
    interactive: bool


# ---------
# Sites API shapes (loose)
# ---------
class Site(TypedDict, total=False):
    domain: str
    timezone: str
    custom_properties: List[str]


class SitesListResponse(TypedDict):
    sites: List[Site]
    meta: dict


class TeamsListResponse(TypedDict):
    teams: List[dict]
    meta: dict


class GoalsListResponse(TypedDict):
    goals: List[dict]
    meta: dict
