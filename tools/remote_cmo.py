import os
import json
import sys
import httpx
from pathlib import Path
from typing import Optional, Dict, Any, Generator

from cmo_context import (
    AuthRequiredError,
    BrandSetupRequiredError,
    CMOContextManager,
    ContextBootstrapError,
)
from skill_router import SkillRouter

# ============================================================================
# Configuration
# ============================================================================

def load_env_file():
    """Load environment variables from .env file if it exists."""
    # Look for .env in current directory and parent directories
    current = Path(__file__).parent.parent  # Start from tools/../ (project root)
    env_file = current / ".env"

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:  # Don't override existing env vars
                        os.environ[key] = value

# Load .env file on import
load_env_file()

ROBYNN_API_BASE_URL = os.environ.get("ROBYNN_API_BASE_URL", "https://robynn.ai")
DEFAULT_ASSISTANT = os.environ.get("ROBYNN_CMO_ASSISTANT", "auto").strip().lower()

# ============================================================================
# Remote CMO Execution
# ============================================================================


class RemoteCMO:
    """Handles remote execution of CMO agent tasks via Robynn API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ROBYNN_API_KEY")
        self.base_url = ROBYNN_API_BASE_URL
        self.context_manager = CMOContextManager(api_key=self.api_key)
        self.router = SkillRouter()

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @staticmethod
    def _resolve_assistant() -> Optional[str]:
        if DEFAULT_ASSISTANT in {"cmo_v2", "cmo_v3"}:
            return DEFAULT_ASSISTANT
        return None

    def _build_payload(self, message: str, refresh_context: bool) -> Dict[str, Any]:
        context = self.context_manager.get_context(refresh=refresh_context)
        organization_id = context.get("organizationId")
        if not organization_id:
            raise ContextBootstrapError("Organization ID missing from context bootstrap.")

        focus_hint = self.router.route(message)
        routed_message = self.router.build_prompt(
            message=message,
            focus_hint=focus_hint,
            organization_id=organization_id,
        )

        payload: Dict[str, Any] = {
            "message": routed_message,
            "organization_id": organization_id,
            "focus_hint": focus_hint,
        }
        assistant = self._resolve_assistant()
        if assistant:
            payload["assistant_id"] = assistant
        return payload

    def stream_query(
        self, message: str, refresh_context: bool = False
    ) -> Generator[Dict[str, Any], None, None]:
        """Execute a query and stream progress/results."""
        url = f"{self.base_url}/api/agents/cmo/stream"

        try:
            payload = self._build_payload(message=message, refresh_context=refresh_context)
        except (AuthRequiredError, BrandSetupRequiredError, ContextBootstrapError) as exc:
            yield {"type": "error", "message": str(exc)}
            return

        try:
            with httpx.stream(
                "POST",
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=600.0,
            ) as response:
                if response.status_code == 401:
                    yield {
                        "type": "error",
                        "message": "Not connected to Robynn.\n\n"
                        "Quick fix: Run 'rory init' to set up your account.\n"
                        "Or if you already have a key: 'rory config <your_key>'",
                    }
                    return
                elif response.status_code != 200:
                    yield {
                        "type": "error",
                        "message": f"Server error: {response.status_code}",
                    }
                    return

                buffer = ""
                for chunk in response.iter_text():
                    buffer += chunk
                    while "\n\n" in buffer:
                        event_block, buffer = buffer.split("\n\n", 1)
                        event_data = self._parse_event(event_block)
                        if event_data:
                            yield event_data
        except Exception as e:
            yield {"type": "error", "message": f"Connection error: {str(e)}"}

    def _parse_event(self, block: str) -> Optional[Dict[str, Any]]:
        """Parse an SSE event block."""
        lines = block.strip().split("\n")
        event_type = "message"
        data_str = ""

        for line in lines:
            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data_str += line[5:].strip()

        if not data_str:
            return None

        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            # Fallback for non-JSON data
            return {"type": event_type, "message": data_str}


def main():
    """CLI entry point for remote execution."""
    if len(sys.argv) < 2:
        print("Usage: rory \"your query\"")
        sys.exit(1)

    args = sys.argv[1:]
    refresh_context = False
    if "--refresh-context" in args:
        args = [arg for arg in args if arg != "--refresh-context"]
        refresh_context = True

    query = " ".join(args).strip()
    if not query:
        print("Usage: rory \"your query\"")
        sys.exit(1)

    cmo = RemoteCMO()

    print(f"\n⠋ Rory is thinking about: {query[:50]}...")

    for event in cmo.stream_query(query, refresh_context=refresh_context):
        etype = event.get("type")
        msg = event.get("message")

        if etype == "status":
            print(f"  → {msg}")
        elif etype == "progress":
            print(f"  ⚙️  {msg}")
        elif etype == "complete":
            print("\n" + "=" * 80)
            data = event.get("data", {})
            print(data.get("response", "Done."))
            print("=" * 80)

            # Display usage if available (can be in data.usage or data.metadata.usage)
            metadata = data.get("metadata", {})
            usage = metadata.get("usage") or data.get("usage")
            if usage:
                remaining = usage.get("tasks_remaining", usage.get("remaining"))
                limit = usage.get("tasks_limit", usage.get("limit"))
                tier = usage.get("tier", "")
                unit = usage.get("unit") or (
                    "day" if tier in {"pro", "anonymous"} else "month"
                )
                if remaining is not None and limit is not None:
                    print(
                        f"✓ {remaining} of {limit} tasks remaining this {unit}. (Tier: {tier})"
                    )

            print("✓ Task complete. Sounds like you.")
            print()
        elif etype == "error":
            print(f"\n❌ Error: {msg}")


if __name__ == "__main__":
    main()
