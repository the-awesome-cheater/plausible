from __future__ import annotations

import os
import time
from typing import Any, Dict, Iterable, Optional

import requests
from requests import Response, Session
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from .errors import (
    PlausibleAPIError,
    PlausibleAuthError,
    PlausibleRateLimitError,
)
from .rate_limiter import RateLimiter


DEFAULT_BASE_URL = "https://plausible.io"
STATS_ENDPOINT = "/api/v2/query"
EVENT_ENDPOINT = "/api/event"
SITES_V1 = "/api/v1/sites"


class PlausibleClient:
    """
    Python SDK client for Plausible Analytics Stats, Events and Sites APIs.

    Authentication:
    - Stats API: bearer token with permission for stats (/api/v2/query)
    - Sites API: bearer token with Sites scope (v1 endpoints)

    You can pass keys directly or rely on env vars:
    - PLAUSIBLE_STATS_API_KEY
    - PLAUSIBLE_SITES_API_KEY
    """

    def __init__(
        self,
        *,
        stats_api_key: Optional[str] = None,
        sites_api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout_s: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        rate_limit_per_hour: Optional[int] = 600,
        session: Optional[Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.stats_api_key = stats_api_key or os.getenv("PLAUSIBLE_STATS_API_KEY")
        self.sites_api_key = sites_api_key or os.getenv("PLAUSIBLE_SITES_API_KEY")
        self.timeout_s = timeout_s

        self.session = session or requests.Session()
        retry = Retry(
            total=max_retries,
            read=max_retries,
            connect=max_retries,
            status=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "PUT", "DELETE"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self._rate_limiter = RateLimiter(capacity=rate_limit_per_hour or 600, refill_window_s=3600)

    # ---------------
    # Stats API (v2)
    # ---------------
    def query_stats(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v2/query
        query: full Plausible stats query JSON.
        Returns parsed JSON dict.
        """
        if not self.stats_api_key:
            raise PlausibleAuthError("Stats API key missing. Set PLAUSIBLE_STATS_API_KEY or pass stats_api_key.")

        self._rate_limiter.acquire()

        url = f"{self.base_url}{STATS_ENDPOINT}"
        resp = self.session.post(
            url,
            json=query,
            headers={
                "Authorization": f"Bearer {self.stats_api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout_s,
        )
        return self._handle_response(resp)

    # ---------------
    # Events API
    # ---------------
    def send_event(
        self,
        *,
        domain: str,
        name: str,
        url: str,
        user_agent: str,
        client_ip: Optional[str] = None,
        referrer: Optional[str] = None,
        props: Optional[Dict[str, Any]] = None,
        revenue: Optional[Dict[str, Any]] = None,
        interactive: bool = True,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        POST /api/event
        Returns {} on 202 Accepted; if debug=True, returns a JSON payload with resolved IP and 200 OK.
        """
        self._rate_limiter.acquire()

        payload: Dict[str, Any] = {
            "domain": domain,
            "name": name,
            "url": url,
            "interactive": interactive,
        }
        if referrer is not None:
            payload["referrer"] = referrer
        if props is not None:
            payload["props"] = props
        if revenue is not None:
            payload["revenue"] = revenue

        headers = {
            "Content-Type": "application/json",
            "User-Agent": user_agent,
        }
        if client_ip:
            headers["X-Forwarded-For"] = client_ip
        if debug:
            headers["X-Debug-Request"] = "true"

        url_ep = f"{self.base_url}{EVENT_ENDPOINT}"
        resp = self.session.post(url_ep, json=payload, headers=headers, timeout=self.timeout_s)
        return self._handle_response(resp)

    # ------------------
    # Sites API (v1)
    # ------------------
    def list_sites(self, *, after: Optional[str] = None, before: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        params: Dict[str, Any] = {}
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if limit is not None:
            params["limit"] = limit

        url = f"{self.base_url}{SITES_V1}"
        resp = self.session.get(url, headers=self._sites_headers(), params=params, timeout=self.timeout_s)
        return self._handle_response(resp)

    def list_teams(self, *, after: Optional[str] = None, before: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        params: Dict[str, Any] = {}
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if limit is not None:
            params["limit"] = limit

        url = f"{self.base_url}{SITES_V1}/teams"
        resp = self.session.get(url, headers=self._sites_headers(), params=params, timeout=self.timeout_s)
        return self._handle_response(resp)

    def create_site(self, *, domain: str, timezone: str = "Etc/UTC", team_id: Optional[str] = None) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        # Sites API expects multipart form data (-F in curl examples)
        data = {
            "domain": f'"{domain}"',
            "timezone": f'"{timezone}"',
        }
        if team_id:
            data["team_id"] = f'"{team_id}"'

        url = f"{self.base_url}{SITES_V1}"
        resp = self.session.post(url, headers=self._sites_headers(), files=data, timeout=self.timeout_s)
        return self._handle_response(resp)

    def update_site_domain(self, *, site_id: str, new_domain: str) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        data = {
            "domain": f'"{new_domain}"',
        }
        url = f"{self.base_url}{SITES_V1}/{site_id}"
        resp = self.session.put(url, headers=self._sites_headers(), files=data, timeout=self.timeout_s)
        return self._handle_response(resp)

    def delete_site(self, *, site_id: str) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        url = f"{self.base_url}{SITES_V1}/{site_id}"
        resp = self.session.delete(url, headers=self._sites_headers(), timeout=self.timeout_s)
        return self._handle_response(resp)

    def get_site(self, *, site_id: str) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        url = f"{self.base_url}{SITES_V1}/{site_id}"
        resp = self.session.get(url, headers=self._sites_headers(), timeout=self.timeout_s)
        return self._handle_response(resp)

    def put_shared_link(self, *, site_id: str, name: str) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        data = {
            "site_id": f'"{site_id}"',
            "name": f'"{name}"',
        }
        url = f"{self.base_url}{SITES_V1}/shared-links"
        resp = self.session.put(url, headers=self._sites_headers(), files=data, timeout=self.timeout_s)
        return self._handle_response(resp)

    # Goals
    def list_goals(self, *, site_id: str, after: Optional[str] = None, before: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        params: Dict[str, Any] = {"site_id": site_id}
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if limit is not None:
            params["limit"] = limit

        url = f"{self.base_url}{SITES_V1}/goals"
        resp = self.session.get(url, headers=self._sites_headers(), params=params, timeout=self.timeout_s)
        return self._handle_response(resp)

    def put_goal(
        self,
        *,
        site_id: str,
        goal_type: str,  # "event" | "page"
        event_name: Optional[str] = None,
        page_path: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        data = {"site_id": f'"{site_id}"', "goal_type": f'"{goal_type}"'}
        if event_name is not None:
            data["event_name"] = f'"{event_name}"'
        if page_path is not None:
            data["page_path"] = f'"{page_path}"'
        if display_name is not None:
            data["display_name"] = f'"{display_name}"'

        url = f"{self.base_url}{SITES_V1}/goals"
        resp = self.session.put(url, headers=self._sites_headers(), files=data, timeout=self.timeout_s)
        return self._handle_response(resp)

    def delete_goal(self, *, goal_id: str, site_id: str) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        data = {"site_id": f'"{site_id}"'}
        url = f"{self.base_url}{SITES_V1}/goals/{goal_id}"
        resp = self.session.delete(url, headers=self._sites_headers(), files=data, timeout=self.timeout_s)
        return self._handle_response(resp)

    # Guests
    def list_guests(self, *, site_id: str, after: Optional[str] = None, before: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        params: Dict[str, Any] = {"site_id": site_id}
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if limit is not None:
            params["limit"] = limit

        url = f"{self.base_url}{SITES_V1}/guests"
        resp = self.session.get(url, headers=self._sites_headers(), params=params, timeout=self.timeout_s)
        return self._handle_response(resp)

    def put_guest(self, *, site_id: str, email: str, role: str) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        data = {"site_id": f'"{site_id}"', "email": f'"{email}"', "role": f'"{role}"'}
        url = f"{self.base_url}{SITES_V1}/guests"
        resp = self.session.put(url, headers=self._sites_headers(), files=data, timeout=self.timeout_s)
        return self._handle_response(resp)

    def delete_guest(self, *, email: str) -> Dict[str, Any]:
        self._require_sites_key()
        self._rate_limiter.acquire()

        url = f"{self.base_url}{SITES_V1}/guests/{email}"
        resp = self.session.delete(url, headers=self._sites_headers(), timeout=self.timeout_s)
        return self._handle_response(resp)

    # ------------------
    # Internal helpers
    # ------------------
    def _sites_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.sites_api_key}",
        }

    def _require_sites_key(self) -> None:
        if not self.sites_api_key:
            raise PlausibleAuthError("Sites API key missing. Set PLAUSIBLE_SITES_API_KEY or pass sites_api_key.")

    def _handle_response(self, resp: Response) -> Dict[str, Any]:
        # Rate limit responses
        if resp.status_code == 429:
            raise PlausibleRateLimitError("Rate limit exceeded", status_code=resp.status_code, response_text=resp.text)

        # Attempt JSON regardless of status code for more details
        try:
            data = resp.json() if resp.content else {}
        except ValueError:
            data = {}

        if 200 <= resp.status_code < 300:
            return data

        if resp.status_code in (401, 403):
            raise PlausibleAuthError("Unauthorized or forbidden", status_code=resp.status_code, response_text=resp.text)

        raise PlausibleAPIError(
            f"HTTP {resp.status_code}",
            status_code=resp.status_code,
            response_text=resp.text,
            payload=data,
        )
