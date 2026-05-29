# MyBroker

MyBroker is a Flyhigh-enabled, beginner-first market understanding and simulation OS.

The product goal is not to ask a beginner investor for a perfect ticker, sector, event,
or investment hypothesis. MyBroker should help create that starting point:

- read local market/evidence seeds;
- build a beginner-readable market map;
- simulate optimistic, base, and downside paths through persona viewpoints;
- explain unfamiliar concepts in plain language;
- produce action candidates such as learn, observe, watchlist, defer, or avoid;
- keep all outputs auditable as local artifacts.

It does not place orders, manage accounts, store brokerage credentials, provide discretionary
trading, or present unsupported personalized financial advice.

## Commands

```bash
PYTHONPATH=src python3 -m unittest
PYTHONPATH=src python3 -m mybroker signals examples/prices.csv
PYTHONPATH=src python3 -m mybroker tasks
PYTHONPATH=src python3 -m mybroker quality --source examples/prices-multi
PYTHONPATH=src python3 -m mybroker research --source examples/prices.csv --output reports/runs/local-momentum-research.json
PYTHONPATH=src python3 -m mybroker research --source examples/prices-multi --run-id multi-file-research --output reports/runs/multi-file-research.json
PYTHONPATH=src python3 -m mybroker validate-report reports/runs/local-momentum-research.json
PYTHONPATH=src python3 -m mybroker scenario --seed examples/seeds --output reports/scenarios/beginner-market-sim.json --verdict-output reports/scenarios/verdict.json
PYTHONPATH=src python3 -m mybroker scenario --seed examples/seeds --profile examples/profiles/beginner-conservative.json --run-id beginner-profile-sim --output reports/scenarios/beginner-profile-sim.json --verdict-output reports/scenarios/profile-verdict.json
PYTHONPATH=src python3 -m mybroker validate-profile examples/profiles/beginner-conservative.json
PYTHONPATH=src python3 -m mybroker validate-scenario reports/scenarios/beginner-market-sim.json
PYTHONPATH=src python3 -m mybroker validate-verdict reports/scenarios/verdict.json
PYTHONPATH=src python3 -m mybroker dashboard --reports-dir reports/runs --output reports/dashboard.html --rollup-output reports/report-rollup.json
PYTHONPATH=src python3 -m mybroker policy --kind research_note
```

## Beginner Simulation Slice

The MiroFish-inspired slice is local and deterministic by default:

1. Markdown or text seed files describe market context in beginner-readable terms.
2. The scenario engine extracts themes such as AI infrastructure, semiconductors, rates,
   inflation, consumer pressure, and market risk.
3. A `scenario_report.v1` artifact records the market map, relationships, persona views,
   evidence catalog, optional beginner profile context, output boundary, scenario paths,
   beginner explanations, policy gate, warnings, and action candidates.
4. A `market_verdict.v1` artifact summarizes the top next step without turning it into
   an order or account-specific recommendation.
5. The dashboard renders a market map, scenario branches, agent perspectives, and action
   candidates so a beginner can decide what to learn or inspect next.

Optional beginner profile context can adjust explanation priority and candidate ordering.
It is deliberately limited to learning goal, risk comfort, time horizon, and decision style.
It does not create account-specific instructions or discretionary trading authority.

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
