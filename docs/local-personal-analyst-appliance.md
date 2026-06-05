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
| Yutori/Hermes scout-worker loops | Always-on scout recommends what matters, workers produce auditable next work | daily scout, 20-minute agenda, role-based analyst tasks, explicit weak-evidence warnings |

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
  -> daily_brief_agenda.v1 + /daily-agenda phone surface
  -> daily_readiness.v1 + /readiness phone surface
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
  -> morning_control_packet.v1 + /morning control surface
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
PYTHONPATH=src python3 -m mybroker appliance scheduler summary
PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --profile examples/profiles/beginner-conservative.json --source gdelt-live --source stooq-live --source sec-sample --dry-run
PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --vault-raw-dir research-vault/raw --vault-wiki-dir research-vault/wiki --dry-run
PYTHONPATH=src python3 -m mybroker appliance today --vault reports/vault/compile.json --memory-surface reports/product/memory.html --archive-manifest reports/archive/2026-06-05/manifest.json
PYTHONPATH=src python3 -m mybroker appliance agenda
PYTHONPATH=src python3 -m mybroker appliance readiness --freshness-hours 24
PYTHONPATH=src python3 -m mybroker appliance memory
PYTHONPATH=src python3 -m mybroker appliance journal
PYTHONPATH=src python3 -m mybroker appliance tasks
PYTHONPATH=src python3 -m mybroker appliance task-ledger
PYTHONPATH=src python3 -m mybroker appliance task-response 'AT-001 complete "checked source freshness"'
PYTHONPATH=src python3 -m mybroker appliance task-status-apply
PYTHONPATH=src python3 -m mybroker appliance morning
PYTHONPATH=src python3 -m mybroker appliance query "semiconductor cycle"
PYTHONPATH=src python3 -m mybroker appliance vault init
PYTHONPATH=src python3 -m mybroker appliance vault compile --raw-dir examples/vault/raw --wiki-dir reports/vault/wiki
PYTHONPATH=src python3 -m mybroker appliance notify --provider telegram --dry-run
```

## Compounding Memory

The local loop now writes three memory-facing surfaces:

- `reports/memory/index.json`: machine-readable topic memory, source relevance, run history, and archive links.
- `reports/product/memory.html`: phone-readable accumulated research notebook.
- `reports/memory/analyst-journal.json`: machine-readable daily analyst work log.
- `reports/product/journal.html`: phone-readable daily analyst journal with today's focus, role notes, evidence gaps, and tomorrow's questions.
- `reports/daily/brief-agenda.json`: machine-readable 20-minute study agenda from scout, evidence, memory, vault, and refresh plan.
- `reports/product/daily-agenda.html`: phone-readable agenda with reading order, source fan-out, weak evidence, role work, and follow-up questions.
- `reports/runtime/daily-readiness.json`: machine-readable freshness/readiness proof for required daily artifacts.
- `reports/product/readiness.html`: phone-readable control page that says whether today's brief is fresh enough, what is stale or missing, and what local run command to use next.
- `reports/runtime/scheduler-operations.json`: machine-readable summary of scheduler assets, local run-once proof, activation preflight, activation verification, and runtime doctor state.
- `reports/product/scheduler.html`: phone-readable scheduler operations page that says whether automation is inactive, locally proven, activation-ready, active, or blocked.
- `reports/memory/analyst-task-queue.json`: machine-readable role-based task queue.
- `reports/product/tasks.html`: phone-readable analyst task board for the next local work loop.
- `reports/memory/analyst-task-ledger.json`: machine-readable task state history.
- `reports/product/task-ledger.html`: phone-readable task ledger for ready, carried, blocked, and retired work.
- `reports/memory/latest-query.json`: machine-readable recall result for one operator question.
- `reports/product/memory-query.html`: phone-readable recall page that links the question to matching topics, archives, and next inspection questions.

This is the Obsidian vault pattern in product form: every run is still a plain local artifact,
but the daily user surface can link back to what MyBroker has learned over time. `journal.html`
is the daily analyst work log: it separates what changed, what stayed stable, what each analyst
role noticed, and which questions should carry into tomorrow. `appliance query` is intentionally
deterministic local retrieval first; a later LLM summary can sit on top of the same artifact
without hiding source context.
`tasks.html` translates that journal into queued work for source_scout, market_mapper, skeptic,
beginner_tutor, memory_librarian, and publisher roles. It does not execute commands; live network,
host writes, notification send, credentials, and trading remain behind separate approval gates.
`task-ledger.html` keeps the queue from being a daily reset: it records whether work is newly ready,
carried from an earlier run, blocked by approval, or no longer present in the current queue.
`task-response` appends a local JSONL response, and `task-status-apply` validates those responses
against the current ledger. Supported actions are `complete`, `carry`, `defer`, and `block`.
The apply artifact records `external_effect_performed: false`; it updates status only.

The local vault is the raw inbox side of the same pattern:

- `research-vault/raw`: where clipped markdown/text source notes can be dropped.
- `research-vault/wiki`: deterministic topic notes and `_master-index.md`.
- `reports/vault/compile.json`: machine-readable compile proof.
- `reports/product/vault.html`: phone-readable list of compiled raw notes.

`appliance vault compile` does not delete or move raw files. It classifies notes against configured
interests when possible, writes wiki notes with source paths and hashes, and keeps the result
research-only.
`appliance run` auto-compiles `research-vault/raw` before `daily-scout` when the raw folder exists.
Use `--skip-vault-compile` for manual-only compile, or pass `--vault-raw-dir`, `--vault-wiki-dir`,
`--vault-output`, and `--vault-surface-output` for a different local vault. The daily archive
records both `vault_compile` and `vault` artifacts.
`appliance memory` and `appliance query` read the compile artifact by default, so raw-source notes
are visible in the same accumulated memory and recall surfaces as generated daily artifacts.
`appliance today` also reads the compile artifact by default. It renders the most relevant compiled
notes in the phone-readable daily brief and adds source-linked inspection questions, so a daily run
can challenge its latest evidence against accumulated raw notes.

`daily-scout` is the local topic-selection step. It writes `reports/daily/scout.json` by ranking
configured interests with source breadth, memory changes, evidence gaps, and linked vault notes.
`appliance run` creates this artifact automatically, and `appliance today` renders it as "오늘 Scout
추천" so the first phone screen explains what to inspect first and why.

`appliance agenda` is the phone-first work-shaping step. It writes
`reports/daily/brief-agenda.json` and `reports/product/daily-agenda.html` from the current scout,
evidence, memory, vault, and refresh plan. The agenda translates the top scout topic into a
20-minute reading sequence, source fan-out, weak-evidence warnings, role-specific analyst work,
and follow-up questions. It does not fetch live data or make investment decisions; it helps the
operator study the right thing first and stop before overclaiming weak evidence.

`appliance readiness` is the cross-day trust check. It writes
`reports/runtime/daily-readiness.json` and `reports/product/readiness.html` by reading existing
local artifacts only. It marks required phone surfaces and machine artifacts as fresh, stale, or
missing, reports scheduler status if available, links the phone surfaces, and shows the next local
`appliance run --dry-run` command. It does not refresh sources, send notifications, install
schedulers, or perform host/network effects.

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

`source-refresh-live-preflight` is the final no-network proof before approved source execution. It
reads `reports/daily/source-refresh-live-run.json` and checks the exact approval state, live-run
readiness, explicit execution intent, live-network confirmation, source ids, evidence output path,
and forbidden external-effect commands. With the default appliance run it remains blocked and
records `external_effect_performed: false`. If the operator later supplies an approved live-run
proof and explicit preflight intent, it can pass without calling the network. `appliance today`
renders it as "라이브 실행 사전점검".

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

`appliance scheduler summary` writes `reports/runtime/scheduler-operations.json` and
`reports/product/scheduler.html`. It does not install, load, start, unload, uninstall, send
notifications, or fetch live sources. It reads the local scheduler proof artifacts and tells the
operator whether the next step is local asset generation, run-once proof, activation preflight,
separate host-write approval, or post-activation log/archive inspection.

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
