# Plausible Analytics SDK (Internal)

Location: `backend/app/core/landing_page/plausible/`

This is a lightweight Python SDK for Plausible Analytics covering:

- Stats API v2: `POST /api/v2/query`
- Events API: `POST /api/event`
- Sites API v1: manage sites, goals, guests, and shared links

## Install/use

This SDK is part of the backend codebase. Import from the package:

```python
from backend.app.core.landing_page.plausible import PlausibleClient, PlausibleAPIError
```

## Environment variables

- `PLAUSIBLE_STATS_API_KEY` — key with Stats scope
- `PLAUSIBLE_SITES_API_KEY` — key with Sites scope (for provisioning)

You can also pass keys directly to `PlausibleClient(...)`.

## Quick start

```python
from backend.app.core.landing_page.plausible import PlausibleClient

client = PlausibleClient()  # reads keys from env

# Stats: last 7 days visitors + pageviews
stats = client.query_stats({
    "site_id": "dummy.site",
    "metrics": ["visitors", "pageviews"],
    "date_range": "7d",
})
print(stats)

# Events: record a server-side pageview
client.send_event(
    domain="dummy.site",
    name="pageview",
    url="https://dummy.site/login",
    user_agent="Mozilla/5.0 ...",    # REQUIRED
    client_ip="203.0.113.10",        # Recommended when sending from backend
    props={"logged_in": "false"},
)

# Sites: list sites
sites = client.list_sites()
print(sites)
```

## Notes

- Rate limiting: a simple token-bucket limiter is applied (default 600 req/hour). Adjust with `rate_limit_per_hour`.
- Retries: HTTP 429/5xx are retried with exponential backoff.
- Errors: raises `PlausibleAuthError`, `PlausibleRateLimitError`, or `PlausibleAPIError`.

## Common patterns

- Do not mix session metrics (e.g., `bounce_rate`, `visit_duration`, `views_per_visit`) with event dimensions (`event:*`).
- Use `date_range` for time selection; time dimensions (`time:*`) are not usable in filters.
- For time-series charts, include `dimensions=["time:day"]` (or hour/month) and optionally `include={"time_labels": true}`.

## Examples

### Country/City breakdown ordered by visitors
```python
resp = client.query_stats({
    "site_id": "dummy.site",
    "metrics": ["visitors", "pageviews"],
    "date_range": ["2024-01-01", "2024-07-01"],
    "dimensions": ["visit:country_name", "visit:city_name"],
    "filters": [["is_not", "visit:country_name", [""]]],
    "order_by": [["visitors", "desc"]],
})
```

### Time-series last 28 days with labels
```python
resp = client.query_stats({
    "site_id": "dummy.site",
    "metrics": ["visitors", "pageviews"],
    "date_range": "28d",
    "dimensions": ["time:day"],
    "include": {"time_labels": True, "total_rows": True},
})
```

### Create a site and a goal
```python
site = client.create_site(domain="test-domain.com", timezone="Europe/London")
goal = client.put_goal(site_id="test-domain.com", goal_type="event", event_name="Signup")
```

## Testing

- Unit tests can mock `requests.Session` to ensure correct method, headers, and body are used.
- For integration, set real API keys and a test domain, then run simple smoke tests for each endpoint.
