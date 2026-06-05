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
PYTHONPATH=src python3 -m mybroker evidence-sources
PYTHONPATH=src python3 -m mybroker ingest-public-evidence --output reports/evidence/public-evidence-catalog.json
PYTHONPATH=src python3 -m mybroker ingest-public-evidence --source gdelt-live --source stooq-live --source sec-sample --output reports/evidence/live-evidence-catalog.json
PYTHONPATH=src python3 -m mybroker validate-public-evidence reports/evidence/public-evidence-catalog.json
PYTHONPATH=src python3 -m mybroker topics init --output config/topics.json
PYTHONPATH=src python3 -m mybroker topics add "Korea semiconductors" --description "Korea memory exporters, AI demand, and cycle risk" --keyword korea --keyword memory --keyword chip --config config/topics.json
PYTHONPATH=src python3 -m mybroker topics list --config config/topics.json
PYTHONPATH=src python3 -m mybroker research-plan --topics config/topics.json --output reports/daily/research-plan.json --run-id daily-research
PYTHONPATH=src python3 -m mybroker collect-evidence --topics config/topics.json --plan reports/daily/research-plan.json --output reports/evidence/daily-evidence-catalog.json --memory-output reports/memory/topic-memory.json
PYTHONPATH=src python3 -m mybroker daily-scout --topics config/topics.json --plan reports/daily/research-plan.json --evidence reports/evidence/daily-evidence-catalog.json --memory reports/memory/topic-memory.json --vault reports/vault/compile.json --output reports/daily/scout.json
PYTHONPATH=src python3 -m mybroker source-refresh-plan --scout reports/daily/scout.json --evidence reports/evidence/daily-evidence-catalog.json --vault reports/vault/compile.json --output reports/daily/source-refresh-plan.json
PYTHONPATH=src python3 -m mybroker source-refresh-apply --refresh-plan reports/daily/source-refresh-plan.json --output reports/daily/source-refresh-apply.json
PYTHONPATH=src python3 -m mybroker source-refresh-live-gate --refresh-apply reports/daily/source-refresh-apply.json --output reports/daily/source-refresh-live-gate.json
PYTHONPATH=src python3 -m mybroker source-refresh-live-run --live-gate reports/daily/source-refresh-live-gate.json --response "" --output reports/daily/source-refresh-live-run.json
PYTHONPATH=src python3 -m mybroker source-refresh-live-preflight --live-run reports/daily/source-refresh-live-run.json --output reports/daily/source-refresh-live-preflight.json
PYTHONPATH=src python3 -m mybroker appliance agenda --scout reports/daily/scout.json --evidence reports/evidence/daily-evidence-catalog.json --memory reports/memory/topic-memory.json --vault reports/vault/compile.json --refresh-plan reports/daily/source-refresh-plan.json
PYTHONPATH=src python3 -m mybroker appliance source-refresh
PYTHONPATH=src python3 -m mybroker appliance readiness --freshness-hours 24
PYTHONPATH=src python3 -m mybroker scenario --seed examples/seeds --profile examples/profiles/beginner-conservative.json --evidence-catalog reports/evidence/public-evidence-catalog.json --run-id public-evidence-sim --output reports/scenarios/public-evidence-sim.json --verdict-output reports/scenarios/public-evidence-verdict.json
PYTHONPATH=src python3 -m mybroker daily-research --topics config/topics.json --profile examples/profiles/beginner-conservative.json --run-id daily-research
PYTHONPATH=src python3 -m mybroker validate-scenario reports/scenarios/beginner-market-sim.json
PYTHONPATH=src python3 -m mybroker validate-verdict reports/scenarios/verdict.json
PYTHONPATH=src python3 -m mybroker validate-daily-scout reports/daily/scout.json
PYTHONPATH=src python3 -m mybroker validate-daily-agenda reports/daily/brief-agenda.json
PYTHONPATH=src python3 -m mybroker validate-daily-readiness reports/runtime/daily-readiness.json
PYTHONPATH=src python3 -m mybroker validate-source-refresh-plan reports/daily/source-refresh-plan.json
PYTHONPATH=src python3 -m mybroker validate-source-refresh-apply reports/daily/source-refresh-apply.json
PYTHONPATH=src python3 -m mybroker validate-source-refresh-live-gate reports/daily/source-refresh-live-gate.json
PYTHONPATH=src python3 -m mybroker validate-source-refresh-live-run reports/daily/source-refresh-live-run.json
PYTHONPATH=src python3 -m mybroker validate-source-refresh-live-preflight reports/daily/source-refresh-live-preflight.json
PYTHONPATH=src python3 -m mybroker validate-source-refresh-brief reports/runtime/source-refresh-brief.json
PYTHONPATH=src python3 -m mybroker dashboard --reports-dir reports/runs --output reports/dashboard.html --rollup-output reports/report-rollup.json
PYTHONPATH=src python3 -m mybroker brief --scenario reports/scenarios/public-evidence-sim.json --verdict reports/scenarios/public-evidence-verdict.json --output reports/product/market-brief.html
PYTHONPATH=src python3 -m mybroker appliance playbook
PYTHONPATH=src python3 -m mybroker appliance init --project-root .
PYTHONPATH=src python3 -m mybroker appliance access
PYTHONPATH=src python3 -m mybroker appliance decision-packet
PYTHONPATH=src python3 -m mybroker appliance decision apply --response "approve private_phone_access private_network_exposure"
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
PYTHONPATH=src python3 -m mybroker appliance readiness
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
PYTHONPATH=src python3 -m mybroker validate-vault reports/vault/compile.json
PYTHONPATH=src python3 -m mybroker appliance notify --provider telegram --dry-run
PYTHONPATH=src python3 -m mybroker policy --kind research_note
```

## Surfaces

MyBroker separates four surfaces:

1. Flyhigh operator dashboard: project progress only. It shows issues, PRs, direction reviews, merge gates, validation, blockers, next actions, and live repo state.
2. MyBroker ops/artifact dashboard: builder-facing artifact trust screen for validation, source coverage, freshness, data quality, artifact paths, and blockers.
3. MyBroker product surfaces: beginner-facing MiroFish-inspired market brief and local analyst screens generated by `mybroker brief`, `mybroker appliance today`, `mybroker appliance agenda`, `mybroker appliance source-refresh`, `mybroker appliance readiness`, `mybroker appliance scheduler summary`, `mybroker appliance journal`, `mybroker appliance tasks`, and `mybroker appliance task-ledger`.
4. Machine artifacts: JSON evidence and report artifacts such as `public_evidence_catalog.v1`, `scenario_report.v1`, `market_verdict.v1`, and `research_report.v1`.

The product brief must not expose adapter IDs, schema names, raw validation logs, Flyhigh gates, or implementation details. See `docs/surfaces.md`.

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
5. The product brief renders a market map, scenario branches, agent perspectives, and action
   candidates so a beginner can decide what to learn or inspect next.

Optional beginner profile context can adjust explanation priority and candidate ordering.
It is deliberately limited to learning goal, risk comfort, time horizon, and decision style.
It does not create account-specific instructions or discretionary trading authority.

## Free/Public Evidence Proof

The public evidence slice tests whether beginner-first simulation can work before paid data,
accounts, or execution are introduced.

1. `evidence-sources` prints a feasibility matrix for SEC EDGAR, FRED, GDELT, Stooq,
   Alpha Vantage free tier, Nasdaq Data Link, and any later free source additions.
2. `ingest-public-evidence` reads cached, no-key public-source samples and writes a
   `public_evidence_catalog.v1` artifact under `reports/evidence/`.
3. The catalog records source coverage, freshness, data quality risks, implementation
   priority, normalized evidence items, a market/entity/event graph, and a feasibility
   verdict of `meaningful`, `weak`, or `blocked`.
4. `scenario --evidence-catalog ...` injects the public evidence graph into
   `scenario_report.v1` so scenarios and action candidates can show which free sources
   influenced them.
5. The ops/artifact dashboard shows source coverage, freshness, graph-driven topics, missing evidence,
   and whether the simulation is meaningful enough for the next local research step.
6. The product brief translates scenario and verdict artifacts into a beginner-facing screen.

This proof is intentionally reproducible with local cached samples. Live refresh, source
licensing review, deduplication, and stronger entity extraction remain explicit follow-up gates.

No-key live refresh is available for `gdelt-live` and `stooq-live`. These adapters try the live
source first and fall back to the cached sample shape when the network or source response is not
usable, so scheduled local runs can still produce auditable artifacts.

## Autonomous Daily Research Loop

The next product loop starts from broad interests rather than source dumps. A beginner can
configure topics such as AI infrastructure, semiconductors, US rates, consumer weakness, or
Korea semiconductors. MyBroker then proposes daily questions, collects cached free/public
evidence, updates topic memory, runs scenario simulation, and generates the beginner product
brief.

1. `topics init/add/list` manages local `topic_config.v1` interests under `config/topics.json`.
2. `research-plan` writes `daily_research_plan.v1` with daily questions, source needs, and missing-evidence notes.
3. `collect-evidence` filters no-key cached public evidence by configured interests and writes
   `reports/evidence/daily-evidence-catalog.json`.
4. The same command updates `topic_memory.v1` under `reports/memory/topic-memory.json`, so daily
   research compounds instead of starting fresh.
5. `daily-scout` writes `daily_scout.v1` under `reports/daily/scout.json`. It ranks configured
   interests using memory changes, source breadth, evidence gaps, and compiled vault notes, then
   recommends what to inspect first.
6. `source-refresh-plan` writes `source_refresh_plan.v1` under
   `reports/daily/source-refresh-plan.json`. It chooses dry-run source refresh actions for the
   scout recommendation, such as GDELT live, Stooq live, SEC sample review, or vault compile.
7. `source-refresh-apply` writes `source_refresh_apply.v1` under
   `reports/daily/source-refresh-apply.json`. It classifies each planned action as ready,
   blocked, or skipped before execution. Live network refresh remains blocked by default.
8. `source-refresh-live-gate` writes `source_refresh_live_gate.v1` under
   `reports/daily/source-refresh-live-gate.json`. It turns blocked live-network candidates into
   scoped, copy-ready approval commands without executing them.
9. `source-refresh-live-run` writes `source_refresh_live_run.v1` under
   `reports/daily/source-refresh-live-run.json`. By default it records missing approval and does
   not call the network. A later live call requires both the exact copy-ready response and explicit
   live-network execution flags.
10. `source-refresh-live-preflight` writes `source_refresh_live_preflight.v1` under
   `reports/daily/source-refresh-live-preflight.json`. It checks approval, execution intent,
   confirmation, source ids, output path, and forbidden external-effect commands without calling
   the network.
11. `appliance agenda` writes `daily_brief_agenda.v1` and `reports/product/daily-agenda.html`.
   It turns the scout recommendation into a phone-first 20-minute study sequence, source fan-out,
   weak-evidence warnings, role-specific analyst tasks, and copy-ready follow-up questions.
12. `appliance readiness` writes `daily_readiness.v1` and `reports/product/readiness.html`.
   It checks whether the phone surfaces and required artifacts are fresh enough before the
   operator trusts a daily brief, and it suggests the next local run command without executing it.
13. `daily-research` runs the local loop end to end: plan, collect, memory, scout, refresh plan,
   refresh apply packet, live gate packet, live run proof, live preflight proof, scenario, verdict, ops dashboard, rollup, and product
   brief.

Manual source ingestion can be added later, but it is not the primary beginner UX. The default
path is AI-initiated research from user interests.

## Local Personal Analyst Appliance

The next operating shape is a local appliance rather than a hosted investment app. `mybroker
appliance run` uses the existing daily research loop, then writes:

- `reports/runtime/local-analyst-playbook.json`: the runtime pattern MyBroker is following;
- `reports/runtime/phone-access.json`: private phone access guidance, preferring Tailscale Serve;
- `reports/runtime/operator-decision-packet.json`: pending operator decisions for scheduler activation, notification send, and private phone access;
- `reports/runtime/local-runtime-doctor.json`: local runtime readiness proof for runner assets, artifact freshness, notification gate, and launchd state;
- `reports/runtime/local-runtime-doctor-activation.json`: strict post-activation doctor proof that requires launchd to be loaded;
- `reports/runtime/scheduler-status.json`: scheduler install/load status plus explicit host-level commands;
- `reports/runtime/scheduler-apply.json`: dry-run or confirmed scheduler action proof;
- `reports/runtime/scheduler-run-once.json`: local runner execution proof without launchd install/load;
- `reports/runtime/scheduler-activation-preflight.json`: readiness gate before confirmed host-level activation;
- `reports/runtime/scheduler-activation-verify.json`: post-activation proof for loaded state, installed plist, strict doctor, and fresh artifacts;
- `reports/runtime/scheduler-operations.json` and `reports/product/scheduler.html`: phone-readable scheduler operations summary that separates assets ready, local run-once proof, activation preflight, activation verification, and host-write approval;
- `reports/runtime/daily-readiness.json` and `reports/product/readiness.html`: freshness/readiness proof for phone surfaces, required machine artifacts, scheduler status, and next local run action;
- `reports/vault/compile.json` and `reports/product/vault.html`: deterministic local compile proof and phone-readable vault note list when `research-vault/raw` exists;
- `reports/product/today.html`: a mobile-first `/today` surface for the phone;
- `reports/daily/scout.json`: local scout recommendations for what to inspect first;
- `reports/daily/brief-agenda.json` and `reports/product/daily-agenda.html`: the phone-first daily study agenda that says what to read first, which sources influenced it, what is weak, and what the analyst roles should do next;
- `reports/daily/source-refresh-plan.json`: dry-run source refresh actions for the scout recommendation;
- `reports/daily/source-refresh-apply.json`: dry-run execution-readiness decisions for those refresh actions;
- `reports/daily/source-refresh-live-gate.json`: scoped approval packet for blocked live-network refresh candidates;
- `reports/daily/source-refresh-live-run.json`: approval/execute proof for the live-network gate, with no network call unless explicitly approved and confirmed;
- `reports/daily/source-refresh-live-preflight.json`: no-network preflight proof before any approved live source execution;
- `reports/runtime/source-refresh-brief.json` and `reports/product/source-refresh.html`: phone-readable source refresh judgment that explains weak evidence, proposed free/no-key sources, approval status, preflight status, and the next safe action without calling the network;
- `reports/product/journal.html` and `reports/memory/analyst-journal.json`: the daily analyst work log with today's focus, role notes, weak evidence, and follow-up questions;
- `reports/product/tasks.html` and `reports/memory/analyst-task-queue.json`: role-based analyst task queue for source scout, market mapper, skeptic, tutor, librarian, and publisher work;
- `reports/product/task-ledger.html` and `reports/memory/analyst-task-ledger.json`: task status history for ready, carried, blocked, and retired analyst work;
- `reports/product/morning.html` and `reports/runtime/morning-control.json`: an operator-facing morning control packet that says what to read first, what is blocked, which short responses can close carried tasks, and which phone links are ready;
- `reports/product/memory.html` and `reports/memory/index.json`: accumulated topic memory, source relevance, and archive history;
- `reports/product/memory-query.html` and `reports/memory/latest-query.json`: deterministic recall over accumulated memory and archives;
- `reports/notifications/latest.json`: a dry-run notification payload for Telegram or Pushover;
- `reports/archive/<date>/manifest.json`: a daily archive manifest with copied artifacts;
- `ops/local/run-daily-analyst.sh` and `ops/local/com.mybroker.daily-analyst.plist` from
  `appliance init` for launchd-compatible local scheduling.

The recommended access path is private first: Tailscale Serve, private LAN, or local file. Public
Funnel/tunnel exposure is a later decision after access control and secret boundaries are reviewed. See
`docs/local-personal-analyst-appliance.md`.

This follows the Obsidian-vault pattern: each daily run remains a local artifact, while
`journal.html` records what the personal analyst concluded, doubted, and queued for tomorrow.
`tasks.html` turns that journal into role-based next work without executing it.
`task-ledger.html` records whether queued work is new, carried forward, blocked by approval, or retired from the current queue.
`task-response` and `task-status-apply` let the operator mark local task status with short
responses such as `AT-001 complete "checked source freshness"`; this updates ledger state without
executing tasks or external effects.
`morning.html` is the morning control surface: it is not the market brief, and it does not render
market-map conclusions. It reads existing artifacts, highlights pending gates, and shows copy-ready
local responses so the operator can decide the next step from a phone.
`memory.html` gives the phone-readable view of what has accumulated across runs. `appliance
query` is the librarian step: it searches accumulated topic memory and archive manifests,
writes a reproducible query artifact, and renders a phone-readable recall page for the next
question to inspect.

`appliance vault init` creates a local `research-vault/raw`, `research-vault/wiki`, and
`research-vault/output` structure. `appliance vault compile` files local markdown/text notes from
raw into deterministic wiki notes, `_master-index.md`, `reports/vault/compile.json`, and
`reports/product/vault.html`. Raw files are not deleted or moved. This keeps the Obsidian-style
inbox and librarian workflow separate from generated daily market artifacts, while still letting
compiled source notes feed the daily analyst loop.

`appliance run` auto-compiles `research-vault/raw` before the daily scout when the raw folder
exists. Use `--skip-vault-compile` for manual-only vault handling, or pass `--vault-raw-dir`,
`--vault-wiki-dir`, `--vault-output`, and `--vault-surface-output` to point the daily loop at a
different local vault. The archive manifest records both the compile proof and the vault surface.

`appliance today` reads `reports/vault/compile.json` by default when it exists. The phone-readable
`reports/product/today.html` shows the most relevant raw-source notes as "Vault에서 다시 볼 원천 노트"
and turns them into next inspection questions, so the morning brief can ask whether accumulated
source notes still agree with the latest evidence instead of treating each day as a fresh chat.
It links to `reports/product/daily-agenda.html`, a dedicated 20-minute agenda surface for reading
order, source fan-out, weak evidence, and role-based analyst work.
It also reads `reports/daily/scout.json` when present, rendering "오늘 Scout 추천" above the topic
memory cards so the operator can see which broad interest should be inspected first and why.
When `reports/daily/source-refresh-plan.json` exists, `/today` also shows "오늘 새로고침 계획" so the
operator can see which sources would be refreshed next. These are dry-run plans and must not imply
that live source calls, paid APIs, credential use, private serving, notification send, or trading
actions have occurred.
When `reports/daily/source-refresh-apply.json` exists, `/today` also shows "오늘 실행 판정" so the
operator can see which planned actions are local/dry-run ready and which are blocked behind a
separate live-network or host-effect gate.
When `reports/daily/source-refresh-live-gate.json` exists, `/today` also shows "라이브 새로고침
게이트" with copy-ready approval text. This does not run live network calls; it only defines the
approval scope and stale-context guard for a later explicit decision.
When `reports/daily/source-refresh-live-run.json` exists, `/today` also shows "라이브 실행 증거" so
the operator can see whether the gate is missing approval, ready after an exact approval response,
blocked, or executed. The default daily loop writes this proof with `external_effect_performed:
false`.
When `reports/daily/source-refresh-live-preflight.json` exists, `/today` also shows "라이브 실행
사전점검". This is the final no-network proof before an approved live source refresh: it must pass
approval, execution intent, confirmation, source id, output path, and forbidden-command checks.
`appliance memory` and `appliance query` read `reports/vault/compile.json` by default, so compiled
raw notes appear alongside topic memory and can be retrieved by the same deterministic local query
surface.

Run `appliance doctor` before installing host-level scheduling. It does not install launchd by
default; it writes a readiness proof with pass/warn/fail checks and manual install/uninstall
commands for the operator to review.
Run `appliance decision-packet` when deciding what to approve next. It does not execute external
effects; it separates scheduler activation, notification send, and private phone access into
scoped decisions with current evidence, commands, risks, and rollback notes.
Run `appliance decision apply --response "approve <decision_id> <approval_scope>"` to validate a
short operator approval against the packet and write `reports/runtime/operator-decision-apply.json`.
It still does not execute external effects; it records the exact command plan, blockers, rollback,
and `external_effect_performed=false`.
Run `appliance scheduler status` when deciding whether to activate the schedule. It records the
source asset state, installed plist state, launchd loaded state, log paths, and exact commands
without writing to `~/Library/LaunchAgents`.
Run `appliance scheduler apply --install --load --start-now` to create a dry-run activation plan.
Actual host-level writes require adding `--confirm-host-write`.
Run `appliance scheduler run-once` before host-level activation when you need proof that the
same runner script launchd would call can execute once locally. It records return code, duration,
stdout/stderr excerpts, fresh scheduler status, and doctor paths while keeping
`host_write_performed=false`.
Run `appliance scheduler activation-preflight` after status, dry-run apply, and run-once proof.
It does not install or load anything. It checks runtime doctor, scheduler assets, dry-run apply,
run-once, and notification dry-run artifacts, then records whether the next host-level command is
blocked, ready, or already active.
Run `appliance scheduler activation-verify` only after confirmed activation. It does not install
or load anything; it checks whether launchd is loaded, the installed plist exists and matches the
source asset, strict doctor passes, and recent phone/archive artifacts exist.

## First Pipeline Slice

The first vertical slice is intentionally local and auditable:

1. A price data adapter loads CSV, multiple CSV files, a directory of CSV files, or bundled sample data.
2. The research task registry selects `momentum_research_v1`.
3. Data quality checks evaluate schema, missing values, duplicate rows, date order, symbol coverage, and insufficient history.
4. The runner generates explainable signals through the existing policy gate.
5. A `research_report.v1` JSON artifact is written under `reports/runs/`.
6. The artifact validator checks schema, source metadata, data quality, signals, policy, and summary consistency.
7. The report dashboard command turns local report artifacts into an ops/artifact dashboard at `reports/dashboard.html` and `reports/report-rollup.json` so the latest run, quality status, dataset coverage, and recent run comparison can be inspected without reading raw JSON.

## Flyhigh

Flyhigh is installed into this repo:

```text
AGENTS.md
.flyhigh/
reports/runs/
```

Project-specific domain skills live in `.flyhigh/domain-skills/`.
