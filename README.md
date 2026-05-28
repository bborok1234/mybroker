# MyBroker

MyBroker is a Flyhigh-enabled personal research and signal-generation project.

The first usable scope is deliberately narrow:

- ingest local price observations;
- generate explainable research signals;
- classify risky actions through a policy gate;
- keep project memory and run artifacts under `.flyhigh/` and `reports/runs/`.

It does not place orders, manage accounts, or provide personalized investment advice.

## Commands

```bash
PYTHONPATH=src python3 -m unittest
PYTHONPATH=src python3 -m mybroker signals examples/prices.csv
PYTHONPATH=src python3 -m mybroker tasks
PYTHONPATH=src python3 -m mybroker research --source examples/prices.csv --output reports/runs/local-momentum-research.json
PYTHONPATH=src python3 -m mybroker validate-report reports/runs/local-momentum-research.json
PYTHONPATH=src python3 -m mybroker policy --kind research_note
```

## First Pipeline Slice

The first vertical slice is intentionally local and auditable:

1. A price data adapter loads CSV or bundled sample data.
2. The research task registry selects `momentum_research_v1`.
3. The runner generates explainable signals through the existing policy gate.
4. A `research_report.v1` JSON artifact is written under `reports/runs/`.
5. The artifact validator checks schema, source metadata, signals, policy, and summary consistency.

## Flyhigh

Flyhigh is installed into this repo:

```text
AGENTS.md
.flyhigh/
reports/runs/
```

Project-specific domain skills live in `.flyhigh/domain-skills/`.
