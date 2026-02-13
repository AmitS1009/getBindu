"""Main orchestration entrypoint for the Bindu cross-framework interop swarm."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from researcher import AgnoResearcherAgent
from writer import LangChainWriterAgent


class InteropSwarmOrchestrator:
    """Routes complex tasks across heterogeneous agent frameworks via Bindu metadata."""

    def __init__(self, base_dir: Path | None = None, skill_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(__file__).parent
        self.skill_dir = skill_dir or Path(__file__).parent / "skills"
        self.researcher = AgnoResearcherAgent(base_dir=self.base_dir)
        self.writer = LangChainWriterAgent(base_dir=self.base_dir)

    def load_skill_registry(self) -> dict:
        registry: dict[str, dict] = {}
        for skill_path in [
            self.skill_dir / "researcher" / "skill.yaml",
            self.skill_dir / "writer" / "skill.yaml",
        ]:
            with skill_path.open("r", encoding="utf-8") as handle:
                skill_doc = yaml.safe_load(handle)
            registry[skill_doc["id"]] = skill_doc
        return registry

    def run(self, task: str) -> dict:
        skill_registry = self.load_skill_registry()
        research_packet = self.researcher.research(task)
        report_packet = self.writer.write_report(research_packet)
        return {
            "task": task,
            "negotiation": {
                "selected_skills": [
                    skill_registry["interop-researcher-skill"]["capabilities"],
                    skill_registry["interop-writer-skill"]["capabilities"],
                ]
            },
            "packets": {
                "research": research_packet,
                "report": report_packet,
            },
        }


def main() -> None:
    orchestrator = InteropSwarmOrchestrator()
    task = "Analyze EU AI Act compliance expectations for fintech copilots in 2026"
    result = orchestrator.run(task)
    artifact_path = Path(__file__).parent / "task_artifact.json"
    artifact_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote signed swarm artifact to {artifact_path}")


if __name__ == "__main__":
    main()
