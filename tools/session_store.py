from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

try:
    import keyring  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    keyring = None


SERVICE_NAME = "robynn-cli"
SESSION_USERNAME = "default"
FALLBACK_STATE_PATH = Path.home() / ".config" / "robynn" / "session.json"


class SessionStore:
    """Store Robynn CLI session state in keyring when available, else a local file."""

    def __init__(self, path: Optional[Path] = None):
        self.path = path or FALLBACK_STATE_PATH

    def load(self) -> dict[str, Any]:
        raw = self._read_raw()
        if not raw:
            return {}
        try:
            payload = json.loads(raw)
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def save(self, state: dict[str, Any]) -> None:
        serialized = json.dumps(state)
        self._write_raw(serialized)

    def clear(self) -> None:
        if keyring is not None:
            try:
                keyring.delete_password(SERVICE_NAME, SESSION_USERNAME)
                return
            except Exception:
                pass

        try:
            if self.path.exists():
                self.path.unlink()
        except Exception:
            pass

    def _read_raw(self) -> Optional[str]:
        if keyring is not None:
            try:
                return keyring.get_password(SERVICE_NAME, SESSION_USERNAME)
            except Exception:
                pass

        try:
            if self.path.exists():
                return self.path.read_text()
        except Exception:
            return None
        return None

    def _write_raw(self, raw: str) -> None:
        if keyring is not None:
            try:
                keyring.set_password(SERVICE_NAME, SESSION_USERNAME, raw)
                return
            except Exception:
                pass

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(raw)
        os.chmod(self.path, 0o600)
