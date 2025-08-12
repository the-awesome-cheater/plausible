from __future__ import annotations

from fastapi import Query

from backend.app.core.landing_page.plausible import PlausibleClient
from ._requests import (
    StatsQueryRequest,
    EventRequest,
    CreateSiteRequest,
    UpdateSiteDomainRequest,
    SharedLinkRequest,
    PutGoalRequest,
    PutGuestRequest,
)


# ---------
# Stats API
# ---------

def handle_stats_query(payload: StatsQueryRequest, client: PlausibleClient):
    result = client.query_stats(payload.model_dump(exclude_none=True))
    return result


# ---------
# Events API
# ---------

def handle_send_event(payload: EventRequest, client: PlausibleClient):
    return client.send_event(
        domain=payload.domain,
        name=payload.name,
        url=payload.url,
        user_agent=payload.user_agent,
        client_ip=payload.client_ip,
        referrer=payload.referrer,
        props=payload.props,
        revenue=payload.revenue,
        interactive=payload.interactive,
        debug=payload.debug,
    )


# ---------
# Sites API
# ---------

def handle_list_sites(client: PlausibleClient):
    return client.list_sites()


def handle_list_teams(client: PlausibleClient):
    return client.list_teams()


def handle_create_site(payload: CreateSiteRequest, client: PlausibleClient):
    return client.create_site(domain=payload.domain, timezone=payload.timezone or "Etc/UTC", team_id=payload.team_id)


def handle_update_site(site_id: str, payload: UpdateSiteDomainRequest, client: PlausibleClient):
    return client.update_site_domain(site_id=site_id, new_domain=payload.domain)


def handle_delete_site(site_id: str, client: PlausibleClient):
    return client.delete_site(site_id=site_id)


def handle_get_site(site_id: str, client: PlausibleClient):
    return client.get_site(site_id=site_id)


def handle_put_shared_link(payload: SharedLinkRequest, client: PlausibleClient):
    return client.put_shared_link(site_id=payload.site_id, name=payload.name)


def handle_list_goals(site_id: str, client: PlausibleClient):
    return client.list_goals(site_id=site_id)


def handle_put_goal(payload: PutGoalRequest, client: PlausibleClient):
    return client.put_goal(
        site_id=payload.site_id,
        goal_type=payload.goal_type,
        event_name=payload.event_name,
        page_path=payload.page_path,
        display_name=payload.display_name,
    )


def handle_delete_goal(goal_id: str, site_id: str, client: PlausibleClient):
    return client.delete_goal(goal_id=goal_id, site_id=site_id)


def handle_list_guests(site_id: str, client: PlausibleClient):
    return client.list_guests(site_id=site_id)


def handle_put_guest(payload: PutGuestRequest, client: PlausibleClient):
    return client.put_guest(site_id=payload.site_id, email=payload.email, role=payload.role)


def handle_delete_guest(email: str, client: PlausibleClient):
    return client.delete_guest(email=email)
