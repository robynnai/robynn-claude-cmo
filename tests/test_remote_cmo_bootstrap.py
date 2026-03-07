"""E2E-style tests for strict context bootstrap and routed CMO streaming."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cmo_context
import remote_cmo
from cmo_context import AuthRequiredError, BrandSetupRequiredError, CMOContextManager


def _build_context_client_factory(
    payloads: list[dict[str, Any]],
    call_counter: dict[str, int],
):
    class FakeResponse:
        status_code = 200

        def __init__(self, payload: dict[str, Any]) -> None:
            self._payload = payload

        def json(self) -> dict[str, Any]:
            return self._payload

    class FakeClient:
        def __init__(self, headers=None, timeout=None):
            self.headers = headers
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def get(self, url: str):
            call_counter["count"] += 1
            index = min(call_counter["count"] - 1, len(payloads) - 1)
            return FakeResponse(payloads[index])

    return FakeClient


def _build_stream_stub(stream_payloads: list[dict[str, Any]]):
    class FakeStreamResponse:
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def iter_text(self):
            yield 'data: {"type":"complete","data":{"response":"ok"}}\n\n'

    def fake_stream(method, url, json=None, headers=None, timeout=None):
        stream_payloads.append(json or {})
        return FakeStreamResponse()

    return fake_stream


def _new_remote_cmo_with_manager(cache_file: Path) -> remote_cmo.RemoteCMO:
    cmo = remote_cmo.RemoteCMO(api_key="rb_test_123")
    cmo.context_manager = CMOContextManager(
        api_key="rb_test_123",
        cli_base_url="https://robynn.ai/api/cli",
        cache_file=cache_file,
        ttl_seconds=1800,
    )
    return cmo


def test_stream_query_bootstraps_context_and_caches_org(monkeypatch, tmp_path):
    context_calls = {"count": 0}
    stream_payloads: list[dict[str, Any]] = []
    context_payload = {
        "data": {
            "organizationId": "org-abc",
            "companyName": "Acme",
        }
    }

    fake_client = _build_context_client_factory([context_payload], context_calls)
    monkeypatch.setattr(cmo_context.httpx, "Client", fake_client)
    monkeypatch.setattr(remote_cmo.httpx, "stream", _build_stream_stub(stream_payloads))
    monkeypatch.setattr(remote_cmo, "DEFAULT_ASSISTANT", "auto")

    cmo = _new_remote_cmo_with_manager(tmp_path / "context-cache.json")
    events_1 = list(cmo.stream_query("Write a LinkedIn post about our new feature."))
    events_2 = list(cmo.stream_query("Draft another post with a sharper hook."))

    assert context_calls["count"] == 1
    assert len(stream_payloads) == 2
    assert stream_payloads[0]["organization_id"] == "org-abc"
    assert stream_payloads[1]["organization_id"] == "org-abc"
    assert stream_payloads[0]["focus_hint"] == "content"
    assert stream_payloads[0]["mode"] == "chat"
    assert stream_payloads[0]["route_hint"] == "fast"
    assert stream_payloads[0]["requested_capability"] == "general"
    assert stream_payloads[0]["raw_user_prompt"] == "Write a LinkedIn post about our new feature."
    assert stream_payloads[0]["brand_context_profile"] == "content"
    assert stream_payloads[0]["brand_context_available"] is True
    assert "## Brand Identity" in stream_payloads[0]["brand_context"]
    assert "assistant_id" not in stream_payloads[0]
    assert stream_payloads[0]["message"] == "Write a LinkedIn post about our new feature."
    assert events_1[-1]["type"] == "complete"
    assert events_2[-1]["type"] == "complete"


def test_stream_query_refreshes_context_after_ttl_expiry(monkeypatch, tmp_path):
    context_calls = {"count": 0}
    stream_payloads: list[dict[str, Any]] = []
    cache_file = tmp_path / "context-cache-expiring.json"
    payloads = [
        {"data": {"organizationId": "org-1", "companyName": "Acme"}},
        {"data": {"organizationId": "org-1", "companyName": "Acme"}},
    ]

    fake_client = _build_context_client_factory(payloads, context_calls)
    monkeypatch.setattr(cmo_context.httpx, "Client", fake_client)
    monkeypatch.setattr(remote_cmo.httpx, "stream", _build_stream_stub(stream_payloads))
    monkeypatch.setattr(remote_cmo, "DEFAULT_ASSISTANT", "auto")

    cmo = remote_cmo.RemoteCMO(api_key="rb_test_123")
    cmo.context_manager = CMOContextManager(
        api_key="rb_test_123",
        cli_base_url="https://robynn.ai/api/cli",
        cache_file=cache_file,
        ttl_seconds=1,
    )

    list(cmo.stream_query("Create a content brief"))

    # Force cache expiry to validate refresh behavior.
    cached = json.loads(cache_file.read_text())
    cached["expires_at"] = 0
    cache_file.write_text(json.dumps(cached))

    list(cmo.stream_query("Create another content brief"))

    assert context_calls["count"] == 2
    assert len(stream_payloads) == 2


def test_stream_query_hard_fails_auth_without_stream_call(monkeypatch):
    cmo = remote_cmo.RemoteCMO(api_key="rb_invalid")
    cmo.context_manager = CMOContextManager(api_key="rb_invalid")
    cmo.context_manager.get_context = lambda refresh=False: (_ for _ in ()).throw(  # type: ignore[assignment]
        AuthRequiredError("auth failed")
    )

    stream_called = {"value": False}

    def _stream(*args, **kwargs):
        stream_called["value"] = True
        raise AssertionError("stream should not be called")

    monkeypatch.setattr(remote_cmo.httpx, "stream", _stream)
    events = list(cmo.stream_query("hello"))

    assert stream_called["value"] is False
    assert events == [{"type": "error", "message": "auth failed"}]


def test_stream_query_hard_fails_pending_setup_without_stream_call(monkeypatch):
    cmo = remote_cmo.RemoteCMO(api_key="rb_valid")
    cmo.context_manager = CMOContextManager(api_key="rb_valid")
    cmo.context_manager.get_context = lambda refresh=False: (_ for _ in ()).throw(  # type: ignore[assignment]
        BrandSetupRequiredError("pending setup")
    )

    stream_called = {"value": False}

    def _stream(*args, **kwargs):
        stream_called["value"] = True
        raise AssertionError("stream should not be called")

    monkeypatch.setattr(remote_cmo.httpx, "stream", _stream)
    events = list(cmo.stream_query("hello"))

    assert stream_called["value"] is False
    assert events == [{"type": "error", "message": "pending setup"}]


def test_stream_query_includes_assistant_target_when_configured(monkeypatch, tmp_path):
    context_calls = {"count": 0}
    stream_payloads: list[dict[str, Any]] = []
    context_payload = {"data": {"organizationId": "org-xyz", "companyName": "Acme"}}

    fake_client = _build_context_client_factory([context_payload], context_calls)
    monkeypatch.setattr(cmo_context.httpx, "Client", fake_client)
    monkeypatch.setattr(remote_cmo.httpx, "stream", _build_stream_stub(stream_payloads))
    monkeypatch.setattr(remote_cmo, "DEFAULT_ASSISTANT", "cmo_v3")

    cmo = _new_remote_cmo_with_manager(tmp_path / "context-cache-assistant.json")
    list(cmo.stream_query("Research top competitors and summarize their messaging."))

    assert context_calls["count"] == 1
    assert len(stream_payloads) == 1
    assert stream_payloads[0]["assistant_id"] == "cmo_v3"
    assert stream_payloads[0]["focus_hint"] == "research"
    assert "mode" not in stream_payloads[0]
