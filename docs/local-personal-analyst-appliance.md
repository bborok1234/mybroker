# Local Personal Analyst Appliance

MyBroker should first become a local personal analyst appliance, not a hosted investment
web app. The useful product is a daily workflow that compounds evidence and explanations
while staying narrow, auditable, and research-only.

## Why Not Start With Deployment

A hosted web app adds authentication, secrets, uptime, billing, and public attack surface before
the core analyst loop is proven. For a single operator, the better first system is:

1. run locally on the MacBook;
2. schedule with macOS `launchd`;
3. serve privately to the phone through Tailscale, private LAN, or a local file;
4. send a short notification;
5. preserve every run in local artifacts and archive manifests.

The product surface is the daily brief, not the server.

## Patterns Absorbed

| Source pattern | What matters | MyBroker translation |
| --- | --- | --- |
| Hermes Agent | Persistent memory, skills, messaging gateway, cron-like operation | topic memory, CLI workflows, notification dry-runs, launchd assets |
| OpenClaw | Local workspace assistant, skills, tool routing | narrow research appliance, not broad file/account authority |
| MiroFish | GraphRAG-style market map, personas, counterfactual scenarios | market map, persona views, optimistic/base/downside paths |
| TradingAgents / FinRobot | Role-specialized analyst debate and risk review | source scout, evidence curator, market mapper, scenario analyst, skeptic, tutor |
| Obsidian research vault workflows | File-based knowledge that compounds | archive manifests, topic memory, source-linked daily artifacts |

## Local Runtime Shape

```text
launchd
  -> mybroker appliance run
  -> topic_config.v1
  -> daily_research_plan.v1
  -> public_evidence_catalog.v1
  -> topic_memory.v1
  -> scenario_report.v1 + market_verdict.v1
  -> product brief + /today mobile surface
  -> notification_delivery.v1 dry-run or sender payload
  -> daily_archive.v1
```

## Phone Access

Preferred order:

1. Tailscale Serve or private tailnet URL.
2. Private LAN URL while at home.
3. Static local file if no server is running.
4. Public Cloudflare Tunnel only after access and secret boundaries are reviewed.

## Commands

```bash
PYTHONPATH=src python3 -m mybroker appliance playbook
PYTHONPATH=src python3 -m mybroker appliance init --project-root .
PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --profile examples/profiles/beginner-conservative.json --dry-run
PYTHONPATH=src python3 -m mybroker appliance today
PYTHONPATH=src python3 -m mybroker appliance notify --provider telegram --dry-run
```

The launchd assets are written under `ops/local/`:

- `run-daily-analyst.sh`
- `com.mybroker.daily-analyst.plist`

They are intentionally not installed automatically. Installing a LaunchAgent is a host-level
operation and should remain explicit.

## Safety Boundary

The appliance may:

- collect and normalize free/public evidence;
- generate educational scenarios;
- maintain local memory;
- notify that a brief is ready.

The appliance must not:

- store brokerage credentials;
- place orders;
- manage accounts;
- provide discretionary management;
- present unsupported personalized recommendations;
- use paid or credentialed APIs without explicit scoped approval.
