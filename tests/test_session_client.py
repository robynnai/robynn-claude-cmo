from __future__ import annotations

import json
from pathlib import Path

import session_client
from session_client import RobynnSessionClient, SessionClientError
from session_store import SessionStore


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


class FakeHttpClient:
    def __init__(self, responses: list[FakeResponse], calls: list[dict]):
        self._responses = responses
        self._calls = calls

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def request(self, method, url, headers=None, json=None):
        self._calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "json": json,
            }
        )
        return self._responses.pop(0)


def test_auth_login_persists_api_key_and_orgs(monkeypatch, tmp_path: Path):
    calls: list[dict] = []
    responses = [
        FakeResponse(
            {
                "success": True,
                "requires_org_selection": True,
                "data": {
                    "organizations": [{"id": "org-1", "name": "Acme"}],
                },
            }
        )
    ]
    monkeypatch.setattr(
        session_client.httpx,
        "Client",
        lambda timeout=60.0: FakeHttpClient(responses, calls),
    )

    store = SessionStore(tmp_path / "session.json")
    client = RobynnSessionClient(base_url="https://robynn.ai/api/cli", store=store)

    payload = client.auth_login("rb_test_123")
    state = store.load()

    assert payload["data"]["organizations"][0]["id"] == "org-1"
    assert state["api_key"] == "rb_test_123"
    assert state["organizations"][0]["name"] == "Acme"
    assert calls[0]["url"].endswith("/auth/exchange")


def test_use_org_stores_rotating_session_credentials(monkeypatch, tmp_path: Path):
    calls: list[dict] = []
    responses = [
        FakeResponse(
            {
                "success": True,
                "data": {
                    "access_token": "header.payload.signature",
                    "refresh_token": "refresh-token",
                    "expires_in": 3600,
                    "organizations": [{"id": "org-1", "name": "Acme"}],
                    "active_organization": {"id": "org-1", "name": "Acme"},
                },
            }
        )
    ]
    monkeypatch.setattr(
        session_client.httpx,
        "Client",
        lambda timeout=60.0: FakeHttpClient(responses, calls),
    )
    monkeypatch.setattr(
        RobynnSessionClient,
        "_jwt_expiry",
        staticmethod(lambda token: 9999999999.0),
    )

    store = SessionStore(tmp_path / "session.json")
    store.save({"api_key": "rb_test_123"})

    client = RobynnSessionClient(base_url="https://robynn.ai/api/cli", store=store)
    client.use_org("org-1")

    state = store.load()
    assert state["selected_org_id"] == "org-1"
    assert state["selected_org_name"] == "Acme"
    assert state["access_token"] == "header.payload.signature"
    assert state["refresh_token"] == "refresh-token"
    assert calls[0]["json"] == {"organization_id": "org-1"}


def test_auth_status_reports_org_selection_requirement(tmp_path: Path):
    store = SessionStore(tmp_path / "session.json")
    store.save(
        {
            "api_key": "rb_test_123",
            "organizations": [
                {"id": "org-1", "name": "Acme"},
                {"id": "org-2", "name": "Beta"},
            ],
        }
    )

    client = RobynnSessionClient(base_url="https://robynn.ai/api/cli", store=store)
    payload = client.auth_status()

    assert payload["organization_count"] == 2
    assert payload["requires_org_selection"] is True


def test_status_requires_selected_org_before_api_calls(tmp_path: Path):
    store = SessionStore(tmp_path / "session.json")
    store.save({"api_key": "rb_test_123"})

    client = RobynnSessionClient(base_url="https://robynn.ai/api/cli", store=store)

    try:
        client.status()
    except SessionClientError as exc:
        assert "robynn org list" in str(exc)
        assert "robynn org use <org_id>" in str(exc)
    else:
        raise AssertionError("Expected org selection error")
