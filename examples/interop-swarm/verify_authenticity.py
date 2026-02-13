"""Validate DID signatures in interop swarm task artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from researcher import AgnoResearcherAgent
from writer import LangChainWriterAgent


def verify_packet(packet: dict, verifier) -> bool:
    payload = packet["did"]["message"]["payload"]
    signature = packet["did"]["message"]["signature"]
    return verifier.did_extension.verify_text(payload, signature)


def verify_artifact(artifact_path: Path) -> dict[str, bool]:
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    researcher = AgnoResearcherAgent(base_dir=artifact_path.parent)
    writer = LangChainWriterAgent(base_dir=artifact_path.parent)
    return {
        "research_packet_verified": verify_packet(payload["packets"]["research"], researcher),
        "report_packet_verified": verify_packet(payload["packets"]["report"], writer),
    }


def main() -> None:
    artifact_path = Path(__file__).parent / "task_artifact.json"
    verification = verify_artifact(artifact_path)
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
