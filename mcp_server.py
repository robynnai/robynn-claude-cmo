import json
import logging
import os
import sys
from typing import Any, Optional

from fastmcp import FastMCP

TOOLS_DIR = os.path.join(os.path.dirname(__file__), "tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from session_client import RobynnSessionClient, SessionClientError

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

DEFAULT_TOOLSET = os.environ.get("ROBYNN_MCP_TOOLSET", "minimal").strip().lower()
if DEFAULT_TOOLSET not in {"minimal", "full"}:
    DEFAULT_TOOLSET = "minimal"

mcp = FastMCP("Robynn AI")


def _get_client() -> RobynnSessionClient:
    return RobynnSessionClient()


def _format_error(exc: Exception) -> str:
    if isinstance(exc, SessionClientError):
        return str(exc)
    return f"Unexpected error: {exc}"


def _run_agent(
    agent: str,
    *,
    input_text: Optional[str] = None,
    params: Optional[dict[str, Any]] = None,
) -> str:
    try:
        payload = _get_client().run(agent, input_text=input_text, params=params)
    except Exception as exc:
        return f"Error: {_format_error(exc)}"

    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    output = data.get("output") if isinstance(data, dict) else None
    if isinstance(output, str) and output.strip():
        return output
    return json.dumps(payload, indent=2)


def _status_text() -> str:
    try:
        payload = _get_client().status()
    except Exception as exc:
        return f"Error: {_format_error(exc)}"

    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    active_org = data.get("active_organization", {}) if isinstance(data, dict) else {}
    return (
        "Robynn CLI connected\n"
        f"Active org: {active_org.get('name') or active_org.get('id') or 'unknown'}\n"
        f"User ID: {data.get('user_id', 'unknown')}\n"
        f"Token balance: {data.get('token_balance', 'unknown')}\n"
        f"Can execute: {'yes' if data.get('can_execute') else 'no'}"
    )


def _usage_text() -> str:
    try:
        payload = _get_client().usage()
    except Exception as exc:
        return f"Error: {_format_error(exc)}"

    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    return (
        f"Billing model: {data.get('billing_model', 'unknown')}\n"
        f"Token balance: {data.get('token_balance', 'unknown')}\n"
        f"Can execute: {'yes' if data.get('can_execute') else 'no'}"
    )


def _context_text(scope: str) -> str:
    try:
        payload = _get_client().context_get(scope)
    except Exception as exc:
        return f"Error: {_format_error(exc)}"
    return json.dumps(payload.get("data", {}), indent=2)


def _register_tools(toolset: str) -> None:
    mcp.tool(
        name="robynn_run",
        annotations={"openWorldHint": True},
    )(robynn_run)
    mcp.tool(
        name="robynn_status",
        annotations={"readOnlyHint": True, "openWorldHint": True},
    )(robynn_status)
    mcp.tool(
        name="robynn_usage",
        annotations={"readOnlyHint": True, "openWorldHint": True},
    )(robynn_usage)
    mcp.tool(
        name="robynn_context_get",
        annotations={"readOnlyHint": True, "openWorldHint": True},
    )(robynn_context_get)

    if toolset == "full":
        mcp.tool(name="robynn_website_audit_v2", annotations={"openWorldHint": True})(
            robynn_website_audit_v2
        )
        mcp.tool(name="rory_query", annotations={"openWorldHint": True})(rory_query)
        mcp.tool(name="rory_research_company", annotations={"openWorldHint": True})(
            rory_research_company
        )
        mcp.tool(name="rory_research_competitors", annotations={"openWorldHint": True})(
            rory_research_competitors
        )
        mcp.tool(name="rory_write_content", annotations={"openWorldHint": True})(
            rory_write_content
        )
        mcp.tool(
            name="rory_status",
            annotations={"readOnlyHint": True, "openWorldHint": True},
        )(rory_status)
        mcp.tool(
            name="rory_usage",
            annotations={"readOnlyHint": True, "openWorldHint": True},
        )(rory_usage)


def robynn_run(agent: str, input_text: str = "", params_json: str = "") -> str:
    """Run a Robynn agent by name. Use input_text for CMO-style prompts or params_json for structured agents."""
    params = None
    if params_json.strip():
        try:
            parsed = json.loads(params_json)
        except json.JSONDecodeError as exc:
            return f"Error: invalid params_json - {exc}"
        if not isinstance(parsed, dict):
            return "Error: params_json must decode to a JSON object"
        params = parsed

    return _run_agent(agent, input_text=input_text or None, params=params)


def robynn_status() -> str:
    """Check the active Robynn org and whether execution is available."""
    return _status_text()


def robynn_usage() -> str:
    """Check current Robynn usage and token balance."""
    return _usage_text()


def robynn_context_get(scope: str = "summary") -> str:
    """Fetch scoped Robynn context only when explicitly requested."""
    return _context_text(scope)


def robynn_website_audit_v2(params_json: str) -> str:
    """Run Website Auto-Healer v2 with a JSON params object."""
    try:
        parsed = json.loads(params_json)
    except json.JSONDecodeError as exc:
        return f"Error: invalid params_json - {exc}"
    if not isinstance(parsed, dict):
        return "Error: params_json must decode to a JSON object"
    return _run_agent("website-audit-v2", params=parsed)


def _run_cmo_query(message: str) -> str:
    return _run_agent("cmo", input_text=message)


def rory_query(message: str) -> str:
    """Send any marketing request to Rory."""
    return _run_cmo_query(message)


def rory_research_company(company: str) -> str:
    """Research a company."""
    return _run_cmo_query(f"research {company}")


def rory_research_competitors(company: str) -> str:
    """Analyze competitors for a company."""
    return _run_cmo_query(f"competitors {company}")


def rory_write_content(content_type: str, topic: str) -> str:
    """Create marketing content."""
    return _run_cmo_query(f"write {content_type} {topic}")


def rory_status() -> str:
    """Compatibility alias for Robynn status."""
    return _status_text()


def rory_usage() -> str:
    """Compatibility alias for Robynn usage."""
    return _usage_text()


_register_tools(DEFAULT_TOOLSET)


if __name__ == "__main__":
    mcp.run()
