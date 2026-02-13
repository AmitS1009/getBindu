# Cross-Framework Agent Swarm (Bindu Interop Demo)

This example demonstrates a **heterogeneous multi-agent swarm** where:

- A **researcher agent** is built with **Agno** and DuckDuckGo tools.
- A **writer agent** is built with **LangChain**.
- Both are wrapped with `bindu.penguin.bindufy` and use Bindu DID identity for verifiable outputs.

## Why this matters

This demo shows Bindu as a universal identity + skill layer across frameworks:

1. **Interoperability:** agents can be authored in different frameworks.
2. **Negotiation-ready skills:** capabilities are declared in `skills/*/skill.yaml`.
3. **Authenticity:** every agent packet includes `did.message.signature`.

## Project structure

```text
examples/interop-swarm/
├── orchestrator.py
├── researcher.py
├── writer.py
├── verify_authenticity.py
├── task_artifact.json                # generated runtime artifact
└── skills/
    ├── researcher/skill.yaml
    └── writer/skill.yaml
```

## Environment

Use `uv` and Python 3.12+:

```bash
uv run --python 3.12.9 python -V
```

## Run the swarm

```bash
uv run --python 3.12.9 python examples/interop-swarm/orchestrator.py
```

The orchestrator writes a signed artifact to:

- `examples/interop-swarm/task_artifact.json`

## Verify signatures

```bash
uv run --python 3.12.9 python examples/interop-swarm/verify_authenticity.py
```

Expected output:

```json
{
  "research_packet_verified": true,
  "report_packet_verified": true
}
```

## Testing

```bash
uv run --python 3.12.9 pytest tests/unit/test_interop_swarm.py -q
```
