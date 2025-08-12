from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.core.landing_page.plausible.api import router
from backend.app.core.landing_page.plausible.api.deps import get_client
from backend.app.core.landing_page.plausible.api.exceptions import register_exception_handlers


class FakePlausibleClient:
    def query_stats(self, query: dict):
        return {"results": [{"metrics": [1], "dimensions": []}], "meta": {}, "query": query}

    def send_event(self, **kwargs):
        return {}

    def list_sites(self):
        return {"sites": [], "meta": {}}

    def list_teams(self):
        return {"teams": [], "meta": {}}

    def create_site(self, **kwargs):
        return {"domain": kwargs.get("domain"), "timezone": kwargs.get("timezone", "Etc/UTC")}

    def update_site_domain(self, **kwargs):
        return {"domain": kwargs.get("new_domain")}

    def delete_site(self, **kwargs):
        return {"deleted": True}

    def get_site(self, **kwargs):
        return {"domain": kwargs.get("site_id"), "timezone": "Etc/UTC"}

    def put_shared_link(self, **kwargs):
        return {"name": kwargs.get("name"), "url": "https://plausible.io/share/example?auth=abc"}

    def list_goals(self, **kwargs):
        return {"goals": [], "meta": {}}

    def put_goal(self, **kwargs):
        return {"id": "1", "goal_type": kwargs.get("goal_type")}

    def delete_goal(self, **kwargs):
        return {"deleted": True}

    def list_guests(self, **kwargs):
        return {"guests": [], "meta": {}}

    def put_guest(self, **kwargs):
        return {"email": kwargs.get("email"), "role": kwargs.get("role"), "status": "invited"}

    def delete_guest(self, **kwargs):
        return {"deleted": True}


def create_app():
    app = FastAPI()
    register_exception_handlers(app)
    app.dependency_overrides[get_client] = lambda: FakePlausibleClient()
    app.include_router(router)
    return app


def test_stats_query():
    app = create_app()
    client = TestClient(app)
    resp = client.post(
        "/plausible/stats/query",
        json={"site_id": "dummy.site", "metrics": ["visitors"], "date_range": "7d"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert data["results"][0]["metrics"] == [1]


def test_send_event():
    app = create_app()
    client = TestClient(app)
    resp = client.post(
        "/plausible/events",
        json={
            "domain": "dummy.site",
            "name": "pageview",
            "url": "https://dummy.site/",
            "user_agent": "pytest-UA",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_sites_list_and_get():
    app = create_app()
    client = TestClient(app)

    r1 = client.get("/plausible/sites")
    assert r1.status_code == 200
    assert r1.json()["ok"] is True

    r2 = client.get("/plausible/sites/test-domain.com")
    assert r2.status_code == 200
    assert r2.json()["data"]["domain"] == "test-domain.com"
