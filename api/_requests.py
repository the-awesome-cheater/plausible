from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------
# Stats API
# ---------
class StatsQueryRequest(BaseModel):
    site_id: str
    metrics: List[str]
    date_range: Any
    dimensions: Optional[List[str]] = None
    filters: Optional[List[list]] = None
    order_by: Optional[List[List[str]]] = None
    include: Optional[Dict[str, Any]] = None
    pagination: Optional[Dict[str, int]] = None


# ---------
# Events API
# ---------
class EventRequest(BaseModel):
    domain: str
    name: str
    url: str
    user_agent: str = Field(..., description="Required header value for unique visitor counting")
    client_ip: Optional[str] = Field(None, description="Set when sending from server/proxy")
    referrer: Optional[str] = None
    props: Optional[Dict[str, Any]] = None
    revenue: Optional[Dict[str, Any]] = None
    interactive: bool = True
    debug: bool = False


# ---------
# Sites API
# ---------
class CreateSiteRequest(BaseModel):
    domain: str
    timezone: Optional[str] = Field("Etc/UTC")
    team_id: Optional[str] = None


class UpdateSiteDomainRequest(BaseModel):
    domain: str


class SharedLinkRequest(BaseModel):
    site_id: str
    name: str


class PutGoalRequest(BaseModel):
    site_id: str
    goal_type: str  # "event" | "page"
    event_name: Optional[str] = None
    page_path: Optional[str] = None
    display_name: Optional[str] = None


class PutGuestRequest(BaseModel):
    site_id: str
    email: str
    role: str  # "viewer" | "editor"
