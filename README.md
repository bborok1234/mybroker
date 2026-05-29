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
PYTHONPATH=src python3 -m mybroker quality --source examples/prices-multi
PYTHONPATH=src python3 -m mybroker research --source examples/prices.csv --output reports/runs/local-momentum-research.json
PYTHONPATH=src python3 -m mybroker research --source examples/prices-multi --run-id multi-file-research --output reports/runs/multi-file-research.json
PYTHONPATH=src python3 -m mybroker validate-report reports/runs/local-momentum-research.json
PYTHONPATH=src python3 -m mybroker dashboard --reports-dir reports/runs --output reports/dashboard.html --rollup-output reports/report-rollup.json
PYTHONPATH=src python3 -m mybroker policy --kind research_note
```

## First Pipeline Slice

The first vertical slice is intentionally local and auditable:

1. A price data adapter loads CSV, multiple CSV files, a directory of CSV files, or bundled sample data.
2. The research task registry selects `momentum_research_v1`.
3. Data quality checks evaluate schema, missing values, duplicate rows, date order, symbol coverage, and insufficient history.
4. The runner generates explainable signals through the existing policy gate.
5. A `research_report.v1` JSON artifact is written under `reports/runs/`.
6. The artifact validator checks schema, source metadata, data quality, signals, policy, and summary consistency.
7. The report dashboard command turns local report artifacts into `reports/dashboard.html` and `reports/report-rollup.json` so the latest run, quality status, dataset coverage, and recent run comparison can be inspected without reading raw JSON.

## Flyhigh

Flyhigh is installed into this repo:

```text
AGENTS.md
.flyhigh/
reports/runs/
```

Project-specific domain skills live in `.flyhigh/domain-skills/`.
