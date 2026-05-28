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
PYTHONPATH=src python3 -m mybroker policy --kind research_note
```

## Flyhigh

Flyhigh is installed into this repo:

```text
AGENTS.md
.flyhigh/
reports/runs/
```

Project-specific domain skills live in `.flyhigh/domain-skills/`.
