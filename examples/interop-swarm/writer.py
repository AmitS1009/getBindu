"""LangChain-based writer agent for cross-framework interop swarm demos."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from langchain_core.prompts import ChatPromptTemplate

from bindu.penguin.bindufy import bindufy
from bindu.penguin.did_setup import initialize_did_extension


class LangChainWriterAgent:
    """Writer agent that transforms researcher artifacts into Markdown reports."""

    def __init__(
        self,
        base_dir: Path | None = None,
    ) -> None:
        self.base_dir = base_dir or Path(__file__).parent
        self.agent_id = f"writer-{uuid4().hex[:12]}"
        self.did_extension = initialize_did_extension(
            agent_id=self.agent_id,
            author="founding.engineer@getbindu.com",
            agent_name="langchain_writer",
            key_dir=self.base_dir / ".agent_state" / "writer",
            recreate_keys=False,
        )
        self.prompt = ChatPromptTemplate.from_template(
            """
You are a technical report writer.
Convert the research packet into a concise markdown report.

Topic: {topic}
Findings: {findings}

Return markdown with sections:
1. Executive Summary
2. Key Findings
3. Recommended Next Actions
""".strip()
        )
        self.config = {
            "author": "founding.engineer@getbindu.com",
            "id": self.agent_id,
            "name": "interop-langchain-writer",
            "description": "LangChain writer for cross-framework swarm discovery.",
            "deployment": {"url": "http://localhost:3774", "expose": False},
            "skills": ["skills/writer"],
            "recreate_keys": False,
        }
        self.manifest = bindufy(
            config=self.config,
            handler=self.handler,
            run_server=False,
            key_dir=self.base_dir / ".agent_state" / "writer",
        )

    def write_report(self, research_packet: dict) -> dict:
        topic = research_packet["artifact"]["topic"]
        findings = research_packet["artifact"]["findings"]
        formatted_prompt = self.prompt.format_messages(topic=topic, findings=findings)
        user_visible_markdown = (
            f"# Interop Swarm Report: {topic}\n\n"
            "## Executive Summary\n"
            f"Cross-framework collaboration produced a verified research packet for **{topic}**.\n\n"
            "## Key Findings\n"
            f"{findings}\n\n"
            "## Recommended Next Actions\n"
            "- Validate claims with domain experts.\n"
            "- Feed this report into downstream planning agents.\n"
        )
        payload = json.dumps(
            {
                "topic": topic,
                "report": user_visible_markdown,
                "prompt_messages": [msg.content for msg in formatted_prompt],
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        signature = self.did_extension.sign_text(payload)
        return {
            "agent": "writer",
            "framework": "langchain",
            "did": {
                "id": self.did_extension.did,
                "message": {"payload": payload, "signature": signature},
            },
            "artifact": {
                "topic": topic,
                "report_markdown": user_visible_markdown,
                "source_research_did": research_packet["did"]["id"],
                "generated_at": datetime.now(UTC).isoformat(),
            },
        }

    def handler(self, messages: list[dict[str, str]]) -> dict:
        if not messages:
            return self.write_report(
                {
                    "artifact": {"topic": "Unknown", "findings": "No findings supplied."},
                    "did": {"id": "did:bindu:unknown"},
                }
            )
        research_packet = json.loads(messages[-1].get("content", "{}"))
        return self.write_report(research_packet)


__all__ = ["LangChainWriterAgent"]
