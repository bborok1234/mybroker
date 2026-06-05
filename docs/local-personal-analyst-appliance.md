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
  -> daily_scout.v1
  -> source_refresh_plan.v1
  -> scenario_report.v1 + market_verdict.v1
  -> product brief + /today mobile surface
  -> /memory accumulated research surface
  -> /memory-query local recall surface
  -> operator_decision_packet.v1
  -> local_runtime_doctor.v1
  -> local_runtime_doctor.v1 strict activation check
  -> local_scheduler_status.v1
  -> local_scheduler_apply.v1
  -> local_scheduler_run_once.v1
  -> local_scheduler_activation_preflight.v1
  -> local_scheduler_activation_verify.v1
  -> notification_delivery.v1 dry-run or sender payload
  -> daily_archive.v1
```

## Phone Access

Preferred order:

1. Tailscale Serve or private tailnet URL.
2. Private LAN URL while at home.
3. Static local file if no server is running.
4. Public Cloudflare Tunnel only after access and secret boundaries are reviewed.

Generate the local access artifact:

```bash
PYTHONPATH=src python3 -m mybroker appliance access
```

The artifact writes the local URL, the private tailnet URL shape, and the commands to run a
local static server plus `tailscale serve --bg`. MyBroker deliberately does not enable Funnel
or public exposure by default.

## Live Evidence Refresh

The default sample-cache path remains deterministic. For actual daily use, prefer no-key live
refresh with cache fallback:

```bash
PYTHONPATH=src python3 -m mybroker ingest-public-evidence \
  --source gdelt-live \
  --source stooq-live \
  --source sec-sample \
  --output reports/evidence/live-evidence-catalog.json

PYTHONPATH=src python3 -m mybroker appliance run \
  --topics config/topics.json \
  --profile examples/profiles/beginner-conservative.json \
  --source gdelt-live \
  --source stooq-live \
  --source sec-sample \
  --dry-run
