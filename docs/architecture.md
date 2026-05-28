# Architecture

```text
local CSV/data source
  -> mybroker.data
  -> mybroker.signals
  -> mybroker.policy
  -> CLI / future app surfaces
```

## Boundaries

- `src/mybroker/data.py`: parse and validate local observations.
- `src/mybroker/signals.py`: deterministic signal generation.
- `src/mybroker/policy.py`: classify risky action categories.
- `src/mybroker/cli.py`: local command interface.
- `.flyhigh/`: project memory, domain skills, dashboard state.
- `reports/runs/`: task-level evidence.

## Flyhigh Usage

Flyhigh owns the engineering harness. MyBroker owns domain-specific behavior. Domain skills stay under `.flyhigh/domain-skills/` so the reusable Flyhigh core remains domain-neutral.
