from __future__ import annotations

import base64
import json
import time
from typing import Any, Optional

import httpx

try:
    from .session_store import SessionStore
    from .url_config import join_url, resolve_cli_base_url
except ImportError:
    from session_store import SessionStore
    from url_config import join_url, resolve_cli_base_url


class SessionClientError(RuntimeError):
    """Raised when the Robynn CLI session workflow fails."""


class RobynnSessionClient:
    """Thin client for Robynn CLI auth, org selection, and agent execution."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        store: Optional[SessionStore] = None,
    ):
        self.base_url = (base_url or resolve_cli_base_url()).rstrip("/")
        self.store = store or SessionStore()

    def auth_login(self, api_key: str) -> dict[str, Any]:
        payload = self._post(
            "/auth/exchange",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json_payload={},
        )

        state = self.store.load()
        state.update(
            {
                "api_key": api_key,
                "organizations": payload.get("data", {}).get("organizations", []),
                "selected_org_id": None,
                "selected_org_name": None,
                "access_token": None,
                "refresh_token": None,
                "access_token_expires_at": None,
            }
        )
        self.store.save(state)
        return payload

    def auth_status(self) -> dict[str, Any]:
        state = self.store.load()
        return {
            "has_api_key": bool(state.get("api_key")),
            "selected_org_id": state.get("selected_org_id"),
            "selected_org_name": state.get("selected_org_name"),
            "has_access_token": bool(state.get("access_token")),
            "has_refresh_token": bool(state.get("refresh_token")),
            "access_token_expires_at": state.get("access_token_expires_at"),
            "storage": "keyring" if self._using_keyring() else "file",
        }

    def logout(self) -> None:
        state = self.store.load()
        refresh_token = state.get("refresh_token")
        if isinstance(refresh_token, str) and refresh_token:
            try:
                self._post(
                    "/auth/logout",
                    headers={"Content-Type": "application/json"},
                    json_payload={"refresh_token": refresh_token},
                )
            except Exception:
                pass
        self.store.clear()

    def list_orgs(self) -> dict[str, Any]:
        headers = self._resolve_auth_headers(prefer_session=True)
        payload = self._get("/orgs", headers=headers)

        state = self.store.load()
        organizations = payload.get("data", {}).get("organizations", [])
        if isinstance(organizations, list):
            state["organizations"] = organizations
            self.store.save(state)
        return payload

    def use_org(self, organization_id: str) -> dict[str, Any]:
        state = self.store.load()
        api_key = state.get("api_key")
        if not isinstance(api_key, str) or not api_key:
            raise SessionClientError(
                "No API key stored. Run `robynn auth login` first."
            )

        payload = self._post(
            "/auth/exchange",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json_payload={"organization_id": organization_id},
        )

        self._save_session_payload(payload, api_key=api_key)
        return payload

    def status(self) -> dict[str, Any]:
        return self._authed_get("/status")

    def usage(self) -> dict[str, Any]:
        return self._authed_get("/usage")

    def context_get(self, scope: str) -> dict[str, Any]:
        return self._authed_get(f"/context/{scope}")

    def run(
        self,
        agent: str,
        *,
        input_text: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if input_text:
            payload["input"] = input_text
        if params:
            payload["params"] = params
        return self._authed_post(f"/agents/{agent}/execute", payload)

    def _authed_get(self, path: str) -> dict[str, Any]:
        return self._request_with_refresh("GET", path)

    def _authed_post(self, path: str, json_payload: dict[str, Any]) -> dict[str, Any]:
        return self._request_with_refresh("POST", path, json_payload=json_payload)

    def _request_with_refresh(
        self,
        method: str,
        path: str,
        json_payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        headers = self._resolve_auth_headers(prefer_session=True)

        try:
            return self._request(method, path, headers=headers, json_payload=json_payload)
        except SessionClientError as exc:
            if "401" not in str(exc):
                raise
            self._refresh_session()
            headers = self._resolve_auth_headers(prefer_session=True)
            return self._request(method, path, headers=headers, json_payload=json_payload)

    def _refresh_session(self) -> None:
        state = self.store.load()
        refresh_token = state.get("refresh_token")
        api_key = state.get("api_key")
        if not isinstance(refresh_token, str) or not refresh_token:
            raise SessionClientError(
                "Session expired and no refresh token is available. Run `robynn auth login` again."
            )

        payload = self._post(
            "/auth/refresh",
            headers={"Content-Type": "application/json"},
            json_payload={"refresh_token": refresh_token},
        )
        self._save_session_payload(
            payload,
            api_key=api_key if isinstance(api_key, str) else None,
        )

    def _save_session_payload(
        self,
        payload: dict[str, Any],
        api_key: Optional[str],
    ) -> None:
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        if not isinstance(data, dict):
            raise SessionClientError("Invalid session response from Robynn")

        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        active_org = data.get("active_organization")

        if not isinstance(access_token, str) or not isinstance(refresh_token, str):
            raise SessionClientError(
                "Robynn session response did not include credentials"
            )

        expires_at = time.time() + int(data.get("expires_in", 0) or 0)
        if expires_at <= time.time():
            jwt_expiry = self._jwt_expiry(access_token)
            if jwt_expiry:
                expires_at = jwt_expiry

        state = self.store.load()
        if api_key:
            state["api_key"] = api_key
        state.update(
            {
                "organizations": data.get(
                    "organizations",
                    state.get("organizations", []),
                ),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "access_token_expires_at": expires_at,
                "selected_org_id": active_org.get("id")
                if isinstance(active_org, dict)
                else None,
                "selected_org_name": active_org.get("name")
                if isinstance(active_org, dict)
                else None,
            }
        )
        self.store.save(state)

    def _resolve_auth_headers(self, prefer_session: bool = True) -> dict[str, str]:
        state = self.store.load()
        if prefer_session:
            access_token = state.get("access_token")
            expires_at = state.get("access_token_expires_at")
            if (
                isinstance(access_token, str)
                and access_token
                and isinstance(expires_at, (int, float))
                and expires_at > time.time() + 30
            ):
                return {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }
            if isinstance(state.get("refresh_token"), str) and state.get("refresh_token"):
                self._refresh_session()
                return self._resolve_auth_headers(prefer_session=True)

        api_key = state.get("api_key")
        if isinstance(api_key, str) and api_key:
            return {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

        raise SessionClientError(
            "Not authenticated. Run `robynn auth login` first."
        )

    def _get(self, path: str, headers: dict[str, str]) -> dict[str, Any]:
        return self._request("GET", path, headers=headers)

    def _post(
        self,
        path: str,
        *,
        headers: dict[str, str],
        json_payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request("POST", path, headers=headers, json_payload=json_payload)

    def _request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str],
        json_payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        url = join_url(self.base_url, path)
        with httpx.Client(timeout=60.0) as client:
            response = client.request(
                method,
                url,
                headers=headers,
                json=json_payload,
            )

        try:
            payload = response.json()
        except Exception:
            payload = None

        if response.status_code >= 400:
            detail = "Request failed"
            if isinstance(payload, dict):
                detail = str(payload.get("error") or payload.get("message") or detail)
            elif response.text.strip():
                detail = response.text.strip()
            raise SessionClientError(f"{detail} (HTTP {response.status_code})")

        if not isinstance(payload, dict):
            raise SessionClientError("Unexpected response format from Robynn")
        return payload

    @staticmethod
    def _jwt_expiry(token: str) -> Optional[float]:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        try:
            body = parts[1]
            padding = "=" * (-len(body) % 4)
            payload = json.loads(
                base64.urlsafe_b64decode(body + padding).decode("utf-8")
            )
            exp = payload.get("exp")
            if isinstance(exp, (int, float)):
                return float(exp)
        except Exception:
            return None
        return None

    def _using_keyring(self) -> bool:
        state_path = getattr(self.store, "path", None)
        return state_path is None or not state_path.exists()
