# Architecture

```text
local CSV/data source, CSV directory, or repeated CSV sources
  -> mybroker.data adapter + quality checks
  -> mybroker.registry
  -> mybroker.signals
  -> mybroker.policy
  -> mybroker.reports
  -> CLI / future app surfaces
```

## Boundaries

- `src/mybroker/data.py`: parse and validate local observations through CSV/sample/directory/multi-file adapters, dataset metadata, and quality checks.
- `src/mybroker/registry.py`: expose named research tasks and execution defaults.
- `src/mybroker/signals.py`: deterministic signal generation.
- `src/mybroker/policy.py`: classify risky action categories.
- `src/mybroker/runner.py`: compose adapter, task, signal generation, policy, and report output.
- `src/mybroker/reports.py`: build and validate `research_report.v1` artifacts with source metadata and data-quality evidence.
- `src/mybroker/cli.py`: local command interface.
- `.flyhigh/`: project memory, domain skills, dashboard state.
- `reports/runs/`: task-level evidence.

## Flyhigh Usage

Flyhigh owns the engineering harness. MyBroker owns domain-specific behavior. Domain skills stay under `.flyhigh/domain-skills/` so the reusable Flyhigh core remains domain-neutral.
# Beginner-First Scenario Layer

MyBroker now has two local artifact families:

- `research_report.v1`: price-data research and signal generation.
- `scenario_report.v1` plus `market_verdict.v1`: beginner-first market understanding and simulation.

The scenario layer is intentionally deterministic in v0. It turns local seed files into:

1. evidence seeds;
2. detected market topics;
3. an evidence catalog with coverage and missing-context notes;
4. optional beginner profile context;
5. a market map of entities and relationships;
6. persona views;
7. scenario paths;
8. beginner explanations;
9. safe action candidates.

This keeps the product useful before live data, paid APIs, external LLM calls, brokerage
credentials, or account-specific personalization are introduced.

Policy boundary:

- scenario simulation is allowed as research/education;
- beginner profile context may change explanation priority but not create trade instructions;
- order execution, account access, credential storage, and discretionary trading are blocked;
- personalized recommendations require human review and suitability context.
