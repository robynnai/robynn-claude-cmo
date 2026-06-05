from __future__ import annotations

import robynn
from robynn import _resolve_run_input, build_parser


def test_run_accepts_trailing_prompt_text():
    parser = build_parser()
    args = parser.parse_args(["run", "cmo", "Write", "a", "launch", "post"])

    assert args.agent == "cmo"
    assert _resolve_run_input(args) == "Write a launch post"


def test_login_alias_accepts_api_key_argument():
    parser = build_parser()
    args = parser.parse_args(["login", "rb_test_123"])

    assert args.command == "login"
    assert args.api_key == "rb_test_123"


def test_website_audit_v2_alias_calls_structured_agent(monkeypatch, capsys):
    calls = []

    class FakeClient:
        def run(self, agent, input_text=None, params=None):
            calls.append({"agent": agent, "input_text": input_text, "params": params})
            return {"data": {"output": "Started Website Auto-Healer v2 audit."}}

    monkeypatch.setattr("robynn.RobynnSessionClient", lambda: FakeClient())

    exit_code = robynn.main(
        [
            "website",
            "audit-v2",
            "--params",
            '{"website_url":"https://example.com"}',
        ]
    )

    assert exit_code == 0
    assert calls == [
        {
            "agent": "website-audit-v2",
            "input_text": None,
            "params": {"website_url": "https://example.com"},
        }
    ]
    assert "Started Website Auto-Healer v2 audit." in capsys.readouterr().out
