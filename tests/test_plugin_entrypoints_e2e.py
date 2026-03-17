"""E2E-style coverage for Claude Code CLI and Claude Desktop MCP entrypoints."""

from __future__ import annotations

from typing import Any

import mcp_server
import remote_cmo


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


def test_desktop_mcp_query_uses_session_client(monkeypatch):
    captured: dict[str, Any] = {}

    class FakeClient:
        def run(self, agent: str, *, input_text=None, params=None):
            captured["agent"] = agent
            captured["input_text"] = input_text
            captured["params"] = params
            return {"data": {"output": "ok"}}

    monkeypatch.setattr(mcp_server, "_get_client", lambda: FakeClient())

    response = mcp_server._run_cmo_query(
        "Write a LinkedIn post announcing our new feature."
    )

    assert response == "ok"
    assert captured["agent"] == "cmo"
    assert captured["input_text"] == "Write a LinkedIn post announcing our new feature."
    assert captured["params"] is None
