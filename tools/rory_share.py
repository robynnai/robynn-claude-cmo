import argparse
import json
import os
import sys
import httpx
from pathlib import Path
from typing import Any, Dict, Optional


ROBYNN_API_BASE_URL = os.environ.get("ROBYNN_API_BASE_URL", "https://robynn.ai")


def _load_env_file() -> None:
    """Load environment variables from .env without overwriting existing values."""
    current = Path(__file__).parent.parent
    env_file = current / ".env"

    if not env_file.exists():
        return

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"").strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _validate_api_key() -> Optional[str]:
    _load_env_file()
    return os.environ.get("ROBYNN_API_KEY")


def _to_int_or_default(raw: Optional[str], default: int) -> int:
    if raw is None:
        return default

    raw_value = raw.strip().lower()
    if raw_value.endswith("h"):
        raw_value = raw_value[:-1]

    value = int(raw_value)
    if value < 1 or value > 168:
        raise ValueError("TTL must be between 1 and 168 hours")
    return value


def _normalize_title(title: Optional[str], file_path: str) -> str:
    if title:
        normalized = title.strip()
        if normalized:
            return normalized
    return Path(file_path).stem or "Shared HTML"


def _read_html(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".html":
        raise ValueError("Only .html files are supported")
    return path.read_text(encoding="utf-8")


def _post_rory_action(params: Dict[str, Any]) -> Dict[str, Any]:
    api_key = _validate_api_key()
    if not api_key:
        raise RuntimeError("Not connected. Run: rory init or rory config <api_key>")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = f"{ROBYNN_API_BASE_URL}/api/cli/execute"

    payload = {"agentId": "rory", "params": params}
    with httpx.Client(headers=headers, timeout=120.0) as client:
        response = client.post(url, json=payload)
        try:
            response_data = response.json()
        except ValueError:
            response_data = None

        if response.status_code >= 400 or (
            isinstance(response_data, dict) and response_data.get("success") is False
        ):
            error_message = (
                response_data.get("error")
                if isinstance(response_data, dict)
                else response.text
            )
            if not error_message:
                error_message = f"Request failed with status {response.status_code}"
            raise RuntimeError(error_message)

        if not isinstance(response_data, dict):
            raise RuntimeError("Unexpected response format from Rory share API")

        return response_data


def _print_share_result(payload: Dict[str, Any], is_json: bool) -> None:
    if is_json:
        print(json.dumps(payload, indent=2, default=str))
        return

    public_url = payload.get("publicUrl")
    state = payload.get("state")
    expires_at = payload.get("expiresAt")
    share_id = payload.get("shareId")

    if public_url:
        print(f"✅ Share created: {public_url}")
        if state:
            print(f"State: {state}")
        if expires_at:
            print(f"Expires: {expires_at}")
        if share_id:
            print(f"Share ID: {share_id}")
    else:
        print(json.dumps(payload, indent=2, default=str))


def _print_error(message: str, is_json: bool) -> None:
    if is_json:
        print(json.dumps({"success": False, "error": message}, indent=2))
    else:
        print(f"❌ {message}")


def _print_list_shares(response: Dict[str, Any], is_json: bool) -> None:
    shares = response.get("shares", response.get("data", {}).get("shares", []))
    if is_json:
        print(json.dumps({"success": True, "shares": shares}, indent=2, default=str))
        return

    if not shares:
        print("No shares found.")
        return

    print("Rory share links:")
    for share in shares:
        slug = share.get("slug")
        state = share.get("state")
        title = share.get("title", "")
        expires_at = share.get("expiresAt", "")
        public_url = share.get("publicUrl", "")
        print(f"- {title or 'Shared HTML'} [{state}]")
        print(f"  ID: {share.get('shareId')}")
        if public_url:
            print(f"  URL: {public_url}")
        if expires_at:
            print(f"  Expires: {expires_at}")


def _print_revoke_result(response: Dict[str, Any], is_json: bool) -> None:
    if is_json:
        print(json.dumps(response, indent=2, default=str))
        return
    success = response.get("success", False)
    if success:
        share_id = response.get("shareId") or response.get("data", {}).get("shareId")
        print(f"✅ Share revoked: {share_id}")
    else:
        error = response.get("error", "Revoke failed")
        print(f"❌ {error}")


def handle_share_command(argv: list[str]) -> None:
    if not argv:
        print(
            "Usage:\n"
            "  rory share <path/to/file.html> [--title TITLE] [--ttl 24] [--slug slug]\n"
            "  rory share list\n"
            "  rory share revoke <shareId>"
        )
        return

    command = argv[0].strip().lower()
    json_output = "--json" in argv
    args = [arg for arg in argv if arg != "--json"]

    if command == "list":
        try:
            response = _post_rory_action({"action": "list_shares"})
            _print_list_shares(response, json_output)
        except RuntimeError as exc:
            _print_error(str(exc), json_output)
        return

    if command == "revoke":
        if len(args) < 2:
            print("Usage: rory share revoke <shareId>")
            return
        share_id = args[1]
        try:
            response = _post_rory_action(
                {
                    "action": "revoke_share",
                    "shareId": share_id,
                },
            )
            _print_revoke_result(response, json_output)
        except RuntimeError as exc:
            _print_error(str(exc), json_output)
        return

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("file", help="Path to local HTML file")
    parser.add_argument("--title", default=None)
    parser.add_argument("--ttl", default="24")
    parser.add_argument("--slug", default=None)
    parser.add_argument("--json", action="store_true", default=False)
    parsed = parser.parse_args(args)

    try:
        html = _read_html(parsed.file)
        ttl_hours = _to_int_or_default(parsed.ttl, 24)
        title = _normalize_title(parsed.title, parsed.file)
        params = {
            "action": "share",
            "title": title,
            "sourceFilename": Path(parsed.file).name,
            "html": html,
            "ttlHours": ttl_hours,
        }
        if parsed.slug:
            params["slug"] = parsed.slug

        response = _post_rory_action(params)
        _print_share_result(response, parsed.json or json_output)
    except (RuntimeError, OSError, ValueError) as exc:
        _print_error(str(exc), parsed.json or json_output)


if __name__ == "__main__":
    handle_share_command(sys.argv[1:])
