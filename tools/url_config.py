"""Shared URL resolution helpers for Rory plugin endpoints."""

from __future__ import annotations

import os


DEFAULT_ROBYNN_API_BASE_URL = "https://robynn.ai"


def _clean_base_url(value: str) -> str:
    return value.strip().rstrip("/")


def resolve_api_base_url() -> str:
    """
    Resolve base URL for app endpoints (e.g. /api/agents/cmo/stream).

    If ROBYNN_API_BASE_URL is accidentally provided as a CLI URL ending in
    /api/cli, normalize it back to the app base to avoid double-path bugs.
    """
    raw = os.environ.get("ROBYNN_API_BASE_URL")
    if not raw or not raw.strip():
        return DEFAULT_ROBYNN_API_BASE_URL

    normalized = _clean_base_url(raw)
    if normalized.endswith("/api/cli"):
        normalized = normalized[: -len("/api/cli")]
    return normalized


def resolve_cli_base_url() -> str:
    """
    Resolve base URL for CLI endpoints (e.g. /context, /usage, /execute).

    Priority:
    1) ROBYNN_CLI_BASE_URL (explicit)
    2) derived from ROBYNN_API_BASE_URL + /api/cli
    """
    raw_cli = os.environ.get("ROBYNN_CLI_BASE_URL")
    if raw_cli and raw_cli.strip():
        cli_base = _clean_base_url(raw_cli)
        if cli_base.endswith("/api/cli"):
            return cli_base
        return f"{cli_base}/api/cli"

    return f"{resolve_api_base_url()}/api/cli"


def join_url(base_url: str, path: str) -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url.rstrip('/')}{normalized_path}"
