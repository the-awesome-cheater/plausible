from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from backend.app.core.landing_page.plausible import PlausibleClient


class PlausibleSettings:
    def __init__(
        self,
        *,
        stats_api_key: Optional[str] = None,
        sites_api_key: Optional[str] = None,
        base_url: str = "https://plausible.io",
        timeout_s: int = 30,
        rate_limit_per_hour: int = 600,
    ) -> None:
        self.stats_api_key = stats_api_key or os.getenv("PLAUSIBLE_STATS_API_KEY")
        self.sites_api_key = sites_api_key or os.getenv("PLAUSIBLE_SITES_API_KEY")
        self.base_url = os.getenv("PLAUSIBLE_BASE_URL", base_url)
        self.timeout_s = int(os.getenv("PLAUSIBLE_TIMEOUT_S", str(timeout_s)))
        self.rate_limit_per_hour = int(os.getenv("PLAUSIBLE_RATE_LIMIT_PER_HOUR", str(rate_limit_per_hour)))


@lru_cache(maxsize=1)
def get_settings() -> PlausibleSettings:
    return PlausibleSettings()


def get_client() -> PlausibleClient:
    s = get_settings()
    return PlausibleClient(
        stats_api_key=s.stats_api_key,
        sites_api_key=s.sites_api_key,
        base_url=s.base_url,
        timeout_s=s.timeout_s,
        rate_limit_per_hour=s.rate_limit_per_hour,
    )
