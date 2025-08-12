from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from typing import Any, Dict

from backend.app.core.landing_page.plausible import PlausibleClient
from .deps import get_client
from ._requests import (
    StatsQueryRequest,
    EventRequest,
    CreateSiteRequest,
    UpdateSiteDomainRequest,
    SharedLinkRequest,
    PutGoalRequest,
    PutGuestRequest,
)
from ._responses import StatsResponse, GenericResponse
from .handlers import (
    handle_stats_query,
    handle_send_event,
    handle_list_sites,
    handle_list_teams,
    handle_create_site,
    handle_update_site,
    handle_delete_site,
    handle_get_site,
    handle_put_shared_link,
    handle_list_goals,
    handle_put_goal,
    handle_delete_goal,
    handle_list_guests,
    handle_put_guest,
    handle_delete_guest,
)

router = APIRouter(prefix="/plausible", tags=["plausible"])


# ---------
# Stats API
# ---------
@router.post("/stats/query", response_model=StatsResponse)
async def stats_query(payload: StatsQueryRequest, client: PlausibleClient = Depends(get_client)):
    result = handle_stats_query(payload, client)
    return StatsResponse(**result)


# ---------
# Events API
# ---------
@router.post("/events", response_model=GenericResponse)
async def send_event(payload: EventRequest, client: PlausibleClient = Depends(get_client)):
    data = handle_send_event(payload, client)
    return GenericResponse(ok=True, data=data)


# ---------
# Sites API
# ---------
@router.get("/sites", response_model=GenericResponse)
async def list_sites(client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_list_sites(client))


@router.get("/sites/teams", response_model=GenericResponse)
async def list_teams(client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_list_teams(client))


@router.post("/sites", response_model=GenericResponse)
async def create_site(payload: CreateSiteRequest, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_create_site(payload, client))


@router.put("/sites/{site_id}", response_model=GenericResponse)
async def update_site(site_id: str, payload: UpdateSiteDomainRequest, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_update_site(site_id, payload, client))


@router.delete("/sites/{site_id}", response_model=GenericResponse)
async def delete_site(site_id: str, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_delete_site(site_id, client))


@router.get("/sites/{site_id}", response_model=GenericResponse)
async def get_site(site_id: str, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_get_site(site_id, client))


@router.put("/sites/shared-links", response_model=GenericResponse)
async def put_shared_link(payload: SharedLinkRequest, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_put_shared_link(payload, client))


@router.get("/sites/{site_id}/goals", response_model=GenericResponse)
async def list_goals(site_id: str, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_list_goals(site_id, client))


@router.put("/sites/goals", response_model=GenericResponse)
async def put_goal(payload: PutGoalRequest, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_put_goal(payload, client))


@router.delete("/sites/goals/{goal_id}", response_model=GenericResponse)
async def delete_goal(goal_id: str, site_id: str = Query(...), client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_delete_goal(goal_id, site_id, client))


@router.get("/sites/{site_id}/guests", response_model=GenericResponse)
async def list_guests(site_id: str, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_list_guests(site_id, client))


@router.put("/sites/guests", response_model=GenericResponse)
async def put_guest(payload: PutGuestRequest, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_put_guest(payload, client))


@router.delete("/sites/guests/{email}", response_model=GenericResponse)
async def delete_guest(email: str, client: PlausibleClient = Depends(get_client)):
    return GenericResponse(ok=True, data=handle_delete_guest(email, client))
