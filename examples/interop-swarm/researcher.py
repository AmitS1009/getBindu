"""Agno-based researcher agent for cross-framework interop swarm demos."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable
from uuid import uuid4

from agno.tools.duckduckgo import DuckDuckGoTools

from bindu.penguin.bindufy import bindufy
from bindu.penguin.did_setup import initialize_did_extension


class AgnoResearcherAgent:
    """Research agent that uses Agno DuckDuckGo tools and Bindu identity."""

    def __init__(
        self,
        base_dir: Path | None = None,
        search_override: Callable[[str], str] | None = None,
    ) -> None:
        self.base_dir = base_dir or Path(__file__).parent
        self.agent_id = f"researcher-{uuid4().hex[:12]}"
        self.did_extension = initialize_did_extension(
            agent_id=self.agent_id,
            author="founding.engineer@getbindu.com",
            agent_name="agno_researcher",
            key_dir=self.base_dir / ".agent_state" / "researcher",
            recreate_keys=False,
        )
        self.tools = DuckDuckGoTools()
        self._search_override = search_override

        self.config = {
            "author": "founding.engineer@getbindu.com",
            "id": self.agent_id,
            "name": "interop-agno-researcher",
            "description": "Agno researcher for cross-framework swarm discovery.",
            "deployment": {"url": "http://localhost:3773", "expose": False},
            "skills": ["skills/researcher"],
            "recreate_keys": False,
        }
        self.manifest = bindufy(
            config=self.config,
            handler=self.handler,
            run_server=False,
            key_dir=self.base_dir / ".agent_state" / "researcher",
        )

    def _search(self, topic: str) -> str:
        if self._search_override:
            return self._search_override(topic)
        try:
            return self.tools.web_search(query=topic, max_results=5)
        except Exception:
            return (
                "DuckDuckGo search unavailable in current environment. "
                f"Fallback summary for: {topic}."
            )

    def research(self, topic: str) -> dict:
        findings = self._search(topic)
        payload = json.dumps(
            {"topic": topic, "findings": findings},
            sort_keys=True,
            ensure_ascii=False,
        )
        signature = self.did_extension.sign_text(payload)
        return {
            "agent": "researcher",
            "framework": "agno",
            "did": {
                "id": self.did_extension.did,
                "message": {"payload": payload, "signature": signature},
            },
            "artifact": {
                "topic": topic,
                "findings": findings,
                "generated_at": datetime.now(UTC).isoformat(),
            },
        }

    def handler(self, messages: list[dict[str, str]]) -> dict:
        user_input = messages[-1].get("content", "") if messages else ""
        return self.research(user_input)


__all__ = ["AgnoResearcherAgent"]
