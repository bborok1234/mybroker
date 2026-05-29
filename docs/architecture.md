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
