"""Strict auth + org-context bootstrap with local caching for Rory plugin."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx


ROBYNN_CLI_BASE_URL = os.environ.get("ROBYNN_API_BASE_URL", "https://robynn.ai/api/cli")
CACHE_FILE_NAME = ".rory_context_cache.json"
DEFAULT_CACHE_TTL_SECONDS = int(os.environ.get("ROBYNN_CONTEXT_CACHE_TTL_SECONDS", "1800"))


class ContextBootstrapError(RuntimeError):
    """Raised when Rory cannot bootstrap org context."""


class AuthRequiredError(ContextBootstrapError):
    """Raised when API key is missing/invalid."""


class BrandSetupRequiredError(ContextBootstrapError):
    """Raised when org exists but brand setup is incomplete."""


class CMOContextManager:
    """Fetches and caches `/api/cli/context` for strict org-scoped execution."""

    def __init__(
        self,
        api_key: str | None = None,
        cli_base_url: str | None = None,
        cache_file: str | Path | None = None,
        ttl_seconds: int | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("ROBYNN_API_KEY")
        self.cli_base_url = (cli_base_url or ROBYNN_CLI_BASE_URL).rstrip("/")
        self.cache_file = (
            Path(cache_file)
            if cache_file is not None
            else Path(__file__).resolve().parent.parent / CACHE_FILE_NAME
        )
        self.ttl_seconds = max(60, ttl_seconds or DEFAULT_CACHE_TTL_SECONDS)

    def get_context(self, refresh: bool = False) -> dict[str, Any]:
        """Return org context, preferring cache when valid."""
        if not self.api_key:
            raise AuthRequiredError(
                "Not connected to Robynn.\n\n"
                "Run `rory init` to connect your account, or `rory config <your_api_key>`."
            )

        now = int(time.time())
        key_fingerprint = self._fingerprint(self.api_key)

        if not refresh:
            cached = self._load_cache()
            if self._is_cache_valid(cached, key_fingerprint, now):
                context = cached["context"]
                self._assert_brand_context_ready(context)
                return context

        context = self._fetch_context_from_api()
        normalized = self._normalize_context(context)
        self._assert_brand_context_ready(normalized)
        self._save_cache(
            context=normalized,
            key_fingerprint=key_fingerprint,
            now=now,
        )
        return normalized

    def invalidate_cache(self) -> None:
        """Remove local context cache if present."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except Exception:
            # Non-fatal best effort
            pass

    def _fetch_context_from_api(self) -> dict[str, Any]:
        url = f"{self.cli_base_url}/context"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            with httpx.Client(headers=headers, timeout=30.0) as client:
                response = client.get(url)
        except Exception as exc:
            raise ContextBootstrapError(
                f"Unable to reach Robynn context API: {exc}"
            ) from exc

        if response.status_code in (401, 403):
            raise AuthRequiredError(
                "Authentication failed for Robynn API key.\n\n"
                "Run `rory init` or update your key via `rory config <your_api_key>`."
            )

        if response.status_code != 200:
            raise ContextBootstrapError(
                f"Context bootstrap failed with status {response.status_code}."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise ContextBootstrapError("Context API returned invalid JSON.") from exc

        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            raise ContextBootstrapError("Context API response missing `data` object.")
        return data

    def _normalize_context(self, data: dict[str, Any]) -> dict[str, Any]:
        context = dict(data)
        organization_id = context.get("organizationId") or context.get("organization_id")
        if not organization_id:
            raise ContextBootstrapError(
                "Context bootstrap succeeded but organization ID was missing."
            )
        context["organizationId"] = organization_id
        return context

    def _assert_brand_context_ready(self, context: dict[str, Any]) -> None:
        if context.get("status") == "pending_setup":
            raise BrandSetupRequiredError(
                "Brand setup is incomplete for your organization.\n\n"
                "Complete Brand Hub setup in Robynn, then retry:\n"
                "1. Open https://robynn.ai/dashboard\n"
                "2. Go to Settings -> Brand Hub\n"
                "3. Add company, product, and voice details"
            )

    def _load_cache(self) -> dict[str, Any] | None:
        if not self.cache_file.exists():
            return None

        try:
            raw = self.cache_file.read_text()
            payload = json.loads(raw)
            if isinstance(payload, dict):
                return payload
        except Exception:
            return None
        return None

    def _save_cache(self, context: dict[str, Any], key_fingerprint: str, now: int) -> None:
        payload = {
            "version": 1,
            "cached_at": now,
            "expires_at": now + self.ttl_seconds,
            "key_fingerprint": key_fingerprint,
            "context": context,
        }
        try:
            self.cache_file.write_text(json.dumps(payload))
        except Exception:
            # Cache write failure is non-fatal for request execution.
            pass

    @staticmethod
    def _is_cache_valid(
        cached: dict[str, Any] | None,
        key_fingerprint: str,
        now: int,
    ) -> bool:
        if not isinstance(cached, dict):
            return False
        if cached.get("key_fingerprint") != key_fingerprint:
            return False
        expires_at = cached.get("expires_at")
        context = cached.get("context")
        if not isinstance(expires_at, int) or not isinstance(context, dict):
            return False
        return expires_at > now

    @staticmethod
    def _fingerprint(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