```

`gdelt-live` and `stooq-live` try the live source first. If the network, source response, or
parsing fails, they return the existing cached sample shape with `live_error_fallback_sample`
freshness. This keeps the local morning loop useful while making weak or stale evidence visible.

## Commands

```bash
PYTHONPATH=src python3 -m mybroker appliance playbook
PYTHONPATH=src python3 -m mybroker appliance init --project-root .
PYTHONPATH=src python3 -m mybroker appliance access
PYTHONPATH=src python3 -m mybroker appliance decision-packet
PYTHONPATH=src python3 -m mybroker appliance doctor
PYTHONPATH=src python3 -m mybroker appliance scheduler status
PYTHONPATH=src python3 -m mybroker appliance scheduler apply --install --load --start-now
PYTHONPATH=src python3 -m mybroker appliance scheduler run-once
PYTHONPATH=src python3 -m mybroker appliance scheduler activation-preflight
PYTHONPATH=src python3 -m mybroker appliance scheduler activation-verify
PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --profile examples/profiles/beginner-conservative.json --source gdelt-live --source stooq-live --source sec-sample --dry-run
PYTHONPATH=src python3 -m mybroker appliance today --vault reports/vault/compile.json --memory-surface reports/product/memory.html --archive-manifest reports/archive/2026-06-05/manifest.json
PYTHONPATH=src python3 -m mybroker appliance memory
PYTHONPATH=src python3 -m mybroker appliance query "semiconductor cycle"
PYTHONPATH=src python3 -m mybroker appliance vault init
PYTHONPATH=src python3 -m mybroker appliance vault compile --raw-dir examples/vault/raw --wiki-dir reports/vault/wiki
PYTHONPATH=src python3 -m mybroker appliance notify --provider telegram --dry-run
```

## Compounding Memory

The local loop now writes two memory surfaces:

- `reports/memory/index.json`: machine-readable topic memory, source relevance, run history, and archive links.
- `reports/product/memory.html`: phone-readable accumulated research notebook.
- `reports/memory/latest-query.json`: machine-readable recall result for one operator question.
- `reports/product/memory-query.html`: phone-readable recall page that links the question to matching topics, archives, and next inspection questions.

This is the Obsidian vault pattern in product form: every run is still a plain local artifact,
but the daily user surface can link back to what MyBroker has learned over time. `appliance
query` is intentionally deterministic local retrieval first; a later LLM summary can sit on
top of the same artifact without hiding source context.

The local vault is the raw inbox side of the same pattern:

- `research-vault/raw`: where clipped markdown/text source notes can be dropped.
- `research-vault/wiki`: deterministic topic notes and `_master-index.md`.
- `reports/vault/compile.json`: machine-readable compile proof.
- `reports/product/vault.html`: phone-readable list of compiled raw notes.

`appliance vault compile` does not delete or move raw files. It classifies notes against configured
interests when possible, writes wiki notes with source paths and hashes, and keeps the result
research-only.
`appliance memory` and `appliance query` read the compile artifact by default, so raw-source notes
are visible in the same accumulated memory and recall surfaces as generated daily artifacts.
`appliance today` also reads the compile artifact by default. It renders the most relevant compiled
notes in the phone-readable daily brief and adds source-linked inspection questions, so a daily run
can challenge its latest evidence against accumulated raw notes.

`daily-scout` is the local topic-selection step. It writes `reports/daily/scout.json` by ranking
configured interests with source breadth, memory changes, evidence gaps, and linked vault notes.
`appliance run` creates this artifact automatically, and `appliance today` renders it as "오늘 Scout
추천" so the first phone screen explains what to inspect first and why.

`source-refresh-plan` is the no-execution source cadence step. It writes
`reports/daily/source-refresh-plan.json` with dry-run-only actions such as GDELT live, Stooq live,
SEC sample review, or vault compile. `appliance run` creates it automatically, and `appliance
today` renders it as "오늘 새로고침 계획". The artifact records `external_effect_performed: false` and
does not execute live calls, paid APIs, host writes, private serving, notification send, account
access, or trading.

`source-refresh-apply` is the execution-readiness step. It writes
`reports/daily/source-refresh-apply.json` with dry-run decisions for each planned action. Local or
sample-cache actions can be marked ready, while live network actions remain blocked behind a
separate operator gate. `appliance run` creates it automatically, and `appliance today` renders it
as "오늘 실행 판정". This artifact also records `external_effect_performed: false`.

`source-refresh-live-gate` is the scoped approval step for blocked live network candidates. It
writes `reports/daily/source-refresh-live-gate.json` with copy-ready approval text, proposed
commands, and stale-context guards. `appliance run` creates it automatically, and `appliance today`
renders it as "라이브 새로고침 게이트". This artifact does not execute live network calls; it only
defines what a later explicit approval would authorize.

`source-refresh-live-run` is the approval and execution-proof step. It writes
`reports/daily/source-refresh-live-run.json` after reading the live gate. With the default empty
response it records `approval_status: missing` and `external_effect_performed: false`. If the
operator later supplies the exact copy-ready response, the artifact can become ready to execute;
an actual live network refresh still requires explicit execution and live-network confirmation
flags. `appliance run` creates the proof automatically, and `appliance today` renders it as
"라이브 실행 증거".

The launchd assets are written under `ops/local/`:

- `run-daily-analyst.sh`
- `com.mybroker.daily-analyst.plist`

They are intentionally not installed automatically. Installing a LaunchAgent is a host-level
operation and should remain explicit.

`appliance decision-packet` writes `reports/runtime/operator-decision-packet.json`. It is the
operator handoff between local proof and external effects. It separates three approval scopes:
confirmed scheduler host write, one notification send, and private phone access serving. The
packet records current readiness, blockers, exact commands, risks, and rollback notes, but it
does not execute any of those effects.

`appliance decision apply --response "approve <decision_id> <approval_scope>"` validates the short
operator response against that packet and writes `reports/runtime/operator-decision-apply.json`.
It emits commands only when the decision exists, the approval scope matches exactly, and readiness
is `ready`. It is still a dry-run plan: `external_effect_performed=false` and host/network/send
effects remain separate explicit actions.

`appliance doctor` writes `reports/runtime/local-runtime-doctor.json`. It checks runner assets,
topic config, artifact freshness, notification payload state, private phone access guidance, and
whether the `com.mybroker.daily-analyst` LaunchAgent is loaded for the current user. By default,
an unloaded LaunchAgent is a warning rather than a failure. Use `--require-launchd-loaded` only
when validating an installed daily setup.

`appliance scheduler status` writes `reports/runtime/scheduler-status.json`. It does not install
or load anything. It records whether the source runner assets exist, whether a plist is installed
under `~/Library/LaunchAgents`, whether launchd reports the job as loaded, where logs will land,
and the exact install/load/start/status/unload/uninstall commands for review.

`appliance scheduler apply --install --load --start-now` writes
`reports/runtime/scheduler-apply.json`. By default it is a dry-run plan and records
`host_write_performed=false`. To actually install, load, or start the LaunchAgent, the operator
must add `--confirm-host-write`; that host-level action should be treated as a separate explicit
operation with fresh status and doctor evidence afterward.

`appliance scheduler run-once` writes `reports/runtime/scheduler-run-once.json`. It executes the
local `ops/local/run-daily-analyst.sh` runner once, records command, return code, duration,
stdout/stderr excerpts, post-run scheduler status, and doctor paths, and keeps
`host_write_performed=false`. This is the proof step between a dry-run activation plan and a
host-level launchd install/load.

`appliance scheduler activation-preflight` writes
`reports/runtime/scheduler-activation-preflight.json`. It does not install, load, or start
launchd. It checks runtime doctor, scheduler assets, dry-run apply, run-once, and notification
dry-run artifacts, then records `blocked`, `ready`, or `already_active`. A `ready` result means
the operator has enough local proof to decide whether to run the separate host-level
`--confirm-host-write` activation command.

`appliance scheduler activation-verify` writes
`reports/runtime/scheduler-activation-verify.json`. It is the post-activation proof step and
also performs no host-level writes. It checks that launchd is loaded, the installed plist exists
and matches the source asset, strict doctor passes with launchd required, and the latest phone
surface plus archive manifest are fresh. Before confirmed activation it should return `blocked`;
after successful activation it should return `active_verified`.
The strict doctor evidence is written separately to
`reports/runtime/local-runtime-doctor-activation.json` so ordinary readiness checks are not
overwritten when activation has not happened yet.

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
