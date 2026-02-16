"""E2E-style coverage for Claude Code CLI and Claude Desktop MCP entrypoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cmo_context
import mcp_server
import remote_cmo
from cmo_context import CMOContextManager


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


def _new_remote_cmo(cache_file: Path) -> remote_cmo.RemoteCMO:
    cmo = remote_cmo.RemoteCMO(api_key="rb_test_123")
    cmo.context_manager = CMOContextManager(
        api_key="rb_test_123",
        cli_base_url="https://robynn.ai/api/cli",
        cache_file=cache_file,
        ttl_seconds=1800,
    )
    return cmo


def test_cli_main_honors_refresh_context_flag(monkeypatch):
    captured: dict[str, Any] = {}

    class FakeRemoteCMO:
        def stream_query(self, message: str, refresh_context: bool = False):
            captured["message"] = message
            captured["refresh_context"] = refresh_context
            yield {"type": "complete", "data": {"response": "ok"}}

    monkeypatch.setattr(remote_cmo, "RemoteCMO", FakeRemoteCMO)
    monkeypatch.setattr(
        remote_cmo.sys,
        "argv",
        ["remote_cmo.py", "--refresh-context", "Draft", "launch", "positioning"],
    )

    remote_cmo.main()

    assert captured["message"] == "Draft launch positioning"
    assert captured["refresh_context"] is True


def test_desktop_mcp_query_uses_bootstrap_context_and_focus_hint(monkeypatch, tmp_path):
    context_calls = {"count": 0}
    stream_payloads: list[dict[str, Any]] = []
    context_payload = {
        "data": {
            "organizationId": "org-desktop",
            "companyName": "Desktop Co",
        }
    }

    fake_client = _build_context_client_factory([context_payload], context_calls)
    monkeypatch.setattr(cmo_context.httpx, "Client", fake_client)
    monkeypatch.setattr(remote_cmo.httpx, "stream", _build_stream_stub(stream_payloads))
    monkeypatch.setattr(remote_cmo, "DEFAULT_ASSISTANT", "auto")

    cmo = _new_remote_cmo(tmp_path / "desktop-context-cache.json")
    monkeypatch.setattr(mcp_server, "RemoteCMO", lambda: cmo)

    response = mcp_server._run_cmo_query(
        "Write a LinkedIn post announcing our new feature."
    )

    assert response == "ok"
    assert context_calls["count"] == 1
    assert len(stream_payloads) == 1
    assert stream_payloads[0]["organization_id"] == "org-desktop"
    assert stream_payloads[0]["focus_hint"] == "content"
    assert "Rory Routing Context" in stream_payloads[0]["message"]
