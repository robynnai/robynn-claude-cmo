#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from session_client import RobynnSessionClient, SessionClientError


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2))


def _load_params(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SessionClientError(f"Invalid JSON for --params: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SessionClientError("--params must decode to a JSON object")
    return parsed


def _prompt_api_key() -> str:
    api_key = input("Robynn API key: ").strip()
    if not api_key:
        raise SessionClientError("API key is required")
    return api_key


def _format_auth_status(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"API key stored: {'yes' if payload.get('has_api_key') else 'no'}",
            f"Active org: {payload.get('selected_org_name') or payload.get('selected_org_id') or 'none'}",
            f"Session token: {'yes' if payload.get('has_access_token') else 'no'}",
            f"Refresh token: {'yes' if payload.get('has_refresh_token') else 'no'}",
            f"Credential storage: {payload.get('storage', 'unknown')}",
        ]
    )


def _format_status(payload: dict[str, Any]) -> str:
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    active_org = data.get("active_organization", {}) if isinstance(data, dict) else {}
    organizations = data.get("organizations", []) if isinstance(data, dict) else []
    lines = [
        "Robynn CLI connected",
        f"Active org: {active_org.get('name') or active_org.get('id') or 'unknown'}",
        f"User ID: {data.get('user_id', 'unknown')}",
        f"Token balance: {data.get('token_balance', 'unknown')}",
        f"Can execute: {'yes' if data.get('can_execute') else 'no'}",
        f"Available orgs: {len(organizations) if isinstance(organizations, list) else 0}",
    ]
    return "\n".join(lines)


def _format_usage(payload: dict[str, Any]) -> str:
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    return "\n".join(
        [
            f"Billing model: {data.get('billing_model', 'unknown')}",
            f"Token balance: {data.get('token_balance', 'unknown')}",
            f"Can execute: {'yes' if data.get('can_execute') else 'no'}",
        ]
    )


def _format_orgs(payload: dict[str, Any]) -> str:
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    active_org_id = data.get("active_organization_id")
    orgs = data.get("organizations", []) if isinstance(data, dict) else []
    lines = []
    for org in orgs if isinstance(orgs, list) else []:
        marker = "*" if org.get("id") == active_org_id else "-"
        lines.append(f"{marker} {org.get('id')}: {org.get('name')}")
    return "\n".join(lines) if lines else "No organizations available."


def _format_context(payload: dict[str, Any]) -> str:
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    return json.dumps(data, indent=2)


def _format_run(payload: dict[str, Any]) -> str:
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    output = data.get("output")
    if isinstance(output, str) and output.strip():
        return output
    return json.dumps(data, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Robynn agent CLI")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser("auth")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command", required=True)
    login_parser = auth_subparsers.add_parser("login")
    login_parser.add_argument("api_key", nargs="?", help="User API key")
    auth_subparsers.add_parser("status")
    auth_subparsers.add_parser("logout")

    org_parser = subparsers.add_parser("org")
    org_subparsers = org_parser.add_subparsers(dest="org_command", required=True)
    org_subparsers.add_parser("list")
    use_parser = org_subparsers.add_parser("use")
    use_parser.add_argument("organization_id")

    subparsers.add_parser("status")
    subparsers.add_parser("usage")

    context_parser = subparsers.add_parser("context")
    context_subparsers = context_parser.add_subparsers(dest="context_command", required=True)
    context_get_parser = context_subparsers.add_parser("get")
    context_get_parser.add_argument("--scope", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("agent")
    run_parser.add_argument("--input")
    run_parser.add_argument("--params", help="JSON object for structured agent params")

    mcp_parser = subparsers.add_parser("mcp")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", required=True)
    mcp_serve_parser = mcp_subparsers.add_parser("serve")
    mcp_serve_parser.add_argument("--toolset", choices=["minimal", "full"], default="minimal")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    client = RobynnSessionClient()

    try:
        if args.command == "auth":
            if args.auth_command == "login":
                api_key = args.api_key or _prompt_api_key()
                payload = client.auth_login(api_key)
                if args.json:
                    _print_json(payload)
                else:
                    orgs = payload.get("data", {}).get("organizations", [])
                    print("Stored your Robynn API key.")
                    if isinstance(orgs, list) and orgs:
                        print("Select an org with:")
                        for org in orgs:
                            print(f"  robynn org use {org.get('id')}  # {org.get('name')}")
                    else:
                        print("No organizations were returned for this account.")
                return 0

            if args.auth_command == "status":
                payload = client.auth_status()
                if args.json:
                    _print_json(payload)
                else:
                    print(_format_auth_status(payload))
                return 0

            if args.auth_command == "logout":
                client.logout()
                if args.json:
                    _print_json({"success": True})
                else:
                    print("Logged out of Robynn CLI.")
                return 0

        if args.command == "org":
            if args.org_command == "list":
                payload = client.list_orgs()
                if args.json:
                    _print_json(payload)
                else:
                    print(_format_orgs(payload))
                return 0

            if args.org_command == "use":
                payload = client.use_org(args.organization_id)
                if args.json:
                    _print_json(payload)
                else:
                    active = payload.get("data", {}).get("active_organization", {})
                    print(
                        f"Active org set to {active.get('name') or active.get('id') or args.organization_id}."
                    )
                return 0

        if args.command == "status":
            payload = client.status()
            if args.json:
                _print_json(payload)
            else:
                print(_format_status(payload))
            return 0

        if args.command == "usage":
            payload = client.usage()
            if args.json:
                _print_json(payload)
            else:
                print(_format_usage(payload))
            return 0

        if args.command == "context" and args.context_command == "get":
            payload = client.context_get(args.scope)
            if args.json:
                _print_json(payload)
            else:
                print(_format_context(payload))
            return 0

        if args.command == "run":
            params = _load_params(args.params)
            payload = client.run(args.agent, input_text=args.input, params=params)
            if args.json:
                _print_json(payload)
            else:
                print(_format_run(payload))
            return 0

        if args.command == "mcp" and args.mcp_command == "serve":
            env = os.environ.copy()
            env["ROBYNN_MCP_TOOLSET"] = args.toolset
            return subprocess.call(
                [sys.executable, str(Path(__file__).resolve().parent / "mcp_server.py")],
                env=env,
            )

    except SessionClientError as exc:
        if args.json:
            _print_json({"success": False, "error": str(exc)})
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
