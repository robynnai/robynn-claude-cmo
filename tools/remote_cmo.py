import os
import json
import sys
import httpx
import re
from pathlib import Path
from typing import Optional, Dict, Any, Generator

from cmo_context import (
    AuthRequiredError,
    BrandSetupRequiredError,
    CMOContextManager,
    ContextBootstrapError,
)
from skill_router import SkillRouter
try:
    from .url_config import join_url, resolve_api_base_url, resolve_cli_base_url
except ImportError:
    from url_config import join_url, resolve_api_base_url, resolve_cli_base_url

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

DEFAULT_ASSISTANT = os.environ.get("ROBYNN_CMO_ASSISTANT", "auto").strip().lower()

# ============================================================================
# Remote CMO Execution
# ============================================================================


class RemoteCMO:
    """Handles remote execution of CMO agent tasks via Robynn API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ROBYNN_API_KEY")
        self.base_url = resolve_api_base_url()
        self.context_manager = CMOContextManager(
            api_key=self.api_key,
            cli_base_url=resolve_cli_base_url(),
        )
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
        lane = self._determine_execution_lane(message=message, focus_hint=focus_hint)
        brand_context = self._build_cached_brand_context(
            context=context,
            focus_hint=focus_hint,
            fast_text=lane["fast_text"],
        )
        brand_context_profile = self._select_brand_context_profile(
            focus_hint=focus_hint,
            fast_text=lane["fast_text"],
        )

        payload: Dict[str, Any] = {
            "message": message.strip(),
            "organization_id": organization_id,
            "focus_hint": focus_hint,
            "raw_user_prompt": message.strip(),
            "brand_context_profile": brand_context_profile,
        }
        if brand_context:
            payload["brand_context"] = brand_context
            payload["company_context"] = brand_context
            payload["brand_context_available"] = True
        if lane["fast_text"]:
            payload["mode"] = "chat"
            payload["route_hint"] = "fast"
            payload["requested_capability"] = "general"
            payload["max_turns"] = 3
        assistant = self._resolve_assistant()
        if assistant:
            payload["assistant_id"] = assistant
        return payload

    @staticmethod
    def _contains_url(text: str) -> bool:
        return "http://" in text or "https://" in text

    def _determine_execution_lane(self, message: str, focus_hint: str) -> Dict[str, Any]:
        text = (message or "").strip().lower()
        if not text:
            return {"fast_text": False, "reason": "empty_message"}

        if self._contains_url(text):
            return {"fast_text": False, "reason": "contains_url"}

        heavy_patterns = (
            r"\bresearch\b",
            r"\bcompetitor(s)?\b",
            r"\bmonitor\b",
            r"\bmentions?\b",
            r"\bknowledge base\b",
            r"\bgraphlit\b",
            r"\bingest\b",
            r"\bcrawl\b",
            r"\bspreadsheet\b",
            r"\bcsv\b",
            r"\bslide(s)?\b",
            r"\bdeck\b",
            r"\bpresentation\b",
            r"\bimage\b",
            r"\bvideo\b",
            r"\bgraphic(s)?\b",
            r"\bdesign\b",
            r"\bpdf\b",
            r"\battachment(s)?\b",
        )
        for pattern in heavy_patterns:
            if re.search(pattern, text):
                return {"fast_text": False, "reason": f"matched:{pattern}"}

        if focus_hint in {"content", "strategy", "general"}:
            return {"fast_text": True, "reason": f"focus_hint:{focus_hint}"}

        return {"fast_text": False, "reason": f"focus_hint:{focus_hint}"}

    @staticmethod
    def _select_brand_context_profile(focus_hint: str, fast_text: bool) -> str:
        if focus_hint == "content":
            return "content"
        if focus_hint in {"research", "monitoring", "knowledge"}:
            return "competitive"
        if fast_text:
            return "core"
        return "full"

    def _build_cached_brand_context(
        self,
        context: Dict[str, Any],
        focus_hint: str,
        fast_text: bool,
    ) -> str:
        identity = context.get("identity", {})
        audience = context.get("audience", {})
        voice = context.get("voice", {})
        product_knowledge = context.get("productKnowledge", {})
        terminology = context.get("terminology", {})

        lines: list[str] = []
        company_name = (
            context.get("companyName")
            or identity.get("companyName")
            or identity.get("name")
        )
        company_website = context.get("companyWebsite")
        tagline = identity.get("tagline")
        if company_name:
            lines.append("## Brand Identity")
            lines.append(f"Company: {company_name}")
            if company_website:
                lines.append(f"Website: {company_website}")
            if tagline:
                lines.append(f"Tagline: {tagline}")

        primary_audience = audience.get("primary")
        pain_points = audience.get("painPoints")
        if primary_audience:
            lines.append("")
            lines.append("## Audience")
            lines.append(str(primary_audience))
            if isinstance(pain_points, list) and pain_points:
                lines.append(f"Pain Points: {'; '.join(str(p) for p in pain_points[:4])}")

        core_attributes = voice.get("coreAttributes")
        tone_spectrum = voice.get("toneSpectrum")
        if (
            isinstance(core_attributes, list)
            and core_attributes
        ) or isinstance(tone_spectrum, dict):
            lines.append("")
            lines.append("## Voice")
            if isinstance(core_attributes, list) and core_attributes:
                lines.append(
                    f"Core Attributes: {', '.join(str(attr) for attr in core_attributes[:6])}"
                )
            if isinstance(tone_spectrum, dict):
                described_tone = ", ".join(
                    f"{key}: {value}"
                    for key, value in tone_spectrum.items()
                    if value is not None
                )
                if described_tone:
                    lines.append(f"Tone Spectrum: {described_tone}")

        if focus_hint in {"content", "strategy", "general"}:
            preferred_terms = terminology.get("preferredTerms")
            if isinstance(preferred_terms, list) and preferred_terms:
                preview_terms = []
                for term in preferred_terms[:6]:
                    if isinstance(term, dict):
                        preview_terms.append(str(term.get("term", "")).strip())
                    else:
                        preview_terms.append(str(term).strip())
                preview_terms = [term for term in preview_terms if term]
                if preview_terms:
                    lines.append("")
                    lines.append("## Terminology")
                    lines.append(f"Preferred Terms: {', '.join(preview_terms)}")

        if focus_hint in {"content", "strategy", "general"} or not fast_text:
            features = product_knowledge.get("features")
            differentiators = product_knowledge.get("differentiators")
            feature_lines: list[str] = []
            if isinstance(features, list):
                for feature in features[:4]:
                    if isinstance(feature, dict):
                        name = str(feature.get("name", "")).strip()
                        benefit = str(feature.get("benefit", "")).strip()
                        if name:
                            feature_lines.append(
                                f"- {name}: {benefit}" if benefit else f"- {name}"
                            )
            if feature_lines:
                lines.append("")
                lines.append("## Product Knowledge")
                lines.extend(feature_lines)
            if isinstance(differentiators, list) and differentiators:
                diff_lines = []
                for item in differentiators[:3]:
                    if isinstance(item, dict):
                        diff_lines.append(str(item.get("point", "")).strip())
                    else:
                        diff_lines.append(str(item).strip())
                diff_lines = [diff for diff in diff_lines if diff]
                if diff_lines:
                    if "## Product Knowledge" not in lines:
                        lines.append("")
                        lines.append("## Product Knowledge")
                    lines.append(f"Key Differentiators: {'; '.join(diff_lines)}")

        return "\n".join(line for line in lines if line).strip()

    def stream_query(
        self, message: str, refresh_context: bool = False
    ) -> Generator[Dict[str, Any], None, None]:
        """Execute a query and stream progress/results."""
        url = join_url(self.base_url, "/api/agents/cmo/stream")

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
                    raw_error_body = ""
                    try:
                        raw_error_body = response.read().decode("utf-8", errors="ignore")
                    except Exception:
                        raw_error_body = ""

                    detail = ""
                    try:
                        error_payload = json.loads(raw_error_body) if raw_error_body else {}
                        if isinstance(error_payload, dict):
                            detail = str(
                                error_payload.get("message")
                                or error_payload.get("error")
                                or ""
                            ).strip()
                    except Exception:
                        detail = raw_error_body[:300].strip()

                    suffix = f" ({detail})" if detail else ""
                    yield {
                        "type": "error",
                        "message": f"Server error: {response.status_code}{suffix}",
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
