"""Unit tests for the cross-framework interop swarm example."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import yaml


EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "examples" / "interop-swarm"


def _load_module(module_name: str, file_name: str):
    if str(EXAMPLE_DIR) not in sys.path:
        sys.path.insert(0, str(EXAMPLE_DIR))
    spec = importlib.util.spec_from_file_location(module_name, EXAMPLE_DIR / file_name)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_skill_yamls_expose_expected_capabilities():
    researcher_skill = yaml.safe_load(
        (EXAMPLE_DIR / "skills" / "researcher" / "skill.yaml").read_text(encoding="utf-8")
    )
    writer_skill = yaml.safe_load(
        (EXAMPLE_DIR / "skills" / "writer" / "skill.yaml").read_text(encoding="utf-8")
    )

    assert researcher_skill["capabilities"] == ["web_search", "data_extraction"]
    assert "input_schema" in writer_skill
    assert "output_schema" in writer_skill


def test_orchestrator_routes_work_and_signs_packets(tmp_path: Path):
    researcher_mod = _load_module("interop_researcher", "researcher.py")
    writer_mod = _load_module("interop_writer", "writer.py")
    orchestrator_mod = _load_module("interop_orchestrator", "orchestrator.py")

    researcher = researcher_mod.AgnoResearcherAgent(
        base_dir=tmp_path, search_override=lambda topic: f"mock findings for {topic}"
    )
    writer = writer_mod.LangChainWriterAgent(base_dir=tmp_path)

    orchestrator = orchestrator_mod.InteropSwarmOrchestrator(base_dir=tmp_path)
    orchestrator.researcher = researcher
    orchestrator.writer = writer

    result = orchestrator.run("bindu protocol interop")

    research_packet = result["packets"]["research"]
    report_packet = result["packets"]["report"]

    assert research_packet["framework"] == "agno"
    assert report_packet["framework"] == "langchain"
    assert researcher.did_extension.verify_text(
        research_packet["did"]["message"]["payload"],
        research_packet["did"]["message"]["signature"],
    )
    assert writer.did_extension.verify_text(
        report_packet["did"]["message"]["payload"],
        report_packet["did"]["message"]["signature"],
    )


def test_verify_authenticity_script_checks_did_signatures(tmp_path: Path):
    researcher_mod = _load_module("interop_researcher_2", "researcher.py")
    writer_mod = _load_module("interop_writer_2", "writer.py")
    verify_mod = _load_module("interop_verify", "verify_authenticity.py")

    researcher = researcher_mod.AgnoResearcherAgent(
        base_dir=tmp_path, search_override=lambda _: "mock"
    )
    writer = writer_mod.LangChainWriterAgent(base_dir=tmp_path)

    research = researcher.research("zero trust agent identity")
    report = writer.write_report(research)
    artifact = {"packets": {"research": research, "report": report}}

    artifact_path = tmp_path / "task_artifact.json"
    artifact_path.write_text(json.dumps(artifact), encoding="utf-8")

    verified = verify_mod.verify_artifact(artifact_path)

    assert verified == {
        "research_packet_verified": True,
        "report_packet_verified": True,
    }
