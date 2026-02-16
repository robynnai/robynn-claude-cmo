"""Prompt routing helpers for Rory plugin.

The plugin intentionally routes into coarse focus hints only. Final private
skill selection happens server-side in robynnv3_agents.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RouteRule:
    focus_hint: str
    patterns: tuple[str, ...]


ROUTE_RULES: tuple[RouteRule, ...] = (
    RouteRule(
        focus_hint="analytics",
        patterns=(
            r"\banalytics?\b",
            r"\bga4\b",
            r"\bmetrics?\b",
            r"\bkpi(s)?\b",
            r"\bperformance\b",
            r"\bconversion rate\b",
        ),
    ),
    RouteRule(
        focus_hint="research",
        patterns=(
            r"\bresearch\b",
            r"\bcompetitor(s)?\b",
            r"\bmarket\b",
            r"\bindustry\b",
            r"\bpositioning\b",
            r"\bblindspot(s)?\b",
        ),
    ),
    RouteRule(
        focus_hint="campaigns",
        patterns=(
            r"\bcampaign(s)?\b",
            r"\bads?\b",
            r"\bpaid\b",
            r"\blaunch\b",
            r"\bpromotion\b",
            r"\bgtm\b",
        ),
    ),
    RouteRule(
        focus_hint="content",
        patterns=(
            r"\bcontent\b",
            r"\bblog\b",
            r"\bpost\b",
            r"\blinkedin\b",
            r"\btweet\b",
            r"\bcopy\b",
            r"\bemail\b",
            r"\bnewsletter\b",
        ),
    ),
    RouteRule(
        focus_hint="knowledge",
        patterns=(
            r"\bknowledge base\b",
            r"\bgraphlit\b",
            r"\bingest\b",
            r"\bsource(s)?\b",
            r"\bcrawl\b",
        ),
    ),
    RouteRule(
        focus_hint="monitoring",
        patterns=(
            r"\bmonitor\b",
            r"\bmentions?\b",
            r"\bbrand monitor\b",
            r"\breputation\b",
        ),
    ),
    RouteRule(
        focus_hint="strategy",
        patterns=(
            r"\bstrategy\b",
            r"\broadmap\b",
            r"\bplan\b",
            r"\bpriorit(y|ize)\b",
            r"\bframework\b",
        ),
    ),
)


FOCUS_HINT_DESCRIPTIONS: dict[str, str] = {
    "analytics": "Performance analytics and measurement",
    "research": "Market and competitive research",
    "campaigns": "Campaign and go-to-market execution",
    "content": "Content ideation and drafting",
    "knowledge": "Knowledge base retrieval and ingestion",
    "monitoring": "Brand monitoring and mention analysis",
    "strategy": "Marketing strategy and planning",
    "general": "General marketing support",
}


class SkillRouter:
    """Routes user prompts to coarse, non-secret focus hints."""

    def route(self, message: str) -> str:
        text = (message or "").strip().lower()
        if not text:
            return "general"

        for rule in ROUTE_RULES:
            for pattern in rule.patterns:
                if re.search(pattern, text):
                    return rule.focus_hint
        return "general"

    def build_header(self, focus_hint: str, organization_id: str) -> str:
        hint = focus_hint if focus_hint in FOCUS_HINT_DESCRIPTIONS else "general"
        description = FOCUS_HINT_DESCRIPTIONS[hint]
        return (
            "## Rory Routing Context\n"
            f"- Organization ID: {organization_id}\n"
            f"- Focus Hint: {hint}\n"
            f"- Focus Description: {description}\n"
            "- Directive: Use internal private skill routing based on this focus hint, "
            "the user prompt, and the organization's brand context.\n"
            "- Note: Do not ask the user to provide private skill names.\n"
        )

    def build_prompt(self, message: str, focus_hint: str, organization_id: str) -> str:
        header = self.build_header(focus_hint=focus_hint, organization_id=organization_id)
        return f"{header}\n## User Request\n{message.strip()}"

