from __future__ import annotations

from typing import Optional
from fastapi import Depends, Header, HTTPException, status

from backend.app.core.landing_page.plausible import PlausibleClient
from .config import get_client as get_default_client


def get_client(authorization: Optional[str] = Header(None)) -> PlausibleClient:
    """
    Provide a PlausibleClient.
    - If Authorization: Bearer <token> is provided, use it for both stats and sites.
    - Otherwise, return the default client configured from env via config.get_client().
    """
    if not authorization:
        return get_default_client()

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
    token = parts[1]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty bearer token")

    return PlausibleClient(stats_api_key=token, sites_api_key=token)
