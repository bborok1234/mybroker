from __future__ import annotations

import html
import json
import os
import shlex
import shutil
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mybroker.topics import (
    DEFAULT_DAILY_EVIDENCE_OUTPUT,
    DEFAULT_DAILY_REVIEW_OUTPUT,
    DEFAULT_DAILY_SCOUT_OUTPUT,
    DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    DEFAULT_TOPIC_MEMORY_OUTPUT,
)
from mybroker.vault import DEFAULT_VAULT_COMPILE_OUTPUT, DEFAULT_VAULT_SURFACE_OUTPUT


TODAY_SURFACE_SCHEMA_VERSION = "today_surface.v1"
DAILY_OPERATOR_HOME_SCHEMA_VERSION = "daily_operator_home.v1"
DAILY_BRIEF_AGENDA_SCHEMA_VERSION = "daily_brief_agenda.v1"
DAILY_READINESS_SCHEMA_VERSION = "daily_readiness.v1"
SOURCE_REFRESH_BRIEF_SCHEMA_VERSION = "source_refresh_brief.v1"
SOURCE_FRESHNESS_INTAKE_SCHEMA_VERSION = "source_freshness_intake.v1"
SOURCE_REFRESH_EXECUTION_BRIEF_SCHEMA_VERSION = "source_refresh_execution_brief.v1"
HANDOFF_STUDY_RESOLUTION_SCHEMA_VERSION = "handoff_study_resolution.v1"
NOTIFICATION_SCHEMA_VERSION = "notification_delivery.v1"
ARCHIVE_SCHEMA_VERSION = "daily_archive.v1"
RUNTIME_PLAYBOOK_SCHEMA_VERSION = "personal_analyst_runtime_playbook.v1"
AGENT_PATTERN_RADAR_SCHEMA_VERSION = "agent_pattern_radar.v1"
PATTERN_EVIDENCE_INTAKE_SCHEMA_VERSION = "pattern_evidence_intake.v1"
PATTERN_DRY_RUN_PROOF_SCHEMA_VERSION = "pattern_dry_run_proof.v1"
PHONE_ACCESS_SCHEMA_VERSION = "phone_access_plan.v1"
PHONE_ACCESS_VERIFY_SCHEMA_VERSION = "phone_access_verify.v1"
OPERATOR_DECISION_PACKET_SCHEMA_VERSION = "operator_decision_packet.v1"
OPERATOR_DECISION_APPLY_SCHEMA_VERSION = "operator_decision_apply.v1"
MEMORY_INDEX_SCHEMA_VERSION = "personal_memory_index.v1"
MEMORY_QUERY_SCHEMA_VERSION = "personal_memory_query.v1"
MEMORY_AUDIT_SCHEMA_VERSION = "personal_memory_audit.v1"
ANALYST_COUNCIL_SCHEMA_VERSION = "analyst_council.v1"
ANALYST_JOURNAL_SCHEMA_VERSION = "personal_analyst_journal.v1"
LEARNING_LEDGER_SCHEMA_VERSION = "personal_learning_ledger.v1"
ANALYST_TASK_QUEUE_SCHEMA_VERSION = "personal_analyst_task_queue.v1"
ANALYST_TASK_LEDGER_SCHEMA_VERSION = "personal_analyst_task_ledger.v1"
ANALYST_TASK_STATUS_APPLY_SCHEMA_VERSION = "personal_analyst_task_status_apply.v1"
DAILY_REVIEW_SCHEMA_VERSION = "daily_review.v1"
OPERATOR_REVIEW_PROMPT_SCHEMA_VERSION = "operator_review_prompt.v1"
OPERATOR_REVIEW_EFFECT_SCHEMA_VERSION = "operator_review_effect.v1"
OPERATOR_REVIEW_RESPONSE_APPLY_SCHEMA_VERSION = "operator_review_response_apply.v1"
OPERATOR_COUNCIL_RESPONSE_APPLY_SCHEMA_VERSION = "operator_council_response_apply.v1"
OPERATOR_HANDOFF_RESPONSE_APPLY_SCHEMA_VERSION = "operator_handoff_response_apply.v1"
MORNING_CONTROL_SCHEMA_VERSION = "morning_control_packet.v1"
RUN_TRACE_SCHEMA_VERSION = "local_run_trace.v1"
DAILY_RUN_LEDGER_SCHEMA_VERSION = "daily_run_ledger.v1"
DAILY_HANDOFF_SCHEMA_VERSION = "daily_handoff.v1"
DRIFT_REVIEW_SCHEMA_VERSION = "local_drift_review.v1"
RUNTIME_DOCTOR_SCHEMA_VERSION = "local_runtime_doctor.v1"
SCHEDULER_STATUS_SCHEMA_VERSION = "local_scheduler_status.v1"
SCHEDULER_APPLY_SCHEMA_VERSION = "local_scheduler_apply.v1"
SCHEDULER_RUN_ONCE_SCHEMA_VERSION = "local_scheduler_run_once.v1"
SCHEDULER_ACTIVATION_PREFLIGHT_SCHEMA_VERSION = "local_scheduler_activation_preflight.v1"
SCHEDULER_ACTIVATION_VERIFY_SCHEMA_VERSION = "local_scheduler_activation_verify.v1"
SCHEDULER_OPERATIONS_SCHEMA_VERSION = "local_scheduler_operations.v1"
LAUNCHD_LABEL = "com.mybroker.daily-analyst"

DEFAULT_TODAY_OUTPUT = Path("reports/product/today.html")
DEFAULT_DAILY_HOME_OUTPUT = Path("reports/runtime/daily-home.json")
DEFAULT_DAILY_HOME_SURFACE = Path("reports/product/daily-home.html")
DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT = Path("reports/daily/brief-agenda.json")
DEFAULT_DAILY_BRIEF_AGENDA_SURFACE = Path("reports/product/daily-agenda.html")
DEFAULT_DAILY_READINESS_OUTPUT = Path("reports/runtime/daily-readiness.json")
DEFAULT_DAILY_READINESS_SURFACE = Path("reports/product/readiness.html")
DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT = Path("reports/runtime/source-refresh-brief.json")
DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE = Path("reports/product/source-refresh.html")
DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT = Path("reports/runtime/source-freshness-intake.json")
DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE = Path("reports/product/source-freshness-intake.html")
DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT = Path("reports/runtime/source-refresh-execution-brief.json")
DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE = Path("reports/product/source-refresh-execution.html")
DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT = Path("reports/runtime/handoff-study-resolution.json")
DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE = Path("reports/product/handoff-study-resolution.html")
DEFAULT_NOTIFICATION_OUTPUT = Path("reports/notifications/latest.json")
DEFAULT_ARCHIVE_ROOT = Path("reports/archive")
DEFAULT_RUNTIME_PLAYBOOK_OUTPUT = Path("reports/runtime/local-analyst-playbook.json")
DEFAULT_AGENT_PATTERN_RADAR_OUTPUT = Path("reports/runtime/agent-pattern-radar.json")
DEFAULT_AGENT_PATTERN_RADAR_SURFACE = Path("reports/product/pattern-radar.html")
DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT = Path("reports/runtime/pattern-evidence-intake.json")
DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE = Path("reports/product/pattern-evidence-intake.html")
DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT = Path("reports/runtime/pattern-dry-run-proof.json")
DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE = Path("reports/product/pattern-dry-run.html")
DEFAULT_PHONE_ACCESS_OUTPUT = Path("reports/runtime/phone-access.json")
DEFAULT_PHONE_ACCESS_VERIFY_OUTPUT = Path("reports/runtime/phone-access-verify.json")
DEFAULT_PHONE_ACCESS_VERIFY_SURFACE = Path("reports/product/phone-access.html")
DEFAULT_OPERATOR_DECISION_PACKET_OUTPUT = Path("reports/runtime/operator-decision-packet.json")
DEFAULT_OPERATOR_DECISION_APPLY_OUTPUT = Path("reports/runtime/operator-decision-apply.json")
DEFAULT_MEMORY_INDEX_OUTPUT = Path("reports/memory/index.json")
DEFAULT_MEMORY_OUTPUT = Path("reports/product/memory.html")
DEFAULT_MEMORY_QUERY_OUTPUT = Path("reports/memory/latest-query.json")
DEFAULT_MEMORY_QUERY_SURFACE = Path("reports/product/memory-query.html")
DEFAULT_MEMORY_AUDIT_OUTPUT = Path("reports/memory/audit.json")
DEFAULT_MEMORY_AUDIT_SURFACE = Path("reports/product/memory-audit.html")
DEFAULT_ANALYST_COUNCIL_OUTPUT = Path("reports/runtime/analyst-council.json")
DEFAULT_ANALYST_COUNCIL_SURFACE = Path("reports/product/council.html")
DEFAULT_ANALYST_JOURNAL_OUTPUT = Path("reports/product/journal.html")
DEFAULT_ANALYST_JOURNAL_ARTIFACT = Path("reports/memory/analyst-journal.json")
DEFAULT_LEARNING_LEDGER_OUTPUT = Path("reports/memory/learning-ledger.json")
DEFAULT_LEARNING_LEDGER_SURFACE = Path("reports/product/learning.html")
DEFAULT_ANALYST_TASK_QUEUE_OUTPUT = Path("reports/product/tasks.html")
DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT = Path("reports/memory/analyst-task-queue.json")
DEFAULT_ANALYST_TASK_LEDGER_OUTPUT = Path("reports/product/task-ledger.html")
DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT = Path("reports/memory/analyst-task-ledger.json")
DEFAULT_ANALYST_TASK_RESPONSES = Path("reports/memory/analyst-task-responses.jsonl")
DEFAULT_ANALYST_TASK_STATUS_APPLY = Path("reports/memory/analyst-task-status-apply.json")
DEFAULT_DAILY_REVIEW_RESPONSES = Path("reports/memory/daily-review-responses.jsonl")
DEFAULT_DAILY_REVIEW_SURFACE = Path("reports/product/review.html")
DEFAULT_REVIEW_PROMPT_OUTPUT = Path("reports/runtime/review-prompt.json")
DEFAULT_REVIEW_PROMPT_SURFACE = Path("reports/product/review-prompt.html")
DEFAULT_REVIEW_EFFECT_OUTPUT = Path("reports/runtime/review-effect.json")
DEFAULT_REVIEW_EFFECT_SURFACE = Path("reports/product/review-effect.html")
DEFAULT_REVIEW_RESPONSE_APPLY_OUTPUT = Path("reports/runtime/review-response-apply.json")
DEFAULT_REVIEW_RESPONSE_APPLY_SURFACE = Path("reports/product/review-response-apply.html")
DEFAULT_COUNCIL_RESPONSE_APPLY_OUTPUT = Path("reports/runtime/council-response-apply.json")
DEFAULT_COUNCIL_RESPONSE_APPLY_SURFACE = Path("reports/product/council-response-apply.html")
DEFAULT_HANDOFF_RESPONSES = Path("reports/memory/daily-handoff-responses.jsonl")
DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT = Path("reports/runtime/handoff-response-apply.json")
DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE = Path("reports/product/handoff-response-apply.html")
DEFAULT_MORNING_CONTROL_OUTPUT = Path("reports/runtime/morning-control.json")
DEFAULT_MORNING_CONTROL_SURFACE = Path("reports/product/morning.html")
DEFAULT_RUN_TRACE_OUTPUT = Path("reports/runtime/run-trace.json")
DEFAULT_RUN_TRACE_SURFACE = Path("reports/product/run-trace.html")
DEFAULT_DAILY_RUN_LEDGER_OUTPUT = Path("reports/runtime/daily-run-ledger.json")
DEFAULT_DAILY_RUN_LEDGER_SURFACE = Path("reports/product/run-ledger.html")
DEFAULT_DAILY_HANDOFF_OUTPUT = Path("reports/runtime/daily-handoff.json")
DEFAULT_DAILY_HANDOFF_SURFACE = Path("reports/product/handoff.html")
DEFAULT_DRIFT_REVIEW_OUTPUT = Path("reports/runtime/drift-review.json")
DEFAULT_DRIFT_REVIEW_SURFACE = Path("reports/product/drift-review.html")
DEFAULT_RUNTIME_DOCTOR_OUTPUT = Path("reports/runtime/local-runtime-doctor.json")
DEFAULT_RUNTIME_DOCTOR_ACTIVATION_OUTPUT = Path("reports/runtime/local-runtime-doctor-activation.json")
DEFAULT_SCHEDULER_STATUS_OUTPUT = Path("reports/runtime/scheduler-status.json")
DEFAULT_SCHEDULER_APPLY_OUTPUT = Path("reports/runtime/scheduler-apply.json")
DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT = Path("reports/runtime/scheduler-run-once.json")
DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT = Path("reports/runtime/scheduler-activation-preflight.json")
DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT = Path("reports/runtime/scheduler-activation-verify.json")
DEFAULT_SCHEDULER_OPERATIONS_OUTPUT = Path("reports/runtime/scheduler-operations.json")
DEFAULT_SCHEDULER_OPERATIONS_SURFACE = Path("reports/product/scheduler.html")
DEFAULT_LOCAL_OPS_DIR = Path("ops/local")


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(payload: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def esc(value: Any) -> str:
    return html.escape(str(value))


def write_runtime_playbook(output_path: str | Path = DEFAULT_RUNTIME_PLAYBOOK_OUTPUT) -> Path:
    payload = {
        "schema_version": RUNTIME_PLAYBOOK_SCHEMA_VERSION,
        "generated_at": _now(),
        "goal": "Run MyBroker as a local personal analyst appliance, not as a generic web app.",
        "absorbed_patterns": [
            {
                "source": "Hermes Agent",
                "pattern": "persistent memory, skill-like workflows, messaging gateway, scheduled loops",
                "mybroker_translation": "topic memory, CLI workflows, notification dry-runs, launchd schedule assets",
            },
            {
                "source": "OpenClaw",
                "pattern": "local workspace assistant with skills and tool routing",
                "mybroker_translation": "narrow finance-research appliance with explicit safety boundaries instead of broad file/account authority",
            },
            {
                "source": "MiroFish",
                "pattern": "graph-based simulation, personas, scenario paths, narrative maps",
                "mybroker_translation": "market map, persona views, optimistic/base/downside scenarios, beginner explanations",
            },
            {
                "source": "TradingAgents and FinRobot",
                "pattern": "role-specialized analyst debate and risk review",
                "mybroker_translation": "source scout, evidence curator, market mapper, scenario analyst, skeptic, tutor, memory librarian, publisher",
            },
            {
                "source": "Obsidian research vault workflows",
                "pattern": "local markdown/file memory that compounds over time",
                "mybroker_translation": "archive manifests, topic memory, source-linked artifacts, daily brief history",
            },
            {
                "source": "Claude Code finance research appliance workflows",
                "pattern": "plain-language operator commands, Obsidian-style memory, browser/scraper tools, recurring compile/query/audit loops",
                "mybroker_translation": "phone copy-ready commands, local vault compile, deterministic recall, review-response-apply handoff, and explicit no-external-effect proof",
            },
        ],
        "recommended_runtime": {
            "scheduler": "macOS launchd",
            "phone_access": "Tailscale Serve or private LAN URL before public deployment",
            "notification": "Pushover or Telegram via explicit environment secrets; dry-run by default",
            "storage": "local reports/ artifacts plus topic memory and daily archive",
            "run_control": "daily-run-ledger keeps one canonical run per local day and shows duplicate/manual validation runs separately",
        },
        "agent_roles": [
            "source_scout",
            "evidence_curator",
            "market_mapper",
            "scenario_analyst",
            "skeptic",
            "beginner_tutor",
            "memory_librarian",
            "publisher",
        ],
        "safety_boundaries": [
            "research_only",
            "no_brokerage_credentials",
            "no_live_trading",
            "no_discretionary_management",
            "no_unsupported_personalized_recommendations",
            "paid_or_credentialed_sources_require_explicit_approval",
        ],
    }
    return write_json(payload, output_path)


def build_agent_pattern_radar(
    *,
    playbook_path: str | Path = DEFAULT_RUNTIME_PLAYBOOK_OUTPUT,
    pattern_proof_path: str | Path = DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    playbook = _load_optional_json(playbook_path)
    previous_proof = _load_optional_json(pattern_proof_path)
    cases = [
        {
            "source": "Hermes Agent",
            "source_url": "https://github.com/NousResearch/hermes-agent",
            "observed_pattern": "persistent workspace memory, staged tool use, messaging-style handoff",
            "decision": "adopt",
            "mybroker_translation": "keep daily artifacts, task state, review memory, and morning control as local files before any external effects",
            "why": "This supports a daily operator loop without requiring a hosted web app or broad account authority.",
            "risk": "over-automation if external-effect approvals are collapsed",
            "guardrail": "prepare, approve, preflight, and execute remain separate gates",
            "priority": "high",
        },
        {
            "source": "OpenClaw",
            "source_url": "https://openclaw.ai/",
            "observed_pattern": "agent-native computer workspace with local memory and tool routing",
            "decision": "adopt",
            "mybroker_translation": "use narrow appliance commands and phone-readable surfaces instead of a generic unrestricted assistant",
            "why": "Local workspace control is useful, but MyBroker needs finance-research boundaries and explicit non-execution defaults.",
            "risk": "capability, identity, and knowledge poisoning if unchecked tools or untrusted memory shape decisions",
            "guardrail": "validate artifacts, mark source freshness, and keep credentialed or live actions behind scoped approval",
            "priority": "high",
        },
        {
            "source": "MiroFish",
            "source_url": "https://github.com/666ghj/MiroFish",
            "observed_pattern": "graph-style entity/event map, persona simulation, scenario paths",
            "decision": "adopt",
            "mybroker_translation": "market map, beginner explanations, persona viewpoints, and optimistic/base/downside paths",
            "why": "The user wants a beginner-first way to understand market flows without having to provide a precise thesis.",
            "risk": "simulation can feel authoritative when evidence is weak",
            "guardrail": "show confidence, missing evidence, stale sources, and research-only action candidates",
            "priority": "high",
        },
        {
            "source": "TradingAgents",
            "source_url": "https://github.com/TauricResearch/TradingAgents",
            "observed_pattern": "specialized analyst roles debate market, fundamentals, sentiment, and risk before a decision",
            "decision": "adopt",
            "mybroker_translation": "source scout, evidence curator, market mapper, scenario analyst, skeptic, tutor, memory librarian, publisher",
            "why": "Role separation improves coverage and makes weak evidence visible to beginners.",
            "risk": "role debate can drift into unsupported recommendations",
            "guardrail": "roles produce questions, explanations, and research-only next inspections, not trade instructions",
            "priority": "medium",
        },
        {
            "source": "FinRobot",
            "source_url": "https://github.com/AI4Finance-Foundation/FinRobot",
            "observed_pattern": "financial LLM agents grounded in reports, data, and analyst workflows",
            "decision": "adopt_partial",
            "mybroker_translation": "ground generated briefs in local artifacts, source status, and archive history",
            "why": "Grounding and auditability matter more than adding model complexity at this stage.",
            "risk": "finance-specific agents may assume paid datasets, account context, or professional workflows",
            "guardrail": "keep free/public/local evidence first and separate beginner education from execution",
            "priority": "medium",
        },
        {
            "source": "Obsidian vault research workflow",
            "source_url": "https://obsidian.md/",
            "observed_pattern": "raw inbox, compiled wiki, linked notes, recurring audit",
            "decision": "adopt",
            "mybroker_translation": "compile local raw notes into reports/vault/wiki and feed scout, memory, today, and archive",
            "why": "A personal analyst becomes useful when research compounds across days.",
            "risk": "stale or biased notes can dominate later runs",
            "guardrail": "surface source paths, freshness, and review feedback; do not delete raw notes automatically",
            "priority": "high",
        },
        {
            "source": "Claude Code finance research appliance workflow",
            "source_url": "https://x.com/leopardracer/status/2058949350315667829",
            "observed_pattern": "plain-language research operator, local knowledge base, browser automation, scraper gateway, and four verbs: clip, compile, query, audit",
            "decision": "adopt",
            "mybroker_translation": "keep the phone as a command/review surface while the laptop loop records local memory, compiles vault notes, asks for short feedback, and proves whether feedback shaped the next scout",
            "why": "The useful personal analyst pattern is not a hosted app first; it is a disciplined local research appliance whose memory compounds and whose operator handoffs are short.",
            "risk": "browser/scraper access can quietly expand authority or pull weak sources into memory",
            "guardrail": "live network, host writes, notifications, credentials, and paid/API operations stay behind scoped gates; copied feedback uses review-response-apply only",
            "priority": "high",
        },
        {
            "source": "Browser-use / Playwright / Firecrawl",
            "source_url": "https://github.com/browser-use/browser-use",
            "observed_pattern": "agent-driven browser use and web extraction can gather current evidence beyond local cache",
            "decision": "defer",
            "mybroker_translation": "treat browser and scraper tools as live-source candidates behind source-refresh preflight, not as default daily behavior",
            "why": "They can improve source freshness, but they also widen the authority and source-quality surface.",
            "risk": "unreviewed web extraction can import weak, stale, or unsafe source content into memory",
            "guardrail": "only move through source-refresh approval, preflight, cached output, and validation before it influences the daily brief",
            "priority": "watch",
        },
        {
            "source": "work-buddy",
            "source_url": "https://github.com/gusye1234/work-buddy",
            "observed_pattern": "Claude Code plus local MCP gateway, Obsidian memory, task backlog, and cross-session context",
            "decision": "adopt_partial",
            "mybroker_translation": "treat the local vault, task ledger, review log, and recall page as the first narrow gateway before adding broader tool access",
            "why": "Personal agent systems are becoming useful through disciplined local memory and gateway boundaries, not through a generic always-on web app.",
            "risk": "a broad gateway can turn stale memory or weak tasks into hidden authority",
            "guardrail": "keep gateway-like commands narrow, artifact-backed, and separately validated before any external effect",
            "priority": "high",
        },
        {
            "source": "Hermes Studio",
            "source_url": "https://github.com/JPeetz/Hermes-Studio",
            "observed_pattern": "agent operations console with cron jobs, approvals, memory graph, audit trail, cost awareness, and Kanban-style work state",
            "decision": "adopt_partial",
            "mybroker_translation": "keep the phone home, morning control, run ledger, handoff, and pattern radar as local control surfaces before building a hosted frontend",
            "why": "The useful pattern is an operator control plane over long-running work, not a generic web app first.",
            "risk": "too much console surface can bury the beginner in operational noise",
            "guardrail": "first screen shows only the next reading/action queue; detailed traces and gates stay one link away",
            "priority": "high",
        },
        {
            "source": "OpenClaw safety research",
            "source_url": "https://arxiv.org/abs/2604.04759",
            "observed_pattern": "personal agent systems need explicit protection against capability, identity, and knowledge poisoning before broad tool use",
            "decision": "adopt",
            "mybroker_translation": "treat source freshness, memory audit warnings, and scoped approvals as first-class daily artifacts before any browser, account, or host authority expands",
            "why": "A personal analyst becomes dangerous when stale memory or untrusted sources silently steer automated actions.",
            "risk": "new live-source tools can look helpful while increasing poisoning and authority risk",
            "guardrail": "live network, browser/scraper, credentials, notifications, host writes, and account access remain separate approval scopes",
            "priority": "high",
        },
        {
            "source": "SemaClaw",
            "source_url": "https://arxiv.org/abs/2604.11548",
            "observed_pattern": "agent-native work improves through harness engineering: typed DAGs, permission bridges, layered context, and agentic wiki memory",
            "decision": "adopt_partial",
            "mybroker_translation": "prefer typed local artifacts, validators, archive manifests, and vault/wiki compounding over a larger prompt-only assistant",
            "why": "The daily analyst should improve by strengthening the harness and evidence contracts, not by trusting larger unstructured prompts.",
            "risk": "overbuilding the harness can slow the actual daily learning loop",
            "guardrail": "new harness pieces must produce a phone-readable operator outcome and a validator before adoption",
            "priority": "high",
        },
        {
            "source": "Dexter",
            "source_url": "https://github.com/kamalkraj/Dexter",
            "observed_pattern": "autonomous research-agent loops with planning, source gathering, synthesis, and evaluation",
            "decision": "adopt_partial",
            "mybroker_translation": "split daily work into agenda, scout, evidence, skeptic, tutor, memory, and publisher outputs with explicit quality checks",
            "why": "A personal analyst needs repeatable research workflows and evals more than a chat-only interface.",
            "risk": "autonomous synthesis can overstate confidence when sources are thin",
            "guardrail": "show weak spots, source freshness, disagreement, and no-execution status in every user-facing research surface",
            "priority": "high",
        },
        {
            "source": "TradingAgents Lab",
            "source_url": "https://github.com/PatrickKalkman/TradingAgents",
            "observed_pattern": "local desktop research lab around multi-agent financial workflows and portfolio inspection",
            "decision": "adopt_partial",
            "mybroker_translation": "favor a local appliance and phone-readable surfaces over a hosted dashboard, while keeping execution out of scope",
            "why": "The useful part is local research ergonomics and role-specialized outputs; the risky part is drifting toward account-connected automation.",
            "risk": "desktop lab metaphors can hide execution assumptions or professional-user assumptions",
            "guardrail": "keep MyBroker beginner-first, research-only, and separate from account, order, or credential flows",
            "priority": "medium",
        },
        {
            "source": "TaskWeaver",
            "source_url": "https://github.com/microsoft/TaskWeaver",
            "observed_pattern": "code-first data analytics agent that turns requests into executable analysis steps",
            "decision": "defer",
            "mybroker_translation": "later add sandboxed data-analysis notebooks for simulations and chart generation after artifact schemas are stable",
            "why": "Code-first analytics could improve scenario simulation, but it should not precede memory quality, source quality, and clear user surfaces.",
            "risk": "generated code can create nondeterministic or unverifiable conclusions",
            "guardrail": "only run generated analysis in a sandbox with deterministic inputs, saved outputs, and validation",
            "priority": "watch",
        },
        {
            "source": "TraceAgent",
            "source_url": "https://github.com/Scale3-Labs/TraceAgent",
            "observed_pattern": "agent observability and traces for tool calls, decisions, and runtime behavior",
            "decision": "adopt_partial",
            "mybroker_translation": "add run trace artifacts that explain which local steps shaped today's brief, recall result, and follow-up queue",
            "why": "As the appliance becomes more autonomous, the operator needs traces to debug drift without reading every raw JSON file.",
            "risk": "trace volume can become another unreadable log pile",
            "guardrail": "summarize traces into a small daily proof, keep raw traces linkable, and validate freshness",
            "priority": "medium",
        },
        {
            "source": "Hermes/OpenClaw-style heartbeat ledgers",
            "source_url": "",
            "observed_pattern": "persistent local agent loops keep heartbeat, latest-run, and duplicate-run state visible to the operator",
            "decision": "adopt_partial",
            "mybroker_translation": "write a daily run ledger that identifies the canonical run for each local day, duplicate/manual runs, archive links, and no-external-effect proof",
            "why": "A scheduled personal analyst must stay understandable when launchd, manual runs, and validation runs happen on the same day.",
            "risk": "a ledger can become another unread log if it is not phone-readable",
            "guardrail": "render a compact run-ledger surface and link it from morning/readiness/trace outputs",
            "priority": "high",
        },
        {
            "source": "Hosted trading bots and broker-connected agents",
            "source_url": "",
            "observed_pattern": "always-on execution, account credentials, live orders, discretionary automation",
            "decision": "reject",
            "mybroker_translation": "none",
            "why": "This violates the current local research-only objective.",
            "risk": "financial loss, compliance risk, and unsafe personalized execution",
            "guardrail": "no brokerage credentials, no live trading, no discretionary management",
            "priority": "blocked",
        },
        {
            "source": "Farol-style exchange-connected bots",
            "source_url": "https://github.com/FredericoRB/farol",
            "observed_pattern": "self-hosted automated market agents connected to exchange credentials and live execution loops",
            "decision": "reject",
            "mybroker_translation": "none",
            "why": "This is outside the current personal learning and research appliance boundary.",
            "risk": "credential exposure, live execution loss, and unsupported personalized automation",
            "guardrail": "no exchange credentials, no account connection, no live orders, no autonomous execution",
            "priority": "blocked",
        },
    ]
    adopted = [case for case in cases if case["decision"] in {"adopt", "adopt_partial"}]
    deferred = [case for case in cases if case["decision"] == "defer"]
    rejected = [case for case in cases if case["decision"] == "reject"]
    dry_run_candidates = _pattern_dry_run_candidates(cases)
    pattern_scout = _build_pattern_scout(cases=cases, dry_run_candidates=dry_run_candidates, previous_proof=previous_proof)
    payload = {
        "schema_version": AGENT_PATTERN_RADAR_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "status": "ready",
        "objective": "Evolve MyBroker as a local daily personal analyst by absorbing only verified agentic workflow patterns.",
        "playbook_source": Path(playbook_path).as_posix(),
        "previous_pattern_proof": Path(pattern_proof_path).as_posix() if Path(pattern_proof_path).exists() else "",
        "playbook_pattern_count": len(playbook.get("absorbed_patterns", [])),
        "summary": {
            "case_count": len(cases),
            "adopted_count": len(adopted),
            "deferred_count": len(deferred),
            "rejected_count": len(rejected),
            "dry_run_candidate_count": len(dry_run_candidates),
            "ready_dry_run_count": sum(1 for item in dry_run_candidates if item["status"] == "ready"),
            "gated_dry_run_count": sum(1 for item in dry_run_candidates if item["status"] == "requires_approval"),
            "top_next_pattern": pattern_scout["recommended_next"]["title"],
        },
        "cases": cases,
        "pattern_scout": pattern_scout,
        "dry_run_candidates": dry_run_candidates,
        "adoption_gate": {
            "allowed_transitions": [
                "observed_to_candidate",
                "candidate_to_dry_run",
                "dry_run_to_adopted",
                "dry_run_to_rejected",
            ],
            "required_evidence_before_adopted": [
                "local proof artifact generated",
                "validator covers the artifact schema",
                "phone surface explains operator impact",
                "source freshness or memory quality impact is explicit",
                "external effects remain separated by approval scope",
            ],
            "blocked_transitions": [
                "observed_to_adopted_without_dry_run",
                "candidate_to_live_execution_without_preflight",
                "dry_run_to_external_effect_without_scoped_approval",
            ],
        },
        "adopted_patterns": [
            {
                "source": case["source"],
                "priority": case["priority"],
                "translation": case["mybroker_translation"],
                "guardrail": case["guardrail"],
            }
            for case in adopted
        ],
        "rejected_patterns": [
            {
                "source": case["source"],
                "why": case["why"],
                "guardrail": case["guardrail"],
            }
            for case in rejected
        ],
        "operator_next_questions": [
            "내일의 daily brief에서 어떤 주제를 더 자주 보고 싶은가?",
            "현재는 source refresh 실행보다 memory recall 품질을 먼저 높이는 것이 맞는가?",
            "host scheduler 활성화는 별도 승인할 만큼 충분히 믿을 수 있는가?",
        ],
        "next_safe_slice_candidates": [
            {
                "candidate": "memory_recall_quality",
                "why": "daily review and vault notes are now available, so recall quality can improve without external effects.",
                "requires_approval": False,
            },
            {
                "candidate": "run_trace_observability",
                "why": "the local loop now has enough steps that the operator needs a compact proof of what influenced each daily output.",
                "requires_approval": False,
            },
            {
                "candidate": "approved_no_key_source_execution",
                "why": "source refresh response and preflight exist, but actual live network execution is still a separate gate.",
                "requires_approval": True,
            },
            {
                "candidate": "host_scheduler_activation",
                "why": "scheduler operations are activation-ready, but host writes require explicit confirmation.",
                "requires_approval": True,
            },
        ],
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "pattern_radar_reads_local_research_only",
            "does_not_execute_live_network",
            "does_not_write_host_scheduler",
            "does_not_send_notifications",
            "does_not_use_credentials",
            "no_account_access",
            "no_live_trading",
        ],
    }
    return payload


def write_agent_pattern_radar(
    *,
    playbook_path: str | Path = DEFAULT_RUNTIME_PLAYBOOK_OUTPUT,
    pattern_proof_path: str | Path = DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_OUTPUT,
    surface_output_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_SURFACE,
) -> Path:
    payload = build_agent_pattern_radar(playbook_path=playbook_path, pattern_proof_path=pattern_proof_path)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_agent_pattern_radar(payload), encoding="utf-8")
    return target


def build_pattern_evidence_intake(
    *,
    pattern_radar_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_OUTPUT,
    pattern_proof_path: str | Path = DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    radar = _load_optional_json(pattern_radar_path)
    proof = _load_optional_json(pattern_proof_path)
    cases = radar.get("cases", []) if radar.get("schema_version") == AGENT_PATTERN_RADAR_SCHEMA_VERSION else []
    candidates = radar.get("dry_run_candidates", []) if radar.get("schema_version") == AGENT_PATTERN_RADAR_SCHEMA_VERSION else []
    proof_by_id = {
        row.get("candidate_id", ""): row
        for row in proof.get("candidate_results", [])
        if row.get("candidate_id")
    } if proof.get("schema_version") == PATTERN_DRY_RUN_PROOF_SCHEMA_VERSION else {}
    recommended = radar.get("pattern_scout", {}).get("recommended_next", {}) if radar.get("schema_version") == AGENT_PATTERN_RADAR_SCHEMA_VERSION else {}
    evidence_items = [
        _pattern_evidence_item(case=case, candidates=candidates, proof_by_id=proof_by_id)
        for case in cases
    ]
    candidate_assessments = [
        _pattern_candidate_assessment(candidate=candidate, proof=proof_by_id.get(candidate.get("candidate_id", ""), {}))
        for candidate in candidates
    ]
    repeated = [row for row in candidate_assessments if row.get("intake_status") == "already_verified"]
    approval_gated = [row for row in candidate_assessments if row.get("intake_status") == "approval_gated"]
    blocked = [row for row in candidate_assessments if row.get("intake_status") == "blocked"]
    unproven_local = [row for row in candidate_assessments if row.get("intake_status") == "local_candidate"]
    recommended_status = next(
        (row.get("intake_status", "missing") for row in candidate_assessments if row.get("candidate_id") == recommended.get("candidate_id")),
        "missing",
    )
    status = "ready" if unproven_local else ("review" if approval_gated else "blocked")
    payload = {
        "schema_version": PATTERN_EVIDENCE_INTAKE_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "status": status,
        "source_artifacts": {
            "pattern_radar": Path(pattern_radar_path).as_posix(),
            "pattern_dry_run_proof": Path(pattern_proof_path).as_posix(),
        },
        "summary": {
            "case_count": len(evidence_items),
            "candidate_count": len(candidate_assessments),
            "already_verified_count": len(repeated),
            "local_candidate_count": len(unproven_local),
            "approval_gated_count": len(approval_gated),
            "blocked_count": len(blocked),
            "recommended_candidate": recommended.get("candidate_id", ""),
            "recommended_candidate_status": recommended_status,
        },
        "evidence_items": evidence_items,
        "candidate_assessments": candidate_assessments,
        "next_candidate": unproven_local[0] if unproven_local else (approval_gated[0] if approval_gated else {}),
        "operator_rule": "새 agent/workflow 사례는 바로 daily loop에 섞지 않습니다. local_candidate는 proof artifact와 validator를 먼저 통과해야 하고, approval_gated는 별도 scope 승인이 필요합니다.",
        "phone_links": {
            "pattern_evidence_intake": DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE.as_posix(),
            "pattern_radar": DEFAULT_AGENT_PATTERN_RADAR_SURFACE.as_posix(),
            "pattern_dry_run": DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE.as_posix(),
            "daily_home": DEFAULT_DAILY_HOME_SURFACE.as_posix(),
            "trace": DEFAULT_RUN_TRACE_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_existing_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_open_browser_or_scraper",
            "does_not_write_host_scheduler",
            "does_not_send_notifications",
            "does_not_use_credentials",
            "no_account_access",
            "no_order_execution",
        ],
    }
    return payload


def write_pattern_evidence_intake(
    *,
    pattern_radar_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_OUTPUT,
    pattern_proof_path: str | Path = DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT,
    surface_output_path: str | Path = DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE,
) -> Path:
    payload = build_pattern_evidence_intake(pattern_radar_path=pattern_radar_path, pattern_proof_path=pattern_proof_path)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_pattern_evidence_intake(payload), encoding="utf-8")
    return target


def _pattern_evidence_item(*, case: dict[str, Any], candidates: list[dict[str, Any]], proof_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = case.get("source", "")
    linked_candidates = [
        candidate.get("candidate_id", "")
        for candidate in candidates
        if source and (source in candidate.get("source", "") or candidate.get("source", "") in source)
    ]
    proof_states = [
        proof_by_id.get(candidate_id, {}).get("proof_status", "missing")
        for candidate_id in linked_candidates
    ]
    return {
        "source": source,
        "source_url": case.get("source_url", ""),
        "decision": case.get("decision", ""),
        "priority": case.get("priority", ""),
        "observed_pattern": case.get("observed_pattern", ""),
        "mybroker_translation": case.get("mybroker_translation", ""),
        "guardrail": case.get("guardrail", ""),
        "linked_candidates": linked_candidates,
        "proof_states": proof_states,
        "intake_note": _pattern_intake_note(case=case, proof_states=proof_states),
    }


def _pattern_candidate_assessment(*, candidate: dict[str, Any], proof: dict[str, Any]) -> dict[str, Any]:
    proof_status = proof.get("proof_status", "missing")
    if proof_status == "passed":
        intake_status = "already_verified"
    elif candidate.get("status") == "requires_approval":
        intake_status = "approval_gated"
    elif candidate.get("status") == "blocked":
        intake_status = "blocked"
    else:
        intake_status = "local_candidate"
    return {
        "candidate_id": candidate.get("candidate_id", ""),
        "source": candidate.get("source", ""),
        "candidate_status": candidate.get("status", ""),
        "proof_status": proof_status,
        "intake_status": intake_status,
        "approval_scope": candidate.get("approval_scope", ""),
        "expected_artifact": candidate.get("expected_artifact", ""),
        "proof_command": candidate.get("proof_command", ""),
        "why": candidate.get("why", ""),
        "promotion_rule": candidate.get("promotion_rule", ""),
        "external_effect_performed": False,
    }


def _pattern_intake_note(*, case: dict[str, Any], proof_states: list[str]) -> str:
    if "passed" in proof_states:
        return "이미 local proof가 있는 사례입니다. 반복 추천보다 다음 미검증 후보를 봐야 합니다."
    if case.get("decision") == "defer":
        return "보류 사례입니다. live/browser/scraper/host 권한을 넓히기 전에 별도 승인과 preflight가 필요합니다."
    if case.get("decision") == "reject":
        return "거절 사례입니다. 현재 research-only 경계를 넘습니다."
    return "채택 또는 부분채택 사례입니다. local proof 후보와 연결될 때만 daily loop에 더 깊게 들어갑니다."


def validate_pattern_evidence_intake_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != PATTERN_EVIDENCE_INTAKE_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"ready", "review", "blocked"}:
        errors.append("status must be ready, review, or blocked")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    summary = payload.get("summary", {})
    for field in ["case_count", "candidate_count", "already_verified_count", "local_candidate_count", "approval_gated_count", "blocked_count", "recommended_candidate", "recommended_candidate_status"]:
        if field not in summary:
            errors.append(f"summary missing {field}")
    if not payload.get("evidence_items"):
        errors.append("evidence_items must not be empty")
    if not payload.get("candidate_assessments"):
        errors.append("candidate_assessments must not be empty")
    for index, row in enumerate(payload.get("candidate_assessments", [])):
        for field in ["candidate_id", "source", "candidate_status", "proof_status", "intake_status", "approval_scope", "expected_artifact", "proof_command", "promotion_rule"]:
            if field not in row:
                errors.append(f"candidate_assessments[{index}] missing {field}")
        if row.get("intake_status") not in {"already_verified", "local_candidate", "approval_gated", "blocked"}:
            errors.append(f"candidate_assessments[{index}] invalid intake_status")
        if row.get("external_effect_performed") is not False:
            errors.append(f"candidate_assessments[{index}] external_effect_performed must be false")
    for field in ["pattern_evidence_intake", "pattern_radar", "pattern_dry_run", "daily_home", "trace"]:
        if not payload.get("phone_links", {}).get(field):
            errors.append(f"phone_links.{field} must not be empty")
    if "reads_existing_local_artifacts_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include reads_existing_local_artifacts_only")
    return errors


def validate_pattern_evidence_intake_file(path: str | Path) -> list[str]:
    return validate_pattern_evidence_intake_payload(load_json(path))


def render_pattern_evidence_intake(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    next_candidate = payload.get("next_candidate", {})
    status_label = {
        "ready": "다음 local 후보 있음",
        "review": "승인 게이트 검토",
        "blocked": "새 local 후보 없음",
    }.get(payload.get("status", ""), payload.get("status", "review"))
    candidate_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(row.get('intake_status', ''))} · {esc(row.get('proof_status', ''))}</span>"
        f"<h2>{esc(row.get('candidate_id', ''))}</h2>"
        f"<p>{esc(row.get('why', ''))}</p>"
        f"<small>scope: {esc(row.get('approval_scope', ''))}</small>"
        f"<code>{esc(row.get('proof_command', ''))}</code>"
        "</article>"
        for row in payload.get("candidate_assessments", [])
    )
    evidence_cards = "".join(
        "<article class='mini'>"
        f"<strong>{esc(row.get('source', ''))}</strong>"
        f"<p>{esc(row.get('intake_note', ''))}</p>"
        f"<small>{esc(row.get('guardrail', ''))}</small>"
        "</article>"
        for row in payload.get("evidence_items", [])[:8]
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "pattern_evidence_intake"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Pattern Evidence Intake</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow,.card span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:32px; line-height:1.1; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small,li {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.card,.mini {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics,.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.metric,.card,.mini {{ background:white; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:27px; }}
.stack {{ display:grid; grid-template-columns:1fr; gap:10px; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:11px; color:var(--blue); font-weight:900; text-decoration:none; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:28px; }} .metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Pattern Evidence Intake · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>새 에이전트 방법론을 루프에 넣어도 되나</h1>
<p>외부 사례 자체가 아니라, 로컬 proof와 승인 경계를 기준으로 다음 후보를 분류합니다.</p>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<h2>{esc(status_label)}</h2>
<p>{esc(payload.get('operator_rule', ''))}</p>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Cases</span><strong>{esc(summary.get('case_count', 0))}</strong></article>
<article class="metric"><span>Local candidates</span><strong>{esc(summary.get('local_candidate_count', 0))}</strong></article>
<article class="metric"><span>Already verified</span><strong>{esc(summary.get('already_verified_count', 0))}</strong></article>
<article class="metric"><span>Approval gated</span><strong>{esc(summary.get('approval_gated_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>다음 후보</h2>
<article class="card">
<span>{esc(next_candidate.get('intake_status', 'missing'))}</span>
<h2>{esc(next_candidate.get('candidate_id', '후보 없음'))}</h2>
<p>{esc(next_candidate.get('why', '새 local 후보가 없습니다. approval-gated 후보는 별도 승인 전까지 보류합니다.'))}</p>
</article>
</section>
<section class="section">
<h2>후보 판정</h2>
<div class="stack">{candidate_cards}</div>
</section>
<section class="section">
<h2>근거 사례</h2>
<div class="stack">{evidence_cards}</div>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
</main>
</body>
</html>
"""


def _build_pattern_scout(*, cases: list[dict[str, Any]], dry_run_candidates: list[dict[str, Any]], previous_proof: dict[str, Any] | None = None) -> dict[str, Any]:
    passed_ids = {
        row.get("candidate_id", "")
        for row in (previous_proof or {}).get("candidate_results", [])
        if row.get("proof_status") == "passed"
    }
    ready_local = [
        candidate
        for candidate in dry_run_candidates
        if candidate.get("status") == "ready" and candidate.get("approval_scope") == "local_dry_run_only"
    ]
    unproven_ready = [candidate for candidate in ready_local if candidate.get("candidate_id") not in passed_ids]
    recommended = next(
        (candidate for candidate in unproven_ready if candidate.get("candidate_id") == "pattern-method-evidence-intake"),
        unproven_ready[0] if unproven_ready else (ready_local[0] if ready_local else {}),
    )
    watchlist = [
        {
            "source": case.get("source", ""),
            "why_watch": case.get("why", ""),
            "blocked_by": case.get("guardrail", ""),
            "decision": case.get("decision", ""),
        }
        for case in cases
        if case.get("decision") == "defer"
    ]
    rejected = [
        {
            "source": case.get("source", ""),
            "why_rejected": case.get("why", ""),
            "boundary": case.get("guardrail", ""),
        }
        for case in cases
        if case.get("decision") == "reject"
    ]
    return {
        "status": "ready" if recommended else "blocked",
        "cadence": "run inside the daily appliance loop before adopting or widening any agent workflow pattern",
        "recommended_next": {
            "candidate_id": recommended.get("candidate_id", ""),
            "title": _pattern_candidate_title(recommended.get("candidate_id", "")),
            "source": recommended.get("source", ""),
            "why_now": recommended.get(
                "why",
                "새 agent 사례가 빠르게 바뀌므로 live authority를 넓히기 전에 로컬 레이더와 증거 계약부터 갱신합니다.",
            ),
            "proof_command": recommended.get("proof_command", ""),
            "approval_scope": recommended.get("approval_scope", ""),
            "previously_passed_candidate_count": len(passed_ids),
            "operator_decision_needed": recommended.get("approval_scope") != "local_dry_run_only",
            "done_when": [
                "agent_pattern_radar.v1 validates",
                "pattern-radar phone surface shows the recommended next local experiment",
                "deferred and rejected patterns remain explicit",
                "external_effect_performed and host_write_performed remain false",
            ],
        },
        "deferred_watchlist": watchlist,
        "rejected_boundary": rejected,
        "operator_rule": "새 사례는 바로 채택하지 않습니다. 먼저 local-only proof, validator, phone-readable impact, safety boundary를 통과해야 합니다.",
        "external_effect_performed": False,
        "host_write_performed": False,
    }


def _pattern_candidate_title(candidate_id: str) -> str:
    titles = {
        "pattern-freshness-intake": "source freshness intake before live authority",
        "pattern-method-evidence-intake": "pattern evidence intake before workflow adoption",
        "pattern-source-refresh-execution-confirmation": "source refresh execution confirmation before live fetch",
        "pattern-memory-recall-quality": "memory recall quality before daily briefing",
        "pattern-run-trace-observability": "run trace observability before autonomous loop widening",
    }
    return titles.get(candidate_id, "local-only pattern proof before wider authority")


def validate_agent_pattern_radar_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != AGENT_PATTERN_RADAR_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    cases = payload.get("cases", [])
    if len(cases) < 5:
        errors.append("cases must include at least 5 researched patterns")
    allowed = {"adopt", "adopt_partial", "defer", "reject"}
    for index, case in enumerate(cases):
        if case.get("decision") not in allowed:
            errors.append(f"cases[{index}] invalid decision {case.get('decision')}")
        for key in ["source", "observed_pattern", "mybroker_translation", "why", "risk", "guardrail"]:
            if not str(case.get(key, "")).strip():
                errors.append(f"cases[{index}] missing {key}")
    if not payload.get("adopted_patterns"):
        errors.append("adopted_patterns must not be empty")
    if not payload.get("dry_run_candidates"):
        errors.append("dry_run_candidates must not be empty")
    scout = payload.get("pattern_scout", {})
    if scout.get("status") not in {"ready", "blocked"}:
        errors.append("pattern_scout status must be ready or blocked")
    recommended = scout.get("recommended_next", {})
    for key in ["candidate_id", "title", "source", "why_now", "proof_command", "approval_scope", "done_when"]:
        if not recommended.get(key):
            errors.append(f"pattern_scout recommended_next missing {key}")
    if scout.get("external_effect_performed") is not False:
        errors.append("pattern_scout external_effect_performed must be false")
    if scout.get("host_write_performed") is not False:
        errors.append("pattern_scout host_write_performed must be false")
    if not scout.get("deferred_watchlist"):
        errors.append("pattern_scout deferred_watchlist must not be empty")
    if not scout.get("rejected_boundary"):
        errors.append("pattern_scout rejected_boundary must not be empty")
    for index, candidate in enumerate(payload.get("dry_run_candidates", [])):
        for key in ["candidate_id", "source", "status", "proof_command", "expected_artifact", "approval_scope", "promotion_rule"]:
            if not str(candidate.get(key, "")).strip():
                errors.append(f"dry_run_candidates[{index}] missing {key}")
        if candidate.get("status") not in {"ready", "requires_approval", "blocked"}:
            errors.append(f"dry_run_candidates[{index}] invalid status")
        if candidate.get("external_effect_performed") is not False:
            errors.append(f"dry_run_candidates[{index}] external_effect_performed must be false")
        command = candidate.get("proof_command", "")
        if candidate.get("approval_scope") == "local_dry_run_only" and any(fragment in command for fragment in ["--send", "--confirm-host-write", "launchctl", "tailscale serve --bg"]):
            errors.append(f"dry_run_candidates[{index}] local proof command crosses external-effect boundary")
    gate = payload.get("adoption_gate", {})
    if "dry_run_to_adopted" not in gate.get("allowed_transitions", []):
        errors.append("adoption_gate must include dry_run_to_adopted transition")
    if "does_not_execute_live_network" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_execute_live_network")
    return errors


def validate_agent_pattern_radar_file(path: str | Path) -> list[str]:
    return validate_agent_pattern_radar_payload(load_json(path))


def _pattern_proof_artifact_check(*, candidate: dict[str, Any], payload: dict[str, Any], surface_path: Path) -> tuple[str, list[str]]:
    candidate_id = candidate.get("candidate_id", "")
    reasons: list[str] = []
    status = "passed"
    if candidate.get("approval_scope") != "local_dry_run_only":
        return "approval_required", ["승격하려면 별도 승인 scope가 필요합니다."]
    if not payload:
        return "failed", ["기대 artifact가 없습니다."]
    if candidate_id == "pattern-memory-recall-quality":
        errors = validate_memory_audit_payload(payload)
        if errors:
            status = "failed"
            reasons.extend(errors)
        if payload.get("status") not in {"ready", "needs_attention", "blocked"}:
            status = "failed"
            reasons.append("memory audit status가 허용 범위 밖입니다.")
        if not surface_path.exists():
            status = "failed"
            reasons.append("phone-readable memory audit surface가 없습니다.")
    elif candidate_id == "pattern-run-trace-observability":
        errors = validate_run_trace_payload(payload)
        if errors:
            status = "failed"
            reasons.extend(errors)
        if payload.get("status") not in {"ready", "review", "blocked"}:
            status = "failed"
            reasons.append("run trace status가 허용 범위 밖입니다.")
        if not surface_path.exists():
            status = "failed"
            reasons.append("phone-readable run trace surface가 없습니다.")
    elif candidate_id == "pattern-freshness-intake":
        errors = validate_agent_pattern_radar_payload(payload)
        if errors:
            status = "failed"
            reasons.extend(errors)
        candidates = payload.get("dry_run_candidates", [])
        if not any(row.get("candidate_id") == "pattern-freshness-intake" and row.get("status") == "ready" for row in candidates):
            status = "failed"
            reasons.append("pattern freshness intake 후보가 ready 상태로 남아 있지 않습니다.")
        if not surface_path.exists():
            status = "failed"
            reasons.append("phone-readable pattern radar surface가 없습니다.")
    elif candidate_id == "pattern-method-evidence-intake":
        errors = validate_pattern_evidence_intake_payload(payload)
        if errors:
            status = "failed"
            reasons.extend(errors)
        if payload.get("status") not in {"ready", "review", "blocked"}:
            status = "failed"
            reasons.append("pattern evidence intake status가 허용 범위 밖입니다.")
        if not surface_path.exists():
            status = "failed"
            reasons.append("phone-readable pattern evidence intake surface가 없습니다.")
    elif candidate_id == "pattern-source-refresh-execution-confirmation":
        errors = validate_source_refresh_execution_brief_payload(payload)
        if errors:
            status = "failed"
            reasons.extend(errors)
        if payload.get("status") not in {"not_required", "approval_required", "preflight_required", "ready_for_final_confirmation", "executed", "blocked"}:
            status = "failed"
            reasons.append("source refresh execution status가 허용 범위 밖입니다.")
        if not surface_path.exists():
            status = "failed"
            reasons.append("phone-readable source refresh execution surface가 없습니다.")
    else:
        status = "blocked"
        reasons.append("이 후보에 대한 local proof 규칙이 아직 없습니다.")
    if payload.get("external_effect_performed") is not False:
        status = "failed"
        reasons.append("external_effect_performed가 false가 아닙니다.")
    if payload.get("host_write_performed") is not False:
        status = "failed"
        reasons.append("host_write_performed가 false가 아닙니다.")
    if not reasons:
        reasons.append("로컬 artifact와 phone surface가 있고 외부 효과 플래그가 없습니다.")
    return status, reasons


def _pattern_proof_surface_for_candidate(candidate_id: str) -> Path:
    if candidate_id == "pattern-memory-recall-quality":
        return DEFAULT_MEMORY_AUDIT_SURFACE
    if candidate_id == "pattern-run-trace-observability":
        return DEFAULT_RUN_TRACE_SURFACE
    if candidate_id == "pattern-freshness-intake":
        return DEFAULT_AGENT_PATTERN_RADAR_SURFACE
    if candidate_id == "pattern-method-evidence-intake":
        return DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE
    if candidate_id == "pattern-source-refresh-execution-confirmation":
        return DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE
    if candidate_id == "pattern-live-source-browser-gateway":
        return DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE
    return Path("reports/product/missing.html")


def build_pattern_dry_run_proof(
    *,
    pattern_radar_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(timezone.utc)
    radar = load_json(pattern_radar_path)
    candidates = radar.get("dry_run_candidates", [])
    results: list[dict[str, Any]] = []
    for candidate in candidates:
        artifact_path = Path(candidate.get("expected_artifact", ""))
        surface_path = _pattern_proof_surface_for_candidate(candidate.get("candidate_id", ""))
        payload = _load_optional_json(artifact_path)
        if candidate.get("status") == "requires_approval":
            proof_status = "approval_required"
            proof_notes = ["live network, browser, scraper, credential, 또는 host write 경계는 별도 승인 전에는 실행하지 않습니다."]
        elif candidate.get("status") == "blocked":
            proof_status = "blocked"
            proof_notes = [candidate.get("why", "아직 deterministic local proof가 없습니다.")]
        else:
            proof_status, proof_notes = _pattern_proof_artifact_check(candidate=candidate, payload=payload, surface_path=surface_path)
        results.append({
            "candidate_id": candidate.get("candidate_id", ""),
            "source": candidate.get("source", ""),
            "input_status": candidate.get("status", ""),
            "approval_scope": candidate.get("approval_scope", ""),
            "proof_status": proof_status,
            "expected_artifact": artifact_path.as_posix(),
            "artifact_exists": artifact_path.exists(),
            "artifact_schema_version": payload.get("schema_version", "missing"),
            "surface": surface_path.as_posix(),
            "surface_exists": surface_path.exists(),
            "promotion_rule": candidate.get("promotion_rule", ""),
            "proof_notes": proof_notes,
            "external_effect_performed": False,
            "host_write_performed": False,
        })
    passed = [row for row in results if row.get("proof_status") == "passed"]
    approval_required = [row for row in results if row.get("proof_status") == "approval_required"]
    blocked = [row for row in results if row.get("proof_status") == "blocked"]
    failed = [row for row in results if row.get("proof_status") == "failed"]
    return {
        "schema_version": PATTERN_DRY_RUN_PROOF_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": "blocked" if failed else ("proof_ready" if passed else "review"),
        "source_artifact": Path(pattern_radar_path).as_posix(),
        "summary": {
            "candidate_count": len(results),
            "passed_count": len(passed),
            "approval_required_count": len(approval_required),
            "blocked_count": len(blocked),
            "failed_count": len(failed),
        },
        "promotion_decisions": [
            {
                "candidate_id": row["candidate_id"],
                "decision": "adopted_proof_ready",
                "reason": "로컬 proof artifact와 phone surface가 검증됐으므로 daily loop에 더 깊게 연결할 수 있습니다.",
                "requires_operator_approval": False,
            }
            for row in passed
        ],
        "candidate_results": results,
        "operator_reading_order": [
            "summary",
            "promotion_decisions",
            "candidate_results",
            "safety_boundary",
        ],
        "phone_links": {
            "pattern_radar": DEFAULT_AGENT_PATTERN_RADAR_SURFACE.as_posix(),
            "memory_audit": DEFAULT_MEMORY_AUDIT_SURFACE.as_posix(),
            "run_trace": DEFAULT_RUN_TRACE_SURFACE.as_posix(),
            "source_refresh": DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_existing_local_artifacts_only",
            "does_not_execute_candidate_commands",
            "does_not_fetch_live_network",
            "does_not_open_browser_or_scraper",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_order_execution",
            "external_effects_require_separate_gate",
        ],
    }


def validate_pattern_dry_run_proof_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != PATTERN_DRY_RUN_PROOF_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"proof_ready", "review", "blocked"}:
        errors.append(f"invalid status {payload.get('status')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if not payload.get("candidate_results"):
        errors.append("candidate_results must not be empty")
    for index, row in enumerate(payload.get("candidate_results", [])):
        for field in ["candidate_id", "source", "approval_scope", "proof_status", "expected_artifact", "artifact_exists", "surface", "surface_exists", "promotion_rule"]:
            if field not in row:
                errors.append(f"candidate_results[{index}] missing {field}")
        if row.get("proof_status") not in {"passed", "approval_required", "blocked", "failed"}:
            errors.append(f"candidate_results[{index}] invalid proof_status")
        if row.get("external_effect_performed") is not False:
            errors.append(f"candidate_results[{index}] external_effect_performed must be false")
        if row.get("host_write_performed") is not False:
            errors.append(f"candidate_results[{index}] host_write_performed must be false")
        if row.get("proof_status") == "passed" and (not row.get("artifact_exists") or not row.get("surface_exists")):
            errors.append(f"candidate_results[{index}] passed proof requires artifact and surface")
        if row.get("approval_scope") != "local_dry_run_only" and row.get("proof_status") == "passed":
            errors.append(f"candidate_results[{index}] non-local scope cannot pass dry-run proof")
    boundary = payload.get("safety_boundary", [])
    for required in ["reads_existing_local_artifacts_only", "does_not_execute_candidate_commands", "does_not_fetch_live_network"]:
        if required not in boundary:
            errors.append(f"safety_boundary must include {required}")
    if payload.get("summary", {}).get("passed_count", 0) < 1:
        errors.append("at least one local candidate must pass")
    return errors


def validate_pattern_dry_run_proof_file(path: str | Path) -> list[str]:
    return validate_pattern_dry_run_proof_payload(load_json(path))


def render_pattern_dry_run_proof(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    status_label = {
        "proof_ready": "로컬 채택 후보 있음",
        "review": "검토 필요",
        "blocked": "막힌 증거 있음",
    }.get(payload.get("status", ""), payload.get("status", "review"))
    result_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(row.get('proof_status', 'review'))} · {esc(row.get('approval_scope', ''))}</span>"
        f"<h2>{esc(row.get('source', ''))}</h2>"
        f"<strong>{esc(row.get('candidate_id', ''))}</strong>"
        f"<p>{esc('; '.join(row.get('proof_notes', [])[:2]))}</p>"
        f"<small>Artifact: {esc(row.get('expected_artifact', ''))} · Surface: {esc(row.get('surface', ''))}</small>"
        "</article>"
        for row in payload.get("candidate_results", [])
    )
    decision_cards = "".join(
        "<article class='mini'>"
        f"<strong>{esc(item.get('candidate_id', ''))}</strong>"
        f"<p>{esc(item.get('reason', ''))}</p>"
        "</article>"
        for item in payload.get("promotion_decisions", [])
    ) or "<p>아직 daily loop에 더 깊게 연결할 local proof 후보가 없습니다.</p>"
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if path
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Pattern Dry-run Proof</title>
<style>
:root {{ --bg:#f8f7f2; --ink:#17212b; --muted:#66717e; --line:#dfe2d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; --bad:#9f2d2d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:900px; margin:0 auto; padding:16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:20px; }}
p,small {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics,.grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric,.card,.mini {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; min-width:0; }}
.metric strong {{ display:block; font-size:24px; }}
.card span {{ color:var(--green); font-size:12px; font-weight:900; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
@media (max-width:680px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.grid,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Pattern Proof · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>새 에이전트 패턴을 실제 루프에 넣어도 되는가</h1>
<p>후보 명령을 실행하지 않고 기존 로컬 artifact와 phone surface만 읽어 승격 가능성을 판정합니다.</p>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<strong class="status">{esc(status_label)}</strong>
<div class="metrics">
<article class="metric"><span>후보</span><strong>{esc(summary.get('candidate_count', 0))}</strong></article>
<article class="metric"><span>통과</span><strong>{esc(summary.get('passed_count', 0))}</strong></article>
<article class="metric"><span>승인필요</span><strong>{esc(summary.get('approval_required_count', 0))}</strong></article>
<article class="metric"><span>막힘</span><strong>{esc(summary.get('blocked_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>승격 가능한 후보</h2>
<div class="grid">{decision_cards}</div>
</section>
<section class="section">
<h2>후보별 dry-run 증거</h2>
<div class="grid">{result_cards}</div>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 live network, browser/scraper, credential, 알림 발송, host scheduler write, 계좌 접근, 주문 실행을 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def write_pattern_dry_run_proof(
    *,
    pattern_radar_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT,
    surface_output_path: str | Path = DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE,
) -> Path:
    payload = build_pattern_dry_run_proof(pattern_radar_path=pattern_radar_path)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_pattern_dry_run_proof(payload), encoding="utf-8")
    return target


def _pattern_dry_run_candidates(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_source = {case.get("source", ""): case for case in cases}
    rows = [
        {
            "candidate_id": "pattern-freshness-intake",
            "source": "Hermes Studio / OpenClaw safety research / SemaClaw",
            "status": "ready",
            "why": "New personal-agent practices change quickly, so the daily loop needs a local proof that the radar has absorbed current patterns without widening authority.",
            "proof_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker validate-agent-pattern-radar reports/runtime/agent-pattern-radar.json",
            "expected_artifact": "reports/runtime/agent-pattern-radar.json",
            "approval_scope": "local_dry_run_only",
            "promotion_rule": "Adopt only if pattern_scout recommends a local next experiment, deferred/rejected boundaries remain explicit, and the phone surface validates.",
            "source_decision": "adopt_partial",
            "external_effect_performed": False,
        },
        {
            "candidate_id": "pattern-method-evidence-intake",
            "source": "Hermes / OpenClaw / MiroFish / TradingAgents / Obsidian vault research",
            "status": "ready",
            "why": "The radar currently absorbs researched practices as static cases; the next safe step is a local evidence intake that shows which cases are new, already proven, stale, approval-gated, or rejected before they alter the daily loop.",
            "proof_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker validate-pattern-evidence-intake reports/runtime/pattern-evidence-intake.json",
            "expected_artifact": "reports/runtime/pattern-evidence-intake.json",
            "approval_scope": "local_dry_run_only",
            "promotion_rule": "Adopt only if the intake validates, shows stale/repeated recommendations, links the phone surface, and keeps external_effect_performed false.",
            "source_decision": "adopt_partial",
            "external_effect_performed": False,
        },
        {
            "candidate_id": "pattern-source-refresh-execution-confirmation",
            "source": "OpenClaw safety research / source freshness gate",
            "status": "ready",
            "why": "Approval response and preflight need a final phone-readable confirmation layer before any live source execution.",
            "proof_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker validate-source-refresh-execution-brief reports/runtime/source-refresh-execution-brief.json",
            "expected_artifact": "reports/runtime/source-refresh-execution-brief.json",
            "approval_scope": "local_dry_run_only",
            "promotion_rule": "Adopt only if approval, preflight, final confirmation, and actual execution remain separate states.",
            "source_decision": "adopt_partial",
            "external_effect_performed": False,
        },
        {
            "candidate_id": "pattern-memory-recall-quality",
            "source": "Obsidian vault research workflow",
            "status": "ready",
            "why": "Local vault, memory, archive, and audit artifacts can be evaluated without external effects.",
            "proof_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance audit",
            "expected_artifact": "reports/memory/audit.json",
            "approval_scope": "local_dry_run_only",
            "promotion_rule": "Adopt only if memory audit artifact validates and phone surface shows stale or weak coverage clearly.",
            "source_decision": by_source.get("Obsidian vault research workflow", {}).get("decision", "observed"),
            "external_effect_performed": False,
        },
        {
            "candidate_id": "pattern-run-trace-observability",
            "source": "TraceAgent",
            "status": "ready",
            "why": "Run trace already exists and can prove which local steps influenced the daily loop.",
            "proof_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker validate-run-trace reports/runtime/run-trace.json",
            "expected_artifact": "reports/runtime/run-trace.json",
            "approval_scope": "local_dry_run_only",
            "promotion_rule": "Adopt only if trace stays compact, fresh, and linked from daily home/readiness surfaces.",
            "source_decision": by_source.get("TraceAgent", {}).get("decision", "observed"),
            "external_effect_performed": False,
        },
        {
            "candidate_id": "pattern-live-source-browser-gateway",
            "source": "Browser-use / Playwright / Firecrawl",
            "status": "requires_approval",
            "why": "Browser/scraper tools can improve freshness but cross the live-network boundary.",
            "proof_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance source-refresh-live-preflight --intend-execute --confirm-live-network",
            "expected_artifact": "reports/daily/source-refresh-live-preflight.json",
            "approval_scope": "live_network_refresh",
            "promotion_rule": "Adopt only after scoped approval, preflight, cached output validation, and source freshness labeling.",
            "source_decision": by_source.get("Browser-use / Playwright / Firecrawl", {}).get("decision", "observed"),
            "external_effect_performed": False,
        },
        {
            "candidate_id": "pattern-code-analytics-sandbox",
            "source": "TaskWeaver",
            "status": "blocked",
            "why": "Generated analysis code needs a deterministic sandbox and report schema before it can shape the daily brief.",
            "proof_command": "not_available_until_sandbox_schema_exists",
            "expected_artifact": "reports/runtime/analytics-sandbox-proof.json",
            "approval_scope": "future_local_sandbox",
            "promotion_rule": "Adopt only after deterministic inputs, saved outputs, validator, and no external effect proof exist.",
            "source_decision": by_source.get("TaskWeaver", {}).get("decision", "observed"),
            "external_effect_performed": False,
        },
    ]
    return rows


def render_agent_pattern_radar(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    scout = payload.get("pattern_scout", {})
    recommended = scout.get("recommended_next", {})
    done_when = "".join(f"<li>{esc(item)}</li>" for item in recommended.get("done_when", []))
    deferred_cards = "".join(
        "<article class='mini'>"
        f"<strong>{esc(item.get('source', ''))}</strong>"
        f"<p>{esc(item.get('why_watch', ''))}</p>"
        f"<small>{esc(item.get('blocked_by', ''))}</small>"
        "</article>"
        for item in scout.get("deferred_watchlist", [])
    ) or "<p>오늘 보류 중인 패턴은 없습니다.</p>"
    boundary_cards = "".join(
        "<article class='mini reject'>"
        f"<strong>{esc(item.get('source', ''))}</strong>"
        f"<p>{esc(item.get('why_rejected', ''))}</p>"
        f"<small>{esc(item.get('boundary', ''))}</small>"
        "</article>"
        for item in scout.get("rejected_boundary", [])
    ) or "<p>명시적으로 거부한 경계가 없습니다.</p>"
    case_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(case.get('decision', 'review'))} · {esc(case.get('priority', ''))}</span>"
        f"<h2>{esc(case.get('source', ''))}</h2>"
        f"<p>{esc(case.get('observed_pattern', ''))}</p>"
        f"<strong>MyBroker 적용</strong><p>{esc(case.get('mybroker_translation', ''))}</p>"
        f"<small>Guardrail: {esc(case.get('guardrail', ''))}</small>"
        "</article>"
        for case in payload.get("cases", [])
    )
    adopted_cards = "".join(
        "<article class='mini'>"
        f"<strong>{esc(item.get('source', ''))}</strong>"
        f"<p>{esc(item.get('translation', ''))}</p>"
        "</article>"
        for item in payload.get("adopted_patterns", [])
    )
    rejected_cards = "".join(
        "<article class='mini reject'>"
        f"<strong>{esc(item.get('source', ''))}</strong>"
        f"<p>{esc(item.get('why', ''))}</p>"
        "</article>"
        for item in payload.get("rejected_patterns", [])
    ) or "<p>명시적으로 거부한 패턴이 없습니다.</p>"
    question_items = "".join(f"<li>{esc(question)}</li>" for question in payload.get("operator_next_questions", []))
    next_cards = "".join(
        "<article class='mini'>"
        f"<strong>{esc(item.get('candidate', ''))}</strong>"
        f"<p>{esc(item.get('why', ''))}</p>"
        f"<small>승인 필요: {esc('예' if item.get('requires_approval') else '아니오')}</small>"
        "</article>"
        for item in payload.get("next_safe_slice_candidates", [])
    )
    dry_run_cards = "".join(
        "<article class='mini'>"
        f"<strong>{esc(item.get('source', ''))}</strong>"
        f"<p>{esc(item.get('why', ''))}</p>"
        f"<small>{esc(item.get('status', ''))} · {esc(item.get('approval_scope', ''))}</small>"
        f"<code>{esc(item.get('proof_command', ''))}</code>"
        "</article>"
        for item in payload.get("dry_run_candidates", [])
    )
    gate_items = "".join(
        f"<li>{esc(item)}</li>"
        for item in payload.get("adoption_gate", {}).get("required_evidence_before_adopted", [])
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Pattern Radar</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:860px; margin:0 auto; padding:18px; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small,li {{ color:var(--muted); overflow-wrap:anywhere; }}
.eyebrow,.card span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.hero,.section,.card,.mini {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics,.grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
.metric,.card,.mini {{ background:white; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:28px; }}
.stack {{ display:grid; grid-template-columns:minmax(0,1fr); gap:10px; }}
.reject {{ border-color:#d7b36a; }}
@media (max-width:680px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Pattern Radar · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>개인 애널리스트 방식 업데이트</h1>
<p>최신 agentic workflow 사례에서 검증된 패턴만 로컬 daily analyst loop에 흡수하기 위한 운영 레이더입니다.</p>
</header>
	<section class="hero">
	<span class="eyebrow">이번 판단</span>
	<h2>{esc(summary.get('top_next_pattern', 'pattern freshness audit'))}</h2>
	<p>{esc(payload.get('objective', ''))}</p>
<div class="metrics">
<article class="metric"><span>Cases</span><strong>{esc(summary.get('case_count', 0))}</strong></article>
<article class="metric"><span>Adopt</span><strong>{esc(summary.get('adopted_count', 0))}</strong></article>
<article class="metric"><span>Dry-run</span><strong>{esc(summary.get('dry_run_candidate_count', 0))}</strong></article>
	</div>
	</section>
	<section class="section">
	<h2>오늘의 방식 Scout</h2>
	<div class="grid">
	<article class="mini">
	<strong>{esc(recommended.get('title', '다음 local 실험 없음'))}</strong>
	<p>{esc(recommended.get('why_now', ''))}</p>
	<small>{esc(recommended.get('source', ''))} · {esc(recommended.get('approval_scope', ''))}</small>
	<code>{esc(recommended.get('proof_command', ''))}</code>
	</article>
	<article class="mini">
	<strong>Done when</strong>
	<ul>{done_when}</ul>
	</article>
	<article class="mini">
	<strong>운영 규칙</strong>
	<p>{esc(scout.get('operator_rule', '새 패턴은 proof 없이 채택하지 않습니다.'))}</p>
	</article>
	</div>
	</section>
	<section class="section">
	<h2>Dry-run 승격 큐</h2>
	<div class="grid">{dry_run_cards}</div>
	</section>
	<section class="section">
	<h2>보류 중인 최신 패턴</h2>
	<div class="grid">{deferred_cards}</div>
	</section>
	<section class="section">
	<h2>넘지 않을 경계</h2>
	<div class="stack">{boundary_cards}</div>
	</section>
	<section class="section">
	<h2>채택 게이트</h2>
<ul>{gate_items}</ul>
</section>
<section class="section">
<h2>사례별 채택/거부 판단</h2>
<div class="stack">{case_cards}</div>
</section>
<section class="section">
<h2>이번에 흡수한 패턴</h2>
<div class="grid">{adopted_cards}</div>
</section>
<section class="section">
<h2>명시적으로 피할 패턴</h2>
<div class="stack">{rejected_cards}</div>
</section>
<section class="section">
<h2>다음 안전한 slice 후보</h2>
<div class="grid">{next_cards}</div>
</section>
<section class="section">
<h2>내일 사람이 판단할 질문</h2>
<ul>{question_items}</ul>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 레이더는 로컬 리서치와 운영 방식만 갱신합니다. live network, host scheduler write, 알림 전송, credential 사용, 계좌 접근, 주문 실행을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def write_phone_access_plan(
    *,
    output_path: str | Path = DEFAULT_PHONE_ACCESS_OUTPUT,
    port: int = 8787,
    tailnet_host: str = "mybroker-mac",
) -> Path:
    payload = {
        "schema_version": PHONE_ACCESS_SCHEMA_VERSION,
        "generated_at": _now(),
        "recommended_path": "tailscale_serve_private",
        "local_url": f"http://localhost:{port}/reports/product/daily-home.html",
        "private_phone_url": f"https://{tailnet_host}/reports/product/daily-home.html",
        "entrypoint": DEFAULT_DAILY_HOME_SURFACE.as_posix(),
        "commands": [
            {
                "purpose": "serve local MyBroker artifacts",
                "command": f"cd <mybroker-repo> && python3 -m http.server {port}",
            },
            {
                "purpose": "share the local server only inside the tailnet",
                "command": f"tailscale serve --bg {port}",
            },
            {
                "purpose": "stop private serving",
                "command": "tailscale serve reset",
            },
        ],
        "do_not_default_to": [
            "public_tunnel",
            "funnel",
            "unauthenticated_public_hosting",
        ],
        "operator_checklist": [
            "MacBook remains powered and awake enough for scheduled jobs.",
            "Phone is on the same tailnet or private LAN.",
            "No secret values are committed to the repository.",
            "Notification sender is tested with dry-run before --send.",
        ],
    }
    return write_json(payload, output_path)


def _project_path(root: Path, path: str | Path) -> Path:
    target = Path(path)
    return target if target.is_absolute() else root / target


def _local_href_targets(html_text: str) -> list[str]:
    targets: list[str] = []
    marker = "href='"
    for part in html_text.split(marker)[1:]:
        href = part.split("'", 1)[0].strip()
        if href:
            targets.append(href)
    marker = 'href="'
    for part in html_text.split(marker)[1:]:
        href = part.split('"', 1)[0].strip()
        if href:
            targets.append(href)
    return targets


def _verify_check(name: str, passed: bool, message: str, *, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pass" if passed else "fail",
        "message": message,
        "evidence": evidence or {},
    }


def build_phone_access_verify(
    *,
    project_root: str | Path = ".",
    phone_access_path: str | Path = DEFAULT_PHONE_ACCESS_OUTPUT,
    daily_home_path: str | Path = DEFAULT_DAILY_HOME_SURFACE,
    today_path: str | Path = DEFAULT_TODAY_OUTPUT,
    port: int = 8787,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    generated = generated_at or datetime.now(timezone.utc)
    phone_access_file = _project_path(root, phone_access_path)
    daily_home_file = _project_path(root, daily_home_path)
    today_file = _project_path(root, today_path)
    phone_access = load_json(phone_access_file) if phone_access_file.exists() else {}
    commands = [item.get("command", "") for item in phone_access.get("commands", [])]
    lowered_commands = " ".join(commands).lower()
    public_fragments = ["funnel", "cloudflare", "ngrok", "public_tunnel", "0.0.0.0"]
    hrefs: list[str] = []
    missing_hrefs: list[str] = []
    optional_missing_hrefs: list[str] = []
    optional_hrefs = {
        DEFAULT_PHONE_ACCESS_VERIFY_SURFACE.as_posix(),
        DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE.as_posix(),
        DEFAULT_REVIEW_RESPONSE_APPLY_SURFACE.as_posix(),
        DEFAULT_COUNCIL_RESPONSE_APPLY_SURFACE.as_posix(),
    }
    if daily_home_file.exists():
        html_text = daily_home_file.read_text(encoding="utf-8")
        for href in _local_href_targets(html_text):
            parsed = urllib.parse.urlparse(href)
            if parsed.scheme in {"http", "https", "mailto", "tel"} or href.startswith("#"):
                continue
            href_path = parsed.path
            if not href_path:
                continue
            hrefs.append(href_path)
            if href_path in optional_hrefs:
                if not _project_path(root, href_path).exists():
                    optional_missing_hrefs.append(href_path)
                continue
            if not _project_path(root, href_path).exists():
                missing_hrefs.append(href_path)
    checks = [
        _verify_check(
            "phone_access_plan",
            phone_access.get("schema_version") == PHONE_ACCESS_SCHEMA_VERSION,
            "Private-first access plan exists.",
            evidence={"path": phone_access_file.as_posix(), "schema_version": phone_access.get("schema_version", "missing")},
        ),
        _verify_check(
            "daily_home_entrypoint",
            daily_home_file.exists(),
            "Daily home exists as the first phone entrypoint.",
            evidence={"path": daily_home_file.as_posix()},
        ),
        _verify_check(
            "today_surface",
            today_file.exists(),
            "Today surface exists for the first reading step.",
            evidence={"path": today_file.as_posix()},
        ),
        _verify_check(
            "local_static_server_command",
            any("python3 -m http.server" in command for command in commands),
            "A reversible local static server command is present but not executed.",
            evidence={"commands": commands},
        ),
        _verify_check(
            "private_share_command",
            any("tailscale serve --bg" in command for command in commands),
            "A private tailnet share command is present but not executed.",
            evidence={"commands": commands},
        ),
        _verify_check(
            "rollback_command",
            any("tailscale serve reset" in command for command in commands),
            "A private serving rollback command is present.",
            evidence={"commands": commands},
        ),
        _verify_check(
            "no_public_default",
            not any(fragment in lowered_commands for fragment in public_fragments)
            and {"public_tunnel", "funnel", "unauthenticated_public_hosting"}.issubset(set(phone_access.get("do_not_default_to", []))),
            "Access guidance remains private-first and does not default to public exposure.",
            evidence={"do_not_default_to": phone_access.get("do_not_default_to", []), "blocked_fragments": public_fragments},
        ),
        _verify_check(
            "daily_home_local_links",
            daily_home_file.exists() and not missing_hrefs,
            "Daily home local links resolve to files in the project workspace.",
            evidence={"checked_count": len(hrefs), "missing": missing_hrefs[:12], "optional_missing": optional_missing_hrefs[:12]},
        ),
    ]
    fail_count = sum(1 for check in checks if check["status"] == "fail")
    payload = {
        "schema_version": PHONE_ACCESS_VERIFY_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": "ready" if fail_count == 0 else "blocked",
        "summary": {
            "entrypoint": Path(daily_home_path).as_posix(),
            "daily_home_local_url": f"http://localhost:{port}/{Path(daily_home_path).as_posix()}",
            "private_phone_url": phone_access.get("private_phone_url", ""),
            "check_count": len(checks),
            "fail_count": fail_count,
            "missing_link_count": len(missing_hrefs),
            "optional_missing_link_count": len(optional_missing_hrefs),
        },
        "checks": checks,
        "safe_manual_commands": [
            {
                "label": "로컬 정적 서버",
                "command": f"cd {root.as_posix()} && python3 -m http.server {port}",
                "requires_approval": False,
                "effect": "현재 터미널에서만 로컬 파일을 서빙합니다. 중지하려면 Ctrl-C를 누릅니다.",
            },
            {
                "label": "비공개 tailnet 공유",
                "command": f"tailscale serve --bg {port}",
                "requires_approval": True,
                "effect": "폰에서 tailnet URL로 접근할 수 있게 합니다. 별도 private_network_exposure 승인이 필요합니다.",
            },
        ],
        "external_effect_performed": False,
        "host_write_performed": False,
        "live_network_performed": False,
        "public_exposure_performed": False,
        "safety_boundary": [
            "verification_reads_existing_artifacts_only",
            "does_not_start_server",
            "does_not_run_tailscale",
            "does_not_open_public_tunnel",
            "does_not_send_notifications",
            "does_not_write_host_state",
            "no_account_access",
            "no_live_trading",
        ],
        "next_action": (
            "Phone access is ready to test locally. Start the local server manually, then use private phone access only after scoped approval."
            if fail_count == 0
            else "Regenerate appliance run/access artifacts before testing phone access."
        ),
    }
    return payload


def write_phone_access_verify(
    *,
    artifact_output_path: str | Path = DEFAULT_PHONE_ACCESS_VERIFY_OUTPUT,
    surface_output_path: str | Path = DEFAULT_PHONE_ACCESS_VERIFY_SURFACE,
    **paths: Any,
) -> Path:
    payload = build_phone_access_verify(**paths)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_phone_access_verify(payload), encoding="utf-8")
    return target


def validate_phone_access_verify_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != PHONE_ACCESS_VERIFY_SCHEMA_VERSION:
        errors.append("schema_version must be phone_access_verify.v1")
    if payload.get("status") not in {"ready", "blocked"}:
        errors.append("status must be ready or blocked")
    if not payload.get("checks"):
        errors.append("checks must not be empty")
    for field in ["external_effect_performed", "host_write_performed", "live_network_performed", "public_exposure_performed"]:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false")
    for item in payload.get("checks", []):
        if item.get("status") not in {"pass", "fail"}:
            errors.append(f"check {item.get('name', '<missing>')} has invalid status")
    if "verification_reads_existing_artifacts_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include verification_reads_existing_artifacts_only")
    if not payload.get("summary", {}).get("daily_home_local_url", "").endswith("daily-home.html"):
        errors.append("summary.daily_home_local_url must point to daily-home.html")
    return errors


def validate_phone_access_verify_file(path: str | Path) -> list[str]:
    return validate_phone_access_verify_payload(load_json(path))


def render_phone_access_verify(payload: dict[str, Any]) -> str:
    status_label = "폰 접근 테스트 준비됨" if payload.get("status") == "ready" else "폰 접근 전 확인 필요"
    check_rows = "".join(
        "<tr>"
        f"<td><strong>{esc(check.get('name', ''))}</strong><span>{esc(check.get('message', ''))}</span></td>"
        f"<td>{esc(check.get('status', ''))}</td>"
        "</tr>"
        for check in payload.get("checks", [])
    )
    command_cards = "".join(
        "<article class='command'>"
        f"<span>{esc(command.get('label', 'command'))}</span>"
        f"<code>{esc(command.get('command', ''))}</code>"
        f"<p>{esc(command.get('effect', ''))}</p>"
        "</article>"
        for command in payload.get("safe_manual_commands", [])
    )
    summary = payload.get("summary", {})
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Phone Access</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:820px; margin:0 auto; padding:16px; }}
a {{ color:var(--blue); font-weight:900; text-decoration:none; }}
.eyebrow,.command span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:20px; }}
p,td span {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.command {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:30px; line-height:1.08; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.metric,.command {{ border:1px solid var(--line); border-radius:8px; background:white; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:18px; overflow-wrap:anywhere; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
td strong,td span {{ display:block; }}
@media (max-width:680px) {{ main {{ padding:12px; }} h1 {{ font-size:30px; }} .grid {{ grid-template-columns:1fr; }} table {{ font-size:13px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Phone Access · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>폰 접근 검증</h1>
<p>이 화면은 서버를 켜거나 Tailscale을 실행하지 않습니다. 오늘 첫 화면을 폰에서 열 준비가 되었는지만 확인합니다.</p>
</header>
<section class="hero">
<span class="eyebrow">검증 결과</span>
<strong class="status">{esc(status_label)}</strong>
<div class="grid">
<article class="metric"><span>첫 화면</span><strong>{esc(summary.get('entrypoint', ''))}</strong></article>
<article class="metric"><span>로컬 URL</span><strong>{esc(summary.get('daily_home_local_url', ''))}</strong></article>
<article class="metric"><span>비공개 URL</span><strong>{esc(summary.get('private_phone_url', ''))}</strong></article>
<article class="metric"><span>깨진 링크</span><strong>{esc(summary.get('missing_link_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>확인한 항목</h2>
<table><tbody>{check_rows}</tbody></table>
</section>
<section class="section">
<h2>수동 테스트 명령</h2>
<div class="grid">{command_cards}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 proof는 기존 파일만 읽습니다. 서버 시작, Tailscale 실행, 공용 터널, 알림 전송, host write, 계좌 접근, 주문 실행을 하지 않습니다.</p>
<p>{esc(payload.get('next_action', ''))}</p>
</section>
</main>
</body>
</html>
"""


def write_runtime_doctor(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_RUNTIME_DOCTOR_OUTPUT,
    freshness_hours: int = 36,
    require_launchd_loaded: bool = False,
) -> Path:
    root = Path(project_root).resolve()
    ops_dir = root / DEFAULT_LOCAL_OPS_DIR
    script_path = ops_dir / "run-daily-analyst.sh"
    plist_path = ops_dir / "com.mybroker.daily-analyst.plist"
    checks = [
        _doctor_check_path("project_root", root, "fail", "MyBroker project root exists."),
        _doctor_check_path("topics_config", root / "config" / "topics.json", "fail", "Daily interests are configured."),
        _doctor_check_path("runner_script", script_path, "fail", "Daily runner script exists.", executable=True),
        _doctor_check_path("launchd_plist", plist_path, "fail", "LaunchAgent plist exists."),
        _doctor_check_path("phone_access_plan", root / DEFAULT_PHONE_ACCESS_OUTPUT, "warn", "Private phone access guidance exists."),
        _doctor_check_path("today_surface", root / DEFAULT_TODAY_OUTPUT, "warn", "Phone-readable today surface exists.", freshness_hours=freshness_hours),
        _doctor_check_path("memory_surface", root / DEFAULT_MEMORY_OUTPUT, "warn", "Accumulated memory surface exists.", freshness_hours=freshness_hours),
        _doctor_check_path("memory_query_surface", root / DEFAULT_MEMORY_QUERY_SURFACE, "warn", "Memory recall surface exists.", freshness_hours=freshness_hours),
        _doctor_check_path("archive_manifest", _latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT), "warn", "Latest daily archive manifest exists.", freshness_hours=freshness_hours),
        _doctor_check_notification(root / DEFAULT_NOTIFICATION_OUTPUT),
        _doctor_check_launchd(plist_path, require_launchd_loaded=require_launchd_loaded),
    ]
    fail_count = sum(1 for check in checks if check["status"] == "fail")
    warn_count = sum(1 for check in checks if check["status"] == "warn")
    payload = {
        "schema_version": RUNTIME_DOCTOR_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "status": "ready" if fail_count == 0 else "blocked",
        "fail_count": fail_count,
        "warn_count": warn_count,
        "checks": checks,
        "next_actions": _doctor_next_actions(checks),
        "install_boundary": {
            "launchd_install_is_host_level": True,
            "default_behavior": "diagnose_only",
            "manual_install_commands": [
                f"mkdir -p ~/Library/LaunchAgents",
                f"cp {plist_path.as_posix()} ~/Library/LaunchAgents/com.mybroker.daily-analyst.plist",
                "launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.mybroker.daily-analyst.plist",
                "launchctl kickstart -k gui/$(id -u)/com.mybroker.daily-analyst",
            ],
            "manual_uninstall_commands": [
                "launchctl bootout gui/$(id -u)/com.mybroker.daily-analyst",
                "rm ~/Library/LaunchAgents/com.mybroker.daily-analyst.plist",
            ],
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_status(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_STATUS_OUTPUT,
) -> Path:
    root = Path(project_root).resolve()
    source_plist = root / DEFAULT_LOCAL_OPS_DIR / f"{LAUNCHD_LABEL}.plist"
    source_script = root / DEFAULT_LOCAL_OPS_DIR / "run-daily-analyst.sh"
    installed_plist = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"
    launchd = _launchd_state()
    log_paths = {
        "stdout": (root / "reports" / "runtime" / "daily-analyst.out.log").as_posix(),
        "stderr": (root / "reports" / "runtime" / "daily-analyst.err.log").as_posix(),
    }
    payload = {
        "schema_version": SCHEDULER_STATUS_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "host_write_performed": False,
        "status": _scheduler_status(source_plist=source_plist, source_script=source_script, installed_plist=installed_plist, loaded=launchd["loaded"]),
        "source_assets": {
            "script": source_script.as_posix(),
            "script_exists": source_script.exists(),
            "script_executable": source_script.exists() and os.access(source_script, os.X_OK),
            "plist": source_plist.as_posix(),
            "plist_exists": source_plist.exists(),
        },
        "installed_plist": {
            "path": installed_plist.as_posix(),
            "exists": installed_plist.exists(),
        },
        "launchd": launchd,
        "logs": {
            "paths": log_paths,
            "stdout_exists": Path(log_paths["stdout"]).exists(),
            "stderr_exists": Path(log_paths["stderr"]).exists(),
        },
        "commands": _scheduler_commands(source_plist=source_plist, installed_plist=installed_plist),
        "next_actions": _scheduler_next_actions(
            source_plist=source_plist,
            source_script=source_script,
            installed_plist=installed_plist,
            loaded=launchd["loaded"],
        ),
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_apply(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_APPLY_OUTPUT,
    install: bool = False,
    load: bool = False,
    start_now: bool = False,
    unload: bool = False,
    uninstall: bool = False,
    confirm_host_write: bool = False,
) -> Path:
    root = Path(project_root).resolve()
    source_plist = root / DEFAULT_LOCAL_OPS_DIR / f"{LAUNCHD_LABEL}.plist"
    installed_plist = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"
    actions = _scheduler_apply_actions(
        source_plist=source_plist,
        installed_plist=installed_plist,
        install=install,
        load=load,
        start_now=start_now,
        unload=unload,
        uninstall=uninstall,
    )
    dry_run = not confirm_host_write
    results = []
    for action in actions:
        if dry_run:
            result = dict(action)
            result["status"] = "planned"
            result["executed"] = False
        else:
            result = _execute_scheduler_action(action)
        results.append(result)
    post_status_path = write_scheduler_status(project_root=root, output_path=root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    payload = {
        "schema_version": SCHEDULER_APPLY_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "dry_run": dry_run,
        "host_write_performed": bool(confirm_host_write and actions),
        "requested": {
            "install": install,
            "load": load,
            "start_now": start_now,
            "unload": unload,
            "uninstall": uninstall,
        },
        "actions": results,
        "post_status_path": post_status_path.as_posix(),
        "post_status": load_json(post_status_path),
        "safety": {
            "requires_confirm_host_write": True,
            "default_behavior": "dry_run",
            "notes": [
                "Dry-run records planned host-level commands without changing launchd state.",
                "Actual install/load/start/unload/uninstall requires --confirm-host-write.",
            ],
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_run_once(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT,
    timeout_seconds: int = 240,
) -> Path:
    root = Path(project_root).resolve()
    script_path = root / DEFAULT_LOCAL_OPS_DIR / "run-daily-analyst.sh"
    command = [script_path.as_posix()]
    started_at = datetime.now(timezone.utc)
    status = "failed"
    returncode: int | None = None
    stdout_excerpt = ""
    stderr_excerpt = ""
    error = ""

    if not script_path.exists():
        error = f"Runner script is missing: {script_path.as_posix()}"
    elif not os.access(script_path, os.X_OK):
        error = f"Runner script is not executable: {script_path.as_posix()}"
    else:
        try:
            completed = subprocess.run(
                command,
                cwd=root,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            returncode = completed.returncode
            stdout_excerpt = completed.stdout[-2000:]
            stderr_excerpt = completed.stderr[-2000:]
            status = "passed" if completed.returncode == 0 else "failed"
        except subprocess.TimeoutExpired as exc:
            status = "timeout"
            returncode = None
            stdout_excerpt = _timeout_output_excerpt(exc.stdout)
            stderr_excerpt = _timeout_output_excerpt(exc.stderr)
            error = f"Runner script exceeded timeout_seconds={timeout_seconds}"
        except OSError as exc:
            error = str(exc)

    finished_at = datetime.now(timezone.utc)
    post_status_path = write_scheduler_status(project_root=root, output_path=root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    doctor_path = write_runtime_doctor(project_root=root, output_path=root / DEFAULT_RUNTIME_DOCTOR_OUTPUT)
    payload = {
        "schema_version": SCHEDULER_RUN_ONCE_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "script_path": script_path.as_posix(),
        "command": command,
        "timeout_seconds": timeout_seconds,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": round((finished_at - started_at).total_seconds(), 3),
        "status": status,
        "returncode": returncode,
        "stdout_excerpt": stdout_excerpt,
        "stderr_excerpt": stderr_excerpt,
        "error": error,
        "host_write_performed": False,
        "post_status_path": post_status_path.as_posix(),
        "doctor_path": doctor_path.as_posix(),
        "expected_outputs": [
            DEFAULT_TODAY_OUTPUT.as_posix(),
            DEFAULT_MEMORY_OUTPUT.as_posix(),
            DEFAULT_NOTIFICATION_OUTPUT.as_posix(),
            DEFAULT_ARCHIVE_ROOT.as_posix(),
        ],
        "safety": {
            "launchd_install_performed": False,
            "launchd_load_performed": False,
            "notification_send_performed": False,
            "notes": [
                "This proof executes the same local runner script launchd would call.",
                "It does not install, load, start, unload, or uninstall a LaunchAgent.",
                "The runner uses notification dry-run unless the script is edited by the operator.",
            ],
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_activation_preflight(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT,
    max_proof_age_hours: int = 24,
) -> Path:
    root = Path(project_root).resolve()
    status_path = write_scheduler_status(project_root=root, output_path=root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    doctor_path = write_runtime_doctor(project_root=root, output_path=root / DEFAULT_RUNTIME_DOCTOR_OUTPUT)
    artifacts = {
        "scheduler_status": status_path,
        "runtime_doctor": doctor_path,
        "scheduler_apply": root / DEFAULT_SCHEDULER_APPLY_OUTPUT,
        "scheduler_run_once": root / DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT,
        "notification": root / DEFAULT_NOTIFICATION_OUTPUT,
    }
    loaded_status = load_json(status_path).get("status", "unknown")
    checks = [
        _preflight_artifact_check(
            "runtime_doctor_ready",
            artifacts["runtime_doctor"],
            expected_schema=RUNTIME_DOCTOR_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=lambda payload: payload.get("status") == "ready" and int(payload.get("fail_count", 1)) == 0,
            message="Runtime doctor is ready with zero failures.",
        ),
        _preflight_artifact_check(
            "scheduler_assets_ready",
            artifacts["scheduler_status"],
            expected_schema=SCHEDULER_STATUS_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=lambda payload: payload.get("status") in {"assets_ready", "installed_not_loaded", "loaded"}
            and bool(payload.get("source_assets", {}).get("script_executable"))
            and bool(payload.get("source_assets", {}).get("plist_exists")),
            message="Scheduler source assets are present and executable.",
        ),
        _preflight_artifact_check(
            "dry_run_apply_planned",
            artifacts["scheduler_apply"],
            expected_schema=SCHEDULER_APPLY_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=_dry_run_apply_is_activation_plan,
            message="Dry-run activation plan exists for install/load/start-now without host writes.",
        ),
        _preflight_artifact_check(
            "runner_run_once_passed",
            artifacts["scheduler_run_once"],
            expected_schema=SCHEDULER_RUN_ONCE_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=lambda payload: payload.get("status") == "passed"
            and payload.get("returncode") == 0
            and payload.get("host_write_performed") is False,
            message="The scheduler runner executed once locally without host writes.",
        ),
        _preflight_artifact_check(
            "notification_remains_dry_run",
            artifacts["notification"],
            expected_schema=NOTIFICATION_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=lambda payload: payload.get("dry_run") is True
            and payload.get("delivery_status") == "dry_run_ready",
            message="Notification payload remains dry-run until explicit send approval.",
        ),
    ]
    blockers = [check["message"] for check in checks if check["status"] == "fail"]
    warnings = [check["message"] for check in checks if check["status"] == "warn"]
    if loaded_status == "loaded":
        status = "already_active" if not blockers else "blocked"
        next_action = "Scheduler already appears loaded. Run scheduler status and inspect logs before changing it."
    elif blockers:
        status = "blocked"
        next_action = "Refresh the failed proof artifacts before requesting confirmed host-level activation."
    else:
        status = "ready"
        next_action = "Operator may decide whether to run scheduler apply --install --load --start-now --confirm-host-write."
    payload = {
        "schema_version": SCHEDULER_ACTIVATION_PREFLIGHT_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "status": status,
        "max_proof_age_hours": max_proof_age_hours,
        "host_write_performed": False,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "artifacts": {name: path.as_posix() for name, path in artifacts.items()},
        "activation_command": "PYTHONPATH=src python3 -m mybroker appliance scheduler apply --install --load --start-now --confirm-host-write",
        "next_action": next_action,
        "safety": {
            "requires_explicit_operator_approval": True,
            "preflight_does_not_install_or_load": True,
            "confirmed_activation_is_host_level": True,
            "notification_send_remains_separate": True,
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_activation_verify(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT,
    freshness_hours: int = 36,
) -> Path:
    root = Path(project_root).resolve()
    source_plist = root / DEFAULT_LOCAL_OPS_DIR / f"{LAUNCHD_LABEL}.plist"
    installed_plist = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"
    status_path = write_scheduler_status(project_root=root, output_path=root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    doctor_path = write_runtime_doctor(
        project_root=root,
        output_path=root / DEFAULT_RUNTIME_DOCTOR_ACTIVATION_OUTPUT,
        freshness_hours=freshness_hours,
        require_launchd_loaded=True,
    )
    scheduler_status = load_json(status_path)
    doctor = load_json(doctor_path)
    checks = [
        _activation_verify_check(
            "launchd_loaded",
            bool(scheduler_status.get("launchd", {}).get("loaded")),
            "LaunchAgent is loaded for the current user.",
            evidence=scheduler_status.get("launchd", {}),
        ),
        _activation_verify_check(
            "installed_plist_exists",
            bool(scheduler_status.get("installed_plist", {}).get("exists")),
            "LaunchAgent plist is installed under ~/Library/LaunchAgents.",
            evidence=scheduler_status.get("installed_plist", {}),
        ),
        _activation_verify_check(
            "installed_plist_matches_source",
            _same_file_contents(source_plist, installed_plist),
            "Installed plist matches the source scheduler asset.",
            evidence={
                "source": source_plist.as_posix(),
                "installed": installed_plist.as_posix(),
            },
        ),
        _activation_verify_check(
            "runtime_doctor_strict",
            doctor.get("status") == "ready" and int(doctor.get("fail_count", 1)) == 0,
            "Runtime doctor passes with launchd loaded required.",
            evidence={
                "doctor_path": doctor_path.as_posix(),
                "fail_count": doctor.get("fail_count"),
                "warn_count": doctor.get("warn_count"),
            },
        ),
        _activation_verify_check(
            "today_surface_fresh",
            _path_fresh(root / DEFAULT_TODAY_OUTPUT, freshness_hours),
            f"Phone-readable today surface is fresher than {freshness_hours} hours.",
            evidence={"path": (root / DEFAULT_TODAY_OUTPUT).as_posix()},
        ),
        _activation_verify_check(
            "archive_manifest_fresh",
            _path_fresh(_latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT), freshness_hours),
            f"Latest daily archive manifest is fresher than {freshness_hours} hours.",
            evidence={"path": (_latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT).as_posix() if _latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT) else "")},
        ),
    ]
    stdout_log = root / "reports" / "runtime" / "daily-analyst.out.log"
    stderr_log = root / "reports" / "runtime" / "daily-analyst.err.log"
    warnings = []
    if not stdout_log.exists() and not stderr_log.exists():
        warnings.append("Scheduler log files do not exist yet. This is expected before the first launchd-triggered run.")
    blockers = [check["message"] for check in checks if check["status"] == "fail"]
    status = "active_verified" if not blockers else "blocked"
    payload = {
        "schema_version": SCHEDULER_ACTIVATION_VERIFY_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "status": status,
        "freshness_hours": freshness_hours,
        "host_write_performed": False,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "artifacts": {
            "scheduler_status": status_path.as_posix(),
            "runtime_doctor": doctor_path.as_posix(),
            "today": (root / DEFAULT_TODAY_OUTPUT).as_posix(),
            "latest_archive_manifest": (_latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT).as_posix() if _latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT) else ""),
            "stdout_log": stdout_log.as_posix(),
            "stderr_log": stderr_log.as_posix(),
        },
        "next_action": (
            "Activation is verified. Keep the Mac powered, inspect logs after the next scheduled run, and keep notification send as a separate gate."
            if not blockers
            else "Run activation-preflight, then perform the separate confirmed host-level activation before running verify again."
        ),
        "safety": {
            "verify_does_not_install_or_load": True,
            "confirmed_activation_is_separate": True,
            "notification_send_remains_separate": True,
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def build_scheduler_operations(
    *,
    project_root: str | Path = ".",
    freshness_hours: int = 24,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    generated = generated_at or datetime.now(timezone.utc)
    status_path = root / DEFAULT_SCHEDULER_STATUS_OUTPUT
    run_once_path = root / DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT
    preflight_path = root / DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT
    verify_path = root / DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT
    doctor_path = root / DEFAULT_RUNTIME_DOCTOR_OUTPUT
    status = _load_optional_json(status_path)
    run_once = _load_optional_json(run_once_path)
    preflight = _load_optional_json(preflight_path)
    verify = _load_optional_json(verify_path)
    doctor = _load_optional_json(doctor_path)
    proof_artifacts = [
        _scheduler_proof_artifact(
            name="scheduler_status",
            path=status_path,
            expected_schema=SCHEDULER_STATUS_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
        _scheduler_proof_artifact(
            name="run_once",
            path=run_once_path,
            expected_schema=SCHEDULER_RUN_ONCE_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
        _scheduler_proof_artifact(
            name="activation_preflight",
            path=preflight_path,
            expected_schema=SCHEDULER_ACTIVATION_PREFLIGHT_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
        _scheduler_proof_artifact(
            name="activation_verify",
            path=verify_path,
            expected_schema=SCHEDULER_ACTIVATION_VERIFY_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
        _scheduler_proof_artifact(
            name="runtime_doctor",
            path=doctor_path,
            expected_schema=RUNTIME_DOCTOR_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
    ]
    install_state = {
        "source_assets_status": status.get("status", "missing"),
        "script_ready": bool(status.get("source_assets", {}).get("script_executable")),
        "plist_ready": bool(status.get("source_assets", {}).get("plist_exists")),
        "installed": bool(status.get("installed_plist", {}).get("exists")),
        "loaded": bool(status.get("launchd", {}).get("loaded")),
        "installed_path": status.get("installed_plist", {}).get("path", ""),
    }
    local_run = {
        "status": run_once.get("status", "missing"),
        "returncode": run_once.get("returncode"),
        "duration_seconds": run_once.get("duration_seconds"),
        "host_write_performed": run_once.get("host_write_performed", False),
        "path": run_once_path.as_posix(),
    }
    activation_preflight = {
        "status": preflight.get("status", "missing"),
        "blockers": preflight.get("blockers", []),
        "warnings": preflight.get("warnings", []),
        "next_action": preflight.get("next_action", "Run activation-preflight after dry-run apply and run-once proof."),
        "host_write_performed": preflight.get("host_write_performed", False),
        "path": preflight_path.as_posix(),
    }
    activation_verify = {
        "status": verify.get("status", "missing"),
        "blockers": verify.get("blockers", []),
        "warnings": verify.get("warnings", []),
        "next_action": verify.get("next_action", "Verify only after confirmed activation."),
        "host_write_performed": verify.get("host_write_performed", False),
        "path": verify_path.as_posix(),
    }
    runtime = {
        "doctor_status": doctor.get("status", "missing"),
        "fail_count": doctor.get("fail_count", 0),
        "warn_count": doctor.get("warn_count", 0),
        "path": doctor_path.as_posix(),
    }
    overall_status = _scheduler_operations_status(
        install_state=install_state,
        local_run=local_run,
        activation_preflight=activation_preflight,
        activation_verify=activation_verify,
        runtime=runtime,
        proof_artifacts=proof_artifacts,
    )
    operator_next_action = _scheduler_operations_next_action(
        status=overall_status,
        install_state=install_state,
        local_run=local_run,
        activation_preflight=activation_preflight,
        runtime=runtime,
    )
    payload = {
        "schema_version": SCHEDULER_OPERATIONS_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "project_root": root.as_posix(),
        "status": overall_status,
        "freshness_hours": freshness_hours,
        "install_state": install_state,
        "local_run": local_run,
        "activation_preflight": activation_preflight,
        "activation_verify": activation_verify,
        "runtime": runtime,
        "proof_artifacts": proof_artifacts,
        "operator_next_action": operator_next_action,
        "copy_ready_commands": _scheduler_operations_commands(overall_status=overall_status),
        "phone_links": {
            "scheduler": DEFAULT_SCHEDULER_OPERATIONS_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_install_or_load_scheduler",
            "does_not_start_scheduler",
            "does_not_send_notifications",
            "does_not_fetch_live_network",
            "no_account_access",
            "no_order_execution",
            "host_writes_require_separate_confirmation",
        ],
    }
    return payload


def write_scheduler_operations(
    *,
    project_root: str | Path = ".",
    freshness_hours: int = 24,
    artifact_output_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_OUTPUT,
    surface_output_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_SURFACE,
) -> Path:
    payload = build_scheduler_operations(project_root=project_root, freshness_hours=freshness_hours)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_scheduler_operations(payload), encoding="utf-8")
    return target


def validate_scheduler_operations_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SCHEDULER_OPERATIONS_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"not_ready", "manual_ready", "activation_ready", "active_verified", "blocked"}:
        errors.append("status must be not_ready, manual_ready, activation_ready, active_verified, or blocked")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("operator_next_action"):
        errors.append("operator_next_action must not be empty")
    if not payload.get("proof_artifacts"):
        errors.append("proof_artifacts must not be empty")
    if not payload.get("phone_links", {}).get("scheduler"):
        errors.append("phone_links.scheduler must not be empty")
    if "does_not_install_or_load_scheduler" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_install_or_load_scheduler")
    for index, item in enumerate(payload.get("proof_artifacts", [])):
        for field in ["name", "path", "exists", "freshness_status"]:
            if field not in item:
                errors.append(f"proof_artifacts[{index}] missing {field}")
        if item.get("freshness_status") not in {"fresh", "stale", "missing", "invalid_schema"}:
            errors.append(f"proof_artifacts[{index}] invalid freshness_status")
    for index, command in enumerate(payload.get("copy_ready_commands", [])):
        command_text = command.get("command", "")
        if "--confirm-host-write" in command_text and command.get("requires_separate_approval") is not True:
            errors.append(f"copy_ready_commands[{index}] host write command must require separate approval")
        if command.get("external_effect_performed") is not False:
            errors.append(f"copy_ready_commands[{index}] external_effect_performed must be false")
    return errors


def validate_scheduler_operations_file(path: str | Path) -> list[str]:
    return validate_scheduler_operations_payload(load_json(path))


def render_scheduler_operations(payload: dict[str, Any]) -> str:
    status_label = {
        "active_verified": "자동 실행 확인됨",
        "activation_ready": "활성화 준비됨",
        "manual_ready": "수동 실행은 준비됨",
        "not_ready": "준비 전",
        "blocked": "차단됨",
    }.get(payload.get("status", ""), payload.get("status", "unknown"))
    install = payload.get("install_state", {})
    local_run = payload.get("local_run", {})
    preflight = payload.get("activation_preflight", {})
    verify = payload.get("activation_verify", {})
    runtime = payload.get("runtime", {})
    proof_rows = "".join(
        "<tr>"
        f"<td><strong>{esc(item.get('name', ''))}</strong><span>{esc(item.get('path', ''))}</span></td>"
        f"<td><span class='pill {esc(_readiness_css(item.get('freshness_status', 'missing')))}'>{esc(item.get('freshness_status', ''))}</span></td>"
        f"<td>{esc(item.get('summary_status', ''))}</td>"
        f"<td>{esc(item.get('age_hours', ''))}</td>"
        "</tr>"
        for item in payload.get("proof_artifacts", [])
    )
    commands = "".join(
        "<article class='command'>"
        f"<span>{esc(command.get('label', 'command'))}</span>"
        f"<code>{esc(command.get('command', ''))}</code>"
        f"<small>{esc(command.get('why', ''))}</small>"
        "</article>"
        for command in payload.get("copy_ready_commands", [])
    ) or "<p>지금 복사할 안전한 로컬 명령이 없습니다.</p>"
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "scheduler"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Scheduler Operations</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; --bad:#9f2d2d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow,.command span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small,td span {{ color:var(--muted); }}
.hero,.section,.command {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.panel {{ border:1px solid var(--line); border-radius:8px; background:white; padding:13px; min-width:0; }}
.panel strong {{ display:block; margin-bottom:4px; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
td strong,td span {{ display:block; overflow-wrap:anywhere; }}
.pill {{ display:inline-block; border-radius:999px; padding:2px 8px; font-size:12px; font-weight:900; }}
.fresh {{ background:#e7f5ee; color:var(--green); }}
.stale {{ background:#fff3d8; color:var(--warn); }}
.missing {{ background:#ffe2e2; color:var(--bad); }}
.command {{ background:white; padding:14px; margin:10px 0; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.grid,.links {{ grid-template-columns:1fr; }} table {{ font-size:13px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Scheduler · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>자동 실행 준비 상태</h1>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('operator_next_action', ''))}</p>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Script</span><strong>{esc('OK' if install.get('script_ready') else 'NO')}</strong></article>
<article class="metric"><span>Plist</span><strong>{esc('OK' if install.get('plist_ready') else 'NO')}</strong></article>
<article class="metric"><span>Installed</span><strong>{esc('YES' if install.get('installed') else 'NO')}</strong></article>
<article class="metric"><span>Loaded</span><strong>{esc('YES' if install.get('loaded') else 'NO')}</strong></article>
</div>
</section>
<section class="section">
<h2>운영 증거</h2>
<div class="grid">
<article class="panel"><strong>수동 run-once</strong><p>{esc(local_run.get('status', 'missing'))} · returncode {esc(local_run.get('returncode', ''))}</p></article>
<article class="panel"><strong>Activation preflight</strong><p>{esc(preflight.get('status', 'missing'))} · blockers {esc(len(preflight.get('blockers', [])))}</p></article>
<article class="panel"><strong>Activation verify</strong><p>{esc(verify.get('status', 'missing'))} · blockers {esc(len(verify.get('blockers', [])))}</p></article>
<article class="panel"><strong>Runtime doctor</strong><p>{esc(runtime.get('doctor_status', 'missing'))} · fails {esc(runtime.get('fail_count', 0))} · warns {esc(runtime.get('warn_count', 0))}</p></article>
</div>
</section>
<section class="section">
<h2>다음에 복사할 명령</h2>
{commands}
</section>
<section class="section">
<h2>Proof freshness</h2>
<table><thead><tr><th>Proof</th><th>Freshness</th><th>Status</th><th>Age</th></tr></thead><tbody>{proof_rows}</tbody></table>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 로컬 파일만 읽습니다. 설치, load, start, 알림 전송, live source refresh는 별도 승인과 확인 없이는 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def write_operator_decision_packet(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_OPERATOR_DECISION_PACKET_OUTPUT,
) -> Path:
    root = Path(project_root).resolve()
    preflight_path = write_scheduler_activation_preflight(
        project_root=root,
        output_path=root / DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT,
    )
    verify_path = write_scheduler_activation_verify(
        project_root=root,
        output_path=root / DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT,
    )
    preflight = load_json(preflight_path)
    verify = load_json(verify_path)
    notification_path = root / DEFAULT_NOTIFICATION_OUTPUT
    notification = load_json(notification_path) if notification_path.exists() else {}
    phone_access_path = root / DEFAULT_PHONE_ACCESS_OUTPUT
    phone_access = load_json(phone_access_path) if phone_access_path.exists() else {}
    decisions = [
        _scheduler_activation_decision(preflight=preflight, verify=verify),
        _notification_send_decision(notification=notification),
        _private_phone_access_decision(phone_access=phone_access),
    ]
    payload = {
        "schema_version": OPERATOR_DECISION_PACKET_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "status": "pending_operator_decision",
        "host_write_performed": False,
        "decisions": decisions,
        "summary": {
            "decision_count": len(decisions),
            "ready_count": sum(1 for decision in decisions if decision.get("readiness") == "ready"),
            "blocked_count": sum(1 for decision in decisions if decision.get("readiness") == "blocked"),
            "pending_count": sum(1 for decision in decisions if decision.get("readiness") == "pending"),
        },
        "artifacts": {
            "scheduler_activation_preflight": preflight_path.as_posix(),
            "scheduler_activation_verify": verify_path.as_posix(),
            "notification": notification_path.as_posix(),
            "phone_access": phone_access_path.as_posix(),
        },
        "safety": {
            "packet_does_not_execute_external_effects": True,
            "scheduler_activation_requires_confirm_host_write": True,
            "notification_send_requires_provider_secrets": True,
            "private_serving_changes_network_exposure": True,
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_operator_decision_apply(
    *,
    response: str,
    project_root: str | Path = ".",
    packet_path: str | Path = DEFAULT_OPERATOR_DECISION_PACKET_OUTPUT,
    output_path: str | Path = DEFAULT_OPERATOR_DECISION_APPLY_OUTPUT,
) -> Path:
    root = Path(project_root).resolve()
    packet_file = Path(packet_path)
    if not packet_file.is_absolute():
        packet_file = root / packet_file
    packet = load_json(packet_file)
    parsed = _parse_operator_approval_response(response)
    decision = _find_packet_decision(packet=packet, decision_id=parsed.get("decision_id", ""))
    blockers = _operator_decision_apply_blockers(parsed=parsed, decision=decision)
    commands = list(decision.get("agent_will_run", [])) if decision and not blockers else []
    rollback_command = decision.get("rollback_command", "") if decision else ""
    payload = {
        "schema_version": OPERATOR_DECISION_APPLY_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "packet_path": packet_file.as_posix(),
        "operator_response": response,
        "parsed_response": parsed,
        "decision_id": parsed.get("decision_id", ""),
        "approval_scope": parsed.get("approval_scope", ""),
        "status": "ready_to_apply" if not blockers else "blocked",
        "blockers": blockers,
        "commands": commands,
        "rollback_command": rollback_command,
        "external_effect_performed": False,
        "host_write_performed": False,
        "execution_mode": "dry_run_plan_only",
        "next_action": _operator_decision_apply_next_action(blockers=blockers, decision=decision),
        "safety": {
            "does_not_execute_commands": True,
            "requires_exact_decision_id": True,
            "requires_exact_approval_scope": True,
            "blocked_decisions_do_not_emit_commands": True,
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def build_daily_brief_agenda(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scout = _load_optional_json(scout_path)
    evidence = _load_optional_json(evidence_path)
    memory = _load_optional_json(memory_path)
    vault = _load_optional_json(vault_path)
    refresh_plan = _load_optional_json(refresh_plan_path)
    recommendations = scout.get("recommendations", []) if scout.get("schema_version") == "daily_scout.v1" else []
    source_rows = evidence.get("source_status", []) if evidence.get("schema_version") == "public_evidence_catalog.v1" else []
    evidence_items = evidence.get("items", []) if evidence.get("schema_version") == "public_evidence_catalog.v1" else []
    memory_by_id = {row.get("topic_id"): row for row in memory.get("topics", [])}
    vault_notes = vault.get("compiled_notes", []) if vault.get("schema_version") == "knowledge_vault_compile.v1" else []
    top_cards = [
        _agenda_topic_card(
            recommendation=recommendation,
            evidence_items=evidence_items,
            source_rows=source_rows,
            memory_topic=memory_by_id.get(recommendation.get("topic_id"), {}),
            vault_notes=vault_notes,
        )
        for recommendation in recommendations[:3]
    ]
    primary = top_cards[0] if top_cards else {}
    weak_points = _agenda_weak_points(top_cards=top_cards, source_rows=source_rows, evidence=evidence)
    role_brief = _agenda_role_brief(primary=primary, weak_points=weak_points, refresh_plan=refresh_plan)
    payload = {
        "schema_version": DAILY_BRIEF_AGENDA_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "run_id": scout.get("run_id", ""),
        "mode": "phone_first_local_personal_analyst",
        "operator_time_budget_minutes": 20,
        "primary_topic": primary,
        "study_sequence": _agenda_study_sequence(primary=primary, weak_points=weak_points),
        "topic_cards": top_cards,
        "source_fanout": _agenda_source_fanout(source_rows=source_rows, top_cards=top_cards),
        "role_brief": role_brief,
        "copy_ready_questions": _agenda_questions(primary=primary, weak_points=weak_points),
        "copy_ready_responses": primary.get("copy_ready_responses", []),
        "weak_points": weak_points,
        "external_effect_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "local_artifact_generation_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "no_account_access",
            "no_live_trading",
            "no_discretionary_management",
            "no_unsupported_personalized_recommendations",
        ],
        "inputs": {
            "scout": Path(scout_path).as_posix(),
            "evidence": Path(evidence_path).as_posix(),
            "memory": Path(memory_path).as_posix(),
            "vault": Path(vault_path).as_posix(),
            "refresh_plan": Path(refresh_plan_path).as_posix(),
        },
    }
    return payload


def write_daily_brief_agenda(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    surface_output_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_SURFACE,
) -> Path:
    payload = build_daily_brief_agenda(
        scout_path=scout_path,
        evidence_path=evidence_path,
        memory_path=memory_path,
        vault_path=vault_path,
        refresh_plan_path=refresh_plan_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_daily_brief_agenda(payload), encoding="utf-8")
    return target


def validate_daily_brief_agenda_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DAILY_BRIEF_AGENDA_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if not payload.get("primary_topic"):
        errors.append("primary_topic must not be empty")
    if not payload.get("study_sequence"):
        errors.append("study_sequence must not be empty")
    if not payload.get("topic_cards"):
        errors.append("topic_cards must not be empty")
    if not payload.get("copy_ready_responses"):
        errors.append("copy_ready_responses must not be empty")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    for index, step in enumerate(payload.get("study_sequence", [])):
        for field in ["step", "minutes", "title", "operator_action", "stop_condition"]:
            if field not in step:
                errors.append(f"study_sequence[{index}] missing {field}")
    return errors


def validate_daily_brief_agenda_file(path: str | Path) -> list[str]:
    return validate_daily_brief_agenda_payload(load_json(path))


def build_daily_readiness(
    *,
    project_root: str | Path = ".",
    freshness_hours: int = 24,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    generated = generated_at or datetime.now(timezone.utc)
    artifact_specs = [
        ("daily_home", DEFAULT_DAILY_HOME_OUTPUT, "control_artifact", False),
        ("daily_home_surface", DEFAULT_DAILY_HOME_SURFACE, "phone_surface", False),
        ("phone_access_verify", DEFAULT_PHONE_ACCESS_VERIFY_OUTPUT, "control_artifact", False),
        ("phone_access_verify_surface", DEFAULT_PHONE_ACCESS_VERIFY_SURFACE, "phone_surface", False),
        ("today_surface", DEFAULT_TODAY_OUTPUT, "phone_surface", True),
        ("daily_agenda_surface", DEFAULT_DAILY_BRIEF_AGENDA_SURFACE, "phone_surface", True),
        ("daily_agenda", DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT, "machine_artifact", True),
        ("source_refresh_brief", DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT, "control_artifact", False),
        ("source_refresh_surface", DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE, "phone_surface", False),
        ("source_freshness_intake", DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT, "control_artifact", False),
        ("source_freshness_intake_surface", DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE, "phone_surface", False),
        ("source_refresh_execution_brief", DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT, "control_artifact", False),
        ("source_refresh_execution_surface", DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE, "phone_surface", False),
        ("pattern_dry_run_proof", DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT, "control_artifact", False),
        ("pattern_dry_run_proof_surface", DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE, "phone_surface", False),
        ("morning_control", DEFAULT_MORNING_CONTROL_OUTPUT, "control_artifact", True),
        ("morning_surface", DEFAULT_MORNING_CONTROL_SURFACE, "phone_surface", True),
        ("run_trace", DEFAULT_RUN_TRACE_OUTPUT, "control_artifact", False),
        ("run_trace_surface", DEFAULT_RUN_TRACE_SURFACE, "phone_surface", False),
        ("daily_run_ledger", DEFAULT_DAILY_RUN_LEDGER_OUTPUT, "control_artifact", False),
        ("daily_run_ledger_surface", DEFAULT_DAILY_RUN_LEDGER_SURFACE, "phone_surface", False),
        ("daily_handoff", DEFAULT_DAILY_HANDOFF_OUTPUT, "control_artifact", False),
        ("daily_handoff_surface", DEFAULT_DAILY_HANDOFF_SURFACE, "phone_surface", False),
        ("handoff_study_resolution", DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT, "control_artifact", False),
        ("handoff_study_resolution_surface", DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE, "phone_surface", False),
        ("handoff_response_apply", DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT, "control_artifact", False),
        ("handoff_response_apply_surface", DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE, "phone_surface", False),
        ("drift_review", DEFAULT_DRIFT_REVIEW_OUTPUT, "control_artifact", False),
        ("drift_review_surface", DEFAULT_DRIFT_REVIEW_SURFACE, "phone_surface", False),
        ("review_prompt", DEFAULT_REVIEW_PROMPT_OUTPUT, "control_artifact", False),
        ("review_prompt_surface", DEFAULT_REVIEW_PROMPT_SURFACE, "phone_surface", False),
        ("review_effect", DEFAULT_REVIEW_EFFECT_OUTPUT, "control_artifact", False),
        ("review_effect_surface", DEFAULT_REVIEW_EFFECT_SURFACE, "phone_surface", False),
        ("analyst_council", DEFAULT_ANALYST_COUNCIL_OUTPUT, "control_artifact", False),
        ("analyst_council_surface", DEFAULT_ANALYST_COUNCIL_SURFACE, "phone_surface", False),
        ("learning_ledger", DEFAULT_LEARNING_LEDGER_OUTPUT, "memory_artifact", True),
        ("learning_ledger_surface", DEFAULT_LEARNING_LEDGER_SURFACE, "phone_surface", True),
        ("daily_scout", DEFAULT_DAILY_SCOUT_OUTPUT, "machine_artifact", True),
        ("daily_evidence", DEFAULT_DAILY_EVIDENCE_OUTPUT, "machine_artifact", True),
        ("topic_memory", DEFAULT_TOPIC_MEMORY_OUTPUT, "memory_artifact", True),
        ("scenario_report", Path("reports/scenarios/daily-research-sim.json"), "machine_artifact", True),
        ("market_verdict", Path("reports/scenarios/daily-research-verdict.json"), "machine_artifact", True),
        ("archive_manifest", _latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT) or DEFAULT_ARCHIVE_ROOT / "missing" / "manifest.json", "archive", True),
        ("runtime_doctor", DEFAULT_RUNTIME_DOCTOR_OUTPUT, "runtime_artifact", False),
        ("scheduler_status", DEFAULT_SCHEDULER_STATUS_OUTPUT, "runtime_artifact", False),
        ("scheduler_operations", DEFAULT_SCHEDULER_OPERATIONS_OUTPUT, "runtime_artifact", False),
        ("scheduler_surface", DEFAULT_SCHEDULER_OPERATIONS_SURFACE, "phone_surface", False),
        ("vault_surface", DEFAULT_VAULT_SURFACE_OUTPUT, "phone_surface", False),
        ("memory_surface", DEFAULT_MEMORY_OUTPUT, "phone_surface", False),
        ("memory_query", DEFAULT_MEMORY_QUERY_OUTPUT, "memory_artifact", False),
        ("memory_query_surface", DEFAULT_MEMORY_QUERY_SURFACE, "phone_surface", False),
        ("memory_audit", DEFAULT_MEMORY_AUDIT_OUTPUT, "memory_artifact", False),
        ("memory_audit_surface", DEFAULT_MEMORY_AUDIT_SURFACE, "phone_surface", False),
        ("pattern_evidence_intake", DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT, "control_artifact", False),
        ("pattern_evidence_intake_surface", DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE, "phone_surface", False),
    ]
    artifacts = [
        _readiness_artifact_check(
            root=root,
            name=name,
            path=path,
            kind=kind,
            required=required,
            freshness_hours=freshness_hours,
            now=generated,
        )
        for name, path, kind, required in artifact_specs
    ]
    required = [item for item in artifacts if item["required"]]
    missing_required = [item for item in required if item["freshness_status"] == "missing"]
    stale_required = [item for item in required if item["freshness_status"] == "stale"]
    warn_artifacts = [item for item in artifacts if item["freshness_status"] in {"missing", "stale"} and not item["required"]]
    scheduler = _readiness_scheduler_state(root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    status = _readiness_status(missing_required=missing_required, stale_required=stale_required)
    next_actions = _readiness_next_actions(
        status=status,
        missing_required=missing_required,
        stale_required=stale_required,
        scheduler=scheduler,
    )
    payload = {
        "schema_version": DAILY_READINESS_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": status,
        "freshness_hours": freshness_hours,
        "summary": {
            "required_count": len(required),
            "fresh_required_count": sum(1 for item in required if item["freshness_status"] == "fresh"),
            "missing_required_count": len(missing_required),
            "stale_required_count": len(stale_required),
            "warning_count": len(warn_artifacts),
        },
        "artifacts": artifacts,
        "scheduler": scheduler,
        "phone_links": {
            "daily_home": DEFAULT_DAILY_HOME_SURFACE.as_posix(),
            "phone_access": DEFAULT_PHONE_ACCESS_VERIFY_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "scheduler": DEFAULT_SCHEDULER_OPERATIONS_SURFACE.as_posix(),
            "source_refresh": DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix(),
            "source_freshness_intake": DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE.as_posix(),
            "source_refresh_execution": DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE.as_posix(),
            "pattern_evidence_intake": DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE.as_posix(),
            "pattern_dry_run": DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE.as_posix(),
            "trace": DEFAULT_RUN_TRACE_SURFACE.as_posix(),
            "run_ledger": DEFAULT_DAILY_RUN_LEDGER_SURFACE.as_posix(),
            "handoff": DEFAULT_DAILY_HANDOFF_SURFACE.as_posix(),
            "handoff_study_resolution": DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE.as_posix(),
            "handoff_apply": DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE.as_posix(),
            "drift_review": DEFAULT_DRIFT_REVIEW_SURFACE.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
            "review_effect": DEFAULT_REVIEW_EFFECT_SURFACE.as_posix(),
            "council": DEFAULT_ANALYST_COUNCIL_SURFACE.as_posix(),
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "agenda": DEFAULT_DAILY_BRIEF_AGENDA_SURFACE.as_posix(),
            "memory": DEFAULT_MEMORY_OUTPUT.as_posix(),
            "memory_query": DEFAULT_MEMORY_QUERY_SURFACE.as_posix(),
            "learning": DEFAULT_LEARNING_LEDGER_SURFACE.as_posix(),
            "vault": DEFAULT_VAULT_SURFACE_OUTPUT.as_posix(),
        },
        "next_actions": next_actions,
        "recommended_local_run": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --profile examples/profiles/beginner-conservative.json --dry-run",
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "no_account_access",
            "no_order_execution",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_daily_readiness(
    *,
    project_root: str | Path = ".",
    freshness_hours: int = 24,
    artifact_output_path: str | Path = DEFAULT_DAILY_READINESS_OUTPUT,
    surface_output_path: str | Path = DEFAULT_DAILY_READINESS_SURFACE,
) -> Path:
    payload = build_daily_readiness(project_root=project_root, freshness_hours=freshness_hours)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_daily_readiness(payload), encoding="utf-8")
    return target


def validate_daily_readiness_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DAILY_READINESS_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"ready", "review", "stale", "blocked"}:
        errors.append("status must be ready, review, stale, or blocked")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("artifacts"):
        errors.append("artifacts must not be empty")
    if not payload.get("next_actions"):
        errors.append("next_actions must not be empty")
    required_names = {item.get("name") for item in payload.get("artifacts", []) if item.get("required")}
    for name in ["today_surface", "daily_agenda", "daily_scout", "daily_evidence", "learning_ledger", "archive_manifest"]:
        if name not in required_names:
            errors.append(f"required artifact missing from readiness checks: {name}")
    for index, item in enumerate(payload.get("artifacts", [])):
        for field in ["name", "path", "kind", "required", "exists", "freshness_status"]:
            if field not in item:
                errors.append(f"artifacts[{index}] missing {field}")
        if item.get("freshness_status") not in {"fresh", "stale", "missing"}:
            errors.append(f"artifacts[{index}] invalid freshness_status")
    return errors


def validate_daily_readiness_file(path: str | Path) -> list[str]:
    return validate_daily_readiness_payload(load_json(path))


def build_run_trace(
    *,
    playbook_path: str | Path = DEFAULT_RUNTIME_PLAYBOOK_OUTPUT,
    pattern_radar_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_OUTPUT,
    pattern_evidence_intake_path: str | Path = DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT,
    plan_path: str | Path = Path("reports/daily/research-plan.json"),
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    memory_query_path: str | Path = DEFAULT_MEMORY_QUERY_OUTPUT,
    agenda_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    source_refresh_brief_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT,
    source_freshness_intake_path: str | Path = DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT,
    source_refresh_execution_brief_path: str | Path = DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT,
    scenario_path: str | Path = Path("reports/scenarios/daily-research-sim.json"),
    verdict_path: str | Path = Path("reports/scenarios/daily-research-verdict.json"),
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    task_queue_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    daily_review_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    review_prompt_path: str | Path = DEFAULT_REVIEW_PROMPT_OUTPUT,
    review_effect_path: str | Path = DEFAULT_REVIEW_EFFECT_OUTPUT,
    analyst_council_path: str | Path = DEFAULT_ANALYST_COUNCIL_OUTPUT,
    memory_audit_path: str | Path = DEFAULT_MEMORY_AUDIT_OUTPUT,
    learning_ledger_path: str | Path = DEFAULT_LEARNING_LEDGER_OUTPUT,
    handoff_study_resolution_path: str | Path = DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT,
    scheduler_operations_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_OUTPUT,
    today_path: str | Path = DEFAULT_TODAY_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(timezone.utc)
    step_specs = [
        ("runtime_playbook", playbook_path, "setup", "Defines the local appliance operating pattern.", True),
        ("pattern_radar", pattern_radar_path, "strategy", "Classifies external workflow patterns before they shape future work.", True),
        ("pattern_evidence_intake", pattern_evidence_intake_path, "strategy", "Classifies researched agent patterns against local proof, stale repeats, and approval-gated boundaries.", False),
        ("research_plan", plan_path, "plan", "Turns configured interests into today's candidate topics.", True),
        ("daily_scout", scout_path, "prioritize", "Chooses what the operator should inspect first.", True),
        ("evidence_catalog", evidence_path, "evidence", "Records which local/free sources support the daily scenario.", True),
        ("topic_memory", memory_path, "memory", "Carries accumulated observations into today's context.", True),
        ("memory_query", memory_query_path, "memory", "Recalls prior local context for the scout-selected topic.", False),
        ("daily_agenda", agenda_path, "study", "Converts the scout recommendation into a phone-first study sequence.", True),
        ("source_refresh_brief", source_refresh_brief_path, "gate", "Explains weak evidence and blocked refresh authority.", False),
        ("source_freshness_intake", source_freshness_intake_path, "gate", "Packages source freshness, blocked live candidates, and scoped approval response before any live refresh.", False),
        ("source_refresh_execution_brief", source_refresh_execution_brief_path, "gate", "Shows final-confirmation, stop conditions, rollback, and absorption path before any live source execution.", False),
        ("scenario_report", scenario_path, "simulate", "Builds beginner-readable paths from available evidence.", True),
        ("verdict", verdict_path, "summarize", "Summarizes the research-only next inspection posture.", True),
        ("analyst_journal", journal_path, "reflect", "Records role notes and follow-up questions.", True),
        ("task_queue", task_queue_path, "queue", "Turns the journal into local analyst tasks.", True),
        ("task_ledger", task_ledger_path, "queue", "Preserves task state across days.", True),
        ("daily_review", daily_review_path, "feedback", "Records what the operator read, skipped, or wants more of.", False),
        ("review_prompt", review_prompt_path, "feedback", "Suggests copy-ready responses so operator feedback can shape the next run.", False),
        ("review_effect", review_effect_path, "feedback", "Proves whether recorded review feedback actually shaped scout scoring.", False),
        ("analyst_council", analyst_council_path, "review", "Checks today's brief through role-specific agreement, disagreement, and beginner-readiness.", False),
        ("memory_audit", memory_audit_path, "memory", "Audits accumulated memory, vault notes, archives, source posture, and review feedback.", False),
        ("learning_ledger", learning_ledger_path, "learn", "Turns today's brief into beginner concepts and carried questions.", True),
        ("handoff_study_resolution", handoff_study_resolution_path, "learn", "Turns unresolved handoff items into answer candidates, evidence refs, and stop conditions.", False),
        ("scheduler_operations", scheduler_operations_path, "ops", "Shows automation readiness without host writes.", False),
        ("today_surface", today_path, "publish", "Renders the phone-readable daily entry point.", True),
    ]
    trace_steps = [
        _run_trace_step(name=name, path=path, stage=stage, influence=influence, required=required, now=generated)
        for name, path, stage, influence, required in step_specs
    ]
    payloads = {step["name"]: _load_optional_json(step["path"]) for step in trace_steps}
    missing_required = [step for step in trace_steps if step["required"] and step["status"] == "missing"]
    stale_steps = [step for step in trace_steps if step["freshness_status"] == "stale"]
    external_flags = _run_trace_external_flags(payloads)
    payload = {
        "schema_version": RUN_TRACE_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": "blocked" if missing_required else ("review" if stale_steps else "ready"),
        "run_id": _run_trace_run_id(payloads),
        "summary": {
            "step_count": len(trace_steps),
            "fresh_count": sum(1 for step in trace_steps if step["freshness_status"] == "fresh"),
            "missing_required_count": len(missing_required),
            "stale_count": len(stale_steps),
            "external_effect_flag_count": len(external_flags),
        },
        "what_shaped_today": _run_trace_influences(payloads),
        "trace_steps": trace_steps,
        "weak_spots": _run_trace_weak_spots(trace_steps=trace_steps, payloads=payloads, external_flags=external_flags),
        "operator_debug_order": [
            "daily_scout",
            "evidence_catalog",
            "topic_memory",
            "scenario_report",
            "verdict",
            "pattern_evidence_intake",
            "source_refresh_brief",
            "source_refresh_execution_brief",
            "task_ledger",
            "daily_review",
            "review_prompt",
            "review_effect",
            "analyst_council",
            "memory_audit",
            "handoff_study_resolution",
        ],
        "phone_links": {
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
            "trace": DEFAULT_RUN_TRACE_SURFACE.as_posix(),
            "run_ledger": DEFAULT_DAILY_RUN_LEDGER_SURFACE.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
            "review_effect": DEFAULT_REVIEW_EFFECT_SURFACE.as_posix(),
            "handoff_apply": DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE.as_posix(),
            "council": DEFAULT_ANALYST_COUNCIL_SURFACE.as_posix(),
            "pattern_radar": DEFAULT_AGENT_PATTERN_RADAR_SURFACE.as_posix(),
            "pattern_evidence_intake": DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE.as_posix(),
            "memory": DEFAULT_MEMORY_OUTPUT.as_posix(),
            "memory_query": DEFAULT_MEMORY_QUERY_SURFACE.as_posix(),
            "memory_audit": DEFAULT_MEMORY_AUDIT_SURFACE.as_posix(),
            "learning": DEFAULT_LEARNING_LEDGER_SURFACE.as_posix(),
            "handoff_study_resolution": DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE.as_posix(),
            "tasks": DEFAULT_ANALYST_TASK_QUEUE_OUTPUT.as_posix(),
            "source_refresh": DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix(),
            "source_freshness_intake": DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE.as_posix(),
            "source_refresh_execution": DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "trace_reads_existing_artifacts_only",
            "does_not_execute_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_live_trading",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_run_trace(
    *,
    artifact_output_path: str | Path = DEFAULT_RUN_TRACE_OUTPUT,
    surface_output_path: str | Path = DEFAULT_RUN_TRACE_SURFACE,
    **paths: Any,
) -> Path:
    payload = build_run_trace(**paths)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_run_trace(payload), encoding="utf-8")
    return target


def validate_run_trace_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != RUN_TRACE_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"ready", "review", "blocked"}:
        errors.append(f"invalid status {payload.get('status')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    steps = payload.get("trace_steps", [])
    if not steps:
        errors.append("trace_steps must not be empty")
    names = {step.get("name") for step in steps}
    for name in ["daily_scout", "evidence_catalog", "scenario_report", "verdict", "learning_ledger", "today_surface"]:
        if name not in names:
            errors.append(f"trace missing required step {name}")
    for index, step in enumerate(steps):
        for field in ["name", "stage", "path", "status", "freshness_status", "influence", "required"]:
            if field not in step:
                errors.append(f"trace_steps[{index}] missing {field}")
        if step.get("freshness_status") not in {"fresh", "stale", "missing"}:
            errors.append(f"trace_steps[{index}] invalid freshness_status")
    boundary = payload.get("safety_boundary", [])
    if "trace_reads_existing_artifacts_only" not in boundary:
        errors.append("safety_boundary must include trace_reads_existing_artifacts_only")
    if "does_not_execute_live_network" not in boundary:
        errors.append("safety_boundary must include does_not_execute_live_network")
    return errors


def validate_run_trace_file(path: str | Path) -> list[str]:
    return validate_run_trace_payload(load_json(path))


def build_daily_run_ledger(
    *,
    previous_ledger_path: str | Path = DEFAULT_DAILY_RUN_LEDGER_OUTPUT,
    run_trace_path: str | Path = DEFAULT_RUN_TRACE_OUTPUT,
    morning_path: str | Path = DEFAULT_MORNING_CONTROL_OUTPUT,
    readiness_path: str | Path = DEFAULT_DAILY_READINESS_OUTPUT,
    scheduler_operations_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_OUTPUT,
    archive_manifest_path: str | Path | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(timezone.utc)
    trace = _load_optional_json(run_trace_path)
    morning = _load_optional_json(morning_path)
    readiness = _load_optional_json(readiness_path)
    scheduler = _load_optional_json(scheduler_operations_path)
    archive_path = Path(archive_manifest_path) if archive_manifest_path else _latest_archive_manifest(DEFAULT_ARCHIVE_ROOT)
    archive = _load_optional_json(archive_path) if archive_path else {}
    previous = _load_optional_json(previous_ledger_path)
    previous_entries = previous.get("entries", []) if previous.get("schema_version") == DAILY_RUN_LEDGER_SCHEMA_VERSION else []
    entry = _daily_run_ledger_entry(
        generated=generated,
        trace=trace,
        morning=morning,
        readiness=readiness,
        scheduler=scheduler,
        archive=archive,
        archive_path=archive_path,
        run_trace_path=run_trace_path,
        morning_path=morning_path,
        readiness_path=readiness_path,
        scheduler_operations_path=scheduler_operations_path,
    )
    entries = _daily_run_ledger_entries(previous_entries=previous_entries, current_entry=entry)
    local_day = entry["local_day"]
    today_entries = [item for item in entries if item.get("local_day") == local_day]
    canonical_entry_id = _daily_run_ledger_canonical_entry_id(today_entries)
    for item in entries:
        if item.get("local_day") == local_day:
            item["canonical_status"] = "canonical" if item.get("entry_id") == canonical_entry_id else "duplicate_same_day"
        elif item.get("canonical_status") == "canonical":
            item["canonical_status"] = "historical_canonical"
    payload = {
        "schema_version": DAILY_RUN_LEDGER_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": "ready" if entry["run_status"] in {"ready", "review", "aligned"} else "review",
        "canonical_entry_id": canonical_entry_id,
        "today_local_day": local_day,
        "summary": {
            "entry_count": len(entries),
            "today_run_count": len(today_entries),
            "duplicate_today_count": max(0, len(today_entries) - 1),
            "latest_run_status": entry["run_status"],
            "latest_scheduler_status": entry["scheduler_status"],
            "latest_external_effect_performed": entry["external_effect_performed"],
            "latest_host_write_performed": entry["host_write_performed"],
        },
        "entries": entries[:40],
        "phone_links": {
            "run_ledger": DEFAULT_DAILY_RUN_LEDGER_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
            "trace": DEFAULT_RUN_TRACE_SURFACE.as_posix(),
            "scheduler": DEFAULT_SCHEDULER_OPERATIONS_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "ledger_reads_existing_artifacts_only",
            "does_not_execute_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_live_trading",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_daily_run_ledger(
    *,
    artifact_output_path: str | Path = DEFAULT_DAILY_RUN_LEDGER_OUTPUT,
    surface_output_path: str | Path = DEFAULT_DAILY_RUN_LEDGER_SURFACE,
    **paths: Any,
) -> Path:
    payload = build_daily_run_ledger(previous_ledger_path=artifact_output_path, **paths)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_daily_run_ledger(payload), encoding="utf-8")
    return target


def validate_daily_run_ledger_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DAILY_RUN_LEDGER_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"ready", "review"}:
        errors.append(f"invalid status {payload.get('status')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if not payload.get("canonical_entry_id"):
        errors.append("canonical_entry_id must not be empty")
    entries = payload.get("entries", [])
    if not entries:
        errors.append("entries must not be empty")
    canonical_count = sum(1 for entry in entries if entry.get("canonical_status") == "canonical")
    if canonical_count != 1:
        errors.append("exactly one current canonical entry is required")
    for index, entry in enumerate(entries):
        for field in ["entry_id", "local_day", "run_id", "generated_at", "run_status", "canonical_status", "archive_manifest", "today_path"]:
            if field not in entry:
                errors.append(f"entries[{index}] missing {field}")
        if entry.get("external_effect_performed") is not False:
            errors.append(f"entries[{index}] external_effect_performed must be false")
        if entry.get("host_write_performed") is not False:
            errors.append(f"entries[{index}] host_write_performed must be false")
    boundary = payload.get("safety_boundary", [])
    if "ledger_reads_existing_artifacts_only" not in boundary:
        errors.append("safety_boundary must include ledger_reads_existing_artifacts_only")
    if "does_not_write_host_scheduler" not in boundary:
        errors.append("safety_boundary must include does_not_write_host_scheduler")
    return errors


def validate_daily_run_ledger_file(path: str | Path) -> list[str]:
    return validate_daily_run_ledger_payload(load_json(path))


def render_daily_run_ledger(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    rows = "".join(
        "<tr>"
        f"<td><strong>{esc(entry.get('local_day', ''))}</strong><span>{esc(entry.get('canonical_status', ''))}</span></td>"
        f"<td>{esc(entry.get('run_id', ''))}</td>"
        f"<td>{esc(entry.get('run_status', ''))}</td>"
        f"<td>{esc(entry.get('scheduler_status', ''))}</td>"
        f"<td><a href='{esc(_relative_href(Path(entry.get('today_path', ''))))}'>today</a> · <a href='{esc(_relative_href(Path(entry.get('archive_manifest', ''))))}'>archive</a></td>"
        "</tr>"
        for entry in payload.get("entries", [])[:12]
    )
    duplicate_note = (
        "오늘 같은 local day에 여러 run이 있습니다. canonical run만 먼저 읽고 나머지는 validation/manual run으로 취급하세요."
        if summary.get("duplicate_today_count", 0)
        else "오늘은 현재 canonical run 하나만 기록되어 있습니다."
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if path and label != "run_ledger"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Daily Run Ledger</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:840px; margin:0 auto; padding:16px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small,td span {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:14px 0; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
td strong,td span {{ display:block; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
@media (max-width:680px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.links {{ grid-template-columns:1fr; }} table {{ font-size:13px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Run Ledger · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘 어떤 run을 믿을지</h1>
<p>예약 실행, 수동 실행, 검증 실행이 같은 날 겹쳐도 canonical run과 중복 run을 분리해서 봅니다.</p>
</header>
<section class="hero">
<div class="metrics">
<article class="metric"><span>Today Runs</span><strong>{esc(summary.get('today_run_count', 0))}</strong></article>
<article class="metric"><span>Duplicates</span><strong>{esc(summary.get('duplicate_today_count', 0))}</strong></article>
<article class="metric"><span>Status</span><strong>{esc(summary.get('latest_run_status', ''))}</strong></article>
<article class="metric"><span>Effects</span><strong>{esc('yes' if summary.get('latest_external_effect_performed') else 'no')}</strong></article>
</div>
<p>{esc(duplicate_note)}</p>
</section>
<section class="section">
<h2>Run history</h2>
<table><thead><tr><th>Day</th><th>Run</th><th>Status</th><th>Scheduler</th><th>Links</th></tr></thead><tbody>{rows}</tbody></table>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 ledger는 기존 로컬 artifact만 읽고 오늘의 canonical run을 표시합니다. live network, 알림 발송, host scheduler write, credential 사용, 계좌 접근, 주문 실행은 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def build_daily_handoff(
    *,
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    daily_review_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    review_effect_path: str | Path = DEFAULT_REVIEW_EFFECT_OUTPUT,
    analyst_council_path: str | Path = DEFAULT_ANALYST_COUNCIL_OUTPUT,
    memory_audit_path: str | Path = DEFAULT_MEMORY_AUDIT_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    run_ledger_path: str | Path = DEFAULT_DAILY_RUN_LEDGER_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(timezone.utc)
    journal = _load_optional_json(journal_path)
    task_ledger = _load_optional_json(task_ledger_path)
    daily_review = _load_optional_json(daily_review_path)
    review_effect = _load_optional_json(review_effect_path)
    council = _load_optional_json(analyst_council_path)
    memory_audit = _load_optional_json(memory_audit_path)
    scout = _load_optional_json(scout_path)
    run_ledger = _load_optional_json(run_ledger_path)
    canonical_run = _daily_handoff_canonical_run(run_ledger)
    carried_forward = _daily_handoff_carried_items(
        journal=journal,
        task_ledger=task_ledger,
        daily_review=daily_review,
        review_effect=review_effect,
        council=council,
        memory_audit=memory_audit,
        scout=scout,
    )
    reflected = [item for item in carried_forward if item.get("reflected_today")]
    unresolved = [item for item in carried_forward if not item.get("reflected_today")]
    study_closure = _daily_handoff_study_closure(unresolved=unresolved, council=council, memory_audit=memory_audit, scout=scout)
    duplicate_count = int(run_ledger.get("summary", {}).get("duplicate_today_count", 0) or 0)
    status = "blocked" if not canonical_run else ("review" if unresolved or duplicate_count else "ready")
    payload = {
        "schema_version": DAILY_HANDOFF_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": status,
        "run_id": canonical_run.get("run_id", journal.get("run_id", scout.get("run_id", ""))),
        "summary": {
            "carried_item_count": len(carried_forward),
            "reflected_today_count": len(reflected),
            "unresolved_count": len(unresolved),
            "duplicate_today_count": duplicate_count,
            "review_effect_status": review_effect.get("status", "missing"),
            "council_status": council.get("status", "missing"),
            "memory_risk_count": int(memory_audit.get("summary", {}).get("risk_count", 0) or 0),
            "study_closure_count": study_closure.get("item_count", 0),
        },
        "canonical_run": canonical_run,
        "carried_forward": carried_forward,
        "reflected_today": reflected,
        "unresolved": unresolved,
        "study_closure": study_closure,
        "copy_ready_commands": _daily_handoff_commands(unresolved=unresolved, scout=scout),
        "artifact_inputs": {
            "journal": Path(journal_path).as_posix(),
            "task_ledger": Path(task_ledger_path).as_posix(),
            "daily_review": Path(daily_review_path).as_posix(),
            "review_effect": Path(review_effect_path).as_posix(),
            "analyst_council": Path(analyst_council_path).as_posix(),
            "memory_audit": Path(memory_audit_path).as_posix(),
            "daily_scout": Path(scout_path).as_posix(),
            "daily_run_ledger": Path(run_ledger_path).as_posix(),
        },
        "phone_links": {
            "handoff": DEFAULT_DAILY_HANDOFF_SURFACE.as_posix(),
            "handoff_apply": DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "run_ledger": DEFAULT_DAILY_RUN_LEDGER_SURFACE.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
            "review_effect": DEFAULT_REVIEW_EFFECT_SURFACE.as_posix(),
            "council": DEFAULT_ANALYST_COUNCIL_SURFACE.as_posix(),
            "tasks": DEFAULT_ANALYST_TASK_LEDGER_OUTPUT.as_posix(),
            "memory_audit": DEFAULT_MEMORY_AUDIT_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "handoff_reads_existing_artifacts_only",
            "does_not_execute_tasks",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_live_trading",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_daily_handoff(
    *,
    artifact_output_path: str | Path = DEFAULT_DAILY_HANDOFF_OUTPUT,
    surface_output_path: str | Path = DEFAULT_DAILY_HANDOFF_SURFACE,
    **paths: Any,
) -> Path:
    payload = build_daily_handoff(**paths)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_daily_handoff(payload), encoding="utf-8")
    return target


def validate_daily_handoff_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DAILY_HANDOFF_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"ready", "review", "blocked"}:
        errors.append(f"invalid status {payload.get('status')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    summary = payload.get("summary", {})
    for field in ["carried_item_count", "reflected_today_count", "unresolved_count", "duplicate_today_count", "study_closure_count"]:
        if field not in summary:
            errors.append(f"summary missing {field}")
    if payload.get("status") != "blocked" and not payload.get("canonical_run", {}).get("entry_id"):
        errors.append("canonical_run.entry_id must not be empty unless blocked")
    for index, item in enumerate(payload.get("carried_forward", [])):
        for field in ["id", "kind", "title", "source", "reflected_today", "evidence", "next_action"]:
            if field not in item:
                errors.append(f"carried_forward[{index}] missing {field}")
    closure = payload.get("study_closure", {})
    for field in ["status", "item_count", "items", "external_effect_performed", "host_write_performed"]:
        if field not in closure:
            errors.append(f"study_closure missing {field}")
    if closure.get("external_effect_performed") is not False:
        errors.append("study_closure.external_effect_performed must be false")
    if closure.get("host_write_performed") is not False:
        errors.append("study_closure.host_write_performed must be false")
    if closure.get("item_count", 0) != len(closure.get("items", [])):
        errors.append("study_closure.item_count must match items length")
    for index, item in enumerate(closure.get("items", [])):
        for field in ["id", "kind", "title", "beginner_question", "why_it_matters", "source", "linked_surface", "copy_ready_command", "done_when", "severity", "external_effect_performed", "host_write_performed"]:
            if field not in item:
                errors.append(f"study_closure.items[{index}] missing {field}")
        if item.get("external_effect_performed") is not False:
            errors.append(f"study_closure.items[{index}].external_effect_performed must be false")
        if item.get("host_write_performed") is not False:
            errors.append(f"study_closure.items[{index}].host_write_performed must be false")
    for index, command in enumerate(payload.get("copy_ready_commands", [])):
        if not command.get("command"):
            errors.append(f"copy_ready_commands[{index}] missing command")
        if command.get("external_effect_performed") is not False:
            errors.append(f"copy_ready_commands[{index}] external_effect_performed must be false")
    if not payload.get("phone_links", {}).get("handoff"):
        errors.append("phone_links.handoff must not be empty")
    boundary = payload.get("safety_boundary", [])
    if "handoff_reads_existing_artifacts_only" not in boundary:
        errors.append("safety_boundary must include handoff_reads_existing_artifacts_only")
    if "does_not_execute_tasks" not in boundary:
        errors.append("safety_boundary must include does_not_execute_tasks")
    return errors


def validate_daily_handoff_file(path: str | Path) -> list[str]:
    return validate_daily_handoff_payload(load_json(path))


def build_handoff_study_resolution(
    *,
    handoff_path: str | Path = DEFAULT_DAILY_HANDOFF_OUTPUT,
    learning_ledger_path: str | Path = DEFAULT_LEARNING_LEDGER_OUTPUT,
    memory_query_path: str | Path = DEFAULT_MEMORY_QUERY_OUTPUT,
    memory_audit_path: str | Path = DEFAULT_MEMORY_AUDIT_OUTPUT,
    source_freshness_intake_path: str | Path = DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT,
    analyst_council_path: str | Path = DEFAULT_ANALYST_COUNCIL_OUTPUT,
    review_prompt_path: str | Path = DEFAULT_REVIEW_PROMPT_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(timezone.utc)
    handoff = _load_optional_json(handoff_path)
    learning = _load_optional_json(learning_ledger_path)
    memory_query = _load_optional_json(memory_query_path)
    memory_audit = _load_optional_json(memory_audit_path)
    freshness = _load_optional_json(source_freshness_intake_path)
    council = _load_optional_json(analyst_council_path)
    review_prompt = _load_optional_json(review_prompt_path)
    items: list[dict[str, Any]] = []
    study_items = handoff.get("study_closure", {}).get("items", [])
    freshness_summary = freshness.get("summary", {}) if freshness.get("schema_version") == SOURCE_FRESHNESS_INTAKE_SCHEMA_VERSION else {}
    freshness_blocked = int(freshness_summary.get("blocked_live_candidate_count", 0) or 0)
    weak_sources = int(freshness_summary.get("stale_or_sample_source_count", 0) or 0)
    memory_quality = memory_query.get("recall_quality", {}) if memory_query.get("schema_version") == MEMORY_QUERY_SCHEMA_VERSION else {}
    memory_level = memory_quality.get("level", "missing")
    memory_summary = memory_quality.get("summary", "로컬 기억 회상 품질을 아직 판단할 수 없습니다.")
    learning_questions = learning.get("questions", []) if learning.get("schema_version") == LEARNING_LEDGER_SCHEMA_VERSION else []
    review_cards = review_prompt.get("prompt_cards", []) if review_prompt.get("schema_version") == OPERATOR_REVIEW_PROMPT_SCHEMA_VERSION else []
    council_decision = council.get("decision", {}) if council.get("schema_version") == ANALYST_COUNCIL_SCHEMA_VERSION else {}

    for index, item in enumerate(study_items, start=1):
        kind = item.get("kind", "study_closure")
        blocked_by_freshness = kind in {"follow_up_question", "council_warning"} and freshness_blocked > 0
        if blocked_by_freshness:
            status = "blocked_by_source_freshness"
            confidence = "low"
            answer = "현재 답변 후보는 sample/cache 근거에 의존합니다. live source refresh 승인이 없으면 방향성 학습용으로만 읽어야 합니다."
        elif memory_level in {"strong", "usable"}:
            status = "ready_to_study"
            confidence = "medium"
            answer = f"로컬 기억은 {memory_level} 상태입니다. 오늘은 '{item.get('beginner_question', item.get('title', '질문'))}'에 대해 기억/브리프/경고를 연결해 한 문장으로 정리할 수 있습니다."
        else:
            status = "needs_operator_response"
            confidence = "low"
            answer = f"근거가 아직 얇습니다. 먼저 '{item.get('beginner_question', item.get('title', '질문'))}'에 답이 되는 문장 하나와 모르는 점 하나를 분리해 적으세요."
        if kind == "council_warning":
            answer = f"council은 오늘 결론을 바로 믿기보다 '{council_decision.get('operator_action', item.get('title', '주의 항목'))}'를 먼저 확인하라고 요구합니다."
        elif kind == "memory_warning":
            answer = f"기억 경고는 결론 문제가 아니라 누적 맥락 문제입니다. {memory_summary}"
        evidence_refs = [
            {
                "label": "handoff",
                "path": Path(handoff_path).as_posix(),
                "note": item.get("why_it_matters", ""),
            },
            {
                "label": "memory",
                "path": Path(memory_query_path).as_posix(),
                "note": memory_summary,
            },
            {
                "label": "source freshness",
                "path": Path(source_freshness_intake_path).as_posix(),
                "note": f"weak={weak_sources}, blocked_live={freshness_blocked}",
            },
        ]
        linked_questions = [
            question.get("question", question.get("title", ""))
            for question in learning_questions
            if question.get("question") or question.get("title")
        ][:3]
        if not linked_questions:
            linked_questions = [
                card.get("question", card.get("title", ""))
                for card in review_cards
                if card.get("question") or card.get("title")
            ][:3]
        items.append({
            "id": f"HSR-{index:03d}",
            "source_item_id": item.get("source_item_id", item.get("id", "")),
            "kind": kind,
            "title": item.get("title", "남은 질문"),
            "status": status,
            "confidence": confidence,
            "beginner_question": item.get("beginner_question", item.get("title", "")),
            "why_it_matters": item.get("why_it_matters", ""),
            "answer_candidate": answer,
            "evidence_refs": evidence_refs,
            "linked_learning_questions": linked_questions,
            "done_when": item.get("done_when", "답이 되는 문장 하나와 아직 부족한 근거 하나를 말할 수 있습니다."),
            "stop_condition": "오늘은 이 질문을 매수/매도 판단으로 바꾸지 않고, 공부용 응답 한 줄만 남기면 충분합니다.",
            "copy_ready_command": item.get("copy_ready_command", ""),
            "external_effect_performed": False,
            "host_write_performed": False,
        })
    ready_count = sum(1 for item in items if item["status"] == "ready_to_study")
    blocked_count = sum(1 for item in items if item["status"] == "blocked_by_source_freshness")
    response_count = sum(1 for item in items if item.get("copy_ready_command"))
    status = "clear" if not items else ("blocked_by_source_freshness" if blocked_count == len(items) else "review")
    return {
        "schema_version": HANDOFF_STUDY_RESOLUTION_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": status,
        "run_id": handoff.get("run_id", ""),
        "summary": {
            "handoff_unresolved_count": handoff.get("summary", {}).get("unresolved_count", 0),
            "resolution_item_count": len(items),
            "ready_to_study_count": ready_count,
            "blocked_by_source_freshness_count": blocked_count,
            "copy_ready_response_count": response_count,
            "memory_recall_quality": memory_level,
            "weak_source_count": weak_sources,
        },
        "operator_rule": "이 화면은 질문을 자동으로 닫지 않습니다. 답변 후보를 읽고, 사람이 복사 가능한 local 응답 한 줄을 실행했을 때만 다음 run에 반영됩니다.",
        "items": items,
        "phone_links": {
            "handoff_study_resolution": DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE.as_posix(),
            "handoff": DEFAULT_DAILY_HANDOFF_SURFACE.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
            "learning": DEFAULT_LEARNING_LEDGER_SURFACE.as_posix(),
            "memory_query": DEFAULT_MEMORY_QUERY_SURFACE.as_posix(),
            "memory_audit": DEFAULT_MEMORY_AUDIT_SURFACE.as_posix(),
            "source_freshness_intake": DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE.as_posix(),
            "daily_home": DEFAULT_DAILY_HOME_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_order_execution",
            "operator_response_required_to_close",
        ],
    }


def write_handoff_study_resolution(
    *,
    artifact_output_path: str | Path = DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT,
    surface_output_path: str | Path = DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE,
    **paths: Any,
) -> Path:
    payload = build_handoff_study_resolution(**paths)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_handoff_study_resolution(payload), encoding="utf-8")
    return target


def validate_handoff_study_resolution_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != HANDOFF_STUDY_RESOLUTION_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"clear", "review", "blocked_by_source_freshness"}:
        errors.append("status must be clear, review, or blocked_by_source_freshness")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    summary = payload.get("summary", {})
    for field in ["handoff_unresolved_count", "resolution_item_count", "ready_to_study_count", "blocked_by_source_freshness_count", "copy_ready_response_count", "memory_recall_quality", "weak_source_count"]:
        if field not in summary:
            errors.append(f"summary missing {field}")
    if summary.get("resolution_item_count", 0) != len(payload.get("items", [])):
        errors.append("summary.resolution_item_count must match items length")
    for index, item in enumerate(payload.get("items", [])):
        for field in ["id", "source_item_id", "kind", "title", "status", "confidence", "beginner_question", "answer_candidate", "evidence_refs", "done_when", "stop_condition", "copy_ready_command", "external_effect_performed", "host_write_performed"]:
            if field not in item:
                errors.append(f"items[{index}] missing {field}")
        if item.get("status") not in {"ready_to_study", "needs_operator_response", "blocked_by_source_freshness"}:
            errors.append(f"items[{index}].status invalid")
        if item.get("confidence") not in {"low", "medium", "high"}:
            errors.append(f"items[{index}].confidence invalid")
        if item.get("external_effect_performed") is not False:
            errors.append(f"items[{index}].external_effect_performed must be false")
        if item.get("host_write_performed") is not False:
            errors.append(f"items[{index}].host_write_performed must be false")
        if not item.get("evidence_refs"):
            errors.append(f"items[{index}].evidence_refs must not be empty")
    for field in ["handoff_study_resolution", "handoff", "review_prompt", "learning", "memory_query", "source_freshness_intake", "daily_home"]:
        if not payload.get("phone_links", {}).get(field):
            errors.append(f"phone_links.{field} must not be empty")
    for required in ["reads_local_artifacts_only", "operator_response_required_to_close", "does_not_fetch_live_network"]:
        if required not in payload.get("safety_boundary", []):
            errors.append(f"safety_boundary must include {required}")
    forbidden = [" --send", "--confirm-host-write", "--execute", "--confirm-live-network", "launchctl bootstrap"]
    for index, item in enumerate(payload.get("items", [])):
        command = item.get("copy_ready_command", "")
        if any(fragment in command for fragment in forbidden):
            errors.append(f"items[{index}].copy_ready_command includes gated execution fragment")
    return errors


def validate_handoff_study_resolution_file(path: str | Path) -> list[str]:
    return validate_handoff_study_resolution_payload(load_json(path))


def render_handoff_study_resolution(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    status_label = {
        "clear": "닫을 handoff 없음",
        "review": "공부 후 응답 필요",
        "blocked_by_source_freshness": "근거 신선도 승인 전",
    }.get(payload.get("status", ""), payload.get("status", "review"))
    cards = "".join(
        "<article class='card'>"
        f"<span>{esc(item.get('status', ''))} · confidence {esc(item.get('confidence', ''))}</span>"
        f"<h2>{esc(item.get('title', ''))}</h2>"
        f"<p><strong>질문</strong> {esc(item.get('beginner_question', ''))}</p>"
        f"<p><strong>답변 후보</strong> {esc(item.get('answer_candidate', ''))}</p>"
        f"<p><strong>끝나는 조건</strong> {esc(item.get('done_when', ''))}</p>"
        f"<p><strong>멈춤 기준</strong> {esc(item.get('stop_condition', ''))}</p>"
        f"<code>{esc(item.get('copy_ready_command', ''))}</code>"
        "</article>"
        for item in payload.get("items", [])
    ) or "<p>오늘 handoff에서 따로 닫을 공부 항목은 없습니다.</p>"
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "handoff_study_resolution" and path
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Handoff Study Resolution</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#64707d; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
html,body {{ max-width:100%; overflow-x:hidden; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:430px; margin:0; padding:14px; }}
a {{ color:var(--blue); font-weight:900; text-decoration:none; }}
.eyebrow,.metric span,.card span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:31px; line-height:1.12; overflow-wrap:anywhere; }}
h2 {{ margin:6px 0 8px; font-size:19px; line-height:1.2; }}
p {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.card,.metric {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:15px; margin:12px 0; }}
.status {{ display:block; margin:10px 0; font-size:25px; line-height:1.15; }}
.metrics {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.metric,.card {{ padding:12px; background:white; min-width:0; }}
.metric strong {{ display:block; font-size:24px; }}
.stack {{ display:grid; grid-template-columns:minmax(0,1fr); gap:9px; }}
code {{ display:block; white-space:pre-wrap; word-break:break-word; border:1px solid var(--line); border-radius:8px; background:#f1f5f7; padding:10px; color:var(--ink); font-size:12px; }}
.links {{ display:grid; grid-template-columns:1fr; gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Handoff Study · {_local_date_label(payload.get('generated_at', ''))}</span>
<h1>남은 질문을 공부로 닫기</h1>
<p>전날에서 넘어온 질문을 숨기지 않고, 오늘 어떤 근거로 어디까지 답하면 충분한지 보여줍니다.</p>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('operator_rule', ''))}</p>
<div class="metrics">
<article class="metric"><span>Items</span><strong>{esc(summary.get('resolution_item_count', 0))}</strong></article>
<article class="metric"><span>Ready</span><strong>{esc(summary.get('ready_to_study_count', 0))}</strong></article>
<article class="metric"><span>Blocked</span><strong>{esc(summary.get('blocked_by_source_freshness_count', 0))}</strong></article>
<article class="metric"><span>Memory</span><strong>{esc(summary.get('memory_recall_quality', 'missing'))}</strong></article>
</div>
</section>
<section class="section">
<h2>질문별 해소 카드</h2>
<div class="stack">{cards}</div>
</section>
<section class="section">
<h2>관련 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 기존 로컬 artifact만 읽습니다. live network, 알림 발송, host scheduler write, credential 사용, 계좌 접근, 주문 실행은 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def parse_handoff_response(response: str) -> dict[str, Any]:
    try:
        parts = shlex.split(response.strip())
    except ValueError as error:
        raise ValueError(f"response must be shell-quote parseable: {error}") from error
    if not parts:
        raise ValueError("response must not be empty")
    first = parts[0].strip()
    route = "task_status" if first.startswith("AT-") else "daily_review"
    if route == "task_status":
        parsed = parse_task_status_response(response)
    else:
        parsed = parse_daily_review_response(response)
    return {
        "schema_version": "daily_handoff_response.v1",
        "recorded_at": _now(),
        "route": route,
        "raw_response": response,
        "parsed_response": parsed,
        "external_effect_performed": False,
    }


def record_handoff_response(
    *,
    response: str,
    responses_path: str | Path = DEFAULT_HANDOFF_RESPONSES,
) -> tuple[Path, dict[str, Any]]:
    payload = parse_handoff_response(response)
    target = Path(responses_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return target, payload


def write_operator_handoff_response_apply(
    *,
    payload: dict[str, Any],
    artifact_output_path: str | Path = DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT,
    surface_output_path: str | Path = DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE,
) -> Path:
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_operator_handoff_response_apply(payload), encoding="utf-8")
    return target


def validate_operator_handoff_response_apply_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != OPERATOR_HANDOFF_RESPONSE_APPLY_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"applied", "blocked"}:
        errors.append("status must be applied or blocked")
    if payload.get("route") not in {"daily_review", "task_status"}:
        errors.append("route must be daily_review or task_status")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    for field in ["operator_response", "handoff_response", "responses_path", "daily_handoff", "next_action"]:
        if field not in payload:
            errors.append(f"missing {field}")
    if not payload.get("daily_handoff", {}).get("surface"):
        errors.append("daily_handoff.surface must not be empty")
    if "local_handoff_response_apply_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include local_handoff_response_apply_only")
    if payload.get("route") == "daily_review" and "review_effect" not in payload:
        errors.append("daily_review route must include review_effect")
    if payload.get("route") == "task_status" and "task_status_apply" not in payload:
        errors.append("task_status route must include task_status_apply")
    return errors


def validate_operator_handoff_response_apply_file(path: str | Path) -> list[str]:
    return validate_operator_handoff_response_apply_payload(load_json(path))


def render_operator_handoff_response_apply(payload: dict[str, Any]) -> str:
    handoff = payload.get("daily_handoff", {})
    review = payload.get("daily_review", {})
    effect = payload.get("review_effect", {})
    task_apply = payload.get("task_status_apply", {})
    task_ledger = payload.get("task_ledger", {})
    route_label = "review feedback" if payload.get("route") == "daily_review" else "task status"
    metrics = [
        ("Route", route_label),
        ("Status", payload.get("status", "")),
        ("Handoff", handoff.get("status", "unknown")),
        ("Unresolved", handoff.get("unresolved_count", 0)),
    ]
    if payload.get("route") == "daily_review":
        metrics.extend([
            ("Responses", review.get("response_count", 0)),
            ("Effect", effect.get("status", "unknown")),
        ])
    else:
        metrics.extend([
            ("Task applied", task_apply.get("applied_count", 0)),
            ("Ledger", task_ledger.get("entry_count", 0)),
        ])
    metric_cards = "".join(
        "<article class='metric'>"
        f"<span>{esc(label)}</span>"
        f"<strong>{esc(value)}</strong>"
        "</article>"
        for label, value in metrics
    )
    links = {
        "handoff": handoff.get("surface", DEFAULT_DAILY_HANDOFF_SURFACE.as_posix()),
        "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
        "review_effect": effect.get("surface", DEFAULT_REVIEW_EFFECT_SURFACE.as_posix()),
        "task_ledger": task_ledger.get("surface", DEFAULT_ANALYST_TASK_LEDGER_OUTPUT.as_posix()),
    }
    link_cards = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in links.items()
        if path
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Handoff Response Apply</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow,.metric span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics,.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:24px; overflow-wrap:anywhere; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Handoff Apply · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>handoff 응답 적용</h1>
<p>handoff에서 복사한 짧은 응답을 로컬 메모리와 증거 산출물에 반영한 proof입니다.</p>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<strong class="status">{esc(payload.get('status', ''))}</strong>
<p>{esc(payload.get('next_action', ''))}</p>
<code>{esc(payload.get('operator_response', ''))}</code>
</section>
<section class="section">
<h2>적용 결과</h2>
<div class="metrics">{metric_cards}</div>
</section>
<section class="section">
<h2>갱신된 화면</h2>
<div class="links">{link_cards}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 apply는 로컬 review/task/handoff proof만 갱신합니다. task 실행, live network, 알림 전송, host write, credential, 계좌 접근, 주문 실행을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_daily_handoff(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    canonical = payload.get("canonical_run", {})
    study = payload.get("study_closure", {})
    carried_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(item.get('kind', 'item'))} · {esc('반영됨' if item.get('reflected_today') else '남아있음')}</span>"
        f"<h2>{esc(item.get('title', ''))}</h2>"
        f"<p>{esc(item.get('evidence', ''))}</p>"
        f"<small>{esc(item.get('next_action', ''))}</small>"
        "</article>"
        for item in payload.get("carried_forward", [])
    ) or "<p>이월된 질문이나 작업이 아직 없습니다. 오늘 실행부터 기억이 쌓입니다.</p>"
    unresolved_cards = "".join(
        "<article class='card warn'>"
        f"<span>{esc(item.get('source', ''))}</span>"
        f"<h2>{esc(item.get('title', ''))}</h2>"
        f"<p>{esc(item.get('evidence', ''))}</p>"
        f"<small>{esc(item.get('next_action', ''))}</small>"
        "</article>"
        for item in payload.get("unresolved", [])
    ) or "<p>오늘 handoff에서 즉시 처리할 unresolved 항목은 없습니다.</p>"
    study_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(item.get('kind', 'study'))} · {esc(item.get('severity', 'normal'))}</span>"
        f"<h2>{esc(item.get('title', ''))}</h2>"
        f"<p>{esc(item.get('beginner_question', ''))}</p>"
        f"<p>{esc(item.get('why_it_matters', ''))}</p>"
        f"<small>닫는 기준: {esc(item.get('done_when', ''))}</small>"
        f"<code>{esc(item.get('copy_ready_command', ''))}</code>"
        f"<p><a href='{esc(_relative_href(Path(item.get('linked_surface', 'reports/product/handoff.html'))))}'>관련 화면 열기</a></p>"
        "</article>"
        for item in study.get("items", [])
    ) or "<p>오늘 공부로 닫을 handoff 항목은 없습니다.</p>"
    command_cards = "".join(
        "<article class='command'>"
        f"<span>{esc(command.get('label', 'local command'))}</span>"
        f"<code>{esc(command.get('command', ''))}</code>"
        f"<small>{esc(command.get('why', ''))}</small>"
        "</article>"
        for command in payload.get("copy_ready_commands", [])
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if path and label != "handoff"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Daily Handoff</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:860px; margin:0 auto; padding:16px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
.eyebrow,.card span,.command span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.card,.command {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin-top:12px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.card,.command {{ background:white; padding:14px; min-width:0; }}
.warn {{ border-color:#d7b36a; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
@media (max-width:680px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.grid,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Handoff · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>어제가 오늘에 반영됐나</h1>
<p>전날 남은 질문, 피드백, task, council/memory 경고가 오늘 실행에 실제로 반영됐는지 확인하는 로컬 proof입니다.</p>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<h2>{esc(payload.get('status', 'review'))}</h2>
<p>canonical run: {esc(canonical.get('run_id', 'missing'))} · {esc(canonical.get('local_day', ''))}</p>
<div class="metrics">
<article class="metric"><span>Carried</span><strong>{esc(summary.get('carried_item_count', 0))}</strong></article>
<article class="metric"><span>Reflected</span><strong>{esc(summary.get('reflected_today_count', 0))}</strong></article>
<article class="metric"><span>Unresolved</span><strong>{esc(summary.get('unresolved_count', 0))}</strong></article>
<article class="metric"><span>Study</span><strong>{esc(summary.get('study_closure_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>오늘 공부로 닫을 항목</h2>
<p>{esc(study.get('operator_rule', '남은 질문과 주의 항목을 읽고 짧은 local feedback으로 내일 루프에 넘깁니다.'))}</p>
<div class="grid">{study_cards}</div>
</section>
<section class="section">
<h2>이월 항목 전체</h2>
<div class="grid">{carried_cards}</div>
</section>
<section class="section">
<h2>아직 남은 것</h2>
<div class="grid">{unresolved_cards}</div>
</section>
<section class="section">
<h2>다음 로컬 응답</h2>
<div class="grid">{command_cards}</div>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 handoff는 기존 로컬 artifact만 읽습니다. task 실행, live network, 알림 발송, host scheduler write, credential 사용, 계좌 접근, 주문 실행은 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def build_drift_review(
    *,
    run_trace_path: str | Path = DEFAULT_RUN_TRACE_OUTPUT,
    pattern_radar_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_OUTPUT,
    readiness_path: str | Path = DEFAULT_DAILY_READINESS_OUTPUT,
    source_refresh_brief_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    daily_review_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(timezone.utc)
    trace = _load_optional_json(run_trace_path)
    pattern = _load_optional_json(pattern_radar_path)
    readiness = _load_optional_json(readiness_path)
    source_refresh = _load_optional_json(source_refresh_brief_path)
    ledger = _load_optional_json(task_ledger_path)
    review = _load_optional_json(daily_review_path)
    signals = _drift_review_signals(
        trace=trace,
        pattern=pattern,
        readiness=readiness,
        source_refresh=source_refresh,
        ledger=ledger,
        review=review,
    )
    decision = _drift_review_decision(signals=signals)
    payload = {
        "schema_version": DRIFT_REVIEW_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": decision["status"],
        "run_id": trace.get("run_id", "local-daily-loop"),
        "decision": decision,
        "signals": signals,
        "operator_next_steps": _drift_review_next_steps(decision=decision, signals=signals),
        "input_artifacts": {
            "run_trace": Path(run_trace_path).as_posix(),
            "pattern_radar": Path(pattern_radar_path).as_posix(),
            "readiness": Path(readiness_path).as_posix(),
            "source_refresh_brief": Path(source_refresh_brief_path).as_posix(),
            "task_ledger": Path(task_ledger_path).as_posix(),
            "daily_review": Path(daily_review_path).as_posix(),
        },
        "phone_links": {
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
            "trace": DEFAULT_RUN_TRACE_SURFACE.as_posix(),
            "drift_review": DEFAULT_DRIFT_REVIEW_SURFACE.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
            "review_effect": DEFAULT_REVIEW_EFFECT_SURFACE.as_posix(),
            "pattern_radar": DEFAULT_AGENT_PATTERN_RADAR_SURFACE.as_posix(),
            "source_refresh": DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix(),
            "tasks": DEFAULT_ANALYST_TASK_QUEUE_OUTPUT.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "drift_review_reads_existing_artifacts_only",
            "does_not_execute_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_live_trading",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_drift_review(
    *,
    artifact_output_path: str | Path = DEFAULT_DRIFT_REVIEW_OUTPUT,
    surface_output_path: str | Path = DEFAULT_DRIFT_REVIEW_SURFACE,
    **paths: Any,
) -> Path:
    payload = build_drift_review(**paths)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_drift_review(payload), encoding="utf-8")
    return target


def validate_drift_review_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DRIFT_REVIEW_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"aligned", "inspect", "approval_required", "blocked"}:
        errors.append(f"invalid status {payload.get('status')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if not payload.get("signals"):
        errors.append("signals must not be empty")
    decision = payload.get("decision", {})
    if not decision.get("recommended_branch"):
        errors.append("decision.recommended_branch must not be empty")
    if not payload.get("operator_next_steps"):
        errors.append("operator_next_steps must not be empty")
    boundary = payload.get("safety_boundary", [])
    if "drift_review_reads_existing_artifacts_only" not in boundary:
        errors.append("safety_boundary must include drift_review_reads_existing_artifacts_only")
    if "does_not_execute_live_network" not in boundary:
        errors.append("safety_boundary must include does_not_execute_live_network")
    return errors


def validate_drift_review_file(path: str | Path) -> list[str]:
    return validate_drift_review_payload(load_json(path))


def render_drift_review(payload: dict[str, Any]) -> str:
    decision = payload.get("decision", {})
    signal_cards = "".join(
        "<article class='mini'>"
        f"<strong>{esc(signal.get('name', ''))}</strong>"
        f"<p>{esc(signal.get('value', ''))}</p>"
        f"<small>{esc(signal.get('interpretation', ''))}</small>"
        "</article>"
        for signal in payload.get("signals", [])
    )
    step_items = "".join(f"<li>{esc(step)}</li>" for step in payload.get("operator_next_steps", []))
    inputs = "".join(
        "<tr>"
        f"<td>{esc(name)}</td>"
        f"<td>{esc(path)}</td>"
        "</tr>"
        for name, path in payload.get("input_artifacts", {}).items()
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if path and label != "drift_review"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Drift Review</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; --bad:#9f2d2d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:840px; margin:0 auto; padding:16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,li,small,td {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.mini {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; min-width:0; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
@media (max-width:680px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .grid,.links {{ grid-template-columns:1fr; }} table {{ font-size:13px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Drift Review · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘 방향 이탈 점검</h1>
<p>trace와 운영 artifact를 읽어 현재 루프가 계속 진행 가능한지, 점검이 필요한지, 별도 승인 gate가 필요한지 판단합니다.</p>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<strong class="status">{esc(payload.get('status', 'inspect'))}</strong>
<h2>{esc(decision.get('recommended_branch', 'inspect'))}</h2>
<p>{esc(decision.get('rationale', ''))}</p>
</section>
<section class="section">
<h2>판단 신호</h2>
<div class="grid">{signal_cards}</div>
</section>
<section class="section">
<h2>다음 행동</h2>
<ul>{step_items}</ul>
</section>
<section class="section">
<h2>입력 artifact</h2>
<table><thead><tr><th>Input</th><th>Path</th></tr></thead><tbody>{inputs}</tbody></table>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 review는 기존 로컬 artifact만 읽습니다. live network, 알림 발송, host scheduler write, credential 사용, 계좌 접근, 주문 실행은 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_run_trace(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    influence_cards = "".join(
        "<article class='mini'>"
        f"<strong>{esc(item.get('label', ''))}</strong>"
        f"<p>{esc(item.get('value', ''))}</p>"
        f"<small>{esc(item.get('source', ''))}</small>"
        "</article>"
        for item in payload.get("what_shaped_today", [])
    )
    step_rows = "".join(
        "<tr>"
        f"<td><strong>{esc(step.get('name', ''))}</strong><span>{esc(step.get('stage', ''))}</span></td>"
        f"<td><span class='pill {esc(_readiness_css(step.get('freshness_status', 'missing')))}'>{esc(step.get('freshness_status', ''))}</span></td>"
        f"<td>{esc(step.get('schema_version', ''))}</td>"
        f"<td>{esc(step.get('influence', ''))}</td>"
        "</tr>"
        for step in payload.get("trace_steps", [])
    )
    weak_items = "".join(f"<li>{esc(item)}</li>" for item in payload.get("weak_spots", [])) or "<li>오늘 trace에서 즉시 막힌 항목은 없습니다.</li>"
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if path and label != "trace"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Run Trace</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; --bad:#9f2d2d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:860px; margin:0 auto; padding:16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,li,small,td span {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics,.grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric,.mini {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; min-width:0; }}
.metric strong {{ display:block; font-size:24px; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
td strong,td span {{ display:block; }}
.pill {{ display:inline-block; border-radius:999px; padding:2px 8px; font-size:12px; font-weight:900; }}
.fresh {{ background:#e7f5ee; color:var(--green); }}
.stale {{ background:#fff3d8; color:var(--warn); }}
.missing {{ background:#ffe2e2; color:var(--bad); }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
@media (max-width:680px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.grid,.links {{ grid-template-columns:1fr; }} table {{ font-size:13px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Trace · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘 실행 근거 추적</h1>
<p>오늘 브리프, 메모리, task, 관제 화면이 어떤 로컬 단계와 artifact에서 만들어졌는지 확인하는 작은 proof입니다.</p>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<strong class="status">{esc(payload.get('status', 'review'))}</strong>
<div class="metrics">
<article class="metric"><span>Steps</span><strong>{esc(summary.get('step_count', 0))}</strong></article>
<article class="metric"><span>Fresh</span><strong>{esc(summary.get('fresh_count', 0))}</strong></article>
<article class="metric"><span>Missing</span><strong>{esc(summary.get('missing_required_count', 0))}</strong></article>
<article class="metric"><span>External</span><strong>{esc(summary.get('external_effect_flag_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>오늘 결과에 영향을 준 것</h2>
<div class="grid">{influence_cards}</div>
</section>
<section class="section">
<h2>단계별 trace</h2>
<table><thead><tr><th>Step</th><th>Freshness</th><th>Schema</th><th>Influence</th></tr></thead><tbody>{step_rows}</tbody></table>
</section>
<section class="section">
<h2>약한 부분</h2>
<ul>{weak_items}</ul>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 trace는 기존 로컬 artifact만 읽습니다. live network, 알림 발송, host scheduler write, credential 사용, 계좌 접근, 주문 실행은 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def build_source_refresh_brief(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    refresh_apply_path: str | Path = DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scout = _load_optional_json(scout_path)
    evidence = _load_optional_json(evidence_path)
    refresh_plan = _load_optional_json(refresh_plan_path)
    refresh_apply = _load_optional_json(refresh_apply_path)
    live_gate = _load_optional_json(refresh_live_gate_path)
    live_run = _load_optional_json(refresh_live_run_path)
    preflight = _load_optional_json(refresh_live_preflight_path)
    actions = _source_refresh_brief_actions(refresh_plan=refresh_plan, refresh_apply=refresh_apply, live_gate=live_gate)
    blocked_live = [action for action in actions if action.get("approval_required") == "live_network_refresh"]
    ready_local = [action for action in actions if action.get("decision") == "ready"]
    weak_evidence = _source_refresh_weak_evidence(evidence=evidence, scout=scout)
    freshness_scorecard = _source_refresh_freshness_scorecard(evidence=evidence)
    status = _source_refresh_brief_status(
        actions=actions,
        live_gate=live_gate,
        live_run=live_run,
        preflight=preflight,
    )
    payload = {
        "schema_version": SOURCE_REFRESH_BRIEF_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "status": status,
        "recommended_topic": scout.get("recommended_topic", {}),
        "summary": {
            "action_count": len(actions),
            "ready_local_count": len(ready_local),
            "blocked_live_count": len(blocked_live),
            "weak_evidence_count": len(weak_evidence),
            "gate_status": live_gate.get("status", "missing"),
            "approval_status": live_run.get("approval_status", "missing"),
            "live_run_status": live_run.get("execution", {}).get("status", "missing"),
            "preflight_status": preflight.get("status", "missing"),
            "source_count": len(freshness_scorecard),
            "fresh_source_count": sum(1 for row in freshness_scorecard if row["trust_state"] == "fresh_enough"),
            "weak_source_count": sum(1 for row in freshness_scorecard if row["trust_state"] != "fresh_enough"),
        },
        "source_freshness": freshness_scorecard,
        "weak_evidence": weak_evidence,
        "actions": actions,
        "operator_decision": _source_refresh_operator_decision(live_gate=live_gate, live_run=live_run, preflight=preflight),
        "next_action": _source_refresh_next_action(status=status, live_gate=live_gate, live_run=live_run, preflight=preflight),
        "phone_links": {
            "source_refresh": DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix(),
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "agenda": DEFAULT_DAILY_BRIEF_AGENDA_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
        },
        "inputs": {
            "scout": Path(scout_path).as_posix(),
            "evidence": Path(evidence_path).as_posix(),
            "refresh_plan": Path(refresh_plan_path).as_posix(),
            "refresh_apply": Path(refresh_apply_path).as_posix(),
            "refresh_live_gate": Path(refresh_live_gate_path).as_posix(),
            "refresh_live_run": Path(refresh_live_run_path).as_posix(),
            "refresh_live_preflight": Path(refresh_live_preflight_path).as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "no_paid_api",
            "no_credentials",
            "no_account_access",
            "no_order_execution",
            "live_refresh_requires_separate_approval_and_confirmation",
        ],
    }
    return payload


def write_source_refresh_brief(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    refresh_apply_path: str | Path = DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT,
    surface_output_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE,
) -> Path:
    payload = build_source_refresh_brief(
        scout_path=scout_path,
        evidence_path=evidence_path,
        refresh_plan_path=refresh_plan_path,
        refresh_apply_path=refresh_apply_path,
        refresh_live_gate_path=refresh_live_gate_path,
        refresh_live_run_path=refresh_live_run_path,
        refresh_live_preflight_path=refresh_live_preflight_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_source_refresh_brief(payload), encoding="utf-8")
    return target


def validate_source_refresh_brief_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SOURCE_REFRESH_BRIEF_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"no_refresh_needed", "local_ready", "approval_required", "preflight_required", "ready_to_execute", "executed", "blocked"}:
        errors.append("status must be a recognized source refresh brief status")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("next_action"):
        errors.append("next_action must not be empty")
    if not payload.get("phone_links", {}).get("source_refresh"):
        errors.append("phone_links.source_refresh must not be empty")
    if not payload.get("source_freshness"):
        errors.append("source_freshness must not be empty")
    for index, row in enumerate(payload.get("source_freshness", [])):
        for field in ["source_name", "freshness_status", "relevance_label", "trust_state", "operator_rule"]:
            if field not in row:
                errors.append(f"source_freshness[{index}] missing {field}")
        if row.get("trust_state") not in {"fresh_enough", "sample_or_fallback", "weak_or_unknown"}:
            errors.append(f"source_freshness[{index}] invalid trust_state")
    if "does_not_fetch_live_network" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_fetch_live_network")
    for index, action in enumerate(payload.get("actions", [])):
        for field in ["source_name", "adapter_id", "decision", "status", "approval_required", "reason"]:
            if field not in action:
                errors.append(f"actions[{index}] missing {field}")
        command = action.get("command", "")
        if any(fragment in command for fragment in ["--send", "--confirm-host-write", "launchctl", "tailscale serve --bg"]):
            errors.append(f"actions[{index}] command crosses non-refresh external-effect boundary")
    decision = payload.get("operator_decision", {})
    if decision.get("approval_required") and not decision.get("copy_ready_response"):
        errors.append("operator_decision with approval_required must include copy_ready_response")
    return errors


def validate_source_refresh_brief_file(path: str | Path) -> list[str]:
    return validate_source_refresh_brief_payload(load_json(path))


def build_source_freshness_intake(
    *,
    source_refresh_brief_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(timezone.utc)
    brief = _load_optional_json(source_refresh_brief_path)
    live_gate = _load_optional_json(refresh_live_gate_path)
    live_run = _load_optional_json(refresh_live_run_path)
    preflight = _load_optional_json(refresh_live_preflight_path)
    source_freshness = brief.get("source_freshness", [])
    actions = brief.get("actions", [])
    blocked_live = [
        action for action in actions
        if action.get("approval_required") == "live_network_refresh"
        or action.get("decision") == "requires_approval"
        or action.get("status") in {"blocked_live_network", "approval_required"}
    ]
    stale_sources = [
        source for source in source_freshness
        if source.get("trust_state") != "fresh_enough"
    ]
    decision = brief.get("operator_decision", {})
    gate_decision = (live_gate.get("decisions") or [{}])[0]
    copy_ready_response = (
        decision.get("copy_ready_response")
        or gate_decision.get("copy_ready_response")
        or "approve live_network_refresh live_network_refresh"
    )
    status = "ready_for_operator_review"
    if not source_freshness:
        status = "blocked_missing_source_refresh_brief"
    elif not blocked_live and not stale_sources:
        status = "no_intake_needed"
    elif decision.get("approval_required") or live_gate.get("status") == "approval_required":
        status = "approval_packet_ready"
    payload = {
        "schema_version": SOURCE_FRESHNESS_INTAKE_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": status,
        "summary": {
            "source_count": len(source_freshness),
            "fresh_source_count": sum(1 for source in source_freshness if source.get("trust_state") == "fresh_enough"),
            "stale_or_sample_source_count": len(stale_sources),
            "blocked_live_candidate_count": len(blocked_live),
            "approval_status": live_run.get("approval_status", "missing"),
            "preflight_status": preflight.get("status", "missing"),
        },
        "operator_question": "오늘 brief가 sample/cache 근거에 기대고 있으므로, live 공개 소스 refresh를 승인할지 판단하세요.",
        "source_freshness": source_freshness,
        "blocked_live_candidates": [
            {
                "source_name": action.get("source_name", ""),
                "adapter_id": action.get("adapter_id", ""),
                "why_blocked": action.get("reason", ""),
                "approval_required": action.get("approval_required", "live_network_refresh"),
                "expected_artifact": action.get("expected_artifact", ""),
                "candidate_command": action.get("command", ""),
            }
            for action in blocked_live
        ],
        "approval_packet": {
            "decision_id": decision.get("id", gate_decision.get("id", "live_network_refresh")),
            "approval_scope": decision.get("approval_scope", gate_decision.get("approval_scope", "live_network_refresh")),
            "risk_level": decision.get("risk_level", gate_decision.get("risk_level", "medium")),
            "reversibility": gate_decision.get("reversibility", "cache_artifact_can_be_deleted"),
            "copy_ready_response": copy_ready_response,
            "apply_command": f'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance source-refresh-response "{copy_ready_response}" --intend-execute --confirm-live-network',
            "agent_will_run": gate_decision.get("agent_will_run", []),
            "agent_will_not_run": gate_decision.get(
                "agent_will_not_run",
                ["paid API calls", "credentialed sources", "notification send", "host-level writes", "orders or brokerage actions"],
            ),
        },
        "stale_context_guard": {
            "guard": decision.get("stale_context_guard", gate_decision.get("stale_context_guard", "Regenerate intake if scout, source plan, or source-refresh brief changed.")),
            "input_artifacts": {
                "source_refresh_brief": Path(source_refresh_brief_path).as_posix(),
                "source_refresh_live_gate": Path(refresh_live_gate_path).as_posix(),
                "source_refresh_live_run": Path(refresh_live_run_path).as_posix(),
                "source_refresh_live_preflight": Path(refresh_live_preflight_path).as_posix(),
            },
        },
        "expected_after_approval": [
            {
                "artifact": DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix(),
                "meaning": "승인 응답이 정확한 scope와 decision id를 통과했는지 기록합니다.",
            },
            {
                "artifact": DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix(),
                "meaning": "실행 의도와 live-network 확인이 모두 있는지 네트워크 없이 점검합니다.",
            },
            {
                "artifact": DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT.as_posix(),
                "meaning": "승인/사전점검 상태를 다시 읽어 source refresh 판단을 갱신합니다.",
            },
        ],
        "next_action": _source_freshness_intake_next_action(status=status, response=copy_ready_response),
        "phone_links": {
            "source_freshness_intake": DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE.as_posix(),
            "source_refresh_execution": DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE.as_posix(),
            "source_refresh": DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix(),
            "daily_home": DEFAULT_DAILY_HOME_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
            "trace": DEFAULT_RUN_TRACE_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_paid_api",
            "no_account_access",
            "no_order_execution",
            "approval_response_is_not_execution",
        ],
    }
    return payload


def write_source_freshness_intake(
    *,
    source_refresh_brief_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT,
    surface_output_path: str | Path = DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE,
) -> Path:
    payload = build_source_freshness_intake(
        source_refresh_brief_path=source_refresh_brief_path,
        refresh_live_gate_path=refresh_live_gate_path,
        refresh_live_run_path=refresh_live_run_path,
        refresh_live_preflight_path=refresh_live_preflight_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_source_freshness_intake(payload), encoding="utf-8")
    return target


def validate_source_freshness_intake_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SOURCE_FRESHNESS_INTAKE_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"approval_packet_ready", "ready_for_operator_review", "no_intake_needed", "blocked_missing_source_refresh_brief"}:
        errors.append("status must be a recognized source freshness intake status")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("operator_question"):
        errors.append("operator_question must not be empty")
    if not payload.get("source_freshness"):
        errors.append("source_freshness must not be empty")
    packet = payload.get("approval_packet", {})
    for field in ["decision_id", "approval_scope", "risk_level", "copy_ready_response", "apply_command", "agent_will_not_run"]:
        if not packet.get(field):
            errors.append(f"approval_packet.{field} must not be empty")
    if packet.get("approval_scope") != "live_network_refresh" and payload.get("status") == "approval_packet_ready":
        errors.append("approval_packet.approval_scope must remain live_network_refresh for approval packets")
    if "--confirm-live-network" not in packet.get("apply_command", ""):
        errors.append("approval_packet.apply_command must show explicit live-network confirmation")
    if not payload.get("stale_context_guard", {}).get("guard"):
        errors.append("stale_context_guard.guard must not be empty")
    if not payload.get("expected_after_approval"):
        errors.append("expected_after_approval must not be empty")
    if not payload.get("next_action"):
        errors.append("next_action must not be empty")
    if not payload.get("phone_links", {}).get("source_freshness_intake"):
        errors.append("phone_links.source_freshness_intake must not be empty")
    boundary = payload.get("safety_boundary", [])
    for required in ["reads_local_artifacts_only", "does_not_fetch_live_network", "approval_response_is_not_execution"]:
        if required not in boundary:
            errors.append(f"safety_boundary must include {required}")
    forbidden = [" --send", "--confirm-host-write", "launchctl bootstrap", "tailscale serve --bg"]
    commands = [packet.get("apply_command", "")]
    commands.extend(item.get("candidate_command", "") for item in payload.get("blocked_live_candidates", []))
    for index, command in enumerate(commands):
        if any(fragment in command for fragment in forbidden):
            errors.append(f"command[{index}] crosses non-source-refresh external-effect boundary")
    return errors


def validate_source_freshness_intake_file(path: str | Path) -> list[str]:
    return validate_source_freshness_intake_payload(load_json(path))


def build_source_refresh_execution_brief(
    *,
    source_refresh_brief_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(timezone.utc)
    brief = _load_optional_json(source_refresh_brief_path)
    gate = _load_optional_json(refresh_live_gate_path)
    live_run = _load_optional_json(refresh_live_run_path)
    preflight = _load_optional_json(refresh_live_preflight_path)
    execution = live_run.get("execution", {}) if live_run.get("schema_version") == "source_refresh_live_run.v1" else {}
    approval_status = live_run.get("approval_status", "missing")
    live_run_status = execution.get("status", "missing")
    preflight_status = preflight.get("status", "missing")
    blockers = list(preflight.get("blockers", [])) + list(execution.get("blockers", []))
    warnings = list(preflight.get("warnings", []))
    proposed_commands = list(execution.get("proposed_commands", []))
    source_ids = list(execution.get("source_ids", []))
    status = "blocked"
    if gate.get("status") == "no_live_refresh_requested" or approval_status == "not_required":
        status = "not_required"
    elif live_run_status == "executed":
        status = "executed"
    elif preflight_status == "passed" and approval_status == "approved" and live_run_status == "ready_to_execute":
        status = "ready_for_final_confirmation"
    elif approval_status == "approved":
        status = "preflight_required"
    elif gate.get("status") == "approval_required":
        status = "approval_required"
    run_command = "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance source-refresh-execution"
    if status == "ready_for_final_confirmation":
        run_command = (
            "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker source-refresh-live-run "
            f"--live-gate {Path(refresh_live_gate_path).as_posix()} "
            f"--response {shlex.quote(str(live_run.get('response') or (gate.get('decisions') or [{}])[0].get('copy_ready_response', '')))} "
            f"--output {Path(refresh_live_run_path).as_posix()} "
            f"--evidence-output {live_run.get('inputs', {}).get('evidence_output_path', 'reports/evidence/live-evidence-catalog.json')} "
            "--execute --confirm-live-network"
        )
    operator_must_confirm = [
        "이 명령은 실제 live network를 호출합니다.",
        "무료/no-key 공개 source만 대상이어야 합니다.",
        "실행 결과는 research evidence artifact일 뿐 투자 추천이나 주문이 아닙니다.",
    ]
    if status != "ready_for_final_confirmation":
        operator_must_confirm = [
            "이 명령은 기존 로컬 artifact만 읽고 확인 화면을 다시 생성합니다.",
            "approval/preflight가 통과하기 전까지 live network 실행 명령을 노출하지 않습니다.",
            "실행 결과는 research evidence artifact일 뿐 투자 추천이나 주문이 아닙니다.",
        ]
    stop_conditions = [
        "approval_status가 approved가 아니면 실행하지 않습니다.",
        "preflight status가 passed가 아니면 실행하지 않습니다.",
        "proposed command 안에 알림, host write, credential, account, order 관련 fragment가 보이면 실행하지 않습니다.",
        "source plan, scout, evidence가 바뀌었으면 approval/preflight를 다시 생성합니다.",
    ]
    next_local_steps = [
        "실행하지 않을 때: source-refresh-intake와 handoff-study-resolution을 읽고 어떤 근거가 약한지 공부용 응답으로 남깁니다.",
        "승인만 기록할 때: appliance source-refresh-response 명령으로 live-run/preflight proof를 갱신합니다.",
        "preflight가 passed일 때만: 별도 최종 확인 후 source-refresh-live-run --execute --confirm-live-network를 사용합니다.",
        "실행 후: live evidence validator를 통과시키고 appliance run --dry-run으로 daily brief에 흡수합니다.",
    ]
    payload = {
        "schema_version": SOURCE_REFRESH_EXECUTION_BRIEF_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": status,
        "summary": {
            "approval_status": approval_status,
            "live_run_status": live_run_status,
            "preflight_status": preflight_status,
            "source_count": len(source_ids),
            "proposed_command_count": len(proposed_commands),
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
            "external_effect_performed": live_run.get("external_effect_performed", False),
        },
        "execution_readiness": {
            "approval_status": approval_status,
            "live_run_status": live_run_status,
            "preflight_status": preflight_status,
            "requested_execution": preflight.get("requested_execution", {}),
            "source_ids": source_ids,
            "proposed_commands": proposed_commands,
            "blockers": blockers,
            "warnings": warnings,
            "evidence_output_path": live_run.get("inputs", {}).get("evidence_output_path", ""),
        },
        "final_confirmation": {
            "required": status == "ready_for_final_confirmation",
            "run_command_preview": run_command,
            "operator_must_confirm": operator_must_confirm,
            "agent_will_not_do": [
                "paid API",
                "credentialed source",
                "notification send",
                "host scheduler write",
                "account access",
                "order execution",
                "personalized/discretionary advice",
            ],
        },
        "stop_conditions": stop_conditions,
        "rollback_plan": [
            "생성된 live evidence artifact를 삭제하거나 archive에서 제외하면 로컬 상태를 되돌릴 수 있습니다.",
            "실행 후 daily brief가 약해지면 source freshness intake와 run trace를 비교해 해당 source를 보류합니다.",
            "네트워크 실패는 실패 artifact로 남기고 같은 run에서 재시도하지 않습니다.",
        ],
        "next_local_steps": next_local_steps,
        "input_artifacts": {
            "source_refresh_brief": Path(source_refresh_brief_path).as_posix(),
            "source_refresh_live_gate": Path(refresh_live_gate_path).as_posix(),
            "source_refresh_live_run": Path(refresh_live_run_path).as_posix(),
            "source_refresh_live_preflight": Path(refresh_live_preflight_path).as_posix(),
        },
        "phone_links": {
            "source_refresh_execution": DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE.as_posix(),
            "source_freshness_intake": DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE.as_posix(),
            "source_refresh": DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix(),
            "daily_home": DEFAULT_DAILY_HOME_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
            "trace": DEFAULT_RUN_TRACE_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_paid_api",
            "no_account_access",
            "no_order_execution",
            "execution_requires_separate_final_confirmation",
        ],
    }
    return payload


def write_source_refresh_execution_brief(
    *,
    artifact_output_path: str | Path = DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT,
    surface_output_path: str | Path = DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE,
    **paths: Any,
) -> Path:
    payload = build_source_refresh_execution_brief(**paths)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_source_refresh_execution_brief(payload), encoding="utf-8")
    return target


def validate_source_refresh_execution_brief_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SOURCE_REFRESH_EXECUTION_BRIEF_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"not_required", "approval_required", "preflight_required", "ready_for_final_confirmation", "executed", "blocked"}:
        errors.append("status must be a recognized source refresh execution status")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    summary = payload.get("summary", {})
    for field in ["approval_status", "live_run_status", "preflight_status", "source_count", "proposed_command_count", "blocker_count", "warning_count", "external_effect_performed"]:
        if field not in summary:
            errors.append(f"summary missing {field}")
    readiness = payload.get("execution_readiness", {})
    for field in ["approval_status", "live_run_status", "preflight_status", "source_ids", "proposed_commands", "blockers", "warnings", "evidence_output_path"]:
        if field not in readiness:
            errors.append(f"execution_readiness missing {field}")
    final = payload.get("final_confirmation", {})
    for field in ["required", "run_command_preview", "operator_must_confirm", "agent_will_not_do"]:
        if field not in final:
            errors.append(f"final_confirmation missing {field}")
    if payload.get("status") == "ready_for_final_confirmation" and final.get("required") is not True:
        errors.append("ready_for_final_confirmation requires final_confirmation.required true")
    if not payload.get("stop_conditions"):
        errors.append("stop_conditions must not be empty")
    if not payload.get("rollback_plan"):
        errors.append("rollback_plan must not be empty")
    if not payload.get("next_local_steps"):
        errors.append("next_local_steps must not be empty")
    for field in ["source_refresh_execution", "source_freshness_intake", "source_refresh", "daily_home", "readiness", "trace"]:
        if not payload.get("phone_links", {}).get(field):
            errors.append(f"phone_links.{field} must not be empty")
    forbidden = [" --send", "--confirm-host-write", "launchctl bootstrap", "tailscale serve --bg"]
    commands = [final.get("run_command_preview", "")]
    commands.extend(readiness.get("proposed_commands", []))
    for index, command in enumerate(commands):
        if any(fragment in command for fragment in forbidden):
            errors.append(f"command[{index}] crosses non-source-refresh external-effect boundary")
    for required in ["reads_local_artifacts_only", "does_not_fetch_live_network", "execution_requires_separate_final_confirmation"]:
        if required not in payload.get("safety_boundary", []):
            errors.append(f"safety_boundary must include {required}")
    return errors


def validate_source_refresh_execution_brief_file(path: str | Path) -> list[str]:
    return validate_source_refresh_execution_brief_payload(load_json(path))


def render_source_refresh_execution_brief(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    readiness = payload.get("execution_readiness", {})
    final = payload.get("final_confirmation", {})
    command_heading = "최종 실행 명령 preview" if final.get("required") else "다음 로컬 확인 명령"
    command_help = (
        "아래 명령은 별도 최종 확인이 있을 때만 사람이 명시적으로 실행합니다."
        if final.get("required")
        else "아직 live 실행 조건이 충족되지 않았습니다. 아래 명령은 이 확인 화면을 다시 생성하는 로컬 명령입니다."
    )
    status_label = {
        "not_required": "오늘 실행 필요 없음",
        "approval_required": "승인 먼저 필요",
        "preflight_required": "사전점검 필요",
        "ready_for_final_confirmation": "실행 전 최종 확인",
        "executed": "실행 증거 있음",
        "blocked": "차단됨",
    }.get(payload.get("status", ""), payload.get("status", "review"))
    blocker_items = "".join(f"<li>{esc(item)}</li>" for item in readiness.get("blockers", [])) or "<li>현재 기록된 blocker는 없습니다.</li>"
    warning_items = "".join(f"<li>{esc(item)}</li>" for item in readiness.get("warnings", [])) or "<li>현재 기록된 warning은 없습니다.</li>"
    stop_items = "".join(f"<li>{esc(item)}</li>" for item in payload.get("stop_conditions", []))
    rollback_items = "".join(f"<li>{esc(item)}</li>" for item in payload.get("rollback_plan", []))
    next_items = "".join(f"<li>{esc(item)}</li>" for item in payload.get("next_local_steps", []))
    confirm_items = "".join(f"<li>{esc(item)}</li>" for item in final.get("operator_must_confirm", []))
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "source_refresh_execution" and path
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Source Refresh Execution</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
html,body {{ max-width:100%; overflow-x:hidden; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:430px; margin:0; padding:14px; }}
a {{ color:var(--blue); font-weight:900; text-decoration:none; }}
.eyebrow,.metric span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:31px; line-height:1.12; overflow-wrap:anywhere; }}
h2 {{ margin:0 0 10px; font-size:19px; }}
p,li,small {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.metric {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:15px; margin:12px 0; }}
.status {{ display:block; margin:10px 0; font-size:24px; line-height:1.15; }}
.metrics {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.metric {{ padding:12px; background:white; min-width:0; }}
.metric strong {{ display:block; font-size:24px; overflow-wrap:anywhere; }}
code {{ display:block; white-space:pre-wrap; word-break:break-word; border:1px solid var(--line); border-radius:8px; background:#f1f5f7; padding:10px; color:var(--ink); font-size:12px; }}
.links {{ display:grid; grid-template-columns:minmax(0,1fr); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:11px; }}
.boundary {{ border-left:4px solid var(--green); }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Source Refresh Execution · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>실행 전 최종 확인</h1>
<p>이 화면은 live source refresh를 실행하지 않습니다. 승인, preflight, stop 조건, 실행 후 흡수 경로를 한 번에 확인합니다.</p>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<strong class="status">{esc(status_label)}</strong>
<div class="metrics">
<article class="metric"><span>Approval</span><strong>{esc(summary.get('approval_status', 'missing'))}</strong></article>
<article class="metric"><span>Preflight</span><strong>{esc(summary.get('preflight_status', 'missing'))}</strong></article>
<article class="metric"><span>Sources</span><strong>{esc(summary.get('source_count', 0))}</strong></article>
<article class="metric"><span>Blockers</span><strong>{esc(summary.get('blocker_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>{esc(command_heading)}</h2>
<p>{esc(command_help)}</p>
<code>{esc(final.get('run_command_preview', ''))}</code>
<ul>{confirm_items}</ul>
</section>
<section class="section">
<h2>현재 blocker</h2>
<ul>{blocker_items}</ul>
<h2>Warning</h2>
<ul>{warning_items}</ul>
</section>
<section class="section">
<h2>멈춤 조건</h2>
<ul>{stop_items}</ul>
</section>
<section class="section">
<h2>Rollback / 재시도 원칙</h2>
<ul>{rollback_items}</ul>
</section>
<section class="section">
<h2>다음 로컬 단계</h2>
<ul>{next_items}</ul>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section boundary">
<h2>안전 경계</h2>
<p>이 화면은 기존 로컬 artifact만 읽습니다. live network, paid API, credential, 알림, host scheduler, 계좌 접근, 주문 실행은 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_source_freshness_intake(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    packet = payload.get("approval_packet", {})
    status_label = {
        "approval_packet_ready": "승인 검토 가능",
        "ready_for_operator_review": "사람 검토 필요",
        "no_intake_needed": "오늘 승인 항목 없음",
        "blocked_missing_source_refresh_brief": "source-refresh brief 먼저 필요",
    }.get(payload.get("status", ""), payload.get("status", "review"))
    source_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(source.get('trust_state', ''))} · {esc(source.get('freshness_status', ''))}</span>"
        f"<strong>{esc(source.get('source_name', 'source'))}</strong>"
        f"<p>{esc(source.get('operator_rule', ''))}</p>"
        f"<small>{esc(source.get('source_id', ''))} · relevance {esc(source.get('relevance_label', 'unscored'))}</small>"
        "</article>"
        for source in payload.get("source_freshness", [])
    ) or "<p>source freshness를 표시하려면 source-refresh brief를 먼저 생성하세요.</p>"
    blocked_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(item.get('approval_required', 'approval'))}</span>"
        f"<strong>{esc(item.get('source_name', 'source'))}</strong>"
        f"<p>{esc(item.get('why_blocked', ''))}</p>"
        f"<small>{esc(item.get('expected_artifact', ''))}</small>"
        "</article>"
        for item in payload.get("blocked_live_candidates", [])
    ) or "<p>승인이 필요한 live refresh 후보가 없습니다.</p>"
    expected_items = "".join(
        "<li>"
        f"<strong>{esc(item.get('artifact', ''))}</strong>: {esc(item.get('meaning', ''))}"
        "</li>"
        for item in payload.get("expected_after_approval", [])
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "source_freshness_intake" and path
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Source Freshness Intake</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
html,body {{ max-width:100%; overflow-x:hidden; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:430px; margin:0; padding:14px; }}
a {{ color:var(--blue); font-weight:900; text-decoration:none; }}
.eyebrow,.card span,.metric span {{ color:var(--green); font-size:12px; font-weight:900; }}
.card span {{ display:block; overflow-wrap:anywhere; }}
h1 {{ margin:8px 0 10px; font-size:31px; line-height:1.12; overflow-wrap:anywhere; }}
h2 {{ margin:0 0 10px; font-size:19px; }}
p,small,li {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.card,.metric,.decision {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:15px; margin:12px 0; }}
.status {{ display:block; margin:10px 0; font-size:24px; line-height:1.15; }}
.metrics {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.metric,.card,.decision {{ padding:12px; background:white; min-width:0; }}
.metric strong {{ display:block; font-size:24px; }}
.stack {{ display:grid; grid-template-columns:minmax(0,1fr); gap:9px; }}
code {{ display:block; white-space:pre-wrap; word-break:break-word; border:1px solid var(--line); border-radius:8px; background:#f1f5f7; padding:10px; color:var(--ink); font-size:13px; }}
.links {{ display:grid; grid-template-columns:minmax(0,1fr); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:11px; }}
.boundary {{ border-left:4px solid var(--green); }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Source Freshness Intake · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>승인 전 근거 신선도 확인</h1>
</header>
<section class="hero">
<span class="eyebrow">지금 판단</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('operator_question', ''))}</p>
<div class="metrics">
<article class="metric"><span>Sources</span><strong>{esc(summary.get('source_count', 0))}</strong></article>
<article class="metric"><span>Weak</span><strong>{esc(summary.get('stale_or_sample_source_count', 0))}</strong></article>
<article class="metric"><span>Blocked live</span><strong>{esc(summary.get('blocked_live_candidate_count', 0))}</strong></article>
<article class="metric"><span>Preflight</span><strong>{esc(summary.get('preflight_status', 'missing'))}</strong></article>
</div>
</section>
<section class="section">
<h2>Source freshness</h2>
<div class="stack">{source_cards}</div>
</section>
<section class="section">
<h2>승인 전 막힌 후보</h2>
<div class="stack">{blocked_cards}</div>
</section>
<section class="section decision">
<h2>복사 가능한 승인 응답</h2>
<p>이 응답은 승인 기록과 preflight proof를 만들 뿐, 이 intake 화면 자체는 live network를 실행하지 않습니다.</p>
<code>{esc(packet.get('copy_ready_response', ''))}</code>
<h2>적용 명령 preview</h2>
<code>{esc(packet.get('apply_command', ''))}</code>
<p>{esc(payload.get('stale_context_guard', {}).get('guard', ''))}</p>
</section>
<section class="section">
<h2>승인 후 생길 증거</h2>
<ul>{expected_items}</ul>
</section>
<section class="section">
<h2>다음 행동</h2>
<p>{esc(payload.get('next_action', ''))}</p>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section boundary">
<h2>안전 경계</h2>
<p>이 화면은 기존 로컬 artifact만 읽습니다. live network, paid API, credential, 알림, host scheduler, 계좌 접근, 주문 실행은 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_source_refresh_brief(payload: dict[str, Any]) -> str:
    status_label = {
        "no_refresh_needed": "새로고침 필요 낮음",
        "local_ready": "로컬 작업 먼저 가능",
        "approval_required": "승인 필요",
        "preflight_required": "사전점검 필요",
        "ready_to_execute": "실행 전 최종 확인",
        "executed": "실행 증거 있음",
        "blocked": "차단됨",
    }.get(payload.get("status", ""), payload.get("status", "unknown"))
    summary = payload.get("summary", {})
    topic = payload.get("recommended_topic", {})
    weak_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(item.get('kind', 'weak'))}</span>"
        f"<strong>{esc(item.get('title', ''))}</strong>"
        f"<p>{esc(item.get('why_it_matters', ''))}</p>"
        "</article>"
        for item in payload.get("weak_evidence", [])
    ) or "<p>오늘 기록된 약한 근거가 없습니다.</p>"
    action_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(action.get('decision', ''))} · {esc(action.get('approval_required', 'none'))}</span>"
        f"<strong>{esc(action.get('source_name', ''))}</strong>"
        f"<p>{esc(action.get('reason', ''))}</p>"
        f"<small>{esc(action.get('expected_artifact', ''))}</small>"
        "</article>"
        for action in payload.get("actions", [])
    ) or "<p>오늘 계획된 source refresh action이 없습니다.</p>"
    freshness_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(row.get('trust_state', ''))} · {esc(row.get('freshness_status', ''))}</span>"
        f"<strong>{esc(row.get('source_name', ''))}</strong>"
        f"<p>{esc(row.get('operator_rule', ''))}</p>"
        f"<small>relevance {esc(row.get('relevance_label', ''))} · items {esc(row.get('item_count', '0'))}</small>"
        "</article>"
        for row in payload.get("source_freshness", [])
    ) or "<p>표시할 source freshness가 없습니다.</p>"
    decision = payload.get("operator_decision", {})
    decision_card = (
        "<article class='decision'>"
        f"<span>{esc(decision.get('risk_level', 'medium'))}</span>"
        f"<strong>{esc(decision.get('title', 'live refresh decision'))}</strong>"
        f"<p>{esc(decision.get('why', ''))}</p>"
        f"<code>{esc(decision.get('copy_ready_response', ''))}</code>"
        f"<small>{esc(decision.get('stale_context_guard', ''))}</small>"
        "</article>"
        if decision.get("approval_required")
        else "<p>지금 승인해야 할 live source refresh 결정은 없습니다.</p>"
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "source_refresh"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Source Refresh</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
a {{ color:var(--blue); font-weight:900; text-decoration:none; }}
.eyebrow,.card span,.decision span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.card,.decision {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
.stack {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.card,.decision {{ background:white; padding:14px; min-width:0; }}
.card strong,.decision strong {{ display:block; margin:5px 0; }}
.card p,.card small,.decision p,.decision small {{ overflow-wrap:anywhere; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.stack,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Source Refresh · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘 근거 새로고침 판단</h1>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('next_action', ''))}</p>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Actions</span><strong>{esc(summary.get('action_count', 0))}</strong></article>
<article class="metric"><span>Local</span><strong>{esc(summary.get('ready_local_count', 0))}</strong></article>
<article class="metric"><span>Live</span><strong>{esc(summary.get('blocked_live_count', 0))}</strong></article>
<article class="metric"><span>Weak</span><strong>{esc(summary.get('weak_evidence_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>오늘 주제</h2>
<article class="card">
<span>{esc(topic.get('confidence', 'unknown'))}</span>
<strong>{esc(topic.get('name', '오늘 추천 주제 없음'))}</strong>
<p>{esc(topic.get('why', topic.get('why_today', '')))}</p>
</article>
</section>
<section class="section">
<h2>약한 근거</h2>
<div class="stack">{weak_cards}</div>
</section>
<section class="section">
<h2>Source freshness</h2>
<div class="stack">{freshness_cards}</div>
</section>
<section class="section">
<h2>Source actions</h2>
<div class="stack">{action_cards}</div>
</section>
<section class="section">
<h2>사람이 결정할 것</h2>
{decision_card}
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 로컬 artifact만 읽습니다. live network refresh, paid API, credential use, notification send, host scheduler write, 계좌 접근, 주문 실행은 별도 승인 없이 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_daily_readiness(payload: dict[str, Any]) -> str:
    status = payload.get("status", "review")
    summary = payload.get("summary", {})
    status_label = {
        "ready": "오늘 읽어도 됨",
        "review": "확인 필요",
        "stale": "다시 실행 권장",
        "blocked": "먼저 생성 필요",
    }.get(status, status)
    artifact_rows = "".join(
        "<tr>"
        f"<td><strong>{esc(item.get('name', ''))}</strong><span>{esc(item.get('kind', ''))}</span></td>"
        f"<td><span class='pill {esc(_readiness_css(item.get('freshness_status', 'missing')))}'>{esc(item.get('freshness_status', ''))}</span></td>"
        f"<td>{esc(item.get('age_hours', ''))}</td>"
        f"<td>{esc(item.get('path', ''))}</td>"
        "</tr>"
        for item in payload.get("artifacts", [])
    )
    actions = "".join(f"<li>{esc(action)}</li>" for action in payload.get("next_actions", []))
    links = "".join(
        f"<a href='{esc(path)}'>{esc(name)}</a>"
        for name, path in payload.get("phone_links", {}).items()
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Daily Readiness</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; --bad:#9f2d2d; }}
* {{ box-sizing:border-box; }}
html,body {{ max-width:100%; overflow-x:hidden; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,li,td span {{ color:var(--muted); }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
td strong,td span {{ display:block; }}
.pill {{ display:inline-block; border-radius:999px; padding:2px 8px; font-size:12px; font-weight:900; }}
.fresh {{ background:#e7f5ee; color:var(--green); }}
.stale {{ background:#fff3d8; color:var(--warn); }}
.missing {{ background:#ffe2e2; color:var(--bad); }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
code {{ display:block; padding:12px; border-radius:8px; background:#f1f5f9; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.links {{ grid-template-columns:1fr; }} table {{ font-size:13px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Daily Readiness · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘 브리프 준비 상태</h1>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<strong class="status">{esc(status_label)}</strong>
<p>전체 daily run을 다시 돌리기 전에도, 지금 폰에서 볼 산출물이 충분히 최신인지 확인합니다.</p>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>필수</span><strong>{esc(summary.get('required_count', 0))}</strong></article>
<article class="metric"><span>Fresh</span><strong>{esc(summary.get('fresh_required_count', 0))}</strong></article>
<article class="metric"><span>Stale</span><strong>{esc(summary.get('stale_required_count', 0))}</strong></article>
<article class="metric"><span>Missing</span><strong>{esc(summary.get('missing_required_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>다음 행동</h2>
<ul>{actions}</ul>
<code>{esc(payload.get('recommended_local_run', ''))}</code>
</section>
<section class="section">
<h2>폰 링크</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>Artifact freshness</h2>
<table><thead><tr><th>Artifact</th><th>Freshness</th><th>Age hours</th><th>Path</th></tr></thead><tbody>{artifact_rows}</tbody></table>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 로컬 파일만 읽습니다. live source refresh, 알림 전송, host scheduler 쓰기, 계좌 접근, 주문 실행은 별도 승인 없이 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_daily_brief_agenda(payload: dict[str, Any]) -> str:
    primary = payload.get("primary_topic", {})
    sequence_cards = "".join(
        "<article class='step'>"
        f"<span>{esc(step.get('minutes', ''))}분 · step {esc(step.get('step', ''))}</span>"
        f"<strong>{esc(step.get('title', ''))}</strong>"
        f"<p>{esc(step.get('operator_action', ''))}</p>"
        f"<small>멈춤 기준: {esc(step.get('stop_condition', ''))}</small>"
        "</article>"
        for step in payload.get("study_sequence", [])
    )
    topic_cards = "".join(
        "<article class='card'>"
        f"<span>#{esc(card.get('priority_rank', ''))} · {esc(card.get('action', 'monitor'))} · {esc(card.get('confidence', ''))}</span>"
        f"<strong>{esc(card.get('name', ''))}</strong>"
        f"<p>{esc(card.get('why_today', ''))}</p>"
        f"<small>근거 {esc(card.get('evidence_count', 0))}개 · source {esc(card.get('source_family_count', 0))}개 · vault {esc(card.get('vault_note_count', 0))}개</small>"
        "</article>"
        for card in payload.get("topic_cards", [])
    )
    source_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(row.get('freshness_status', 'unknown'))} · {esc(row.get('relevance_label', 'unscored'))}</span>"
        f"<strong>{esc(row.get('source_name', 'source'))}</strong>"
        f"<p>{esc(row.get('role', '오늘 주제 근거 확인'))}</p>"
        "</article>"
        for row in payload.get("source_fanout", [])
    )
    role_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(role.get('role', 'analyst'))}</span>"
        f"<strong>{esc(role.get('task', '오늘 근거 점검'))}</strong>"
        f"<p>{esc(role.get('success_condition', ''))}</p>"
        "</article>"
        for role in payload.get("role_brief", [])
    )
    weak_items = "".join(f"<li>{esc(item)}</li>" for item in payload.get("weak_points", [])) or "<li>오늘 기록된 약한 근거가 없습니다.</li>"
    questions = "".join(f"<article class='question'><p>{esc(question)}</p></article>" for question in payload.get("copy_ready_questions", []))
    response_cards = "".join(
        "<article class='question'>"
        f"<p><strong>{esc(response.get('intent', 'response'))}</strong></p>"
        f"<code>{esc(response.get('command', ''))}</code>"
        f"<small>{esc(response.get('effect', '다음 로컬 실행에 반영합니다.'))}</small>"
        "</article>"
        for response in payload.get("copy_ready_responses", [])
    ) or "<p>오늘 복사할 피드백 명령이 없습니다.</p>"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Daily Agenda</title>
<style>
:root {{ --bg:#f6f7f2; --ink:#18212b; --muted:#63707c; --line:#d9dfd5; --panel:#fffefa; --accent:#1f5f8b; --green:#1e6b52; --warn:#93651a; }}
* {{ box-sizing:border-box; }}
html,body {{ max-width:100%; overflow-x:hidden; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:430px; min-width:0; padding:14px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 12px; font-size:32px; line-height:1.1; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p {{ margin:0; color:var(--muted); }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:12px 0; }}
.hero strong {{ display:block; margin:8px 0; font-size:25px; line-height:1.15; }}
.stack {{ display:grid; grid-template-columns:minmax(0,1fr); gap:10px; }}
.step,.card,.question {{ min-width:0; border:1px solid var(--line); border-radius:8px; background:white; padding:13px; }}
.step span,.card span {{ display:block; margin-bottom:7px; color:var(--accent); font-size:12px; font-weight:900; }}
.step strong,.card strong {{ display:block; margin-bottom:6px; }}
.step p,.step small,.card p,.card small,.question p {{ overflow-wrap:anywhere; word-break:break-word; }}
.step small,.card small {{ display:block; color:var(--ink); }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
ul {{ margin:0; padding-left:18px; color:var(--muted); }}
.boundary {{ border-left:4px solid var(--green); }}
@media (max-width:520px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Daily Agenda · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>오늘 20분 시장 공부 순서</h1>
</header>
<section class="hero">
<span class="eyebrow">오늘의 첫 주제</span>
<strong>{esc(primary.get('name', '오늘 추천 주제 없음'))}</strong>
<p>{esc(primary.get('why_today', 'Scout와 근거를 먼저 생성하세요.'))}</p>
</section>
<section class="section">
<h2>읽는 순서</h2>
<div class="stack">{sequence_cards}</div>
</section>
<section class="section">
<h2>오늘 볼 주제 후보</h2>
<div class="stack">{topic_cards}</div>
</section>
<section class="section">
<h2>근거 fan-out</h2>
<div class="stack">{source_cards}</div>
</section>
<section class="section">
<h2>에이전트 역할별 다음 일</h2>
<div class="stack">{role_cards}</div>
</section>
<section class="section">
<h2>아직 결론내리면 안 되는 이유</h2>
<ul>{weak_items}</ul>
</section>
<section class="section">
<h2>오늘 물어볼 질문</h2>
<div class="stack">{questions}</div>
</section>
<section class="section">
<h2>짧게 남길 응답</h2>
<div class="stack">{response_cards}</div>
</section>
<section class="section boundary">
<h2>안전 경계</h2>
<p>이 agenda는 교육/리서치/시뮬레이션용입니다. 계좌 접근, 주문, 투자 일임, 개인화 매수/매도 지시는 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def write_today_surface(
    *,
    scenario_path: str | Path,
    verdict_path: str | Path,
    memory_path: str | Path,
    evidence_path: str | Path,
    brief_path: str | Path,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    refresh_apply_path: str | Path = DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    agenda_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    agenda_surface_path: str | Path | None = DEFAULT_DAILY_BRIEF_AGENDA_SURFACE,
    source_refresh_surface_path: str | Path | None = DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE,
    review_surface_path: str | Path | None = DEFAULT_DAILY_REVIEW_SURFACE,
    review_prompt_surface_path: str | Path | None = DEFAULT_REVIEW_PROMPT_SURFACE,
    review_effect_surface_path: str | Path | None = DEFAULT_REVIEW_EFFECT_SURFACE,
    pattern_radar_surface_path: str | Path | None = DEFAULT_AGENT_PATTERN_RADAR_SURFACE,
    run_trace_surface_path: str | Path | None = DEFAULT_RUN_TRACE_SURFACE,
    drift_review_surface_path: str | Path | None = DEFAULT_DRIFT_REVIEW_SURFACE,
    output_path: str | Path = DEFAULT_TODAY_OUTPUT,
    archive_manifest_path: str | Path | None = None,
    memory_surface_path: str | Path | None = None,
    journal_surface_path: str | Path | None = None,
    task_queue_surface_path: str | Path | None = None,
    task_ledger_surface_path: str | Path | None = None,
) -> Path:
    scenario = load_json(scenario_path)
    verdict = load_json(verdict_path)
    memory = load_json(memory_path)
    evidence = load_json(evidence_path)
    vault = load_json(vault_path) if Path(vault_path).exists() else {}
    scout = load_json(scout_path) if Path(scout_path).exists() else {}
    refresh_plan = load_json(refresh_plan_path) if Path(refresh_plan_path).exists() else {}
    refresh_apply = load_json(refresh_apply_path) if Path(refresh_apply_path).exists() else {}
    refresh_live_gate = load_json(refresh_live_gate_path) if Path(refresh_live_gate_path).exists() else {}
    refresh_live_run = load_json(refresh_live_run_path) if Path(refresh_live_run_path).exists() else {}
    refresh_live_preflight = load_json(refresh_live_preflight_path) if Path(refresh_live_preflight_path).exists() else {}
    agenda = load_json(agenda_path) if Path(agenda_path).exists() else {}
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_today_surface(
            scenario=scenario,
            verdict=verdict,
            memory=memory,
            evidence=evidence,
            vault_notes=_vault_notes_for_memory(vault),
            scout=scout,
            refresh_plan=refresh_plan,
            refresh_apply=refresh_apply,
            refresh_live_gate=refresh_live_gate,
            refresh_live_run=refresh_live_run,
            refresh_live_preflight=refresh_live_preflight,
            agenda=agenda,
            brief_path=Path(brief_path),
            agenda_surface_path=Path(agenda_surface_path) if agenda_surface_path else None,
            source_refresh_surface_path=Path(source_refresh_surface_path) if source_refresh_surface_path else None,
            review_surface_path=Path(review_surface_path) if review_surface_path else None,
            review_prompt_surface_path=Path(review_prompt_surface_path) if review_prompt_surface_path else None,
            review_effect_surface_path=Path(review_effect_surface_path) if review_effect_surface_path else None,
            pattern_radar_surface_path=Path(pattern_radar_surface_path) if pattern_radar_surface_path else None,
            run_trace_surface_path=Path(run_trace_surface_path) if run_trace_surface_path else None,
            drift_review_surface_path=Path(drift_review_surface_path) if drift_review_surface_path else None,
            archive_manifest_path=Path(archive_manifest_path) if archive_manifest_path else None,
            memory_surface_path=Path(memory_surface_path) if memory_surface_path else None,
            journal_surface_path=Path(journal_surface_path) if journal_surface_path else None,
            task_queue_surface_path=Path(task_queue_surface_path) if task_queue_surface_path else None,
            task_ledger_surface_path=Path(task_ledger_surface_path) if task_ledger_surface_path else None,
        ),
        encoding="utf-8",
    )
    return target


def render_today_surface(
    *,
    scenario: dict[str, Any],
    verdict: dict[str, Any],
    memory: dict[str, Any],
    evidence: dict[str, Any],
    vault_notes: list[dict[str, Any]],
    scout: dict[str, Any],
    refresh_plan: dict[str, Any],
    refresh_apply: dict[str, Any],
    refresh_live_gate: dict[str, Any],
    refresh_live_run: dict[str, Any],
    refresh_live_preflight: dict[str, Any],
    agenda: dict[str, Any],
    brief_path: Path,
    agenda_surface_path: Path | None = None,
    source_refresh_surface_path: Path | None = None,
    review_surface_path: Path | None = None,
    review_prompt_surface_path: Path | None = None,
    review_effect_surface_path: Path | None = None,
    pattern_radar_surface_path: Path | None = None,
    run_trace_surface_path: Path | None = None,
    drift_review_surface_path: Path | None = None,
    archive_manifest_path: Path | None = None,
    memory_surface_path: Path | None = None,
    journal_surface_path: Path | None = None,
    task_queue_surface_path: Path | None = None,
    task_ledger_surface_path: Path | None = None,
) -> str:
    market_map = scenario.get("market_map", {})
    primary = verdict.get("primary_next_step") or {}
    scenarios = scenario.get("scenarios", [])
    memory_topics = memory.get("topics", [])
    source_rows = evidence.get("source_status", [])
    gaps = evidence.get("collection_gaps", [])
    generated_at = scenario.get("generated_at", _now())
    scout_recommendations = scout.get("recommendations", []) if scout.get("schema_version") == "daily_scout.v1" else []
    refresh_actions = refresh_plan.get("actions", []) if refresh_plan.get("schema_version") == "source_refresh_plan.v1" else []
    refresh_results = refresh_apply.get("results", []) if refresh_apply.get("schema_version") == "source_refresh_apply.v1" else []
    live_gate_decisions = refresh_live_gate.get("decisions", []) if refresh_live_gate.get("schema_version") == "source_refresh_live_gate.v1" else []
    live_run_execution = refresh_live_run.get("execution", {}) if refresh_live_run.get("schema_version") == "source_refresh_live_run.v1" else {}
    live_preflight_requested = refresh_live_preflight.get("requested_execution", {}) if refresh_live_preflight.get("schema_version") == "source_refresh_live_preflight.v1" else {}
    agenda_primary = agenda.get("primary_topic", {}) if agenda.get("schema_version") == DAILY_BRIEF_AGENDA_SCHEMA_VERSION else {}
    agenda_steps = agenda.get("study_sequence", []) if agenda.get("schema_version") == DAILY_BRIEF_AGENDA_SCHEMA_VERSION else []
    agenda_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(step.get('minutes', ''))}분 · step {esc(step.get('step', ''))}</span>"
        f"<strong>{esc(step.get('title', ''))}</strong>"
        f"<p>{esc(step.get('operator_action', ''))}</p>"
        "</article>"
        for step in agenda_steps[:4]
    ) or "<p>오늘 agenda가 아직 없습니다.</p>"
    scout_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(item.get('action', 'monitor'))} · #{esc(item.get('priority_rank', ''))}</span>"
        f"<strong>{esc(item.get('name', ''))}</strong>"
        f"<p>{esc(item.get('why', ''))}</p>"
        f"<small>질문: {esc(item.get('next_question', ''))}</small>"
        "</article>"
        for item in scout_recommendations[:3]
    ) or "<p>오늘 scout 추천이 아직 없습니다.</p>"
    refresh_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(action.get('priority', 'low'))} · {esc(action.get('cadence', 'review'))}</span>"
        f"<strong>{esc(action.get('source_name', 'source'))}</strong>"
        f"<p>{esc(action.get('reason', ''))}</p>"
        f"<small>{esc(action.get('adapter_id', ''))} · dry-run 계획</small>"
        "</article>"
        for action in refresh_actions[:4]
    ) or "<p>오늘 source refresh plan이 아직 없습니다.</p>"
    refresh_apply_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(result.get('decision', 'review'))} · {esc(result.get('status', 'unknown'))}</span>"
        f"<strong>{esc(result.get('source_name', 'source'))}</strong>"
        f"<p>{esc(result.get('reason', ''))}</p>"
        f"<small>{esc(result.get('adapter_id', ''))} · 실행 여부: {esc('예' if result.get('will_execute') else '아니오')}</small>"
        "</article>"
        for result in refresh_results[:4]
    ) or "<p>오늘 source refresh apply 판정이 아직 없습니다.</p>"
    live_gate_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(decision.get('status', 'review'))} · {esc(decision.get('approval_scope', ''))}</span>"
        f"<strong>{esc(decision.get('id', 'live gate'))}</strong>"
        f"<p>{esc(decision.get('stale_context_guard', ''))}</p>"
        f"<small>{esc(decision.get('copy_ready_response', ''))}</small>"
        "</article>"
        for decision in live_gate_decisions[:3]
    ) or "<p>오늘 승인 대기 중인 live refresh gate가 없습니다.</p>"
    live_run_cards = (
        "<article class='card'>"
        f"<span>{esc(refresh_live_run.get('approval_status', 'unknown'))} · {esc(live_run_execution.get('status', 'unknown'))}</span>"
        "<strong>라이브 실행 증거</strong>"
        f"<p>{esc(refresh_live_run.get('next_step', '아직 live refresh run proof가 없습니다.'))}</p>"
        f"<small>external effect: {esc('yes' if refresh_live_run.get('external_effect_performed') else 'no')} · blockers: {esc(', '.join(live_run_execution.get('blockers', [])) or 'none')}</small>"
        "</article>"
        if refresh_live_run.get("schema_version") == "source_refresh_live_run.v1"
        else "<p>오늘 live refresh run proof가 아직 없습니다.</p>"
    )
    live_preflight_cards = (
        "<article class='card'>"
        f"<span>{esc(refresh_live_preflight.get('status', 'unknown'))} · execute intent: {esc('yes' if live_preflight_requested.get('intend_execute') else 'no')}</span>"
        "<strong>라이브 실행 사전점검</strong>"
        f"<p>{esc(refresh_live_preflight.get('next_step', '아직 live refresh preflight proof가 없습니다.'))}</p>"
        f"<small>external effect: {esc('yes' if refresh_live_preflight.get('external_effect_performed') else 'no')} · blockers: {esc(', '.join(refresh_live_preflight.get('blockers', [])) or 'none')}</small>"
        "</article>"
        if refresh_live_preflight.get("schema_version") == "source_refresh_live_preflight.v1"
        else "<p>오늘 live refresh preflight proof가 아직 없습니다.</p>"
    )
    theme_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(topic.get('name', ''))}</span>"
        f"<strong>{esc('새 변화' if topic.get('changed_since_previous') else '누적 관찰')}</strong>"
        f"<p>{esc(topic.get('latest_summary', ''))}</p>"
        "</article>"
        for topic in memory_topics[:5]
    ) or "<p>아직 누적 주제 기억이 없습니다.</p>"
    vault_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(note.get('topic_name', 'Vault'))}</span>"
        f"<strong>{esc(note.get('title', ''))}</strong>"
        f"<p>{esc(' · '.join(note.get('key_takeaways', [])[:2]))}</p>"
        f"<small>{esc(note.get('source_path', ''))}</small>"
        "</article>"
        for note in _today_vault_notes(vault_notes=vault_notes, memory_topics=memory_topics)[:4]
    ) or "<p>오늘 연결된 vault 원천 노트가 없습니다.</p>"
    path_cards = "".join(
        "<article class='path'>"
        f"<span>{esc(path.get('probability_label', ''))}</span>"
        f"<h3>{esc(path.get('name', ''))}</h3>"
        f"<p>{esc(path.get('beginner_explanation', path.get('summary', '')))}</p>"
        "</article>"
        for path in scenarios[:3]
    )
    source_chips = "".join(
        f"<span class='chip'>{esc(row.get('source_name', 'source'))} · {esc(row.get('freshness_status', 'unknown'))} · {esc(row.get('relevance_label', 'unscored'))}</span>"
        for row in source_rows[:8]
    ) or "<span class='chip'>로컬 seed</span>"
    relevance_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(row.get('source_name', 'source'))}</span>"
        f"<strong>{esc(row.get('relevance_label', 'unscored'))}</strong>"
        f"<p>관련도 {esc(row.get('relevance_score', '0.00'))} · 신선도 {esc(row.get('freshness_status', 'unknown'))}</p>"
        "</article>"
        for row in source_rows[:4]
    )
    gap_items = "".join(f"<li>{esc(_gap_label(gap))}</li>" for gap in gaps[:6]) or "<li>오늘 기록된 차단 이슈는 없습니다.</li>"
    archive_link = (
        f"<a href='{esc(_relative_href(archive_manifest_path))}'>아카이브 manifest</a>"
        if archive_manifest_path
        else "<span>아카이브 manifest 없음</span>"
    )
    memory_link = (
        f"<a href='{esc(_relative_href(memory_surface_path))}'>누적 기억 보기</a>"
        if memory_surface_path
        else "<span>누적 기억 없음</span>"
    )
    journal_link = (
        f"<a href='{esc(_relative_href(journal_surface_path))}'>오늘의 analyst journal</a>"
        if journal_surface_path
        else "<span>Analyst journal 없음</span>"
    )
    task_queue_link = (
        f"<a href='{esc(_relative_href(task_queue_surface_path))}'>다음 analyst tasks</a>"
        if task_queue_surface_path
        else "<span>Analyst tasks 없음</span>"
    )
    task_ledger_link = (
        f"<a href='{esc(_relative_href(task_ledger_surface_path))}'>task ledger</a>"
        if task_ledger_surface_path
        else "<span>Task ledger 없음</span>"
    )
    agenda_link = (
        f"<a href='{esc(_relative_href(agenda_surface_path))}'>오늘 20분 agenda</a>"
        if agenda_surface_path
        else "<span>오늘 agenda 없음</span>"
    )
    source_refresh_link = (
        f"<a href='{esc(_relative_href(source_refresh_surface_path))}'>근거 새로고침 판단</a>"
        if source_refresh_surface_path
        else "<span>근거 새로고침 판단 없음</span>"
    )
    review_link = (
        f"<a href='{esc(_relative_href(review_surface_path))}'>오늘 review 기록</a>"
        if review_surface_path
        else "<span>오늘 review 없음</span>"
    )
    review_prompt_link = (
        f"<a href='{esc(_relative_href(review_prompt_surface_path))}'>오늘 피드백 가이드</a>"
        if review_prompt_surface_path
        else "<span>오늘 피드백 가이드 없음</span>"
    )
    review_effect_link = (
        f"<a href='{esc(_relative_href(review_effect_surface_path))}'>피드백 반영 확인</a>"
        if review_effect_surface_path
        else "<span>피드백 반영 확인 없음</span>"
    )
    pattern_radar_link = (
        f"<a href='{esc(_relative_href(pattern_radar_surface_path))}'>방식 업데이트 레이더</a>"
        if pattern_radar_surface_path
        else "<span>방식 업데이트 없음</span>"
    )
    run_trace_link = (
        f"<a href='{esc(_relative_href(run_trace_surface_path))}'>오늘 실행 trace</a>"
        if run_trace_surface_path
        else "<span>오늘 실행 trace 없음</span>"
    )
    drift_review_link = (
        f"<a href='{esc(_relative_href(drift_review_surface_path))}'>방향 이탈 점검</a>"
        if drift_review_surface_path
        else "<span>방향 이탈 점검 없음</span>"
    )
    questions = _daily_questions(memory_topics, evidence, vault_notes, scout_recommendations)
    question_cards = "".join(f"<article class='question'><p>{esc(question)}</p></article>" for question in questions)

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Today</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
html,body {{ max-width:100%; overflow-x:hidden; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
main {{ width:100%; max-width:430px; min-width:0; margin:0; padding:16px; }}
header {{ padding:26px 0 16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; overflow-wrap:anywhere; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p {{ margin:0; color:var(--muted); }}
.hero {{ border:1px solid var(--line); border-radius:8px; background:linear-gradient(180deg,#fffefa,#f1f7f3); padding:18px; }}
.primary {{ display:block; margin-top:14px; font-size:24px; color:var(--ink); }}
.section {{ width:100%; min-width:0; overflow:hidden; margin:14px 0; padding:16px; border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.stack {{ display:grid; grid-template-columns:minmax(0,1fr); min-width:0; gap:10px; }}
.card,.path,.question {{ min-width:0; border:1px solid var(--line); border-radius:8px; background:white; padding:14px; }}
.card span,.path span {{ display:block; margin-bottom:7px; color:var(--blue); font-size:12px; font-weight:900; }}
.card strong {{ display:block; margin-bottom:6px; }}
.card p,.card small,.path p,.question p {{ overflow-wrap:anywhere; word-break:break-word; }}
.card small {{ display:block; color:var(--ink); line-height:1.5; }}
.chips {{ display:flex; flex-wrap:wrap; gap:7px; }}
.chip {{ display:inline-flex; min-height:28px; align-items:center; border-radius:999px; padding:3px 10px; background:#eef4fb; color:#1f4f78; font-size:12px; font-weight:800; }}
.links {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:8px; }}
.links a,.links span {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
ul {{ margin:0; padding-left:18px; color:var(--muted); }}
.boundary {{ border-left:4px solid var(--green); }}
@media (max-width:520px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; line-height:1.14; }} .links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Today · {esc(_short_date(generated_at))}</span>
<h1>오늘 시장 5분 브리프</h1>
</header>
<section class="hero">
<span class="eyebrow">가장 먼저 볼 것</span>
<strong class="primary">{esc(primary.get('title', '근거 확인부터 시작'))}</strong>
<p>{esc(primary.get('rationale', market_map.get('beginner_summary', '오늘 브리프를 만들 근거를 점검합니다.')))}</p>
</section>
<section class="section">
<h2>오늘 Scout 추천</h2>
<div class="stack">{scout_cards}</div>
</section>
<section class="section">
<h2>오늘 20분 agenda</h2>
<div class="stack">
<article class="card">
<span>{esc(agenda_primary.get('readiness', 'agenda'))}</span>
<strong>{esc(agenda_primary.get('name', '오늘 agenda 없음'))}</strong>
<p>{esc(agenda_primary.get('why_today', 'Scout 추천을 먼저 생성하세요.'))}</p>
</article>
{agenda_cards}
</div>
</section>
<section class="section">
<h2>오늘 새로고침 계획</h2>
<div class="stack">{refresh_cards}</div>
</section>
<section class="section">
<h2>오늘 실행 판정</h2>
<div class="stack">{refresh_apply_cards}</div>
</section>
<section class="section">
<h2>라이브 새로고침 게이트</h2>
<div class="stack">{live_gate_cards}</div>
</section>
<section class="section">
<h2>라이브 실행 증거</h2>
<div class="stack">{live_run_cards}</div>
</section>
<section class="section">
<h2>라이브 실행 사전점검</h2>
<div class="stack">{live_preflight_cards}</div>
</section>
<section class="section">
<h2>오늘의 주제 기억</h2>
<div class="stack">{theme_cards}</div>
</section>
<section class="section">
<h2>Vault에서 다시 볼 원천 노트</h2>
<div class="stack">{vault_cards}</div>
</section>
<section class="section">
<h2>가능한 세 가지 경로</h2>
<div class="stack">{path_cards}</div>
</section>
<section class="section">
<h2>자료 상태</h2>
<div class="chips">{source_chips}</div>
</section>
<section class="section">
<h2>근거 품질</h2>
<div class="stack">{relevance_cards}</div>
</section>
<section class="section">
<h2>아직 약한 부분</h2>
<ul>{gap_items}</ul>
</section>
<section class="section">
<h2>오늘 공부할 질문</h2>
<div class="stack">{question_cards}</div>
</section>
<section class="section">
<h2>연결된 산출물</h2>
<div class="links">
<a href="{esc(_relative_href(brief_path))}">상세 시장 브리프</a>
{agenda_link}
{source_refresh_link}
{review_link}
{review_prompt_link}
{review_effect_link}
{pattern_radar_link}
{run_trace_link}
{drift_review_link}
{journal_link}
{task_queue_link}
{task_ledger_link}
{memory_link}
{archive_link}
</div>
</section>
<section class="section boundary">
<h2>안전 경계</h2>
<p>이 화면은 교육과 리서치, 시뮬레이션용입니다. 계좌 연결, 주문 실행, 일임 운용, 근거 없는 개인화 추천을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def archive_daily_run(
    *,
    run_id: str,
    scenario_path: str | Path,
    verdict_path: str | Path,
    evidence_path: str | Path,
    memory_path: str | Path,
    brief_path: str | Path,
    today_path: str | Path,
    refresh_plan_path: str | Path | None = None,
    refresh_apply_path: str | Path | None = None,
    refresh_live_gate_path: str | Path | None = None,
    refresh_live_run_path: str | Path | None = None,
    refresh_live_preflight_path: str | Path | None = None,
    journal_path: str | Path | None = None,
    task_queue_path: str | Path | None = None,
    task_ledger_path: str | Path | None = None,
    daily_review_path: str | Path | None = None,
    daily_review_surface_path: str | Path | None = None,
    learning_ledger_path: str | Path | None = None,
    learning_ledger_surface_path: str | Path | None = None,
    review_prompt_path: str | Path | None = None,
    review_prompt_surface_path: str | Path | None = None,
    review_effect_path: str | Path | None = None,
    review_effect_surface_path: str | Path | None = None,
    pattern_radar_path: str | Path | None = None,
    pattern_radar_surface_path: str | Path | None = None,
    run_trace_path: str | Path | None = None,
    run_trace_surface_path: str | Path | None = None,
    drift_review_path: str | Path | None = None,
    drift_review_surface_path: str | Path | None = None,
    vault_compile_path: str | Path | None = None,
    vault_surface_path: str | Path | None = None,
    agenda_path: str | Path | None = None,
    agenda_surface_path: str | Path | None = None,
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
) -> Path:
    timestamp = datetime.now(timezone.utc)
    archive_dir = Path(archive_root) / timestamp.strftime("%Y-%m-%d")
    archive_dir.mkdir(parents=True, exist_ok=True)
    copied: dict[str, str] = {}
    for label, source in {
        "scenario": scenario_path,
        "verdict": verdict_path,
        "evidence": evidence_path,
        "memory": memory_path,
        "source_refresh_plan": refresh_plan_path,
        "source_refresh_apply": refresh_apply_path,
        "source_refresh_live_gate": refresh_live_gate_path,
        "source_refresh_live_run": refresh_live_run_path,
        "source_refresh_live_preflight": refresh_live_preflight_path,
        "journal": journal_path,
        "tasks": task_queue_path,
        "task_ledger": task_ledger_path,
        "daily_review": daily_review_path,
        "daily_review_surface": daily_review_surface_path,
        "learning_ledger": learning_ledger_path,
        "learning_ledger_surface": learning_ledger_surface_path,
        "review_prompt": review_prompt_path,
        "review_prompt_surface": review_prompt_surface_path,
        "review_effect": review_effect_path,
        "review_effect_surface": review_effect_surface_path,
        "agent_pattern_radar": pattern_radar_path,
        "agent_pattern_radar_surface": pattern_radar_surface_path,
        "run_trace": run_trace_path,
        "run_trace_surface": run_trace_surface_path,
        "drift_review": drift_review_path,
        "drift_review_surface": drift_review_surface_path,
        "vault_compile": vault_compile_path,
        "vault": vault_surface_path,
        "daily_agenda": agenda_path,
        "daily_agenda_surface": agenda_surface_path,
        "brief": brief_path,
        "today": today_path,
    }.items():
        if source is None:
            continue
        source_path = Path(source)
        if source_path.exists():
            target = archive_dir / source_path.name
            shutil.copy2(source_path, target)
            copied[label] = target.as_posix()
    manifest = {
        "schema_version": ARCHIVE_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at": timestamp.isoformat(),
        "archive_dir": archive_dir.as_posix(),
        "artifacts": copied,
        "policy": "research_only",
    }
    return write_json(manifest, archive_dir / "manifest.json")


def add_archive_artifacts(
    *,
    manifest_path: str | Path,
    artifacts: dict[str, str | Path],
) -> Path:
    manifest = load_json(manifest_path)
    archive_dir = Path(manifest.get("archive_dir", Path(manifest_path).parent))
    copied = dict(manifest.get("artifacts", {}))
    for label, source in artifacts.items():
        source_path = Path(source)
        if source_path.exists():
            target = archive_dir / source_path.name
            shutil.copy2(source_path, target)
            copied[label] = target.as_posix()
    manifest["artifacts"] = copied
    manifest["updated_at"] = _now()
    return write_json(manifest, manifest_path)


def build_analyst_journal(
    *,
    scenario_path: str | Path,
    verdict_path: str | Path,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    archive_manifest_path: str | Path | None = None,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scenario = load_json(scenario_path)
    verdict = load_json(verdict_path)
    memory = load_json(memory_path)
    evidence = load_json(evidence_path) if Path(evidence_path).exists() else {}
    scout = load_json(scout_path) if Path(scout_path).exists() else {}
    vault = load_json(vault_path) if Path(vault_path).exists() else {}
    archive_manifest = load_json(archive_manifest_path) if archive_manifest_path and Path(archive_manifest_path).exists() else {}
    source_rows = evidence.get("source_status", [])
    memory_topics = memory.get("topics", [])
    changed_topics = [topic for topic in memory_topics if topic.get("changed_since_previous")]
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    primary = verdict.get("primary_next_step") or {}
    weak_sources = [
        row for row in source_rows
        if row.get("freshness_status") in {"stale", "unknown"} or row.get("relevance_label") in {"weak", "unscored"}
    ]
    coverage_sources = sorted({source for topic in memory_topics for source in topic.get("source_names", [])})
    follow_up_questions = _journal_follow_up_questions(
        recommended=recommended,
        memory_topics=memory_topics,
        scenario=scenario,
    )
    role_notes = [
        {
            "role": "source_scout",
            "finding": f"{len(source_rows)}개 source 상태를 확인했고 {len(weak_sources)}개는 약하거나 오래된 근거입니다.",
            "next_check": "live refresh 승인 전에는 cached/sample 근거와 freshness를 분리해서 읽습니다.",
        },
        {
            "role": "market_mapper",
            "finding": scenario.get("market_map", {}).get("beginner_summary", "시장 지도 요약이 아직 약합니다."),
            "next_check": "주제, 기업, 이벤트가 같은 방향인지와 충돌하는지 분리합니다.",
        },
        {
            "role": "skeptic",
            "finding": _journal_skeptic_note(evidence=evidence, memory_topics=memory_topics),
            "next_check": "자료 부족을 매수/매도 결론으로 바꾸지 않습니다.",
        },
        {
            "role": "beginner_tutor",
            "finding": primary.get("rationale", "오늘은 결론보다 시장 흐름 이해를 우선합니다."),
            "next_check": "초보자가 먼저 이해할 단어와 원인-결과 연결을 매일 하나씩 남깁니다.",
        },
        {
            "role": "memory_librarian",
            "finding": f"누적 실행 {memory.get('run_count', 0)}회, vault note {len(_vault_notes_for_memory(vault))}개를 연결했습니다.",
            "next_check": "오늘 질문이 내일 다시 검색 가능한 표현인지 확인합니다.",
        },
    ]
    payload = {
        "schema_version": ANALYST_JOURNAL_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "run_id": scenario.get("run_id", ""),
        "status": _journal_status(source_rows=source_rows, memory_topics=memory_topics),
        "today_focus": {
            "title": primary.get("title", recommended.get("name", "오늘 먼저 볼 주제")),
            "rationale": primary.get("rationale", recommended.get("why", "")),
            "recommended_topic": recommended.get("name", ""),
            "recommended_action": recommended.get("action", ""),
            "confidence": recommended.get("confidence", ""),
        },
        "what_changed": [
            {
                "topic_id": topic.get("topic_id", ""),
                "name": topic.get("name", ""),
                "summary": topic.get("latest_summary", ""),
                "latest_titles": topic.get("latest_titles", [])[:5],
            }
            for topic in changed_topics
        ],
        "stable_observations": [
            {
                "topic_id": topic.get("topic_id", ""),
                "name": topic.get("name", ""),
                "summary": topic.get("latest_summary", ""),
            }
            for topic in memory_topics
            if not topic.get("changed_since_previous")
        ][:5],
        "role_notes": role_notes,
        "source_posture": {
            "source_count": len(source_rows),
            "coverage_sources": coverage_sources,
            "weak_or_stale_count": len(weak_sources),
            "collection_gaps": evidence.get("collection_gaps", []),
        },
        "follow_up_questions": follow_up_questions,
        "linked_artifacts": {
            "scenario": Path(scenario_path).as_posix(),
            "verdict": Path(verdict_path).as_posix(),
            "memory": Path(memory_path).as_posix(),
            "evidence": Path(evidence_path).as_posix(),
            "scout": Path(scout_path).as_posix(),
            "archive_manifest": Path(archive_manifest_path).as_posix() if archive_manifest_path else "",
            "archive_dir": archive_manifest.get("archive_dir", ""),
        },
        "operator_reading_order": [
            "today_focus",
            "what_changed",
            "role_notes",
            "follow_up_questions",
            "linked_artifacts",
        ],
        "policy": "research_only",
        "safety_boundary": [
            "education_and_research_only",
            "no_account_access",
            "no_live_trading",
            "no_discretionary_management",
            "no_unsupported_personalized_recommendation",
        ],
    }
    return payload


def write_analyst_journal(
    *,
    scenario_path: str | Path,
    verdict_path: str | Path,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    archive_manifest_path: str | Path | None = None,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    surface_output_path: str | Path = DEFAULT_ANALYST_JOURNAL_OUTPUT,
) -> Path:
    payload = build_analyst_journal(
        scenario_path=scenario_path,
        verdict_path=verdict_path,
        memory_path=memory_path,
        evidence_path=evidence_path,
        scout_path=scout_path,
        archive_manifest_path=archive_manifest_path,
        vault_path=vault_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_analyst_journal(payload), encoding="utf-8")
    return target


def validate_analyst_journal_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != ANALYST_JOURNAL_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("today_focus"):
        errors.append("today_focus must not be empty")
    if not payload.get("role_notes"):
        errors.append("role_notes must not be empty")
    if not payload.get("follow_up_questions"):
        errors.append("follow_up_questions must not be empty")
    linked = payload.get("linked_artifacts", {})
    for field in ["scenario", "verdict", "memory", "evidence", "scout"]:
        if not linked.get(field):
            errors.append(f"linked_artifacts.{field} must not be empty")
    if "no_live_trading" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include no_live_trading")
    return errors


def validate_analyst_journal_file(path: str | Path) -> list[str]:
    return validate_analyst_journal_payload(load_json(path))


def build_learning_ledger(
    *,
    scenario_path: str | Path = Path("reports/scenarios/daily-research-sim.json"),
    verdict_path: str | Path = Path("reports/scenarios/daily-research-verdict.json"),
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scenario = _load_optional_json(scenario_path)
    verdict = _load_optional_json(verdict_path)
    journal = _load_optional_json(journal_path)
    memory = _load_optional_json(memory_path)
    evidence = _load_optional_json(evidence_path)
    topics = memory.get("topics", [])
    changed_topics = [topic for topic in topics if topic.get("changed_since_previous")]
    repeated_topics = [topic for topic in topics if not topic.get("changed_since_previous")]
    primary = verdict.get("primary_next_step", {}) if verdict else {}
    focus = journal.get("today_focus", {}) if journal else {}
    market_map = scenario.get("market_map", {}) if scenario else {}
    beginner_explanations = scenario.get("beginner_explanations", []) if scenario else []
    source_rows = evidence.get("source_status", [])
    source_gaps = evidence.get("collection_gaps", [])
    archive_manifests = sorted(Path(archive_root).glob("*/manifest.json"), reverse=True)
    recent_archives = [path.as_posix() for path in archive_manifests[:5]]
    questions = _dedupe_texts(
        list(journal.get("follow_up_questions", []))
        + [question for topic in topics for question in topic.get("daily_questions", [])]
    )[:8]
    concepts = _learning_concepts(
        primary=primary,
        focus=focus,
        market_map=market_map,
        beginner_explanations=beginner_explanations,
    )
    payload = {
        "schema_version": LEARNING_LEDGER_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "run_id": scenario.get("run_id", journal.get("run_id", "daily-research")),
        "status": _learning_ledger_status(concepts=concepts, questions=questions, source_gaps=source_gaps),
        "summary": {
            "today_focus": focus.get("title", primary.get("title", "오늘 먼저 배울 것")),
            "run_count": memory.get("run_count", 0),
            "changed_topic_count": len(changed_topics),
            "repeated_topic_count": len(repeated_topics),
            "concept_count": len(concepts),
            "question_count": len(questions),
            "source_count": len(source_rows),
            "source_gap_count": len(source_gaps),
            "archive_count": len(recent_archives),
        },
        "today_lesson": {
            "headline": focus.get("title", primary.get("title", "오늘 먼저 배울 것")),
            "why_it_matters": focus.get("rationale", primary.get("rationale", market_map.get("beginner_summary", ""))),
            "beginner_rule": "결론보다 원인-결과, 반복 관찰, 반대 근거를 먼저 남깁니다.",
            "confidence": focus.get("confidence", "low"),
        },
        "concept_cards": concepts,
        "memory_compounding": {
            "changed_topics": [
                {
                    "name": topic.get("name", ""),
                    "summary": topic.get("latest_summary", ""),
                    "latest_titles": topic.get("latest_titles", [])[:3],
                }
                for topic in changed_topics[:5]
            ],
            "repeated_topics": [
                {
                    "name": topic.get("name", ""),
                    "summary": topic.get("latest_summary", ""),
                    "source_names": topic.get("source_names", [])[:4],
                }
                for topic in repeated_topics[:6]
            ],
        },
        "study_path": [
            {
                "step": 1,
                "title": "오늘 배울 핵심 문장 읽기",
                "why": "먼저 무엇을 배우는 날인지 고정합니다.",
                "stop_condition": "한 문장으로 오늘의 원인-결과를 설명할 수 있습니다.",
            },
            {
                "step": 2,
                "title": "반복 관찰과 새 변화를 분리",
                "why": "매일 바뀌는 소음과 여러 번 반복되는 흐름을 구분합니다.",
                "stop_condition": "반복 주제 하나와 확인할 변화 하나를 구분했습니다.",
            },
            {
                "step": 3,
                "title": "모르는 질문을 내일로 넘기기",
                "why": "개인 애널리스트는 답보다 다음 질문이 누적될 때 좋아집니다.",
                "stop_condition": "내일 다시 물어볼 질문을 하나 골랐습니다.",
            },
        ],
        "questions_to_carry": questions,
        "source_posture": {
            "source_names": sorted({row.get("source_name", "") for row in source_rows if row.get("source_name")}),
            "weak_or_stale_count": sum(
                1
                for row in source_rows
                if row.get("freshness_status") in {"stale", "unknown"} or row.get("relevance_label") in {"weak", "unscored"}
            ),
            "collection_gaps": source_gaps,
        },
        "linked_artifacts": {
            "scenario": Path(scenario_path).as_posix(),
            "verdict": Path(verdict_path).as_posix(),
            "journal": Path(journal_path).as_posix(),
            "memory": Path(memory_path).as_posix(),
            "evidence": Path(evidence_path).as_posix(),
            "archive_root": Path(archive_root).as_posix(),
            "recent_archives": recent_archives,
        },
        "phone_links": {
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "journal": DEFAULT_ANALYST_JOURNAL_OUTPUT.as_posix(),
            "memory": DEFAULT_MEMORY_OUTPUT.as_posix(),
            "memory_query": DEFAULT_MEMORY_QUERY_SURFACE.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_existing_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "no_account_access",
            "no_live_trading",
            "no_discretionary_management",
            "no_unsupported_personalized_recommendation",
        ],
    }
    return payload


def write_learning_ledger(
    *,
    scenario_path: str | Path = Path("reports/scenarios/daily-research-sim.json"),
    verdict_path: str | Path = Path("reports/scenarios/daily-research-verdict.json"),
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    artifact_output_path: str | Path = DEFAULT_LEARNING_LEDGER_OUTPUT,
    surface_output_path: str | Path = DEFAULT_LEARNING_LEDGER_SURFACE,
) -> Path:
    payload = build_learning_ledger(
        scenario_path=scenario_path,
        verdict_path=verdict_path,
        journal_path=journal_path,
        memory_path=memory_path,
        evidence_path=evidence_path,
        archive_root=archive_root,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_learning_ledger(payload), encoding="utf-8")
    return target


def validate_learning_ledger_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != LEARNING_LEDGER_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("status") not in {"ready", "review", "thin"}:
        errors.append("status must be ready, review, or thin")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if not payload.get("today_lesson", {}).get("headline"):
        errors.append("today_lesson.headline must not be empty")
    if not payload.get("concept_cards"):
        errors.append("concept_cards must not be empty")
    if not payload.get("questions_to_carry"):
        errors.append("questions_to_carry must not be empty")
    for field in ["scenario", "verdict", "journal", "memory", "evidence"]:
        if not payload.get("linked_artifacts", {}).get(field):
            errors.append(f"linked_artifacts.{field} must not be empty")
    if "reads_existing_local_artifacts_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include reads_existing_local_artifacts_only")
    return errors


def validate_learning_ledger_file(path: str | Path) -> list[str]:
    return validate_learning_ledger_payload(load_json(path))


def build_analyst_council(
    *,
    scenario_path: str | Path = Path("reports/scenarios/daily-research-sim.json"),
    verdict_path: str | Path = Path("reports/scenarios/daily-research-verdict.json"),
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    memory_audit_path: str | Path = DEFAULT_MEMORY_AUDIT_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scenario = _load_optional_json(scenario_path)
    verdict = _load_optional_json(verdict_path)
    journal = _load_optional_json(journal_path)
    memory = _load_optional_json(memory_path)
    evidence = _load_optional_json(evidence_path)
    memory_audit = _load_optional_json(memory_audit_path)
    scout = _load_optional_json(scout_path)
    roles = _analyst_council_roles(
        scenario=scenario,
        verdict=verdict,
        journal=journal,
        memory=memory,
        evidence=evidence,
        memory_audit=memory_audit,
        scout=scout,
    )
    blockers = _analyst_council_blockers(roles=roles, memory_audit=memory_audit, evidence=evidence)
    disagreement = _analyst_council_disagreement(roles=roles)
    decision = _analyst_council_decision(roles=roles, blockers=blockers, disagreement=disagreement)
    return {
        "schema_version": ANALYST_COUNCIL_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "run_id": scenario.get("run_id", journal.get("run_id", scout.get("run_id", ""))),
        "status": decision["status"],
        "council_mode": "local_role_review_before_daily_reading",
        "decision": decision,
        "summary": {
            "role_count": len(roles),
            "agreement_count": sum(1 for role in roles if role.get("stance") == "agree"),
            "caution_count": sum(1 for role in roles if role.get("stance") == "caution"),
            "blocker_count": len(blockers),
            "disagreement_count": len(disagreement),
            "average_confidence": round(sum(float(role.get("confidence", 0.0)) for role in roles) / max(len(roles), 1), 2),
        },
        "roles": roles,
        "disagreement": disagreement,
        "blockers": blockers,
        "beginner_reading_order": _analyst_council_reading_order(decision=decision, roles=roles),
        "next_questions": _analyst_council_next_questions(roles=roles, blockers=blockers, journal=journal, memory_audit=memory_audit),
        "copy_ready_commands": _analyst_council_commands(decision=decision, roles=roles, scout=scout, journal=journal),
        "linked_surfaces": {
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "brief": "reports/product/market-brief.html",
            "journal": DEFAULT_ANALYST_JOURNAL_OUTPUT.as_posix(),
            "memory_audit": DEFAULT_MEMORY_AUDIT_SURFACE.as_posix(),
            "tasks": DEFAULT_ANALYST_TASK_QUEUE_OUTPUT.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
        },
        "linked_artifacts": {
            "scenario": Path(scenario_path).as_posix(),
            "verdict": Path(verdict_path).as_posix(),
            "journal": Path(journal_path).as_posix(),
            "memory": Path(memory_path).as_posix(),
            "evidence": Path(evidence_path).as_posix(),
            "memory_audit": Path(memory_audit_path).as_posix(),
            "scout": Path(scout_path).as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_order_execution",
            "no_discretionary_management",
            "no_unsupported_personalized_recommendation",
        ],
    }


def write_analyst_council(
    *,
    scenario_path: str | Path = Path("reports/scenarios/daily-research-sim.json"),
    verdict_path: str | Path = Path("reports/scenarios/daily-research-verdict.json"),
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    memory_audit_path: str | Path = DEFAULT_MEMORY_AUDIT_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_ANALYST_COUNCIL_OUTPUT,
    surface_output_path: str | Path = DEFAULT_ANALYST_COUNCIL_SURFACE,
) -> Path:
    payload = build_analyst_council(
        scenario_path=scenario_path,
        verdict_path=verdict_path,
        journal_path=journal_path,
        memory_path=memory_path,
        evidence_path=evidence_path,
        memory_audit_path=memory_audit_path,
        scout_path=scout_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_analyst_council(payload), encoding="utf-8")
    return target


def validate_analyst_council_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != ANALYST_COUNCIL_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"ready_to_read", "read_with_caution", "blocked"}:
        errors.append("status must be ready_to_read, read_with_caution, or blocked")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if not payload.get("roles"):
        errors.append("roles must not be empty")
    required_roles = {"source_scout", "evidence_curator", "market_mapper", "scenario_analyst", "skeptic", "beginner_tutor"}
    observed_roles = {role.get("role") for role in payload.get("roles", [])}
    for role in sorted(required_roles - observed_roles):
        errors.append(f"missing council role: {role}")
    for index, role in enumerate(payload.get("roles", [])):
        for field in ["role", "stance", "finding", "confidence", "evidence", "beginner_translation", "next_check"]:
            if field not in role:
                errors.append(f"roles[{index}] missing {field}")
        if role.get("stance") not in {"agree", "caution", "block"}:
            errors.append(f"roles[{index}] invalid stance")
    if not payload.get("beginner_reading_order"):
        errors.append("beginner_reading_order must not be empty")
    if not payload.get("next_questions"):
        errors.append("next_questions must not be empty")
    commands = payload.get("copy_ready_commands", [])
    if not commands:
        errors.append("copy_ready_commands must not be empty")
    for index, command in enumerate(commands):
        command_text = command.get("command", "")
        if "council-response-apply" not in command_text:
            errors.append(f"copy_ready_commands[{index}] must call council-response-apply")
        if command.get("external_effect_performed") is not False:
            errors.append(f"copy_ready_commands[{index}] external_effect_performed must be false")
    if "reads_local_artifacts_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include reads_local_artifacts_only")
    if "no_order_execution" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include no_order_execution")
    return errors


def validate_analyst_council_file(path: str | Path) -> list[str]:
    return validate_analyst_council_payload(load_json(path))


def render_analyst_council(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    decision = payload.get("decision", {})
    role_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(role.get('role', 'analyst'))} · {esc(role.get('stance', 'caution'))}</span>"
        f"<h2>{esc(role.get('finding', ''))}</h2>"
        f"<p>{esc(role.get('beginner_translation', ''))}</p>"
        f"<small>{esc(role.get('next_check', ''))}</small>"
        "</article>"
        for role in payload.get("roles", [])
    )
    disagreements = "".join(
        "<article class='card warn'>"
        f"<span>{esc(item.get('type', 'disagreement'))}</span>"
        f"<h2>{esc(item.get('title', ''))}</h2>"
        f"<p>{esc(item.get('why_it_matters', ''))}</p>"
        "</article>"
        for item in payload.get("disagreement", [])
    ) or "<p>큰 관점 충돌은 없습니다. 그래도 초보자는 결론보다 조건을 먼저 읽습니다.</p>"
    blockers = "".join(
        "<article class='card block'>"
        f"<span>{esc(item.get('severity', 'medium'))}</span>"
        f"<h2>{esc(item.get('title', ''))}</h2>"
        f"<p>{esc(item.get('evidence', ''))}</p>"
        f"<small>{esc(item.get('local_next_action', ''))}</small>"
        "</article>"
        for item in payload.get("blockers", [])
    ) or "<p>오늘 브리프 읽기를 막는 high blocker는 없습니다.</p>"
    reading_order = "".join(f"<li>{esc(item)}</li>" for item in payload.get("beginner_reading_order", []))
    questions = "".join(f"<li>{esc(item)}</li>" for item in payload.get("next_questions", []))
    commands = "".join(
        "<article class='command'>"
        f"<span>{esc(command.get('label', '응답'))}</span>"
        f"<code>{esc(command.get('command', ''))}</code>"
        f"<small>{esc(command.get('why', ''))}</small>"
        "</article>"
        for command in payload.get("copy_ready_commands", [])
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("linked_surfaces", {}).items()
        if path
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Analyst Council</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; --block:#9f2f2f; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:28px 0 16px; }}
.eyebrow,.card span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small,li {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.card {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics,.grid,.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.metric,.card,.links a {{ background:white; border:1px solid var(--line); border-radius:8px; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:26px; }}
.command {{ border:1px solid var(--line); border-radius:8px; background:white; padding:14px; margin-top:10px; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.warn {{ border-color:#d7b36a; }}
.block {{ border-color:#d99; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.grid,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Council · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>오늘 브리프 읽기 전 analyst council</h1>
<p>여러 역할이 같은 산출물을 읽고, 초보자가 무엇을 믿고 무엇을 조심해야 하는지 합의/충돌/블로커로 정리합니다.</p>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<h2>{esc(decision.get('title', payload.get('status', 'read_with_caution')))}</h2>
<p>{esc(decision.get('rationale', ''))}</p>
<div class="metrics">
<article class="metric"><span>Roles</span><strong>{esc(summary.get('role_count', 0))}</strong></article>
<article class="metric"><span>Agree</span><strong>{esc(summary.get('agreement_count', 0))}</strong></article>
<article class="metric"><span>Caution</span><strong>{esc(summary.get('caution_count', 0))}</strong></article>
<article class="metric"><span>Blockers</span><strong>{esc(summary.get('blocker_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>역할별 검토</h2>
<div class="grid">{role_cards}</div>
</section>
<section class="section">
<h2>관점 충돌</h2>
<div class="grid">{disagreements}</div>
</section>
<section class="section">
<h2>블로커</h2>
<div class="grid">{blockers}</div>
</section>
<section class="section">
<h2>초보자 읽기 순서</h2>
<ol>{reading_order}</ol>
</section>
<section class="section">
<h2>다음 질문</h2>
<ul>{questions}</ul>
</section>
<section class="section">
<h2>복사 가능한 council 응답</h2>
{commands}
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 council은 로컬 산출물만 읽습니다. live network, 알림 전송, host write, credential, 계좌 접근, 주문 실행, 일임 판단을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def _analyst_council_roles(
    *,
    scenario: dict[str, Any],
    verdict: dict[str, Any],
    journal: dict[str, Any],
    memory: dict[str, Any],
    evidence: dict[str, Any],
    memory_audit: dict[str, Any],
    scout: dict[str, Any],
) -> list[dict[str, Any]]:
    source_rows = evidence.get("source_status", [])
    weak_rows = [
        row for row in source_rows
        if row.get("freshness_status") in {"stale", "unknown"} or row.get("relevance_label") in {"weak", "unscored"}
    ]
    fallback_rows = [row for row in source_rows if "fallback" in str(row.get("freshness_status", ""))]
    memory_topics = memory.get("topics", [])
    changed_topics = [topic for topic in memory_topics if topic.get("changed_since_previous")]
    audit_summary = memory_audit.get("summary", {})
    audit_risks = memory_audit.get("risks", [])
    high_or_medium_risks = [risk for risk in audit_risks if risk.get("severity") in {"high", "medium"}]
    primary = verdict.get("primary_next_step", {})
    scenarios = scenario.get("scenarios", [])
    market_map = scenario.get("market_map", {})
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    role_notes = {note.get("role"): note for note in journal.get("role_notes", [])}
    source_confidence = max(0.35, min(0.95, 0.9 - (0.12 * len(weak_rows)) - (0.06 * len(fallback_rows))))
    scenario_confidence = float(primary.get("confidence", 0.65) or 0.65)
    memory_confidence = max(0.35, min(0.95, 0.78 + (0.02 * int(audit_summary.get("run_count", 0) or 0)) - (0.12 * len(high_or_medium_risks))))
    return [
        {
            "role": "source_scout",
            "stance": "caution" if weak_rows or fallback_rows else "agree",
            "finding": f"{len(source_rows)}개 source 중 {len(weak_rows)}개는 약하거나 오래됐고 {len(fallback_rows)}개는 fallback 상태입니다.",
            "confidence": round(source_confidence, 2),
            "evidence": [row.get("source_name", row.get("source_id", "")) for row in source_rows][:5],
            "beginner_translation": "근거가 강해 보여도 live 실패 후 sample/cache로 대체된 항목은 오늘 결론의 강도를 낮춰 읽어야 합니다.",
            "next_check": "source-refresh 화면에서 어떤 원천이 실제 최신인지와 어떤 원천이 승인 대기인지 확인합니다.",
        },
        {
            "role": "evidence_curator",
            "stance": "caution" if evidence.get("collection_gaps") or weak_rows else "agree",
            "finding": f"수집 gap {len(evidence.get('collection_gaps', []))}개와 evidence item {len(evidence.get('items', []))}개를 확인했습니다.",
            "confidence": round(max(0.4, source_confidence - (0.05 * len(evidence.get("collection_gaps", [])))), 2),
            "evidence": [_gap_label(gap) for gap in evidence.get("collection_gaps", [])][:5],
            "beginner_translation": "자료가 비어 있거나 중복이면 같은 뉴스가 여러 번 보이는 착시가 생길 수 있습니다.",
            "next_check": "오늘 브리프의 핵심 문장마다 어떤 source가 받치는지 하나씩 연결합니다.",
        },
        {
            "role": "market_mapper",
            "stance": "agree" if market_map.get("beginner_summary") else "caution",
            "finding": market_map.get("beginner_summary", role_notes.get("market_mapper", {}).get("finding", "시장 지도 요약이 약합니다.")),
            "confidence": round(min(0.9, 0.62 + (0.05 * len(scenario.get("relationships", [])))), 2),
            "evidence": [item.get("label", item.get("source", "")) for item in scenario.get("market_map", {}).get("nodes", [])][:5],
            "beginner_translation": "시장 흐름은 한 가지 사건이 아니라 주제, 기업, 지표, 리스크가 연결된 지도처럼 읽어야 합니다.",
            "next_check": "가장 중요한 연결 하나와 그 연결이 깨지는 조건 하나를 적습니다.",
        },
        {
            "role": "scenario_analyst",
            "stance": "agree" if len(scenarios) >= 3 and scenario_confidence >= 0.65 else "caution",
            "finding": f"{len(scenarios)}개 경로와 primary next step confidence {scenario_confidence:.2f}를 확인했습니다.",
            "confidence": round(max(0.4, min(0.94, scenario_confidence)), 2),
            "evidence": [item.get("title", item.get("name", "")) for item in scenarios][:5],
            "beginner_translation": "좋은 브리프는 한 방향 예측이 아니라 기본/긍정/부정 경로를 같이 보여줘야 합니다.",
            "next_check": "각 경로에서 무엇이 사실이면 맞고, 무엇이 나오면 틀리는지 확인합니다.",
        },
        {
            "role": "skeptic",
            "stance": "block" if high_or_medium_risks else ("caution" if audit_risks else "agree"),
            "finding": f"memory audit risk {len(audit_risks)}개 중 high/medium {len(high_or_medium_risks)}개를 확인했습니다.",
            "confidence": round(max(0.45, 0.86 - (0.14 * len(high_or_medium_risks)) - (0.03 * len(audit_risks))), 2),
            "evidence": [risk.get("risk_id", "") for risk in audit_risks][:5],
            "beginner_translation": "근거가 부족한 상태에서는 결론을 키우지 말고 질문을 키워야 합니다.",
            "next_check": "memory-audit의 risk를 먼저 읽고 오늘 결론을 얼마나 약하게 봐야 할지 정합니다.",
        },
        {
            "role": "beginner_tutor",
            "stance": "agree" if primary.get("action_type") in {"learn", "observe", "defer", "watchlist"} else "caution",
            "finding": primary.get("title", recommended.get("name", "오늘 먼저 배울 주제")),
            "confidence": round(max(0.45, min(0.92, scenario_confidence - 0.04)), 2),
            "evidence": primary.get("evidence", [])[:5],
            "beginner_translation": primary.get("rationale", "오늘은 실행보다 시장 흐름 이해와 질문 정리를 우선합니다."),
            "next_check": "오늘 브리프를 읽고 review-prompt의 한 줄 피드백을 남깁니다.",
        },
        {
            "role": "memory_librarian",
            "stance": "caution" if not changed_topics or int(audit_summary.get("review_response_count", 0) or 0) == 0 else "agree",
            "finding": f"누적 실행 {memory.get('run_count', 0)}회, vault note {audit_summary.get('vault_note_count', 0)}개, changed topic {len(changed_topics)}개입니다.",
            "confidence": round(memory_confidence, 2),
            "evidence": [topic.get("name", "") for topic in memory_topics[:5]],
            "beginner_translation": "개인 애널리스트는 새 정보보다 누적 기억이 틀어지는 순간을 먼저 잡아야 합니다.",
            "next_check": "오늘 읽은 뒤 다음 run에 반영할 피드백을 review-response-apply로 남깁니다.",
        },
    ]


def _analyst_council_blockers(
    *,
    roles: list[dict[str, Any]],
    memory_audit: dict[str, Any],
    evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for risk in memory_audit.get("risks", []):
        if risk.get("severity") in {"high", "medium"}:
            blockers.append({
                "severity": risk.get("severity", "medium"),
                "title": risk.get("title", ""),
                "evidence": risk.get("evidence", ""),
                "local_next_action": risk.get("recommended_local_action", ""),
            })
    if not evidence.get("source_status"):
        blockers.append({
            "severity": "medium",
            "title": "source status가 없어 council이 근거 강도를 판단할 수 없습니다",
            "evidence": "source_status is empty",
            "local_next_action": "appliance run 또는 collect-evidence를 다시 실행합니다.",
        })
    if any(role.get("stance") == "block" for role in roles) and not blockers:
        blockers.append({
            "severity": "medium",
            "title": "하나 이상의 역할이 block stance를 냈습니다",
            "evidence": ", ".join(role.get("role", "") for role in roles if role.get("stance") == "block"),
            "local_next_action": "해당 역할 카드의 next_check를 먼저 확인합니다.",
        })
    return blockers


def _analyst_council_disagreement(*, roles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    agreement = [role for role in roles if role.get("stance") == "agree"]
    caution = [role for role in roles if role.get("stance") == "caution"]
    blocked = [role for role in roles if role.get("stance") == "block"]
    items: list[dict[str, Any]] = []
    if agreement and caution:
        items.append({
            "type": "confidence_split",
            "title": f"{len(agreement)}개 역할은 읽기 가능, {len(caution)}개 역할은 주의 필요",
            "why_it_matters": "초보자는 agree 카드보다 caution 카드의 조건을 먼저 읽어야 과신을 줄일 수 있습니다.",
        })
    if blocked:
        items.append({
            "type": "blocker_present",
            "title": f"{len(blocked)}개 역할이 읽기 전 보완을 요구합니다",
            "why_it_matters": "블로커가 있으면 오늘 브리프는 결론보다 보완 작업으로 처리해야 합니다.",
        })
    return items


def _analyst_council_decision(
    *,
    roles: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
    disagreement: list[dict[str, Any]],
) -> dict[str, Any]:
    if any(blocker.get("severity") == "high" for blocker in blockers):
        return {
            "status": "blocked",
            "title": "오늘 브리프는 보완 전까지 읽기 보류",
            "rationale": "high blocker가 있어 근거나 기억 품질을 먼저 보완해야 합니다.",
            "operator_action": "blocker의 local_next_action을 수행한 뒤 appliance run을 다시 실행합니다.",
        }
    if blockers or disagreement or any(role.get("stance") == "caution" for role in roles):
        return {
            "status": "read_with_caution",
            "title": "오늘 브리프는 읽되 조건을 먼저 확인",
            "rationale": "읽기를 막는 high blocker는 없지만 source, memory, scenario 중 일부가 주의 상태입니다.",
            "operator_action": "역할별 caution 카드와 다음 질문을 먼저 읽고 review-response-apply로 피드백을 남깁니다.",
        }
    return {
        "status": "ready_to_read",
        "title": "오늘 브리프 읽기 가능",
        "rationale": "역할별 검토에서 큰 충돌이나 blocker가 보이지 않습니다.",
        "operator_action": "today와 market brief를 읽고 핵심 질문 하나를 vault나 review에 남깁니다.",
    }


def _analyst_council_reading_order(*, decision: dict[str, Any], roles: list[dict[str, Any]]) -> list[str]:
    caution_roles = [role.get("role", "") for role in roles if role.get("stance") in {"caution", "block"}]
    order = [
        f"판정: {decision.get('title', '')}",
        "skeptic과 source_scout 카드에서 근거 약점을 먼저 확인",
        "scenario_analyst 카드에서 base/upside/downside 경로를 비교",
        "beginner_tutor 카드의 쉬운 설명을 읽고 오늘 질문 하나를 고르기",
        "review-prompt 또는 review-response-apply로 실제 피드백 남기기",
    ]
    if caution_roles:
        order.insert(1, f"주의 역할 먼저 읽기: {', '.join(caution_roles)}")
    return order


def _analyst_council_next_questions(
    *,
    roles: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
    journal: dict[str, Any],
    memory_audit: dict[str, Any],
) -> list[str]:
    questions = []
    if blockers:
        questions.append("오늘 브리프를 읽기 전에 어떤 blocker를 로컬에서 먼저 해소해야 하나?")
    questions.extend(journal.get("follow_up_questions", [])[:2])
    questions.extend(memory_audit.get("next_questions", [])[:2])
    caution_roles = [role for role in roles if role.get("stance") in {"caution", "block"}]
    for role in caution_roles[:2]:
        questions.append(f"{role.get('role')}가 지적한 약점은 오늘 결론의 강도를 얼마나 낮추는가?")
    if not questions:
        questions.append("오늘 브리프에서 내가 내일 다시 확인하고 싶은 한 문장은 무엇인가?")
    return questions[:5]


def _analyst_council_commands(
    *,
    decision: dict[str, Any],
    roles: list[dict[str, Any]],
    scout: dict[str, Any],
    journal: dict[str, Any],
) -> list[dict[str, Any]]:
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    focus = journal.get("today_focus", {}) if journal.get("schema_version") == ANALYST_JOURNAL_SCHEMA_VERSION else {}
    topic = recommended.get("name", focus.get("recommended_topic", focus.get("title", "오늘 브리프")))
    caution_roles = [role for role in roles if role.get("stance") in {"caution", "block"}]
    first_caution = caution_roles[0] if caution_roles else {}
    caution_note = first_caution.get("next_check", decision.get("operator_action", "조건을 먼저 확인한다"))
    response_more = f'more "{topic}" "council: {caution_note}"'
    response_confusing = f'confusing "{topic}" "council: 설명과 근거를 더 쉽게 다시 보고 싶다"'
    commands = [
        {
            "label": "조건 확인 후 계속 보기",
            "response": response_more,
            "command": f"PYTHONPATH=src python3 -m mybroker appliance council-response-apply {shlex.quote(response_more)}",
            "why": "council caution을 다음 scout와 review-effect에 반영합니다.",
            "external_effect_performed": False,
        },
        {
            "label": "헷갈림 표시",
            "response": response_confusing,
            "command": f"PYTHONPATH=src python3 -m mybroker appliance council-response-apply {shlex.quote(response_confusing)}",
            "why": "다음 run에서 더 쉬운 설명과 추가 근거가 필요하다는 신호를 남깁니다.",
            "external_effect_performed": False,
        },
    ]
    if decision.get("status") == "ready_to_read":
        response_read = f'read "{topic}" "council: 오늘 브리프를 읽었다"'
        commands.insert(0, {
            "label": "읽었음",
            "response": response_read,
            "command": f"PYTHONPATH=src python3 -m mybroker appliance council-response-apply {shlex.quote(response_read)}",
            "why": "오늘 브리프를 읽었다는 최소 피드백을 남깁니다.",
            "external_effect_performed": False,
        })
    return commands[:3]


def write_operator_council_response_apply(
    *,
    payload: dict[str, Any],
    artifact_output_path: str | Path = DEFAULT_COUNCIL_RESPONSE_APPLY_OUTPUT,
    surface_output_path: str | Path = DEFAULT_COUNCIL_RESPONSE_APPLY_SURFACE,
) -> Path:
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_operator_council_response_apply(payload), encoding="utf-8")
    return target


def validate_operator_council_response_apply_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != OPERATOR_COUNCIL_RESPONSE_APPLY_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"applied", "blocked"}:
        errors.append("status must be applied or blocked")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if "local_council_response_apply_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include local_council_response_apply_only")
    for field in ["operator_response", "responses_path", "daily_review", "daily_scout", "review_effect", "analyst_council"]:
        if field not in payload:
            errors.append(f"missing {field}")
    council = payload.get("analyst_council", {})
    if council.get("status") not in {"ready_to_read", "read_with_caution", "blocked"}:
        errors.append("analyst_council.status is invalid")
    if not payload.get("next_action"):
        errors.append("next_action must not be empty")
    return errors


def validate_operator_council_response_apply_file(path: str | Path) -> list[str]:
    return validate_operator_council_response_apply_payload(load_json(path))


def render_operator_council_response_apply(payload: dict[str, Any]) -> str:
    council = payload.get("analyst_council", {})
    effect = payload.get("review_effect", {})
    review = payload.get("daily_review", {})
    scout = payload.get("daily_scout", {})
    status_label = {
        "applied": "council 응답 적용됨",
        "blocked": "council 응답 적용 차단됨",
    }.get(payload.get("status", ""), payload.get("status", "unknown"))
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Council Response Apply</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow,.metric span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small {{ color:var(--muted); }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics,.links {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:24px; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Council Apply · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>council 응답 적용</h1>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('next_action', ''))}</p>
<code>{esc(payload.get('operator_response', ''))}</code>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Review responses</span><strong>{esc(review.get('response_count', 0))}</strong></article>
<article class="metric"><span>Scout read</span><strong>{esc(scout.get('review_response_count', 0))}</strong></article>
<article class="metric"><span>Council</span><strong>{esc(council.get('status', 'unknown'))}</strong></article>
<article class="metric"><span>Effect</span><strong>{esc(effect.get('status', 'unknown'))}</strong></article>
</div>
</section>
<section class="section">
<h2>갱신된 화면</h2>
<div class="links">
<a href="{esc(_relative_href(DEFAULT_DAILY_REVIEW_SURFACE))}">review</a>
<a href="{esc(_relative_href(DEFAULT_REVIEW_EFFECT_SURFACE))}">review_effect</a>
<a href="{esc(_relative_href(DEFAULT_ANALYST_COUNCIL_SURFACE))}">council</a>
</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 handoff는 로컬 피드백과 로컬 proof만 갱신합니다. live network, 알림 전송, host write, credential, 계좌 접근, 주문 실행을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_analyst_journal(payload: dict[str, Any]) -> str:
    focus = payload.get("today_focus", {})
    changed_cards = "".join(
        "<article class='card'>"
        f"<span>변화 감지</span>"
        f"<h3>{esc(item.get('name', ''))}</h3>"
        f"<p>{esc(item.get('summary', ''))}</p>"
        f"<small>{esc(' · '.join(item.get('latest_titles', [])[:3]))}</small>"
        "</article>"
        for item in payload.get("what_changed", [])
    ) or "<p>오늘 새 변화로 판정된 주제는 없습니다. 그래서 결론보다 source freshness와 반복 관찰을 우선합니다.</p>"
    stable_cards = "".join(
        "<article class='card'>"
        f"<span>반복 관찰</span>"
        f"<h3>{esc(item.get('name', ''))}</h3>"
        f"<p>{esc(item.get('summary', ''))}</p>"
        "</article>"
        for item in payload.get("stable_observations", [])[:4]
    ) or "<p>아직 반복 관찰이 충분하지 않습니다.</p>"
    role_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(note.get('role', 'analyst'))}</span>"
        f"<h3>{esc(note.get('finding', ''))}</h3>"
        f"<p>{esc(note.get('next_check', ''))}</p>"
        "</article>"
        for note in payload.get("role_notes", [])
    )
    questions = "".join(f"<li>{esc(question)}</li>" for question in payload.get("follow_up_questions", []))
    artifacts = payload.get("linked_artifacts", {})
    artifact_links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in artifacts.items()
        if path and label != "archive_dir"
    )
    source = payload.get("source_posture", {})
    gaps = "".join(f"<li>{esc(_gap_label(gap))}</li>" for gap in source.get("collection_gaps", [])) or "<li>기록된 자료 수집 gap 없음</li>"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Analyst Journal</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:28px 0 16px; }}
.eyebrow,.card span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p,small,li {{ color:var(--muted); }}
.hero,.section,.card {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero {{ padding:18px; }}
.section {{ margin:14px 0; padding:16px; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.card {{ background:white; padding:14px; min-width:0; }}
.card h3,.card p,.card small {{ overflow-wrap:anywhere; }}
.metrics {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; margin-top:12px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .grid,.metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Analyst Journal · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>오늘의 개인 애널리스트 작업일지</h1>
<p>브리프의 결론보다, 무엇을 봤고 무엇이 아직 약한지 매일 누적하는 로컬 기록입니다.</p>
</header>
<section class="hero">
<span class="eyebrow">오늘의 초점</span>
<h2>{esc(focus.get('title', '오늘 먼저 볼 주제'))}</h2>
<p>{esc(focus.get('rationale', ''))}</p>
<div class="metrics">
<article class="metric"><span>Status</span><strong>{esc(payload.get('status', 'review'))}</strong></article>
<article class="metric"><span>Sources</span><strong>{esc(source.get('source_count', 0))}</strong></article>
<article class="metric"><span>Weak</span><strong>{esc(source.get('weak_or_stale_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>오늘 바뀐 것</h2>
<div class="grid">{changed_cards}</div>
</section>
<section class="section">
<h2>계속 관찰 중인 것</h2>
<div class="grid">{stable_cards}</div>
</section>
<section class="section">
<h2>역할별 메모</h2>
<div class="grid">{role_cards}</div>
</section>
<section class="section">
<h2>내일 이어서 물어볼 질문</h2>
<ul>{questions}</ul>
</section>
<section class="section">
<h2>자료 gap</h2>
<ul>{gaps}</ul>
</section>
<section class="section">
<h2>연결된 산출물</h2>
<div class="links">{artifact_links}</div>
</section>
<section class="section">
<h2>다음 작업 큐</h2>
<div class="links"><a href="tasks.html">내일 이어갈 analyst tasks</a></div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>교육과 리서치, 시뮬레이션용 기록입니다. 계좌 접근, 주문 실행, 일임 운용, 근거 없는 개인화 추천을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_learning_ledger(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    lesson = payload.get("today_lesson", {})
    source = payload.get("source_posture", {})
    concepts = "".join(
        "<article class='card'>"
        f"<span>{esc(card.get('kind', 'concept'))}</span>"
        f"<h3>{esc(card.get('title', ''))}</h3>"
        f"<p>{esc(card.get('explanation', ''))}</p>"
        f"<small>{esc(card.get('why_beginner_cares', ''))}</small>"
        "</article>"
        for card in payload.get("concept_cards", [])
    )
    changed_cards = "".join(
        "<article class='card'>"
        f"<span>새 변화</span>"
        f"<h3>{esc(topic.get('name', ''))}</h3>"
        f"<p>{esc(topic.get('summary', ''))}</p>"
        f"<small>{esc(' · '.join(topic.get('latest_titles', [])[:3]))}</small>"
        "</article>"
        for topic in payload.get("memory_compounding", {}).get("changed_topics", [])
    ) or "<p>오늘 새 변화로 판정된 주제는 없습니다. 반복 관찰을 먼저 읽습니다.</p>"
    repeated_cards = "".join(
        "<article class='card'>"
        f"<span>반복 관찰</span>"
        f"<h3>{esc(topic.get('name', ''))}</h3>"
        f"<p>{esc(topic.get('summary', ''))}</p>"
        f"<small>{esc(' · '.join(topic.get('source_names', [])[:4]))}</small>"
        "</article>"
        for topic in payload.get("memory_compounding", {}).get("repeated_topics", [])
    ) or "<p>아직 반복 관찰이 충분하지 않습니다.</p>"
    study_steps = "".join(
        "<article class='card'>"
        f"<span>Step {esc(step.get('step', ''))}</span>"
        f"<h3>{esc(step.get('title', ''))}</h3>"
        f"<p>{esc(step.get('why', ''))}</p>"
        f"<small>{esc(step.get('stop_condition', ''))}</small>"
        "</article>"
        for step in payload.get("study_path", [])
    )
    questions = "".join(f"<li>{esc(question)}</li>" for question in payload.get("questions_to_carry", []))
    gaps = "".join(f"<li>{esc(_gap_label(gap))}</li>" for gap in source.get("collection_gaps", [])) or "<li>기록된 자료 수집 gap 없음</li>"
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if path
    )
    artifacts = payload.get("linked_artifacts", {})
    artifact_links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in artifacts.items()
        if isinstance(path, str) and path and label != "archive_root"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Learning Ledger</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --amber:#94630c; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:28px 0 16px; }}
.eyebrow,.card span,.metric span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p,small,li {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.card {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero {{ padding:18px; }}
.section {{ margin:14px 0; padding:16px; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.card {{ background:white; padding:14px; min-width:0; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin-top:12px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; overflow-wrap:anywhere; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .grid,.metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Learning Ledger · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>오늘 배운 것의 누적 원장</h1>
<p>매일 브리프에서 배운 개념, 반복되는 관찰, 아직 모르는 질문을 한 화면에 남깁니다.</p>
</header>
<section class="hero">
<span class="eyebrow">오늘의 학습 문장</span>
<h2>{esc(lesson.get('headline', '오늘 먼저 배울 것'))}</h2>
<p>{esc(lesson.get('why_it_matters', ''))}</p>
<p><strong>{esc(lesson.get('beginner_rule', '결론보다 학습을 먼저 남깁니다.'))}</strong></p>
<div class="metrics">
<article class="metric"><span>Runs</span><strong>{esc(summary.get('run_count', 0))}</strong></article>
<article class="metric"><span>Concepts</span><strong>{esc(summary.get('concept_count', 0))}</strong></article>
<article class="metric"><span>Questions</span><strong>{esc(summary.get('question_count', 0))}</strong></article>
<article class="metric"><span>Gaps</span><strong>{esc(summary.get('source_gap_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>초보자가 오늘 익힐 개념</h2>
<div class="grid">{concepts}</div>
</section>
<section class="section">
<h2>오늘 새로 바뀐 것</h2>
<div class="grid">{changed_cards}</div>
</section>
<section class="section">
<h2>계속 반복 관찰되는 것</h2>
<div class="grid">{repeated_cards}</div>
</section>
<section class="section">
<h2>오늘 읽는 순서</h2>
<div class="grid">{study_steps}</div>
</section>
<section class="section">
<h2>내일 이어갈 질문</h2>
<ul>{questions}</ul>
</section>
<section class="section">
<h2>자료 gap</h2>
<ul>{gaps}</ul>
</section>
<section class="section">
<h2>바로 이어서 열기</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>연결된 산출물</h2>
<div class="links">{artifact_links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>교육과 리서치, 시뮬레이션용 누적 기록입니다. 계좌 접근, 주문 실행, 일임 운용, 근거 없는 개인화 추천을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def build_analyst_task_queue(
    *,
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    journal = load_json(journal_path)
    memory = load_json(memory_path) if Path(memory_path).exists() else {}
    evidence = load_json(evidence_path) if Path(evidence_path).exists() else {}
    scout = load_json(scout_path) if Path(scout_path).exists() else {}
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    source_posture = journal.get("source_posture", {})
    questions = journal.get("follow_up_questions", [])
    collection_gaps = source_posture.get("collection_gaps", evidence.get("collection_gaps", []))
    weak_count = int(source_posture.get("weak_or_stale_count", 0) or 0)
    task_specs = [
        {
            "role": "source_scout",
            "title": "자료 신선도와 부족한 근거를 먼저 확인",
            "why": _task_source_scout_why(collection_gaps=collection_gaps, weak_count=weak_count),
            "priority": "high" if collection_gaps or weak_count else "medium",
            "inputs": ["reports/evidence/daily-evidence-catalog.json", "reports/daily/source-refresh-plan.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker source-refresh-plan",
            "approval_scope": "local_dry_run_only",
        },
        {
            "role": "market_mapper",
            "title": "오늘 초점 주제를 시장 지도에 다시 연결",
            "why": recommended.get("why", journal.get("today_focus", {}).get("rationale", "오늘 초점과 시장 지도 연결을 점검합니다.")),
            "priority": "high",
            "inputs": ["reports/scenarios/daily-research-sim.json", "reports/scenarios/daily-research-verdict.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance today",
            "approval_scope": "local_render_only",
        },
        {
            "role": "skeptic",
            "title": "가장 약한 결론을 반대 근거로 공격",
            "why": _task_skeptic_why(journal=journal),
            "priority": "high",
            "inputs": ["reports/memory/analyst-journal.json", "reports/evidence/daily-evidence-catalog.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance journal",
            "approval_scope": "local_render_only",
        },
        {
            "role": "beginner_tutor",
            "title": "초보자가 이해할 질문 하나를 쉬운 언어로 풀기",
            "why": questions[0] if questions else "오늘 브리프를 처음 보는 사용자가 이해할 출발 질문을 만듭니다.",
            "priority": "medium",
            "inputs": ["reports/product/today.html", "reports/product/journal.html"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance query \"오늘 먼저 볼 주제\"",
            "approval_scope": "local_query_only",
        },
        {
            "role": "memory_librarian",
            "title": "내일 다시 찾을 수 있게 질문과 원천을 정리",
            "why": f"누적 실행 {memory.get('run_count', 0)}회를 다음 질문과 연결합니다.",
            "priority": "medium",
            "inputs": ["reports/memory/topic-memory.json", "reports/vault/compile.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance memory",
            "approval_scope": "local_render_only",
        },
        {
            "role": "publisher",
            "title": "폰에서 볼 표면과 dry-run 알림 상태 점검",
            "why": "오늘 산출물이 폰에서 읽히고 notification은 dry-run 상태인지 확인합니다.",
            "priority": "medium",
            "inputs": ["reports/product/today.html", "reports/product/tasks.html", "reports/notifications/latest.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance notify --dry-run",
            "approval_scope": "local_dry_run_only",
        },
    ]
    tasks = []
    for index, spec in enumerate(task_specs, start=1):
        tasks.append({
            "task_id": f"AT-{index:03d}",
            "role": spec["role"],
            "title": spec["title"],
            "why": spec["why"],
            "priority": spec["priority"],
            "status": "queued",
            "autonomy_level": "autonomous_local",
            "approval_scope": spec["approval_scope"],
            "external_effect_allowed": False,
            "requires_operator_approval": False,
            "inputs": spec["inputs"],
            "suggested_command": spec["suggested_command"],
            "stop_condition": "write_or_refresh_local_artifact_without_external_effect",
        })
    live_task = _maybe_live_refresh_task(journal=journal)
    if live_task:
        tasks.append(live_task)
    payload = {
        "schema_version": ANALYST_TASK_QUEUE_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "run_id": journal.get("run_id", ""),
        "status": "queued",
        "source_journal": Path(journal_path).as_posix(),
        "task_count": len(tasks),
        "tasks": tasks,
        "reading_order": ["high priority", "source_scout", "skeptic", "market_mapper", "beginner_tutor", "memory_librarian", "publisher"],
        "policy": "research_only",
        "safety_boundary": [
            "queued_tasks_do_not_execute",
            "no_account_access",
            "no_live_trading",
            "no_discretionary_management",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_analyst_task_queue(
    *,
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    surface_output_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_OUTPUT,
) -> Path:
    payload = build_analyst_task_queue(
        journal_path=journal_path,
        memory_path=memory_path,
        evidence_path=evidence_path,
        scout_path=scout_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_analyst_task_queue(payload), encoding="utf-8")
    return target


def validate_analyst_task_queue_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != ANALYST_TASK_QUEUE_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    tasks = payload.get("tasks", [])
    if not tasks:
        errors.append("tasks must not be empty")
    for index, task in enumerate(tasks):
        for field in ["task_id", "role", "title", "why", "priority", "status", "approval_scope", "external_effect_allowed", "inputs", "suggested_command"]:
            if field not in task:
                errors.append(f"tasks[{index}] missing {field}")
        if task.get("status") != "queued":
            errors.append(f"tasks[{index}] status must be queued")
        if task.get("external_effect_allowed") is True and task.get("requires_operator_approval") is not True:
            errors.append(f"tasks[{index}] external effects require operator approval")
    if "queued_tasks_do_not_execute" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include queued_tasks_do_not_execute")
    return errors


def validate_analyst_task_queue_file(path: str | Path) -> list[str]:
    return validate_analyst_task_queue_payload(load_json(path))


def render_analyst_task_queue(payload: dict[str, Any]) -> str:
    high_count = sum(1 for task in payload.get("tasks", []) if task.get("priority") == "high")
    task_cards = "".join(
        "<article class='task'>"
        f"<span>{esc(task.get('task_id', ''))} · {esc(task.get('role', ''))} · {esc(task.get('priority', ''))}</span>"
        f"<h2>{esc(task.get('title', ''))}</h2>"
        f"<p>{esc(task.get('why', ''))}</p>"
        f"<small>scope: {esc(task.get('approval_scope', ''))} · external effect: {esc('yes' if task.get('external_effect_allowed') else 'no')}</small>"
        f"<code>{esc(task.get('suggested_command', ''))}</code>"
        "</article>"
        for task in payload.get("tasks", [])
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Analyst Tasks</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
.eyebrow,.task span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.task {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.metric,.task {{ background:white; padding:14px; }}
.metric strong {{ display:block; font-size:24px; }}
.stack {{ display:grid; grid-template-columns:1fr; gap:10px; }}
code {{ display:block; margin-top:10px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Analyst Tasks · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>내일 이어갈 analyst 작업 큐</h1>
<p>실행 명령이 아니라, 로컬 개인 애널리스트가 다음에 처리할 역할별 작업 목록입니다.</p>
</header>
<section class="hero">
<div class="metrics">
<article class="metric"><span>Total</span><strong>{esc(payload.get('task_count', 0))}</strong></article>
<article class="metric"><span>High</span><strong>{esc(high_count)}</strong></article>
<article class="metric"><span>Effects</span><strong>0</strong></article>
</div>
</section>
<section class="section">
<h2>역할별 큐</h2>
<div class="stack">{task_cards}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 큐는 작업을 실행하지 않습니다. live network, host write, notification send, 계좌/주문/일임 행위는 별도 승인 게이트 없이는 허용하지 않습니다.</p>
</section>
<section class="section">
<h2>작업 이력</h2>
<p><a href="task-ledger.html">task ledger에서 완료, 이월, 보류 상태 보기</a></p>
</section>
</main>
</body>
</html>
"""


def build_analyst_task_ledger(
    *,
    task_queue_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    previous_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    status_apply_path: str | Path | None = DEFAULT_ANALYST_TASK_STATUS_APPLY,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    queue = load_json(task_queue_path)
    previous = load_json(previous_ledger_path) if Path(previous_ledger_path).exists() else {}
    status_apply = load_json(status_apply_path) if status_apply_path and Path(status_apply_path).exists() else {}
    overrides = _task_status_overrides(status_apply)
    generated = (generated_at or datetime.now(timezone.utc)).isoformat()
    previous_entries = previous.get("entries", []) if previous.get("schema_version") == ANALYST_TASK_LEDGER_SCHEMA_VERSION else []
    previous_by_fingerprint = {
        entry.get("fingerprint", ""): entry
        for entry in previous_entries
        if entry.get("fingerprint")
    }
    current_entries = []
    for task in queue.get("tasks", []):
        fingerprint = _task_fingerprint(task)
        prior = previous_by_fingerprint.get(fingerprint, {})
        override = overrides.get(task.get("task_id", ""))
        completion = _local_task_completion_evidence(task=task, task_queue_path=task_queue_path)
        status = override.get("status") if override else _ledger_status_for_task(task=task, prior=prior, completion=completion)
        current_entries.append({
            "ledger_id": f"{queue.get('run_id', 'daily')}-{task.get('task_id', '')}",
            "task_id": task.get("task_id", ""),
            "fingerprint": fingerprint,
            "role": task.get("role", ""),
            "title": task.get("title", ""),
            "priority": task.get("priority", ""),
            "status": status,
            "previous_status": prior.get("status", ""),
            "first_seen_at": prior.get("first_seen_at", generated),
            "last_seen_at": generated,
            "run_id": queue.get("run_id", ""),
            "approval_scope": task.get("approval_scope", ""),
            "external_effect_allowed": bool(task.get("external_effect_allowed")),
            "requires_operator_approval": bool(task.get("requires_operator_approval")),
            "suggested_command": task.get("suggested_command", ""),
            "stop_condition": task.get("stop_condition", ""),
            "operator_note": override.get("note") if override and override.get("note") else _ledger_note_for_task(task=task, status=status, completion=completion),
            "operator_override": override or {},
            "local_completion": completion,
        })
    current_fingerprints = {entry["fingerprint"] for entry in current_entries}
    retired_entries = []
    for entry in previous_entries:
        if entry.get("fingerprint") not in current_fingerprints:
            retired = dict(entry)
            retired["status"] = "retired_not_in_current_queue"
            retired["previous_status"] = entry.get("status", "")
            retired["last_seen_at"] = generated
            retired["operator_note"] = "이전 queue에는 있었지만 현재 queue에는 없습니다. 완료됐는지, 필요 없어졌는지 archive에서 확인하세요."
            retired_entries.append(retired)
    entries = current_entries + retired_entries[:12]
    summary = _ledger_summary(entries)
    return {
        "schema_version": ANALYST_TASK_LEDGER_SCHEMA_VERSION,
        "generated_at": generated,
        "run_id": queue.get("run_id", ""),
        "source_task_queue": Path(task_queue_path).as_posix(),
        "previous_ledger": Path(previous_ledger_path).as_posix() if Path(previous_ledger_path).exists() else "",
        "entry_count": len(entries),
        "summary": summary,
        "entries": entries,
        "policy": "research_only",
        "safety_boundary": [
            "ledger_records_status_only",
            "does_not_execute_tasks",
            "completion_inferred_from_local_artifact_presence_only",
            "no_account_access",
            "no_live_trading",
            "external_effects_require_separate_gate",
        ],
    }


def write_analyst_task_ledger(
    *,
    task_queue_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    previous_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    status_apply_path: str | Path | None = DEFAULT_ANALYST_TASK_STATUS_APPLY,
    artifact_output_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    surface_output_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_OUTPUT,
) -> Path:
    payload = build_analyst_task_ledger(
        task_queue_path=task_queue_path,
        previous_ledger_path=previous_ledger_path,
        status_apply_path=status_apply_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_analyst_task_ledger(payload), encoding="utf-8")
    return target


def parse_task_status_response(response: str) -> dict[str, Any]:
    parts = response.strip().split(maxsplit=2)
    if len(parts) < 2:
        raise ValueError("response must look like: AT-001 complete [note]")
    task_id = parts[0].strip()
    action = parts[1].strip().lower()
    note = parts[2].strip().strip('"') if len(parts) > 2 else ""
    status_map = {
        "complete": "completed",
        "completed": "completed",
        "carry": "carried",
        "carried": "carried",
        "defer": "deferred",
        "deferred": "deferred",
        "block": "blocked_by_operator",
        "blocked": "blocked_by_operator",
    }
    if not task_id.startswith("AT-"):
        raise ValueError("task id must start with AT-")
    if action not in status_map:
        raise ValueError("action must be complete, carry, defer, or block")
    return {
        "schema_version": "personal_analyst_task_response.v1",
        "recorded_at": _now(),
        "task_id": task_id,
        "action": action,
        "status": status_map[action],
        "note": note,
        "external_effect_performed": False,
    }


def record_task_status_response(
    *,
    response: str,
    responses_path: str | Path = DEFAULT_ANALYST_TASK_RESPONSES,
) -> Path:
    payload = parse_task_status_response(response)
    target = Path(responses_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return target


def build_task_status_apply(
    *,
    ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    responses_path: str | Path = DEFAULT_ANALYST_TASK_RESPONSES,
    output_path: str | Path = DEFAULT_ANALYST_TASK_STATUS_APPLY,
) -> dict[str, Any]:
    ledger = load_json(ledger_path)
    responses = _load_task_responses(responses_path)
    valid_task_ids = {entry.get("task_id") for entry in ledger.get("entries", [])}
    applied = []
    ignored = []
    for response in responses:
        task_id = response.get("task_id", "")
        if task_id in valid_task_ids:
            applied.append(response)
        else:
            ignored.append({**response, "reason": "task_id_not_in_current_ledger"})
    latest_by_task: dict[str, dict[str, Any]] = {}
    for response in applied:
        latest_by_task[response["task_id"]] = response
    payload = {
        "schema_version": ANALYST_TASK_STATUS_APPLY_SCHEMA_VERSION,
        "generated_at": _now(),
        "ledger_path": Path(ledger_path).as_posix(),
        "responses_path": Path(responses_path).as_posix(),
        "applied_count": len(latest_by_task),
        "ignored_count": len(ignored),
        "applied": list(latest_by_task.values()),
        "ignored": ignored,
        "external_effect_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "local_status_update_only",
            "does_not_execute_tasks",
            "no_live_trading",
            "no_account_access",
        ],
    }
    write_json(payload, output_path)
    return payload


def parse_daily_review_response(response: str) -> dict[str, Any]:
    try:
        parts = shlex.split(response.strip())
    except ValueError as error:
        raise ValueError(f"response must be shell-quote parseable: {error}") from error
    if len(parts) < 2:
        raise ValueError('response must look like: more "Semiconductors" [note]')
    action = parts[0].strip().lower()
    topic = parts[1].strip()
    note = " ".join(parts[2:]).strip()
    status_map = {
        "read": "reviewed",
        "reviewed": "reviewed",
        "more": "want_more",
        "confusing": "confusing",
        "skip": "skipped",
        "skipped": "skipped",
    }
    if action not in status_map:
        raise ValueError("action must be read, more, confusing, or skip")
    return {
        "schema_version": "daily_review_response.v1",
        "recorded_at": _now(),
        "action": action,
        "status": status_map[action],
        "topic": topic,
        "note": note,
        "external_effect_performed": False,
    }


def record_daily_review_response(
    *,
    response: str,
    responses_path: str | Path = DEFAULT_DAILY_REVIEW_RESPONSES,
) -> Path:
    payload = parse_daily_review_response(response)
    target = Path(responses_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return target


def build_daily_review(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    task_status_apply_path: str | Path = DEFAULT_ANALYST_TASK_STATUS_APPLY,
    responses_path: str | Path = DEFAULT_DAILY_REVIEW_RESPONSES,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scout = load_json(scout_path) if Path(scout_path).exists() else {}
    task_status = load_json(task_status_apply_path) if Path(task_status_apply_path).exists() else {}
    responses = _load_daily_review_responses(responses_path)
    recommendations = scout.get("recommendations", []) if scout.get("schema_version") == "daily_scout.v1" else []
    topic_index = _review_topic_index(recommendations)
    signals_by_topic: dict[str, dict[str, Any]] = {}
    ignored = []
    for response in responses:
        matched = _match_review_topic(response.get("topic", ""), topic_index)
        if not matched:
            ignored.append({**response, "reason": "topic_not_in_current_scout"})
            continue
        topic_id = matched["topic_id"]
        signal = signals_by_topic.setdefault(topic_id, {
            "topic_id": topic_id,
            "name": matched.get("name", response.get("topic", "")),
            "responses": [],
            "score_delta": 0.0,
            "reason": "",
        })
        signal["responses"].append(response)
        signal["score_delta"] = round(float(signal["score_delta"]) + _review_action_delta(response.get("status", "")), 2)
    for signal in signals_by_topic.values():
        signal["response_count"] = len(signal["responses"])
        signal["latest_status"] = signal["responses"][-1].get("status", "")
        signal["latest_note"] = signal["responses"][-1].get("note", "")
        signal["reason"] = _review_signal_reason(signal)
    completed_tasks = [
        row for row in task_status.get("applied", [])
        if row.get("status") == "completed"
    ] if task_status.get("schema_version") == ANALYST_TASK_STATUS_APPLY_SCHEMA_VERSION else []
    payload = {
        "schema_version": DAILY_REVIEW_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "inputs": {
            "scout_path": Path(scout_path).as_posix(),
            "task_status_apply_path": Path(task_status_apply_path).as_posix(),
            "responses_path": Path(responses_path).as_posix(),
        },
        "summary": {
            "response_count": len(responses),
            "applied_response_count": sum(len(signal["responses"]) for signal in signals_by_topic.values()),
            "ignored_response_count": len(ignored),
            "completed_task_count": len(completed_tasks),
            "signal_count": len(signals_by_topic),
        },
        "topic_signals": sorted(signals_by_topic.values(), key=lambda row: (-float(row.get("score_delta", 0)), row.get("name", ""))),
        "ignored_responses": ignored,
        "task_feedback": {
            "completed_task_count": len(completed_tasks),
            "completed_tasks": completed_tasks[:6],
        },
        "external_effect_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "local_review_memory_only",
            "does_not_fetch_live_network",
            "does_not_write_host_scheduler",
            "does_not_send_notification",
        ],
        "next_step": "rerun_daily_scout_with_review_signal",
    }
    return payload


def write_daily_review(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    task_status_apply_path: str | Path = DEFAULT_ANALYST_TASK_STATUS_APPLY,
    responses_path: str | Path = DEFAULT_DAILY_REVIEW_RESPONSES,
    artifact_output_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    surface_output_path: str | Path = DEFAULT_DAILY_REVIEW_SURFACE,
) -> Path:
    payload = build_daily_review(
        scout_path=scout_path,
        task_status_apply_path=task_status_apply_path,
        responses_path=responses_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_daily_review(payload), encoding="utf-8")
    return target


def validate_daily_review_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DAILY_REVIEW_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    summary = payload.get("summary", {})
    for field in ["response_count", "applied_response_count", "ignored_response_count", "completed_task_count", "signal_count"]:
        if field not in summary:
            errors.append(f"summary missing {field}")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    for index, signal in enumerate(payload.get("topic_signals", [])):
        for field in ["topic_id", "name", "score_delta", "reason", "responses"]:
            if field not in signal:
                errors.append(f"topic_signals[{index}] missing {field}")
    return errors


def validate_daily_review_file(path: str | Path) -> list[str]:
    return validate_daily_review_payload(load_json(path))


def render_daily_review(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    signal_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(signal.get('latest_status', 'review'))} · delta {esc(signal.get('score_delta', 0))}</span>"
        f"<strong>{esc(signal.get('name', ''))}</strong>"
        f"<p>{esc(signal.get('reason', ''))}</p>"
        f"<small>{esc(signal.get('latest_note', ''))}</small>"
        "</article>"
        for signal in payload.get("topic_signals", [])
    ) or "<p>아직 오늘의 review signal이 없습니다.</p>"
    ignored_cards = "".join(
        "<article class='card muted'>"
        f"<span>{esc(row.get('status', 'ignored'))}</span>"
        f"<strong>{esc(row.get('topic', ''))}</strong>"
        f"<p>{esc(row.get('reason', ''))}</p>"
        "</article>"
        for row in payload.get("ignored_responses", [])[:4]
    ) or "<p>무시된 응답이 없습니다.</p>"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Daily Review</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow,.card span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.card {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics,.stack {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.metric,.card {{ background:white; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:26px; }}
.card strong {{ display:block; margin:5px 0; }}
.card p,.card small {{ overflow-wrap:anywhere; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.stack {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Daily Review · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘 읽은 것과 내일 더 볼 것</h1>
</header>
<section class="hero">
<p>이 화면은 오늘의 로컬 피드백을 내일 scout 점수에 반영하기 위한 메모리 표면입니다. 외부 호출이나 실행은 하지 않습니다.</p>
<code>PYTHONPATH=src python3 -m mybroker appliance review-response-apply 'more "Semiconductors" "메모리 업황을 더 보고 싶다"'</code>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Responses</span><strong>{esc(summary.get('response_count', 0))}</strong></article>
<article class="metric"><span>Signals</span><strong>{esc(summary.get('signal_count', 0))}</strong></article>
<article class="metric"><span>Applied</span><strong>{esc(summary.get('applied_response_count', 0))}</strong></article>
<article class="metric"><span>Completed tasks</span><strong>{esc(summary.get('completed_task_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>내일 scout에 반영될 신호</h2>
<div class="stack">{signal_cards}</div>
</section>
<section class="section">
<h2>무시된 응답</h2>
<div class="stack">{ignored_cards}</div>
</section>
</main>
</body>
</html>
"""


def build_operator_review_prompt(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    daily_review_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    drift_review_path: str | Path = DEFAULT_DRIFT_REVIEW_OUTPUT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scout = _load_optional_json(scout_path)
    review = _load_optional_json(daily_review_path)
    drift = _load_optional_json(drift_review_path)
    ledger = _load_optional_json(task_ledger_path)
    recommendations = scout.get("recommendations", []) if scout.get("schema_version") == "daily_scout.v1" else []
    cards = [
        _operator_review_prompt_card(index=index, recommendation=recommendation)
        for index, recommendation in enumerate(recommendations[:3], start=1)
    ] or [_operator_review_prompt_fallback_card()]
    review_summary = review.get("summary", {}) if review.get("schema_version") == DAILY_REVIEW_SCHEMA_VERSION else {}
    drift_signal = next(
        (signal for signal in drift.get("signals", []) if signal.get("name") == "operator_feedback"),
        {},
    )
    ledger_summary = ledger.get("summary", {}) if ledger.get("schema_version") == ANALYST_TASK_LEDGER_SCHEMA_VERSION else {}
    payload = {
        "schema_version": OPERATOR_REVIEW_PROMPT_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "status": "needs_feedback" if int(review_summary.get("response_count", 0) or 0) == 0 else "ready",
        "summary": {
            "prompt_count": len(cards),
            "current_response_count": int(review_summary.get("response_count", 0) or 0),
            "applied_response_count": int(review_summary.get("applied_response_count", 0) or 0),
            "operator_feedback_signal": str(drift_signal.get("value", review_summary.get("response_count", 0))),
            "ready_task_count": int(ledger_summary.get("ready_for_local_work", 0) or 0),
        },
        "why_this_exists": "다음 scout와 방향 점검이 실제 사용자 피드백을 근거로 조정되도록, 오늘 남길 수 있는 짧은 응답을 제안합니다.",
        "prompt_cards": cards,
        "next_agent_effect": "review-response-apply를 남기면 daily_review, daily_scout, review_prompt, review_effect가 같은 local run에서 갱신되고 operator_review 반영 여부가 증명됩니다.",
        "input_artifacts": {
            "scout": Path(scout_path).as_posix(),
            "daily_review": Path(daily_review_path).as_posix(),
            "drift_review": Path(drift_review_path).as_posix(),
            "task_ledger": Path(task_ledger_path).as_posix(),
        },
        "phone_links": {
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "review": DEFAULT_DAILY_REVIEW_SURFACE.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
            "drift_review": DEFAULT_DRIFT_REVIEW_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "local_review_prompt_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_live_trading",
        ],
    }
    return payload


def write_operator_review_prompt(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    daily_review_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    drift_review_path: str | Path = DEFAULT_DRIFT_REVIEW_OUTPUT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    artifact_output_path: str | Path = DEFAULT_REVIEW_PROMPT_OUTPUT,
    surface_output_path: str | Path = DEFAULT_REVIEW_PROMPT_SURFACE,
) -> Path:
    payload = build_operator_review_prompt(
        scout_path=scout_path,
        daily_review_path=daily_review_path,
        drift_review_path=drift_review_path,
        task_ledger_path=task_ledger_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_operator_review_prompt(payload), encoding="utf-8")
    return target


def validate_operator_review_prompt_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != OPERATOR_REVIEW_PROMPT_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"needs_feedback", "ready"}:
        errors.append("status must be needs_feedback or ready")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if "local_review_prompt_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include local_review_prompt_only")
    cards = payload.get("prompt_cards", [])
    if not cards:
        errors.append("prompt_cards must not be empty")
    for index, card in enumerate(cards):
        for field in ["prompt_id", "topic", "why_feedback_matters", "copy_ready_commands", "next_agent_effect"]:
            if field not in card:
                errors.append(f"prompt_cards[{index}] missing {field}")
        commands = card.get("copy_ready_commands", [])
        if not commands:
            errors.append(f"prompt_cards[{index}] copy_ready_commands must not be empty")
        for command_index, command in enumerate(commands):
            command_text = command.get("command", "")
            if "review-response-apply" not in command_text:
                errors.append(f"prompt_cards[{index}].copy_ready_commands[{command_index}] must call review-response-apply")
            if command.get("external_effect_performed") is not False:
                errors.append(f"prompt_cards[{index}].copy_ready_commands[{command_index}] external_effect_performed must be false")
    return errors


def validate_operator_review_prompt_file(path: str | Path) -> list[str]:
    return validate_operator_review_prompt_payload(load_json(path))


def render_operator_review_prompt(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    cards = "".join(
        "<article class='card'>"
        f"<span>{esc(card.get('prompt_id', 'RP'))} · {esc(card.get('feedback_goal', 'review'))}</span>"
        f"<strong>{esc(card.get('topic', '오늘 주제'))}</strong>"
        f"<p>{esc(card.get('why_feedback_matters', ''))}</p>"
        f"<small>{esc(card.get('next_agent_effect', ''))}</small>"
        + "".join(
            "<div class='command'>"
            f"<b>{esc(command.get('label', '응답'))}</b>"
            f"<code>{esc(command.get('command', ''))}</code>"
            f"<small>{esc(command.get('why', ''))}</small>"
            "</div>"
            for command in card.get("copy_ready_commands", [])
        )
        + "</article>"
        for card in payload.get("prompt_cards", [])
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "review_prompt"
    )
    status_label = {
        "needs_feedback": "피드백 필요",
        "ready": "피드백 있음",
    }.get(payload.get("status", ""), payload.get("status", "unknown"))
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Review Prompt</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow,.card span,.command b {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.card {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics,.links {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.metric,.card,.command {{ background:white; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:26px; }}
.stack {{ display:grid; grid-template-columns:1fr; gap:10px; }}
.card strong {{ display:block; margin:5px 0; font-size:20px; }}
.card p,.card small {{ overflow-wrap:anywhere; }}
.command {{ margin-top:10px; border:1px solid var(--line); border-radius:8px; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Review Prompt · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘 남길 피드백</h1>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('why_this_exists', ''))}</p>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Prompts</span><strong>{esc(summary.get('prompt_count', 0))}</strong></article>
<article class="metric"><span>Responses</span><strong>{esc(summary.get('current_response_count', 0))}</strong></article>
<article class="metric"><span>Applied</span><strong>{esc(summary.get('applied_response_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>복사해서 남길 응답</h2>
<div class="stack">{cards}</div>
</section>
<section class="section">
<h2>다음에 바뀌는 것</h2>
<p>{esc(payload.get('next_agent_effect', ''))}</p>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
</main>
</body>
</html>
"""


def _operator_review_prompt_card(*, index: int, recommendation: dict[str, Any]) -> dict[str, Any]:
    topic = recommendation.get("name", "오늘 주제")
    why = recommendation.get("why", recommendation.get("next_question", "오늘 읽은 뒤 더 볼지 판단합니다."))
    commands = [
        _review_prompt_command("read", topic, "읽었음", "오늘 내용을 읽었고 다음 run에서 기본 관심 신호로 남깁니다."),
        _review_prompt_command("more", topic, "더 보기", "내일도 이 주제를 더 높은 우선순위로 보게 합니다."),
        _review_prompt_command("confusing", topic, "헷갈림", "다음 run에서 더 쉬운 설명과 추가 근거가 필요하다는 신호를 남깁니다."),
        _review_prompt_command("skip", topic, "건너뜀", "이 주제를 당장은 낮은 우선순위로 내리게 합니다."),
    ]
    return {
        "prompt_id": f"RP-{index:03d}",
        "topic": topic,
        "feedback_goal": "내일 scout 조정",
        "why_feedback_matters": why,
        "suggested_question": recommendation.get("next_question", f"{topic}을 내일도 더 볼 가치가 있나?"),
        "copy_ready_commands": commands,
        "next_agent_effect": "응답은 local review memory에만 저장되고 다음 scout 점수에 반영됩니다.",
    }


def _operator_review_prompt_fallback_card() -> dict[str, Any]:
    topic = "오늘 브리프"
    return {
        "prompt_id": "RP-001",
        "topic": topic,
        "feedback_goal": "scout 생성 전 기본 피드백",
        "why_feedback_matters": "아직 scout 추천이 없으므로 먼저 appliance run을 실행하고, 읽은 뒤 가장 가까운 응답을 남깁니다.",
        "suggested_question": "오늘 브리프가 이해됐나, 더 볼 주제가 있나?",
        "copy_ready_commands": [
            _review_prompt_command("read", topic, "읽었음", "오늘 브리프를 읽었다는 최소 피드백을 남깁니다."),
            _review_prompt_command("confusing", topic, "헷갈림", "다음 브리프가 더 쉬운 설명을 요구하도록 남깁니다."),
        ],
        "next_agent_effect": "다음 run에서 daily_review가 생성되면 가능한 범위에서 scout 판단에 반영됩니다.",
    }


def _review_prompt_command(action: str, topic: str, label: str, why: str) -> dict[str, Any]:
    response = f'{action} "{topic}" "{_review_prompt_default_note(action=action, topic=topic)}"'
    return {
        "action": action,
        "label": label,
        "command": f"PYTHONPATH=src python3 -m mybroker appliance review-response-apply {shlex.quote(response)}",
        "why": why,
        "external_effect_performed": False,
    }


def _review_prompt_default_note(*, action: str, topic: str) -> str:
    notes = {
        "read": f"{topic}을 읽었다",
        "more": f"{topic}을 내일도 더 보고 싶다",
        "confusing": f"{topic} 설명이 아직 어렵다",
        "skip": f"{topic}은 오늘은 건너뛴다",
    }
    return notes.get(action, f"{topic} 피드백")


def build_operator_review_effect(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    daily_review_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    review_prompt_path: str | Path = DEFAULT_REVIEW_PROMPT_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scout = _load_optional_json(scout_path)
    review = _load_optional_json(daily_review_path)
    prompt = _load_optional_json(review_prompt_path)
    review_summary = review.get("summary", {}) if review.get("schema_version") == DAILY_REVIEW_SCHEMA_VERSION else {}
    scout_context = scout.get("review_context", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    recommendations = scout.get("recommendations", []) if scout.get("schema_version") == "daily_scout.v1" else []
    topic_effects = _operator_review_topic_effects(review=review, recommendations=recommendations)
    response_count = int(review_summary.get("response_count", 0) or 0)
    scout_response_count = int(scout_context.get("response_count", 0) or 0)
    applied_count = sum(1 for effect in topic_effects if effect.get("effect_status") == "applied")
    status = _operator_review_effect_status(
        scout=scout,
        review=review,
        response_count=response_count,
        scout_response_count=scout_response_count,
        applied_count=applied_count,
    )
    payload = {
        "schema_version": OPERATOR_REVIEW_EFFECT_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "status": status,
        "summary": {
            "response_count": response_count,
            "scout_response_count": scout_response_count,
            "review_signal_count": int(review_summary.get("signal_count", 0) or 0),
            "applied_topic_count": applied_count,
            "prompt_count": int(prompt.get("summary", {}).get("prompt_count", 0) or 0),
        },
        "interpretation": _operator_review_effect_interpretation(status=status),
        "topic_effects": topic_effects,
        "next_actions": _operator_review_effect_next_actions(status=status, prompt=prompt),
        "input_artifacts": {
            "scout": Path(scout_path).as_posix(),
            "daily_review": Path(daily_review_path).as_posix(),
            "review_prompt": Path(review_prompt_path).as_posix(),
        },
        "phone_links": {
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "review": DEFAULT_DAILY_REVIEW_SURFACE.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
            "review_effect": DEFAULT_REVIEW_EFFECT_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "local_review_effect_proof_only",
            "reads_existing_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_live_trading",
        ],
    }
    return payload


def write_operator_review_effect(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    daily_review_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    review_prompt_path: str | Path = DEFAULT_REVIEW_PROMPT_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_REVIEW_EFFECT_OUTPUT,
    surface_output_path: str | Path = DEFAULT_REVIEW_EFFECT_SURFACE,
) -> Path:
    payload = build_operator_review_effect(
        scout_path=scout_path,
        daily_review_path=daily_review_path,
        review_prompt_path=review_prompt_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_operator_review_effect(payload), encoding="utf-8")
    return target


def validate_operator_review_effect_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != OPERATOR_REVIEW_EFFECT_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"no_feedback", "applied", "not_applied", "missing_inputs"}:
        errors.append("status must be no_feedback, applied, not_applied, or missing_inputs")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if "local_review_effect_proof_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include local_review_effect_proof_only")
    summary = payload.get("summary", {})
    for field in ["response_count", "scout_response_count", "review_signal_count", "applied_topic_count", "prompt_count"]:
        if field not in summary:
            errors.append(f"summary missing {field}")
    if not payload.get("next_actions"):
        errors.append("next_actions must not be empty")
    for index, effect in enumerate(payload.get("topic_effects", [])):
        for field in ["topic_id", "topic", "review_delta", "scout_delta", "effect_status", "evidence"]:
            if field not in effect:
                errors.append(f"topic_effects[{index}] missing {field}")
        if effect.get("effect_status") not in {"applied", "not_applied"}:
            errors.append(f"topic_effects[{index}] invalid effect_status")
    return errors


def validate_operator_review_effect_file(path: str | Path) -> list[str]:
    return validate_operator_review_effect_payload(load_json(path))


def write_operator_review_response_apply(
    *,
    payload: dict[str, Any],
    artifact_output_path: str | Path = DEFAULT_REVIEW_RESPONSE_APPLY_OUTPUT,
    surface_output_path: str | Path = DEFAULT_REVIEW_RESPONSE_APPLY_SURFACE,
) -> Path:
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_operator_review_response_apply(payload), encoding="utf-8")
    return target


def validate_operator_review_response_apply_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != OPERATOR_REVIEW_RESPONSE_APPLY_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"applied", "blocked"}:
        errors.append("status must be applied or blocked")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if "local_review_response_apply_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include local_review_response_apply_only")
    for field in ["operator_response", "responses_path", "daily_review", "daily_scout", "review_prompt", "review_effect"]:
        if field not in payload:
            errors.append(f"missing {field}")
    effect = payload.get("review_effect", {})
    if effect.get("status") not in {"applied", "no_feedback", "not_applied", "missing_inputs"}:
        errors.append("review_effect.status is invalid")
    if not payload.get("next_action"):
        errors.append("next_action must not be empty")
    return errors


def validate_operator_review_response_apply_file(path: str | Path) -> list[str]:
    return validate_operator_review_response_apply_payload(load_json(path))


def render_operator_review_response_apply(payload: dict[str, Any]) -> str:
    effect = payload.get("review_effect", {})
    review = payload.get("daily_review", {})
    scout = payload.get("daily_scout", {})
    status_label = {
        "applied": "응답 적용됨",
        "blocked": "응답 적용 차단됨",
    }.get(payload.get("status", ""), payload.get("status", "unknown"))
    effect_label = {
        "applied": "피드백 반영됨",
        "no_feedback": "아직 피드백 없음",
        "not_applied": "피드백 미반영",
        "missing_inputs": "입력 누락",
    }.get(effect.get("status", ""), effect.get("status", "unknown"))
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Review Response Apply</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow,.metric span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small {{ color:var(--muted); }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics,.links {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:24px; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Review Apply · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>피드백 응답 적용</h1>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('next_action', ''))}</p>
<code>{esc(payload.get('operator_response', ''))}</code>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Review responses</span><strong>{esc(review.get('response_count', 0))}</strong></article>
<article class="metric"><span>Scout read</span><strong>{esc(scout.get('review_response_count', 0))}</strong></article>
<article class="metric"><span>Effect</span><strong>{esc(effect_label)}</strong></article>
</div>
</section>
<section class="section">
<h2>갱신된 파일</h2>
<div class="links">
<a href="{esc(_relative_href(DEFAULT_DAILY_REVIEW_SURFACE))}">review</a>
<a href="{esc(_relative_href(DEFAULT_REVIEW_PROMPT_SURFACE))}">review_prompt</a>
<a href="{esc(_relative_href(DEFAULT_REVIEW_EFFECT_SURFACE))}">review_effect</a>
</div>
</section>
</main>
</body>
</html>
"""


def render_operator_review_effect(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    status_label = {
        "no_feedback": "아직 피드백 없음",
        "applied": "피드백 반영됨",
        "not_applied": "피드백 미반영",
        "missing_inputs": "입력 누락",
    }.get(payload.get("status", ""), payload.get("status", "unknown"))
    effect_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(effect.get('effect_status', ''))} · delta {esc(effect.get('scout_delta', 0))}</span>"
        f"<strong>{esc(effect.get('topic', ''))}</strong>"
        f"<p>{esc(effect.get('evidence', ''))}</p>"
        f"<small>review delta {esc(effect.get('review_delta', 0))}</small>"
        "</article>"
        for effect in payload.get("topic_effects", [])
    ) or "<p>아직 scout에 반영할 review signal이 없습니다.</p>"
    action_cards = "".join(
        "<article class='command'>"
        f"<span>{esc(action.get('label', 'next'))}</span>"
        f"<p>{esc(action.get('why', ''))}</p>"
        f"<code>{esc(action.get('command', ''))}</code>"
        "</article>"
        for action in payload.get("next_actions", [])
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "review_effect"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Review Effect</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow,.card span,.command span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.card,.command {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics,.links {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric,.card,.command {{ background:white; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:26px; }}
.stack {{ display:grid; grid-template-columns:1fr; gap:10px; }}
.card strong {{ display:block; margin:5px 0; font-size:20px; }}
.card p,.card small,.command p {{ overflow-wrap:anywhere; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Review Effect · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>피드백 반영 확인</h1>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('interpretation', ''))}</p>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Responses</span><strong>{esc(summary.get('response_count', 0))}</strong></article>
<article class="metric"><span>Scout read</span><strong>{esc(summary.get('scout_response_count', 0))}</strong></article>
<article class="metric"><span>Signals</span><strong>{esc(summary.get('review_signal_count', 0))}</strong></article>
<article class="metric"><span>Applied</span><strong>{esc(summary.get('applied_topic_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>Scout score 반영 증거</h2>
<div class="stack">{effect_cards}</div>
</section>
<section class="section">
<h2>다음 행동</h2>
<div class="stack">{action_cards}</div>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
</main>
</body>
</html>
"""


def _operator_review_topic_effects(*, review: dict[str, Any], recommendations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if review.get("schema_version") != DAILY_REVIEW_SCHEMA_VERSION:
        return []
    recommendations_by_id = {row.get("topic_id"): row for row in recommendations}
    effects = []
    for signal in review.get("topic_signals", []):
        topic_id = signal.get("topic_id", "")
        recommendation = recommendations_by_id.get(topic_id, {})
        score_factors = recommendation.get("score_factors", [])
        scout_factor = next((factor for factor in score_factors if factor.get("name") == "operator_review"), {})
        review_delta = float(signal.get("score_delta", 0) or 0)
        scout_delta = float(scout_factor.get("delta", 0) or 0)
        applied = bool(scout_factor) and round(review_delta, 2) == round(scout_delta, 2)
        effects.append({
            "topic_id": topic_id,
            "topic": signal.get("name", recommendation.get("name", topic_id)),
            "review_delta": round(review_delta, 2),
            "scout_delta": round(scout_delta, 2),
            "effect_status": "applied" if applied else "not_applied",
            "latest_status": signal.get("latest_status", ""),
            "latest_note": signal.get("latest_note", ""),
            "evidence": scout_factor.get("reason") if applied else "현재 scout score_factors에 operator_review delta가 일치하지 않습니다.",
        })
    return effects


def _operator_review_effect_status(
    *,
    scout: dict[str, Any],
    review: dict[str, Any],
    response_count: int,
    scout_response_count: int,
    applied_count: int,
) -> str:
    if scout.get("schema_version") != "daily_scout.v1" or review.get("schema_version") != DAILY_REVIEW_SCHEMA_VERSION:
        return "missing_inputs"
    if response_count == 0:
        return "no_feedback"
    if scout_response_count != response_count:
        return "not_applied"
    if applied_count > 0:
        return "applied"
    return "not_applied"


def _operator_review_effect_interpretation(*, status: str) -> str:
    return {
        "no_feedback": "아직 기록된 review-response가 없어 scout가 개인 피드백을 반영할 수 없습니다.",
        "applied": "daily_review의 topic signal이 현재 scout score_factors에 operator_review로 반영됐습니다.",
        "not_applied": "review-response는 있으나 현재 scout가 같은 응답 수나 delta를 반영하지 못했습니다. review-response-apply로 같은 local run에서 다시 확인해야 합니다.",
        "missing_inputs": "daily_scout 또는 daily_review artifact가 없거나 schema가 맞지 않아 반영 여부를 판단할 수 없습니다.",
    }.get(status, "피드백 반영 상태를 확인해야 합니다.")


def _operator_review_effect_next_actions(*, status: str, prompt: dict[str, Any]) -> list[dict[str, Any]]:
    if status == "no_feedback":
        command = _first_review_prompt_command(prompt)
        return [{
            "label": "피드백 남기기",
            "why": "오늘 읽은 주제에 대해 가장 가까운 응답을 하나 남기면 다음 run에서 scout score에 반영됩니다.",
            "command": command or "PYTHONPATH=src python3 -m mybroker appliance review-prompt",
            "external_effect_performed": False,
        }]
    if status == "not_applied":
        return [{
            "label": "로컬 run 재생성",
            "why": "review-response-apply는 daily_review와 daily_scout를 같은 local run에서 다시 생성해 반영 여부를 맞춥니다.",
            "command": "PYTHONPATH=src python3 -m mybroker appliance review-response-apply 'more \"Semiconductors\" \"내일도 이어서 보고 싶다\"'",
            "external_effect_performed": False,
        }]
    if status == "missing_inputs":
        return [{
            "label": "필수 artifact 생성",
            "why": "daily_scout와 daily_review가 있어야 피드백 반영 여부를 판정할 수 있습니다.",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --profile examples/profiles/beginner-conservative.json --dry-run",
            "external_effect_performed": False,
        }]
    return [{
        "label": "유지",
        "why": "피드백이 현재 scout에 반영됐습니다. 오늘 브리프를 읽고 다음 피드백을 남기면 루프가 계속 개인화됩니다.",
        "command": "PYTHONPATH=src python3 -m mybroker appliance review-prompt",
        "external_effect_performed": False,
    }]


def _first_review_prompt_command(prompt: dict[str, Any]) -> str:
    for card in prompt.get("prompt_cards", []):
        for command in card.get("copy_ready_commands", []):
            if command.get("command"):
                return command["command"]
    return ""


def _load_daily_review_responses(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    rows = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            rows.append({
                "schema_version": "daily_review_response.v1",
                "recorded_at": _now(),
                "action": "invalid",
                "status": "invalid",
                "topic": "",
                "note": line,
                "external_effect_performed": False,
            })
            continue
        rows.append(payload)
    return rows


def _review_topic_index(recommendations: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "topic_id": str(item.get("topic_id", "")),
            "name": str(item.get("name", "")),
            "name_key": str(item.get("name", "")).lower().strip(),
            "topic_key": str(item.get("topic_id", "")).lower().strip(),
        }
        for item in recommendations
        if item.get("topic_id") or item.get("name")
    ]


def _match_review_topic(topic: str, index: list[dict[str, str]]) -> dict[str, str]:
    key = topic.lower().strip()
    for row in index:
        if key in {row["topic_key"], row["name_key"]}:
            return row
    for row in index:
        if key and (key in row["name_key"] or row["name_key"] in key):
            return row
    return {}


def _review_action_delta(status: str) -> float:
    if status == "want_more":
        return 1.2
    if status == "reviewed":
        return 0.6
    if status == "confusing":
        return 0.5
    if status == "skipped":
        return -0.7
    return 0.0


def _review_signal_reason(signal: dict[str, Any]) -> str:
    statuses = [row.get("status", "") for row in signal.get("responses", [])]
    if "want_more" in statuses:
        return "운영자가 이 주제를 더 보고 싶다고 기록했습니다."
    if "confusing" in statuses:
        return "운영자가 이 주제를 이해하기 어렵다고 표시해 초보자 설명을 우선합니다."
    if "reviewed" in statuses:
        return "운영자가 오늘 이 주제를 읽었다고 기록해 다음 루프에도 연결합니다."
    if "skipped" in statuses:
        return "운영자가 오늘 이 주제를 건너뛰어 우선순위를 낮춥니다."
    return "운영자 daily review 응답이 기록됐습니다."


def build_morning_control_packet(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    task_queue_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    notification_path: str | Path = DEFAULT_NOTIFICATION_OUTPUT,
    runtime_doctor_path: str | Path = DEFAULT_RUNTIME_DOCTOR_OUTPUT,
    today_path: str | Path = DEFAULT_TODAY_OUTPUT,
    readiness_surface_path: str | Path = DEFAULT_DAILY_READINESS_SURFACE,
    scheduler_surface_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_SURFACE,
    source_refresh_surface_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE,
    vault_surface_path: str | Path = DEFAULT_VAULT_SURFACE_OUTPUT,
    agenda_surface_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_SURFACE,
    agenda_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    review_surface_path: str | Path = DEFAULT_DAILY_REVIEW_SURFACE,
    review_prompt_surface_path: str | Path = DEFAULT_REVIEW_PROMPT_SURFACE,
    review_effect_surface_path: str | Path = DEFAULT_REVIEW_EFFECT_SURFACE,
    analyst_council_surface_path: str | Path = DEFAULT_ANALYST_COUNCIL_SURFACE,
    memory_query_surface_path: str | Path = DEFAULT_MEMORY_QUERY_SURFACE,
    memory_audit_surface_path: str | Path = DEFAULT_MEMORY_AUDIT_SURFACE,
    pattern_radar_surface_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_SURFACE,
    pattern_dry_run_surface_path: str | Path = DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE,
    run_trace_surface_path: str | Path = DEFAULT_RUN_TRACE_SURFACE,
    run_ledger_surface_path: str | Path = DEFAULT_DAILY_RUN_LEDGER_SURFACE,
    handoff_surface_path: str | Path = DEFAULT_DAILY_HANDOFF_SURFACE,
    handoff_apply_surface_path: str | Path = DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE,
    daily_home_surface_path: str | Path = DEFAULT_DAILY_HOME_SURFACE,
    drift_review_surface_path: str | Path = DEFAULT_DRIFT_REVIEW_SURFACE,
    memory_surface_path: str | Path = DEFAULT_MEMORY_OUTPUT,
    journal_surface_path: str | Path = DEFAULT_ANALYST_JOURNAL_OUTPUT,
    task_queue_surface_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_OUTPUT,
    task_ledger_surface_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scout = _load_optional_json(scout_path)
    journal = _load_optional_json(journal_path)
    queue = _load_optional_json(task_queue_path)
    ledger = _load_optional_json(task_ledger_path)
    live_gate = _load_optional_json(refresh_live_gate_path)
    live_run = _load_optional_json(refresh_live_run_path)
    preflight = _load_optional_json(refresh_live_preflight_path)
    notification = _load_optional_json(notification_path)
    doctor = _load_optional_json(runtime_doctor_path)
    agenda = _load_optional_json(agenda_path)
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    agenda_primary = agenda.get("primary_topic", {}) if agenda.get("schema_version") == DAILY_BRIEF_AGENDA_SCHEMA_VERSION else {}
    focus = journal.get("today_focus", {})
    ledger_summary = ledger.get("summary", {})
    pending_decisions = _morning_pending_decisions(live_gate=live_gate, live_run=live_run, preflight=preflight)
    command_bar = _morning_command_bar(ledger=ledger, pending_decisions=pending_decisions)
    status = _morning_status(
        pending_decisions=pending_decisions,
        ledger_summary=ledger_summary,
        doctor=doctor,
    )
    payload = {
        "schema_version": MORNING_CONTROL_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "status": status,
        "run_id": journal.get("run_id", scout.get("run_id", "")),
        "read_first": {
            "title": agenda_primary.get("name", focus.get("title", recommended.get("name", "오늘 브리프 먼저 확인"))),
            "reason": agenda_primary.get("why_today", focus.get("rationale", recommended.get("why", ""))),
            "recommended_topic": agenda_primary.get("name", recommended.get("name", focus.get("recommended_topic", ""))),
            "confidence": agenda_primary.get("confidence", recommended.get("confidence", focus.get("confidence", ""))),
            "next_question": agenda_primary.get("next_question", recommended.get("next_question", "")),
        },
        "task_state": {
            "total": ledger.get("entry_count", queue.get("task_count", 0)),
            "ready": ledger_summary.get("ready_for_local_work", 0),
            "carried": ledger_summary.get("carried", 0),
            "completed": ledger_summary.get("completed", 0),
            "deferred": ledger_summary.get("deferred", 0),
            "blocked": ledger_summary.get("blocked_requires_approval", 0) + ledger_summary.get("blocked_by_operator", 0),
            "top_tasks": _morning_top_tasks(ledger=ledger, queue=queue),
        },
        "pending_decisions": pending_decisions,
        "command_bar": command_bar,
        "phone_links": {
            "daily_home": Path(daily_home_surface_path).as_posix(),
            "phone_access": DEFAULT_PHONE_ACCESS_VERIFY_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "readiness": Path(readiness_surface_path).as_posix(),
            "scheduler": Path(scheduler_surface_path).as_posix(),
            "source_refresh": Path(source_refresh_surface_path).as_posix(),
            "today": Path(today_path).as_posix(),
            "agenda": Path(agenda_surface_path).as_posix(),
            "review": Path(review_surface_path).as_posix(),
            "review_prompt": Path(review_prompt_surface_path).as_posix(),
            "review_effect": Path(review_effect_surface_path).as_posix(),
            "council": Path(analyst_council_surface_path).as_posix(),
            "memory_query": Path(memory_query_surface_path).as_posix(),
            "memory_audit": Path(memory_audit_surface_path).as_posix(),
            "pattern_radar": Path(pattern_radar_surface_path).as_posix(),
            "pattern_dry_run": Path(pattern_dry_run_surface_path).as_posix(),
            "trace": Path(run_trace_surface_path).as_posix(),
            "run_ledger": Path(run_ledger_surface_path).as_posix(),
            "handoff": Path(handoff_surface_path).as_posix(),
            "handoff_apply": Path(handoff_apply_surface_path).as_posix(),
            "drift_review": Path(drift_review_surface_path).as_posix(),
            "vault": Path(vault_surface_path).as_posix(),
            "journal": Path(journal_surface_path).as_posix(),
            "tasks": Path(task_queue_surface_path).as_posix(),
            "task_ledger": Path(task_ledger_surface_path).as_posix(),
            "memory": Path(memory_surface_path).as_posix(),
        },
        "runtime": {
            "notification_status": notification.get("delivery_status", "missing"),
            "notification_dry_run": notification.get("dry_run", True),
            "runtime_doctor_status": doctor.get("status", "missing"),
            "runtime_warn_count": doctor.get("warn_count", 0),
            "runtime_fail_count": doctor.get("fail_count", 0),
        },
        "artifact_inputs": {
            "scout": Path(scout_path).as_posix(),
            "journal": Path(journal_path).as_posix(),
            "task_queue": Path(task_queue_path).as_posix(),
            "task_ledger": Path(task_ledger_path).as_posix(),
            "source_refresh_live_gate": Path(refresh_live_gate_path).as_posix(),
            "source_refresh_live_run": Path(refresh_live_run_path).as_posix(),
            "source_refresh_live_preflight": Path(refresh_live_preflight_path).as_posix(),
            "notification": Path(notification_path).as_posix(),
            "runtime_doctor": Path(runtime_doctor_path).as_posix(),
            "agenda": Path(agenda_path).as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "control_packet_reads_existing_artifacts_only",
            "does_not_execute_tasks",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "no_account_access",
            "no_live_trading",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_morning_control_packet(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    task_queue_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    notification_path: str | Path = DEFAULT_NOTIFICATION_OUTPUT,
    runtime_doctor_path: str | Path = DEFAULT_RUNTIME_DOCTOR_OUTPUT,
    readiness_surface_path: str | Path = DEFAULT_DAILY_READINESS_SURFACE,
    scheduler_surface_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_SURFACE,
    source_refresh_surface_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE,
    agenda_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    agenda_surface_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_SURFACE,
    review_surface_path: str | Path = DEFAULT_DAILY_REVIEW_SURFACE,
    review_prompt_surface_path: str | Path = DEFAULT_REVIEW_PROMPT_SURFACE,
    review_effect_surface_path: str | Path = DEFAULT_REVIEW_EFFECT_SURFACE,
    analyst_council_surface_path: str | Path = DEFAULT_ANALYST_COUNCIL_SURFACE,
    memory_query_surface_path: str | Path = DEFAULT_MEMORY_QUERY_SURFACE,
    memory_audit_surface_path: str | Path = DEFAULT_MEMORY_AUDIT_SURFACE,
    pattern_radar_surface_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_SURFACE,
    pattern_dry_run_surface_path: str | Path = DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE,
    run_trace_surface_path: str | Path = DEFAULT_RUN_TRACE_SURFACE,
    run_ledger_surface_path: str | Path = DEFAULT_DAILY_RUN_LEDGER_SURFACE,
    handoff_surface_path: str | Path = DEFAULT_DAILY_HANDOFF_SURFACE,
    handoff_apply_surface_path: str | Path = DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE,
    daily_home_surface_path: str | Path = DEFAULT_DAILY_HOME_SURFACE,
    drift_review_surface_path: str | Path = DEFAULT_DRIFT_REVIEW_SURFACE,
    artifact_output_path: str | Path = DEFAULT_MORNING_CONTROL_OUTPUT,
    surface_output_path: str | Path = DEFAULT_MORNING_CONTROL_SURFACE,
) -> Path:
    payload = build_morning_control_packet(
        scout_path=scout_path,
        journal_path=journal_path,
        task_queue_path=task_queue_path,
        task_ledger_path=task_ledger_path,
        refresh_live_gate_path=refresh_live_gate_path,
        refresh_live_run_path=refresh_live_run_path,
        refresh_live_preflight_path=refresh_live_preflight_path,
        notification_path=notification_path,
        runtime_doctor_path=runtime_doctor_path,
        readiness_surface_path=readiness_surface_path,
        scheduler_surface_path=scheduler_surface_path,
        source_refresh_surface_path=source_refresh_surface_path,
        agenda_path=agenda_path,
        agenda_surface_path=agenda_surface_path,
        review_surface_path=review_surface_path,
        review_prompt_surface_path=review_prompt_surface_path,
        review_effect_surface_path=review_effect_surface_path,
        analyst_council_surface_path=analyst_council_surface_path,
        memory_query_surface_path=memory_query_surface_path,
        memory_audit_surface_path=memory_audit_surface_path,
        pattern_radar_surface_path=pattern_radar_surface_path,
        pattern_dry_run_surface_path=pattern_dry_run_surface_path,
        run_trace_surface_path=run_trace_surface_path,
        run_ledger_surface_path=run_ledger_surface_path,
        handoff_surface_path=handoff_surface_path,
        handoff_apply_surface_path=handoff_apply_surface_path,
        daily_home_surface_path=daily_home_surface_path,
        drift_review_surface_path=drift_review_surface_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_morning_control_packet(payload), encoding="utf-8")
    return target


def validate_morning_control_packet_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != MORNING_CONTROL_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("status") not in {"ready", "operator_review", "blocked"}:
        errors.append(f"invalid status {payload.get('status')}")
    if not payload.get("read_first", {}).get("title"):
        errors.append("read_first.title must not be empty")
    if not payload.get("phone_links", {}).get("today"):
        errors.append("phone_links.today must not be empty")
    if "does_not_execute_tasks" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_execute_tasks")
    forbidden_fragments = [" --send", "--confirm-host-write", "--execute", "launchctl bootstrap"]
    for index, item in enumerate(payload.get("command_bar", [])):
        command = item.get("command", "")
        if any(fragment in command for fragment in forbidden_fragments):
            errors.append(f"command_bar[{index}] includes gated execution fragment")
        if item.get("external_effect_performed") is not False:
            errors.append(f"command_bar[{index}] external_effect_performed must be false")
    for index, decision in enumerate(payload.get("pending_decisions", [])):
        if not decision.get("copy_ready_response"):
            errors.append(f"pending_decisions[{index}] missing copy_ready_response")
        if decision.get("agent_will_run") and decision.get("approval_required") is not True:
            errors.append(f"pending_decisions[{index}] runnable action requires approval flag")
    return errors


def validate_morning_control_packet_file(path: str | Path) -> list[str]:
    return validate_morning_control_packet_payload(load_json(path))


def _daily_home_artifact_status(*, name: str, path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    target = Path(path)
    return {
        "name": name,
        "path": target.as_posix(),
        "exists": target.exists(),
        "schema_version": payload.get("schema_version", "missing"),
        "status": payload.get("status", payload.get("delivery_status", "missing")),
        "generated_at": payload.get("generated_at", payload.get("created_at", "")),
    }


def _daily_home_commands(*, payloads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    forbidden_fragments = [" --send", "--confirm-host-write", "--execute", "launchctl bootstrap"]
    for command in payloads.get("handoff", {}).get("copy_ready_commands", [])[:3]:
        if command.get("command"):
            commands.append({
                "source": "handoff",
                "label": command.get("label", "handoff response"),
                "command": command.get("command", ""),
                "why": command.get("why", ""),
                "external_effect_performed": False,
            })
    for command in payloads.get("morning", {}).get("command_bar", [])[:4]:
        command_text = command.get("command", "")
        if command_text and not any(fragment in command_text for fragment in forbidden_fragments):
            commands.append({
                "source": "morning",
                "label": command.get("label", "local command"),
                "command": command_text,
                "why": command.get("effect", "local only"),
                "external_effect_performed": False,
            })
    if not commands:
        commands.append({
            "source": "daily_home",
            "label": "수동 daily run",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --profile examples/profiles/beginner-conservative.json --source gdelt-live --source stooq-live --source sec-sample --dry-run",
            "why": "오늘 산출물이 없거나 오래됐을 때 로컬 dry-run만 다시 생성합니다.",
            "external_effect_performed": False,
        })
    return commands


def _daily_home_action_inbox(
    *,
    morning: dict[str, Any],
    handoff: dict[str, Any],
    handoff_study_resolution: dict[str, Any],
    task_ledger: dict[str, Any],
    source_freshness_intake: dict[str, Any],
    source_refresh_execution_brief: dict[str, Any],
    pattern_radar: dict[str, Any],
    pattern_proof: dict[str, Any],
    pattern_evidence_intake: dict[str, Any],
    links: dict[str, str],
) -> dict[str, Any]:
    pending_decisions = morning.get("pending_decisions", [])
    unresolved = handoff.get("unresolved", [])
    study_items = handoff.get("study_closure", {}).get("items", [])
    resolution_items = handoff_study_resolution.get("items", []) if handoff_study_resolution.get("schema_version") == HANDOFF_STUDY_RESOLUTION_SCHEMA_VERSION else []
    task_entries = task_ledger.get("entries", []) if task_ledger.get("schema_version") == ANALYST_TASK_LEDGER_SCHEMA_VERSION else []
    carried_tasks = [entry for entry in task_entries if entry.get("status") == "carried"]
    ready_tasks = [entry for entry in task_entries if entry.get("status") == "ready_for_local_work"]
    priority_items: list[dict[str, Any]] = []

    for decision in pending_decisions[:2]:
        priority_items.append({
            "kind": "approval_gate",
            "id": decision.get("id", "approval"),
            "title": decision.get("title", "승인 필요"),
            "why": decision.get("why", ""),
            "source": "morning_control",
            "status": "requires_separate_approval",
            "href": links.get("morning", ""),
            "copy_ready_command": decision.get("copy_ready_response", ""),
            "requires_separate_approval": True,
            "external_effect_performed": False,
            "host_write_performed": False,
        })

    if source_freshness_intake.get("schema_version") == SOURCE_FRESHNESS_INTAKE_SCHEMA_VERSION:
        intake_summary = source_freshness_intake.get("summary", {})
        if intake_summary.get("stale_or_sample_source_count", 0) or intake_summary.get("blocked_live_candidate_count", 0):
            priority_items.append({
                "kind": "source_freshness_intake",
                "id": "source-freshness-intake",
                "title": "승인 전 근거 신선도 확인",
                "why": source_freshness_intake.get("next_action", "source freshness intake를 먼저 확인하세요."),
                "source": "source_freshness_intake",
                "status": source_freshness_intake.get("status", "review"),
                "href": links.get("source_freshness_intake", ""),
                "copy_ready_command": source_freshness_intake.get("approval_packet", {}).get("copy_ready_response", ""),
                "requires_separate_approval": source_freshness_intake.get("status") == "approval_packet_ready",
                "external_effect_performed": False,
                "host_write_performed": False,
            })

    if source_refresh_execution_brief.get("schema_version") == SOURCE_REFRESH_EXECUTION_BRIEF_SCHEMA_VERSION:
        execution_summary = source_refresh_execution_brief.get("summary", {})
        if source_refresh_execution_brief.get("status") in {"approval_required", "preflight_required", "ready_for_final_confirmation", "blocked"}:
            execution_status = source_refresh_execution_brief.get("status")
            inspect_command = "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance source-refresh-execution"
            final_command = source_refresh_execution_brief.get("final_confirmation", {}).get("run_command_preview", "")
            priority_items.append({
                "kind": "source_refresh_execution",
                "id": "source-refresh-execution",
                "title": "live refresh 실행 전 최종 확인",
                "why": f"approval {execution_summary.get('approval_status', 'missing')}, preflight {execution_summary.get('preflight_status', 'missing')}, blockers {execution_summary.get('blocker_count', 0)}개를 확인합니다.",
                "source": "source_refresh_execution_brief",
                "status": execution_status,
                "href": links.get("source_refresh_execution", ""),
                "copy_ready_command": final_command if execution_status == "ready_for_final_confirmation" else inspect_command,
                "requires_separate_approval": execution_status == "ready_for_final_confirmation",
                "external_effect_performed": False,
                "host_write_performed": False,
            })

    scout = pattern_radar.get("pattern_scout", {}) if pattern_radar.get("schema_version") == AGENT_PATTERN_RADAR_SCHEMA_VERSION else {}
    recommended = scout.get("recommended_next", {})
    scout_proof = next(
        (
            row for row in pattern_proof.get("candidate_results", [])
            if row.get("candidate_id") == recommended.get("candidate_id")
        ),
        {},
    )
    if recommended and scout_proof.get("proof_status") == "passed":
        priority_items.append({
            "kind": "pattern_scout",
            "id": recommended.get("candidate_id", "pattern-scout"),
            "title": recommended.get("title", "다음 local-only 방식 실험"),
            "why": recommended.get("why_now", ""),
            "source": "pattern_scout",
            "status": "local_proof_ready",
            "href": links.get("pattern_radar", ""),
            "copy_ready_command": recommended.get("proof_command", ""),
            "requires_separate_approval": bool(recommended.get("operator_decision_needed", True)),
            "external_effect_performed": False,
            "host_write_performed": False,
        })

    if pattern_evidence_intake.get("schema_version") == PATTERN_EVIDENCE_INTAKE_SCHEMA_VERSION:
        pattern_intake_summary = pattern_evidence_intake.get("summary", {})
        if pattern_intake_summary.get("local_candidate_count", 0):
            next_candidate = pattern_evidence_intake.get("next_candidate", {})
            priority_items.append({
                "kind": "pattern_evidence_intake",
                "id": next_candidate.get("candidate_id", "pattern-evidence-intake"),
                "title": "새 에이전트 방식 도입 후보 검토",
                "why": next_candidate.get("why", "새 방법론을 바로 도입하지 않고 로컬 증거와 dry-run 후보로 분류합니다."),
                "source": "pattern_evidence_intake",
                "status": pattern_evidence_intake.get("status", "ready"),
                "href": links.get("pattern_evidence_intake", ""),
                "copy_ready_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance pattern-evidence-intake",
                "requires_separate_approval": False,
                "external_effect_performed": False,
                "host_write_performed": False,
            })

    if resolution_items:
        resolution_summary = handoff_study_resolution.get("summary", {})
        priority_items.append({
            "kind": "handoff_study_resolution",
            "id": "handoff-study-resolution",
            "title": "남은 질문을 공부로 닫기",
            "why": f"답변 후보 {resolution_summary.get('resolution_item_count', 0)}개, source freshness block {resolution_summary.get('blocked_by_source_freshness_count', 0)}개를 먼저 확인합니다.",
            "source": "handoff_study_resolution",
            "status": handoff_study_resolution.get("status", "review"),
            "href": links.get("handoff_study_resolution", ""),
            "copy_ready_command": resolution_items[0].get("copy_ready_command", ""),
            "requires_separate_approval": False,
            "external_effect_performed": False,
            "host_write_performed": False,
        })

    for item in ([] if resolution_items else study_items[:4]):
        priority_items.append({
            "kind": item.get("kind", "study_closure"),
            "id": item.get("id", "study"),
            "title": item.get("title", "study closure"),
            "why": item.get("beginner_question", item.get("why_it_matters", "")),
            "source": item.get("source", "study_closure"),
            "status": "study_closure",
            "href": item.get("linked_surface", links.get("handoff", "")),
            "copy_ready_command": item.get("copy_ready_command", ""),
            "requires_separate_approval": False,
            "external_effect_performed": False,
            "host_write_performed": False,
        })

    unresolved_fallback = [] if study_items else unresolved[:3]
    for item in unresolved_fallback:
        command = ""
        if str(item.get("id", "")).startswith("DH-AT-"):
            command = f'{item.get("id", "").replace("DH-", "")} carry "오늘 action inbox에서 계속 이월"'
        elif item.get("title"):
            command = f'more "{str(item.get("title", ""))[:60]}" "내일 이어서 확인"'
        priority_items.append({
            "kind": item.get("kind", "handoff"),
            "id": item.get("id", "handoff"),
            "title": item.get("title", "handoff item"),
            "why": item.get("next_action", item.get("evidence", "")),
            "source": item.get("source", "handoff"),
            "status": "unresolved",
            "href": links.get("handoff", ""),
            "copy_ready_command": command,
            "requires_separate_approval": False,
            "external_effect_performed": False,
            "host_write_performed": False,
        })

    existing_ids = {item.get("id") for item in priority_items}
    for task in (ready_tasks + carried_tasks)[:4]:
        task_id = task.get("task_id", "")
        if f"DH-{task_id}" in existing_ids:
            continue
        priority_items.append({
            "kind": "local_task",
            "id": task_id,
            "title": task.get("title", "local task"),
            "why": task.get("operator_note", task.get("stop_condition", "")),
            "source": "task_ledger",
            "status": task.get("status", "carried"),
            "href": links.get("task_ledger", ""),
            "copy_ready_command": f'{task_id} carry "내일 계속 확인"' if task_id else "",
            "requires_separate_approval": False,
            "external_effect_performed": False,
            "host_write_performed": False,
        })

    status = "clear"
    if pending_decisions:
        status = "approval_review"
    elif unresolved or study_items or carried_tasks or ready_tasks or recommended:
        status = "needs_attention"

    return {
        "pattern_source": "Hermes/OpenClaw operator handoff",
        "status": status,
        "summary": {
            "pending_decision_count": len(pending_decisions),
            "unresolved_handoff_count": len(unresolved),
            "study_closure_count": len(study_items),
            "pattern_scout_count": 1 if recommended else 0,
            "pattern_scout_proof_ready_count": 1 if scout_proof.get("proof_status") == "passed" else 0,
            "pattern_evidence_intake_count": 1 if pattern_evidence_intake.get("schema_version") == PATTERN_EVIDENCE_INTAKE_SCHEMA_VERSION else 0,
            "pattern_evidence_local_candidate_count": pattern_evidence_intake.get("summary", {}).get("local_candidate_count", 0),
            "pattern_evidence_already_verified_count": pattern_evidence_intake.get("summary", {}).get("already_verified_count", 0),
            "source_freshness_intake_count": 1 if source_freshness_intake.get("schema_version") == SOURCE_FRESHNESS_INTAKE_SCHEMA_VERSION else 0,
            "source_refresh_execution_count": 1 if source_refresh_execution_brief.get("schema_version") == SOURCE_REFRESH_EXECUTION_BRIEF_SCHEMA_VERSION else 0,
            "source_refresh_execution_blocker_count": source_refresh_execution_brief.get("summary", {}).get("blocker_count", 0),
            "handoff_resolution_count": 1 if handoff_study_resolution.get("schema_version") == HANDOFF_STUDY_RESOLUTION_SCHEMA_VERSION else 0,
            "handoff_resolution_ready_count": handoff_study_resolution.get("summary", {}).get("ready_to_study_count", 0),
            "handoff_resolution_blocked_count": handoff_study_resolution.get("summary", {}).get("blocked_by_source_freshness_count", 0),
            "carried_task_count": len(carried_tasks),
            "ready_task_count": len(ready_tasks),
            "priority_item_count": len(priority_items),
        },
        "priority_items": priority_items[:8],
        "operator_rule": "action inbox: 먼저 approval gate를 읽되, 실행은 별도 승인 전까지 하지 않습니다. 그 다음 pattern scout와 study closure 질문을 읽고 local 응답 한 줄로 내일 루프에 넘깁니다.",
        "phone_links": {
            "morning": links.get("morning", ""),
            "handoff": links.get("handoff", ""),
            "handoff_study_resolution": links.get("handoff_study_resolution", ""),
            "handoff_apply": links.get("handoff_apply", ""),
            "task_ledger": links.get("task_ledger", ""),
            "pattern_radar": links.get("pattern_radar", ""),
            "pattern_dry_run": links.get("pattern_dry_run", ""),
            "pattern_evidence_intake": links.get("pattern_evidence_intake", ""),
            "source_freshness_intake": links.get("source_freshness_intake", ""),
            "source_refresh_execution": links.get("source_refresh_execution", ""),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
    }


def build_daily_operator_home(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    agenda_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    today_path: str | Path = DEFAULT_TODAY_OUTPUT,
    morning_path: str | Path = DEFAULT_MORNING_CONTROL_OUTPUT,
    readiness_path: str | Path = DEFAULT_DAILY_READINESS_OUTPUT,
    handoff_path: str | Path = DEFAULT_DAILY_HANDOFF_OUTPUT,
    handoff_study_resolution_path: str | Path = DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT,
    handoff_apply_path: str | Path = DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT,
    run_ledger_path: str | Path = DEFAULT_DAILY_RUN_LEDGER_OUTPUT,
    run_trace_path: str | Path = DEFAULT_RUN_TRACE_OUTPUT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    scheduler_operations_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_OUTPUT,
    phone_access_path: str | Path = DEFAULT_PHONE_ACCESS_OUTPUT,
    phone_access_verify_path: str | Path = DEFAULT_PHONE_ACCESS_VERIFY_OUTPUT,
    notification_path: str | Path = DEFAULT_NOTIFICATION_OUTPUT,
    source_freshness_intake_path: str | Path = DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT,
    source_refresh_execution_brief_path: str | Path = DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT,
    memory_query_path: str | Path = DEFAULT_MEMORY_QUERY_OUTPUT,
    memory_audit_path: str | Path = DEFAULT_MEMORY_AUDIT_OUTPUT,
    learning_ledger_path: str | Path = DEFAULT_LEARNING_LEDGER_OUTPUT,
    pattern_radar_path: str | Path = DEFAULT_AGENT_PATTERN_RADAR_OUTPUT,
    pattern_dry_run_proof_path: str | Path = DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT,
    pattern_evidence_intake_path: str | Path = DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(timezone.utc)
    scout = _load_optional_json(scout_path)
    agenda = _load_optional_json(agenda_path)
    morning = _load_optional_json(morning_path)
    readiness = _load_optional_json(readiness_path)
    handoff = _load_optional_json(handoff_path)
    handoff_study_resolution = _load_optional_json(handoff_study_resolution_path)
    handoff_apply = _load_optional_json(handoff_apply_path)
    run_ledger = _load_optional_json(run_ledger_path)
    run_trace = _load_optional_json(run_trace_path)
    task_ledger = _load_optional_json(task_ledger_path)
    scheduler = _load_optional_json(scheduler_operations_path)
    phone_access = _load_optional_json(phone_access_path)
    phone_access_verify = _load_optional_json(phone_access_verify_path)
    notification = _load_optional_json(notification_path)
    source_freshness_intake = _load_optional_json(source_freshness_intake_path)
    source_refresh_execution_brief = _load_optional_json(source_refresh_execution_brief_path)
    memory_query = _load_optional_json(memory_query_path)
    memory_audit = _load_optional_json(memory_audit_path)
    learning_ledger = _load_optional_json(learning_ledger_path)
    pattern_radar = _load_optional_json(pattern_radar_path)
    pattern_proof = _load_optional_json(pattern_dry_run_proof_path)
    pattern_evidence_intake = _load_optional_json(pattern_evidence_intake_path)
    read_first = morning.get("read_first", {})
    scout_topic = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    primary_agenda = agenda.get("primary_topic", {}) if agenda.get("schema_version") == DAILY_BRIEF_AGENDA_SCHEMA_VERSION else {}
    autonomous_topic = scout_topic or primary_agenda
    operator_brief = autonomous_topic.get("operator_brief", {})
    autonomous_name = autonomous_topic.get("name", read_first.get("title", "오늘 브리프"))
    autonomous_why = operator_brief.get(
        "why_today",
        primary_agenda.get("why_today", read_first.get("reason", "오늘 생성된 beginner brief를 먼저 읽습니다.")),
    )
    autonomous_confidence = operator_brief.get(
        "confidence_note",
        primary_agenda.get("confidence_note", "신뢰도는 로컬 산출물과 readiness를 함께 확인해야 합니다."),
    )
    autonomous_missing = operator_brief.get(
        "missing_evidence_note",
        primary_agenda.get("missing_evidence_note", "source freshness와 weak evidence를 agenda에서 확인하세요."),
    )
    unresolved_count = int(handoff.get("summary", {}).get("unresolved_count", 0) or 0)
    pending_decision_count = len(morning.get("pending_decisions", []))
    required_stale = int(readiness.get("summary", {}).get("stale_required_count", 0) or 0)
    required_missing = int(readiness.get("summary", {}).get("missing_required_count", 0) or 0)
    recall_quality = memory_query.get("recall_quality", {}) if memory_query.get("schema_version") == MEMORY_QUERY_SCHEMA_VERSION else {}
    recall_proof = next(
        (
            row for row in pattern_proof.get("candidate_results", [])
            if row.get("candidate_id") == "pattern-memory-recall-quality"
        ),
        {},
    )
    trace_proof = next(
        (
            row for row in pattern_proof.get("candidate_results", [])
            if row.get("candidate_id") == "pattern-run-trace-observability"
        ),
        {},
    )
    pattern_scout = pattern_radar.get("pattern_scout", {}) if pattern_radar.get("schema_version") == AGENT_PATTERN_RADAR_SCHEMA_VERSION else {}
    pattern_recommended = pattern_scout.get("recommended_next", {})
    pattern_scout_proof = next(
        (
            row for row in pattern_proof.get("candidate_results", [])
            if row.get("candidate_id") == pattern_recommended.get("candidate_id")
        ),
        {},
    )
    trace_summary = run_trace.get("summary", {}) if run_trace.get("schema_version") == RUN_TRACE_SCHEMA_VERSION else {}
    if required_missing or morning.get("status") == "blocked" or readiness.get("status") == "blocked":
        status = "blocked"
    elif unresolved_count or pending_decision_count or required_stale or morning.get("status") == "operator_review":
        status = "operator_review"
    else:
        status = "ready"
    links = {
        "daily_home": DEFAULT_DAILY_HOME_SURFACE.as_posix(),
        "today": Path(today_path).as_posix(),
        "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
        "agenda": DEFAULT_DAILY_BRIEF_AGENDA_SURFACE.as_posix(),
        "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
        "handoff": DEFAULT_DAILY_HANDOFF_SURFACE.as_posix(),
        "handoff_study_resolution": DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE.as_posix(),
        "handoff_apply": DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE.as_posix(),
        "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
        "review_effect": DEFAULT_REVIEW_EFFECT_SURFACE.as_posix(),
        "memory": DEFAULT_MEMORY_OUTPUT.as_posix(),
        "memory_query": DEFAULT_MEMORY_QUERY_SURFACE.as_posix(),
        "memory_audit": DEFAULT_MEMORY_AUDIT_SURFACE.as_posix(),
        "learning": DEFAULT_LEARNING_LEDGER_SURFACE.as_posix(),
        "source_freshness_intake": DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE.as_posix(),
        "source_refresh_execution": DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE.as_posix(),
        "pattern_radar": DEFAULT_AGENT_PATTERN_RADAR_SURFACE.as_posix(),
        "pattern_dry_run": DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE.as_posix(),
        "pattern_evidence_intake": DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE.as_posix(),
        "trace": DEFAULT_RUN_TRACE_SURFACE.as_posix(),
        "tasks": DEFAULT_ANALYST_TASK_QUEUE_OUTPUT.as_posix(),
        "task_ledger": DEFAULT_ANALYST_TASK_LEDGER_OUTPUT.as_posix(),
        "scheduler": DEFAULT_SCHEDULER_OPERATIONS_SURFACE.as_posix(),
        "phone_access": DEFAULT_PHONE_ACCESS_VERIFY_SURFACE.as_posix(),
        "phone_access_plan": Path(phone_access_path).as_posix(),
        "notification": Path(notification_path).as_posix(),
    }
    daily_route = [
        {
            "step": 1,
            "label": "오늘 주제 잡기",
            "title": autonomous_name,
            "why": autonomous_why,
            "href": links["agenda"],
            "status": "ready" if agenda.get("schema_version") == DAILY_BRIEF_AGENDA_SCHEMA_VERSION else "missing",
        },
        {
            "step": 2,
            "label": "먼저 읽기",
            "title": read_first.get("title", "오늘 브리프"),
            "why": read_first.get("reason", "오늘 생성된 beginner brief를 먼저 읽습니다."),
            "href": links["today"],
            "status": "ready" if Path(today_path).exists() else "missing",
        },
        {
            "step": 3,
            "label": "오늘 배운 것 남기기",
            "title": "learning ledger",
            "why": "오늘 배운 개념, 반복 관찰, 내일 질문을 한 화면에 누적합니다.",
            "href": links["learning"],
            "status": learning_ledger.get("status", "missing"),
        },
        {
            "step": 4,
            "label": "과거 기억 먼저 불러오기",
            "title": "memory recall",
            "why": f"{autonomous_name}에 대해 로컬 vault, archive, memory가 무엇을 기억하는지 먼저 확인합니다.",
            "href": links["memory_query"],
            "status": memory_query.get("status", "missing"),
        },
        {
            "step": 5,
            "label": "근거 신선도 승인 전 점검",
            "title": "source freshness intake",
            "why": "sample/cache 근거와 blocked live refresh 후보를 한 화면에서 보고, 승인 범위를 복사 전에 확인합니다.",
            "href": links["source_freshness_intake"],
            "status": source_freshness_intake.get("status", "missing"),
        },
        {
            "step": 6,
            "label": "live refresh 실행 전 확인",
            "title": "source refresh execution",
            "why": "승인, preflight, stop 조건, rollback, 실행 후 흡수 경로를 live network 없이 확인합니다.",
            "href": links["source_refresh_execution"],
            "status": source_refresh_execution_brief.get("status", "missing"),
        },
        {
            "step": 7,
            "label": "오늘 결과 영향 경로 확인",
            "title": "run trace",
            "why": "오늘 scout, 근거, memory, review, pattern gate 중 무엇이 결과를 만들었는지 compact trace로 확인합니다.",
            "href": links["trace"],
            "status": run_trace.get("status", "missing"),
        },
        {
            "step": 8,
            "label": "운영 상태 확인",
            "title": "morning control",
            "why": "막힌 승인, 오늘 task, runtime 상태를 확인합니다.",
            "href": links["morning"],
            "status": morning.get("status", "missing"),
        },
        {
            "step": 9,
            "label": "신뢰도 확인",
            "title": "readiness",
            "why": "오늘 파일이 fresh한지, 빠진 필수 artifact가 있는지 확인합니다.",
            "href": links["readiness"],
            "status": readiness.get("status", "missing"),
        },
        {
            "step": 10,
            "label": "남은 질문 공부로 닫기",
            "title": "handoff study resolution",
            "why": "전날에서 넘어온 질문을 답변 후보, 근거, 종료 조건, 복사 응답으로 정리합니다.",
            "href": links["handoff_study_resolution"],
            "status": handoff_study_resolution.get("status", "missing"),
        },
        {
            "step": 11,
            "label": "전날 맥락 닫기",
            "title": "handoff",
            "why": f"남은 항목 {unresolved_count}개를 보고 필요한 응답을 복사합니다.",
            "href": links["handoff"],
            "status": handoff.get("status", "missing"),
        },
        {
            "step": 12,
            "label": "응답 반영 확인",
            "title": "handoff apply proof",
            "why": "복사한 응답이 review memory 또는 task state에 반영됐는지 확인합니다.",
            "href": links["handoff_apply"],
            "status": handoff_apply.get("status", "missing"),
        },
        {
            "step": 13,
            "label": "기억 품질 확인",
            "title": "memory audit",
            "why": "누적 기억, archive, source weakness를 확인하고 다음 질문을 고릅니다.",
            "href": links["memory_audit"],
            "status": memory_audit.get("status", "missing"),
        },
        {
            "step": 14,
            "label": "새 방법론 근거 분류",
            "title": "pattern evidence intake",
            "why": "최신 에이전트/투자 워크플로 사례를 이미 검증됨, 신규 local 후보, 승인 필요, 차단으로 나눠 반복 추천을 막습니다.",
            "href": links["pattern_evidence_intake"],
            "status": pattern_evidence_intake.get("status", "missing"),
        },
        {
            "step": 15,
            "label": "새 작업 방식 증거 확인",
            "title": "pattern dry-run proof",
            "why": "새 에이전트 운영 패턴을 실제 루프에 더 깊게 넣어도 되는지 로컬 증거로 확인합니다.",
            "href": links["pattern_dry_run"],
            "status": pattern_proof.get("status", "missing"),
        },
    ]
    payloads = {"morning": morning, "handoff": handoff}
    action_inbox = _daily_home_action_inbox(
        morning=morning,
        handoff=handoff,
        handoff_study_resolution=handoff_study_resolution,
        task_ledger=task_ledger,
        source_freshness_intake=source_freshness_intake,
        source_refresh_execution_brief=source_refresh_execution_brief,
        pattern_radar=pattern_radar,
        pattern_proof=pattern_proof,
        pattern_evidence_intake=pattern_evidence_intake,
        links=links,
    )
    payload = {
        "schema_version": DAILY_OPERATOR_HOME_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": status,
        "summary": {
            "read_first": read_first.get("title", "오늘 브리프"),
            "unresolved_handoff_count": unresolved_count,
            "pending_decision_count": pending_decision_count,
            "required_stale_count": required_stale,
            "required_missing_count": required_missing,
            "scheduler_status": scheduler.get("status", "missing"),
            "notification_status": notification.get("delivery_status", "missing"),
            "phone_access_path": phone_access.get("recommended_path", "missing"),
            "autonomous_topic": autonomous_name,
            "autonomous_reason": autonomous_why,
            "scout_operator_input_required": scout.get("autonomous_start", {}).get("operator_input_required", False),
            "memory_recall_quality": recall_quality.get("level", "missing"),
            "memory_recall_matches": int(memory_query.get("matched_topic_count", 0) or 0) + int(memory_query.get("matched_archive_count", 0) or 0) + int(memory_query.get("matched_vault_note_count", 0) or 0),
            "learning_status": learning_ledger.get("status", "missing"),
            "learning_concept_count": learning_ledger.get("summary", {}).get("concept_count", 0),
            "learning_question_count": learning_ledger.get("summary", {}).get("question_count", 0),
            "source_freshness_intake_status": source_freshness_intake.get("status", "missing"),
            "source_freshness_blocked_live_count": source_freshness_intake.get("summary", {}).get("blocked_live_candidate_count", 0),
            "source_freshness_weak_count": source_freshness_intake.get("summary", {}).get("stale_or_sample_source_count", 0),
            "source_refresh_execution_status": source_refresh_execution_brief.get("status", "missing"),
            "source_refresh_execution_preflight": source_refresh_execution_brief.get("summary", {}).get("preflight_status", "missing"),
            "source_refresh_execution_blockers": source_refresh_execution_brief.get("summary", {}).get("blocker_count", 0),
            "handoff_resolution_status": handoff_study_resolution.get("status", "missing"),
            "handoff_resolution_ready_count": handoff_study_resolution.get("summary", {}).get("ready_to_study_count", 0),
            "handoff_resolution_blocked_count": handoff_study_resolution.get("summary", {}).get("blocked_by_source_freshness_count", 0),
            "trace_status": run_trace.get("status", "missing"),
            "trace_fresh_count": trace_summary.get("fresh_count", 0),
            "trace_weak_spot_count": len(run_trace.get("weak_spots", [])),
            "pattern_scout_candidate": pattern_recommended.get("candidate_id", "missing"),
            "pattern_scout_proof_status": pattern_scout_proof.get("proof_status", "missing"),
            "pattern_evidence_intake_status": pattern_evidence_intake.get("status", "missing"),
            "pattern_evidence_local_candidate_count": pattern_evidence_intake.get("summary", {}).get("local_candidate_count", 0),
            "pattern_evidence_already_verified_count": pattern_evidence_intake.get("summary", {}).get("already_verified_count", 0),
            "action_item_count": action_inbox.get("summary", {}).get("priority_item_count", 0),
        },
        "daily_route": daily_route,
        "autonomous_scout": {
            "mode": scout.get("autonomous_start", {}).get("mode", "system_recommends_first_topic"),
            "operator_input_required": scout.get("autonomous_start", {}).get("operator_input_required", False),
            "recommended_topic": autonomous_topic,
            "headline": operator_brief.get("headline", primary_agenda.get("headline", f"오늘은 {autonomous_name}부터 봅니다.")),
            "why_today": autonomous_why,
            "confidence_note": autonomous_confidence,
            "missing_evidence_note": autonomous_missing,
            "copy_ready_responses": (
                autonomous_topic.get("copy_ready_responses")
                or agenda.get("copy_ready_responses")
                or [{
                    "intent": "more",
                    "command": f'more "{autonomous_name}" "내일도 이 주제를 더 보고 싶다"',
                    "effect": "다음 로컬 실행에 반영합니다.",
                }]
            )[:3],
        },
        "memory_recall_adoption": {
            "pattern_candidate_id": "pattern-memory-recall-quality",
            "proof_status": recall_proof.get("proof_status", "missing"),
            "query": memory_query.get("query", autonomous_name),
            "status": memory_query.get("status", "missing"),
            "quality_level": recall_quality.get("level", "missing"),
            "quality_summary": recall_quality.get("summary", "아직 로컬 기억 회상 품질을 판단할 수 없습니다."),
            "coverage_label": recall_quality.get("coverage_label", "unknown"),
            "confidence": recall_quality.get("confidence", "low"),
            "matched_topic_count": memory_query.get("matched_topic_count", 0),
            "matched_archive_count": memory_query.get("matched_archive_count", 0),
            "matched_vault_note_count": memory_query.get("matched_vault_note_count", 0),
            "weak_spots": memory_query.get("weak_spots", [])[:3],
            "next_questions": memory_query.get("next_questions", [])[:3],
            "surface": links["memory_query"],
            "external_effect_performed": False,
        },
        "trace_observability_adoption": {
            "pattern_candidate_id": "pattern-run-trace-observability",
            "proof_status": trace_proof.get("proof_status", "missing"),
            "status": run_trace.get("status", "missing"),
            "run_id": run_trace.get("run_id", "missing"),
            "step_count": trace_summary.get("step_count", 0),
            "fresh_count": trace_summary.get("fresh_count", 0),
            "missing_required_count": trace_summary.get("missing_required_count", 0),
            "stale_count": trace_summary.get("stale_count", 0),
            "external_effect_flag_count": trace_summary.get("external_effect_flag_count", 0),
            "what_shaped_today": run_trace.get("what_shaped_today", [])[:6],
            "weak_spots": run_trace.get("weak_spots", [])[:4],
            "debug_order": run_trace.get("operator_debug_order", [])[:8],
            "surface": links["trace"],
            "external_effect_performed": False,
            "host_write_performed": False,
        },
        "source_freshness_intake_adoption": {
            "pattern_candidate_id": "pattern-freshness-intake",
            "status": source_freshness_intake.get("status", "missing"),
            "source_count": source_freshness_intake.get("summary", {}).get("source_count", 0),
            "stale_or_sample_source_count": source_freshness_intake.get("summary", {}).get("stale_or_sample_source_count", 0),
            "blocked_live_candidate_count": source_freshness_intake.get("summary", {}).get("blocked_live_candidate_count", 0),
            "approval_scope": source_freshness_intake.get("approval_packet", {}).get("approval_scope", ""),
            "copy_ready_response": source_freshness_intake.get("approval_packet", {}).get("copy_ready_response", ""),
            "next_action": source_freshness_intake.get("next_action", ""),
            "surface": links["source_freshness_intake"],
            "external_effect_performed": False,
            "host_write_performed": False,
        },
        "source_refresh_execution_adoption": {
            "pattern_candidate_id": "pattern-source-refresh-final-confirmation",
            "status": source_refresh_execution_brief.get("status", "missing"),
            "approval_status": source_refresh_execution_brief.get("summary", {}).get("approval_status", "missing"),
            "live_run_status": source_refresh_execution_brief.get("summary", {}).get("live_run_status", "missing"),
            "preflight_status": source_refresh_execution_brief.get("summary", {}).get("preflight_status", "missing"),
            "blocker_count": source_refresh_execution_brief.get("summary", {}).get("blocker_count", 0),
            "final_confirmation_required": source_refresh_execution_brief.get("final_confirmation", {}).get("required", False),
            "stop_conditions": source_refresh_execution_brief.get("stop_conditions", [])[:4],
            "surface": links["source_refresh_execution"],
            "external_effect_performed": False,
            "host_write_performed": False,
        },
        "pattern_scout_adoption": {
            "pattern_candidate_id": pattern_recommended.get("candidate_id", "missing"),
            "proof_status": pattern_scout_proof.get("proof_status", "missing"),
            "status": pattern_scout.get("status", "missing"),
            "title": pattern_recommended.get("title", "다음 local-only 방식 실험 없음"),
            "source": pattern_recommended.get("source", ""),
            "why_now": pattern_recommended.get("why_now", ""),
            "approval_scope": pattern_recommended.get("approval_scope", ""),
            "operator_decision_needed": bool(pattern_recommended.get("operator_decision_needed", True)),
            "done_when": pattern_recommended.get("done_when", [])[:5],
            "deferred_watchlist": pattern_scout.get("deferred_watchlist", [])[:4],
            "rejected_boundary": pattern_scout.get("rejected_boundary", [])[:4],
            "surface": links["pattern_radar"],
            "proof_surface": links["pattern_dry_run"],
            "external_effect_performed": False,
            "host_write_performed": False,
        },
        "pattern_evidence_intake_adoption": {
            "pattern_candidate_id": "pattern-method-evidence-intake",
            "status": pattern_evidence_intake.get("status", "missing"),
            "candidate_count": pattern_evidence_intake.get("summary", {}).get("candidate_count", 0),
            "local_candidate_count": pattern_evidence_intake.get("summary", {}).get("local_candidate_count", 0),
            "already_verified_count": pattern_evidence_intake.get("summary", {}).get("already_verified_count", 0),
            "approval_gated_count": pattern_evidence_intake.get("summary", {}).get("approval_gated_count", 0),
            "blocked_count": pattern_evidence_intake.get("summary", {}).get("blocked_count", 0),
            "recommended_candidate": pattern_evidence_intake.get("summary", {}).get("recommended_candidate", "missing"),
            "surface": links["pattern_evidence_intake"],
            "external_effect_performed": False,
            "host_write_performed": False,
        },
        "operator_action_inbox": action_inbox,
        "copy_ready_commands": _daily_home_commands(payloads=payloads),
        "phone_links": links,
        "access": {
            "recommended_path": phone_access.get("recommended_path", "missing"),
            "local_url": phone_access.get("local_url", ""),
            "private_phone_url": phone_access.get("private_phone_url", ""),
            "requires_separate_approval": True,
        },
        "notification": {
            "delivery_status": notification.get("delivery_status", "missing"),
            "dry_run": notification.get("dry_run", True),
            "send_requires_separate_approval": True,
        },
        "artifacts": [
            _daily_home_artifact_status(name="scout", path=scout_path, payload=scout),
            _daily_home_artifact_status(name="agenda", path=agenda_path, payload=agenda),
            _daily_home_artifact_status(name="morning", path=morning_path, payload=morning),
            _daily_home_artifact_status(name="readiness", path=readiness_path, payload=readiness),
            _daily_home_artifact_status(name="handoff", path=handoff_path, payload=handoff),
            _daily_home_artifact_status(name="handoff_study_resolution", path=handoff_study_resolution_path, payload=handoff_study_resolution),
            _daily_home_artifact_status(name="handoff_apply", path=handoff_apply_path, payload=handoff_apply),
            _daily_home_artifact_status(name="run_ledger", path=run_ledger_path, payload=run_ledger),
            _daily_home_artifact_status(name="run_trace", path=run_trace_path, payload=run_trace),
            _daily_home_artifact_status(name="task_ledger", path=task_ledger_path, payload=task_ledger),
            _daily_home_artifact_status(name="scheduler", path=scheduler_operations_path, payload=scheduler),
            _daily_home_artifact_status(name="phone_access", path=phone_access_path, payload=phone_access),
            _daily_home_artifact_status(name="phone_access_verify", path=phone_access_verify_path, payload=phone_access_verify),
            _daily_home_artifact_status(name="notification", path=notification_path, payload=notification),
            _daily_home_artifact_status(name="memory_query", path=memory_query_path, payload=memory_query),
            _daily_home_artifact_status(name="memory_audit", path=memory_audit_path, payload=memory_audit),
            _daily_home_artifact_status(name="learning_ledger", path=learning_ledger_path, payload=learning_ledger),
            _daily_home_artifact_status(name="source_freshness_intake", path=source_freshness_intake_path, payload=source_freshness_intake),
            _daily_home_artifact_status(name="source_refresh_execution_brief", path=source_refresh_execution_brief_path, payload=source_refresh_execution_brief),
            _daily_home_artifact_status(name="pattern_radar", path=pattern_radar_path, payload=pattern_radar),
            _daily_home_artifact_status(name="pattern_dry_run_proof", path=pattern_dry_run_proof_path, payload=pattern_proof),
            _daily_home_artifact_status(name="pattern_evidence_intake", path=pattern_evidence_intake_path, payload=pattern_evidence_intake),
        ],
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "daily_home_reads_existing_artifacts_only",
            "does_not_execute_tasks",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_order_execution",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_daily_operator_home(
    *,
    artifact_output_path: str | Path = DEFAULT_DAILY_HOME_OUTPUT,
    surface_output_path: str | Path = DEFAULT_DAILY_HOME_SURFACE,
    **paths: Any,
) -> Path:
    payload = build_daily_operator_home(**paths)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_daily_operator_home(payload), encoding="utf-8")
    return target


def validate_daily_operator_home_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DAILY_OPERATOR_HOME_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"ready", "operator_review", "blocked"}:
        errors.append(f"invalid status {payload.get('status')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if not payload.get("daily_route"):
        errors.append("daily_route must not be empty")
    autonomous = payload.get("autonomous_scout", {})
    if autonomous.get("mode") != "system_recommends_first_topic":
        errors.append("autonomous_scout.mode must be system_recommends_first_topic")
    if autonomous.get("operator_input_required") is not False:
        errors.append("autonomous_scout.operator_input_required must be false")
    if not autonomous.get("why_today"):
        errors.append("autonomous_scout.why_today must not be empty")
    recall = payload.get("memory_recall_adoption", {})
    for field in ["pattern_candidate_id", "proof_status", "query", "status", "quality_level", "quality_summary", "surface", "external_effect_performed"]:
        if field not in recall:
            errors.append(f"memory_recall_adoption missing {field}")
    if recall.get("external_effect_performed") is not False:
        errors.append("memory_recall_adoption.external_effect_performed must be false")
    trace = payload.get("trace_observability_adoption", {})
    for field in ["pattern_candidate_id", "proof_status", "status", "run_id", "step_count", "what_shaped_today", "surface", "external_effect_performed", "host_write_performed"]:
        if field not in trace:
            errors.append(f"trace_observability_adoption missing {field}")
    if trace.get("external_effect_performed") is not False:
        errors.append("trace_observability_adoption.external_effect_performed must be false")
    if trace.get("host_write_performed") is not False:
        errors.append("trace_observability_adoption.host_write_performed must be false")
    if trace.get("status") not in {"ready", "review", "blocked", "missing"}:
        errors.append("trace_observability_adoption.status must be ready, review, blocked, or missing")
    if trace.get("step_count", 0) and not trace.get("what_shaped_today"):
        errors.append("trace_observability_adoption.what_shaped_today must not be empty when trace exists")
    intake = payload.get("source_freshness_intake_adoption", {})
    for field in ["pattern_candidate_id", "status", "source_count", "stale_or_sample_source_count", "blocked_live_candidate_count", "surface", "external_effect_performed", "host_write_performed"]:
        if field not in intake:
            errors.append(f"source_freshness_intake_adoption missing {field}")
    if intake.get("external_effect_performed") is not False:
        errors.append("source_freshness_intake_adoption.external_effect_performed must be false")
    if intake.get("host_write_performed") is not False:
        errors.append("source_freshness_intake_adoption.host_write_performed must be false")
    execution = payload.get("source_refresh_execution_adoption", {})
    for field in ["pattern_candidate_id", "status", "approval_status", "live_run_status", "preflight_status", "blocker_count", "final_confirmation_required", "stop_conditions", "surface", "external_effect_performed", "host_write_performed"]:
        if field not in execution:
            errors.append(f"source_refresh_execution_adoption missing {field}")
    if execution.get("external_effect_performed") is not False:
        errors.append("source_refresh_execution_adoption.external_effect_performed must be false")
    if execution.get("host_write_performed") is not False:
        errors.append("source_refresh_execution_adoption.host_write_performed must be false")
    pattern = payload.get("pattern_scout_adoption", {})
    for field in ["pattern_candidate_id", "proof_status", "status", "title", "why_now", "approval_scope", "done_when", "surface", "proof_surface", "external_effect_performed", "host_write_performed"]:
        if field not in pattern:
            errors.append(f"pattern_scout_adoption missing {field}")
    if pattern.get("external_effect_performed") is not False:
        errors.append("pattern_scout_adoption.external_effect_performed must be false")
    if pattern.get("host_write_performed") is not False:
        errors.append("pattern_scout_adoption.host_write_performed must be false")
    if pattern.get("operator_decision_needed") is not False and pattern.get("approval_scope") == "local_dry_run_only":
        errors.append("local pattern scout must not require operator approval")
    pattern_evidence = payload.get("pattern_evidence_intake_adoption", {})
    for field in ["pattern_candidate_id", "status", "candidate_count", "local_candidate_count", "already_verified_count", "approval_gated_count", "blocked_count", "recommended_candidate", "surface", "external_effect_performed", "host_write_performed"]:
        if field not in pattern_evidence:
            errors.append(f"pattern_evidence_intake_adoption missing {field}")
    if pattern_evidence.get("external_effect_performed") is not False:
        errors.append("pattern_evidence_intake_adoption.external_effect_performed must be false")
    if pattern_evidence.get("host_write_performed") is not False:
        errors.append("pattern_evidence_intake_adoption.host_write_performed must be false")
    inbox = payload.get("operator_action_inbox", {})
    for field in ["pattern_source", "status", "summary", "priority_items", "operator_rule", "external_effect_performed", "host_write_performed"]:
        if field not in inbox:
            errors.append(f"operator_action_inbox missing {field}")
    if inbox.get("status") not in {"clear", "needs_attention", "approval_review"}:
        errors.append("operator_action_inbox.status must be clear, needs_attention, or approval_review")
    if inbox.get("external_effect_performed") is not False:
        errors.append("operator_action_inbox.external_effect_performed must be false")
    if inbox.get("host_write_performed") is not False:
        errors.append("operator_action_inbox.host_write_performed must be false")
    for index, item in enumerate(inbox.get("priority_items", [])):
        for field in ["kind", "id", "title", "why", "source", "status", "href", "requires_separate_approval", "external_effect_performed", "host_write_performed"]:
            if field not in item:
                errors.append(f"operator_action_inbox.priority_items[{index}] missing {field}")
        if item.get("external_effect_performed") is not False:
            errors.append(f"operator_action_inbox.priority_items[{index}] external_effect_performed must be false")
        if item.get("host_write_performed") is not False:
            errors.append(f"operator_action_inbox.priority_items[{index}] host_write_performed must be false")
    for field in ["daily_home", "today", "morning", "readiness", "handoff", "handoff_study_resolution", "handoff_apply", "learning", "source_freshness_intake", "source_refresh_execution", "memory_query", "trace", "pattern_radar", "pattern_dry_run", "pattern_evidence_intake"]:
        if not payload.get("phone_links", {}).get(field):
            errors.append(f"phone_links.{field} must not be empty")
    if "daily_home_reads_existing_artifacts_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include daily_home_reads_existing_artifacts_only")
    forbidden_fragments = [" --send", "--confirm-host-write", "--execute", "launchctl bootstrap"]
    for index, command in enumerate(payload.get("copy_ready_commands", [])):
        command_text = command.get("command", "")
        if not command_text:
            errors.append(f"copy_ready_commands[{index}] missing command")
        if any(fragment in command_text for fragment in forbidden_fragments):
            errors.append(f"copy_ready_commands[{index}] includes gated execution fragment")
        if command.get("external_effect_performed") is not False:
            errors.append(f"copy_ready_commands[{index}] external_effect_performed must be false")
    for index, step in enumerate(payload.get("daily_route", [])):
        for field in ["step", "label", "title", "why", "href", "status"]:
            if field not in step:
                errors.append(f"daily_route[{index}] missing {field}")
    if not any(step.get("title") == "learning ledger" for step in payload.get("daily_route", [])):
        errors.append("daily_route must include learning ledger")
    if not any(step.get("title") == "source freshness intake" for step in payload.get("daily_route", [])):
        errors.append("daily_route must include source freshness intake")
    if not any(step.get("title") == "source refresh execution" for step in payload.get("daily_route", [])):
        errors.append("daily_route must include source refresh execution")
    if not any(step.get("title") == "pattern evidence intake" for step in payload.get("daily_route", [])):
        errors.append("daily_route must include pattern evidence intake")
    if not any(step.get("title") == "handoff study resolution" for step in payload.get("daily_route", [])):
        errors.append("daily_route must include handoff study resolution")
    return errors


def validate_daily_operator_home_file(path: str | Path) -> list[str]:
    return validate_daily_operator_home_payload(load_json(path))


def render_daily_operator_home(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    autonomous = payload.get("autonomous_scout", {})
    recall = payload.get("memory_recall_adoption", {})
    trace = payload.get("trace_observability_adoption", {})
    intake = payload.get("source_freshness_intake_adoption", {})
    pattern = payload.get("pattern_scout_adoption", {})
    pattern_evidence = payload.get("pattern_evidence_intake_adoption", {})
    inbox = payload.get("operator_action_inbox", {})
    status_label = {
        "ready": "오늘 읽기 준비됨",
        "operator_review": "사람 확인 필요",
        "blocked": "먼저 막힌 상태 확인",
    }.get(payload.get("status", ""), payload.get("status", "unknown"))
    scheduler_label = {
        "manual_ready": "수동 준비",
        "activation_ready": "활성화 준비",
        "active_verified": "활성 확인",
        "not_ready": "준비 안 됨",
        "blocked": "막힘",
        "missing": "없음",
    }.get(str(summary.get("scheduler_status", "")), summary.get("scheduler_status", ""))
    route_cards = "".join(
        "<article class='route'>"
        f"<span>Step {esc(step.get('step', ''))} · {esc(step.get('status', ''))}</span>"
        f"<h2>{esc(step.get('label', ''))}</h2>"
        f"<strong>{esc(step.get('title', ''))}</strong>"
        f"<p>{esc(step.get('why', ''))}</p>"
        f"<a href='{esc(_relative_href(Path(step.get('href', ''))))}'>열기</a>"
        "</article>"
        for step in payload.get("daily_route", [])
    )
    command_cards = "".join(
        "<article class='command'>"
        f"<span>{esc(command.get('source', 'local'))} · {esc(command.get('label', 'command'))}</span>"
        f"<code>{esc(command.get('command', ''))}</code>"
        f"<small>{esc(command.get('why', ''))}</small>"
        "</article>"
        for command in payload.get("copy_ready_commands", [])
    ) or "<p>지금 복사할 로컬 응답 명령이 없습니다.</p>"
    scout_response_cards = "".join(
        "<article class='command'>"
        f"<span>scout · {esc(response.get('intent', 'response'))}</span>"
        f"<code>{esc(response.get('command', ''))}</code>"
        f"<small>{esc(response.get('effect', '다음 로컬 실행에 반영합니다.'))}</small>"
        "</article>"
        for response in autonomous.get("copy_ready_responses", [])
    ) or "<p>오늘 scout에 남길 짧은 응답이 아직 없습니다.</p>"
    inbox_summary = inbox.get("summary", {})
    inbox_cards = "".join(
        "<article class='command'>"
        f"<span>{esc(item.get('kind', 'action'))} · {esc(item.get('status', ''))}</span>"
        f"<h2>{esc(item.get('title', ''))}</h2>"
        f"<p>{esc(item.get('why', ''))}</p>"
        f"<small>{esc(item.get('source', ''))} · {esc('별도 승인 필요' if item.get('requires_separate_approval') else 'local only')}</small>"
        + (f"<code>{esc(item.get('copy_ready_command', ''))}</code>" if item.get("copy_ready_command") else "")
        + (f"<p><a href='{esc(_relative_href(Path(item.get('href', ''))))}'>관련 화면 열기</a></p>" if item.get("href") else "")
        + "</article>"
        for item in inbox.get("priority_items", [])
    ) or "<p>오늘 닫을 action inbox 항목은 없습니다.</p>"
    link_cards = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "daily_home" and path
    )
    recall_weak_items = "".join(f"<li>{esc(item)}</li>" for item in recall.get("weak_spots", [])) or "<li>오늘 회상에서 즉시 막힌 약점은 없습니다.</li>"
    recall_question_items = "".join(f"<li>{esc(item)}</li>" for item in recall.get("next_questions", [])) or "<li>오늘 주제와 연결된 질문이 아직 없습니다.</li>"
    trace_influence_items = "".join(
        "<li>"
        f"<strong>{esc(item.get('label', 'influence'))}</strong>: {esc(item.get('value', ''))}"
        f"<span> · {esc(item.get('source', ''))}</span>"
        "</li>"
        for item in trace.get("what_shaped_today", [])
    ) or "<li>아직 오늘 결과를 만든 trace influence가 없습니다.</li>"
    trace_weak_items = "".join(f"<li>{esc(item)}</li>" for item in trace.get("weak_spots", [])) or "<li>trace에서 즉시 막힌 약점은 없습니다.</li>"
    trace_debug_items = "".join(f"<li>{esc(item)}</li>" for item in trace.get("debug_order", [])) or "<li>debug 순서가 아직 없습니다.</li>"
    intake_response = intake.get("copy_ready_response", "")
    pattern_done_items = "".join(f"<li>{esc(item)}</li>" for item in pattern.get("done_when", [])) or "<li>아직 done-when 기준이 없습니다.</li>"
    pattern_watch_items = "".join(
        "<li>"
        f"<strong>{esc(item.get('source', 'watch'))}</strong>: {esc(item.get('why_watch', ''))}"
        f"<span> · {esc(item.get('blocked_by', ''))}</span>"
        "</li>"
        for item in pattern.get("deferred_watchlist", [])
    ) or "<li>오늘 보류 중인 새 방식은 없습니다.</li>"
    pattern_boundary_items = "".join(
        "<li>"
        f"<strong>{esc(item.get('source', 'boundary'))}</strong>: {esc(item.get('why_rejected', ''))}"
        f"<span> · {esc(item.get('boundary', ''))}</span>"
        "</li>"
        for item in pattern.get("rejected_boundary", [])
    ) or "<li>오늘 새로 확인할 거부 경계는 없습니다.</li>"
    artifact_rows = "".join(
        "<tr>"
        f"<td><strong>{esc(item.get('name', ''))}</strong><span>{esc(item.get('path', ''))}</span></td>"
        f"<td>{esc('yes' if item.get('exists') else 'no')}</td>"
        f"<td>{esc(item.get('status', ''))}</td>"
        "</tr>"
        for item in payload.get("artifacts", [])
    )
    access = payload.get("access", {})
    notification = payload.get("notification", {})
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Daily Home</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:820px; margin:0 auto; padding:16px; }}
a {{ color:var(--blue); font-weight:900; text-decoration:none; }}
.eyebrow,.route span,.command span,.metric span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:36px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small,td span {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.route,.command {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:30px; line-height:1.08; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:13px; min-width:0; }}
.metric strong {{ display:block; font-size:24px; overflow-wrap:anywhere; }}
.route-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.route,.command {{ background:white; padding:14px; min-width:0; }}
.route strong {{ display:block; font-size:20px; }}
.commands {{ display:grid; grid-template-columns:1fr; gap:10px; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
td strong,td span {{ display:block; }}
@media (max-width:680px) {{ main {{ padding:12px; }} h1 {{ font-size:30px; }} .metrics,.route-grid,.links {{ grid-template-columns:1fr; }} table {{ font-size:13px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Daily Home · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘의 개인 애널리스트 홈</h1>
<p>폰에서 매일 시작하는 한 화면입니다. 여기서는 읽기와 확인만 하며, 실행 권한은 별도 게이트에 남겨둡니다.</p>
</header>
<section class="hero">
<span class="eyebrow">오늘 판정</span>
<strong class="status">{esc(status_label)}</strong>
<p>먼저 볼 주제: {esc(summary.get('read_first', ''))}</p>
<div class="metrics">
<article class="metric"><span>Handoff</span><strong>{esc(summary.get('unresolved_handoff_count', 0))}</strong></article>
<article class="metric"><span>Decisions</span><strong>{esc(summary.get('pending_decision_count', 0))}</strong></article>
<article class="metric"><span>Missing</span><strong>{esc(summary.get('required_missing_count', 0))}</strong></article>
<article class="metric"><span>Actions</span><strong>{esc(summary.get('action_item_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>오늘 닫을 것</h2>
<p><strong>{esc(inbox.get('status', 'missing'))}</strong></p>
<p>{esc(inbox.get('operator_rule', '오늘 action inbox를 아직 만들 수 없습니다.'))}</p>
<div class="metrics">
	<article class="metric"><span>Approvals</span><strong>{esc(inbox_summary.get('pending_decision_count', 0))}</strong></article>
	<article class="metric"><span>Pattern</span><strong>{esc(inbox_summary.get('pattern_scout_count', 0))}</strong></article>
	<article class="metric"><span>Method</span><strong>{esc(inbox_summary.get('pattern_evidence_local_candidate_count', 0))}</strong></article>
	<article class="metric"><span>Study</span><strong>{esc(inbox_summary.get('study_closure_count', 0))}</strong></article>
	<article class="metric"><span>Handoff</span><strong>{esc(inbox_summary.get('unresolved_handoff_count', 0))}</strong></article>
	<article class="metric"><span>Carried</span><strong>{esc(inbox_summary.get('carried_task_count', 0))}</strong></article>
<article class="metric"><span>Ready</span><strong>{esc(inbox_summary.get('ready_task_count', 0))}</strong></article>
</div>
<div class="commands">{inbox_cards}</div>
</section>
<section class="section">
<h2>Scout가 먼저 고른 주제</h2>
<p><strong>{esc(autonomous.get('headline', summary.get('autonomous_topic', '오늘 추천 주제 없음')))}</strong></p>
<p>{esc(autonomous.get('why_today', summary.get('autonomous_reason', '')))}</p>
<p>{esc(autonomous.get('confidence_note', ''))}</p>
<p>{esc(autonomous.get('missing_evidence_note', ''))}</p>
<div class="commands">{scout_response_cards}</div>
</section>
<section class="section">
<h2>오늘 배운 것 누적</h2>
<p><strong>{esc(summary.get('learning_status', 'missing'))}</strong></p>
<p>오늘 브리프가 단발성 읽기로 끝나지 않도록, 배운 개념과 내일 이어갈 질문을 learning ledger에 남깁니다.</p>
<div class="metrics">
<article class="metric"><span>Concepts</span><strong>{esc(summary.get('learning_concept_count', 0))}</strong></article>
<article class="metric"><span>Questions</span><strong>{esc(summary.get('learning_question_count', 0))}</strong></article>
<article class="metric"><span>Status</span><strong>{esc(summary.get('learning_status', 'missing'))}</strong></article>
<article class="metric"><span>Mode</span><strong>local</strong></article>
</div>
<p><a href="{esc(_relative_href(Path(payload.get('phone_links', {}).get('learning', 'reports/product/learning.html'))))}">learning ledger 열기</a></p>
</section>
<section class="section">
<h2>오늘 기억 회상 품질</h2>
<p><strong>{esc(recall.get('quality_level', 'missing'))} · {esc(recall.get('coverage_label', 'unknown'))}</strong></p>
<p>{esc(recall.get('quality_summary', '로컬 기억 회상 품질을 아직 판단할 수 없습니다.'))}</p>
<div class="metrics">
<article class="metric"><span>Proof</span><strong>{esc(recall.get('proof_status', 'missing'))}</strong></article>
<article class="metric"><span>Topics</span><strong>{esc(recall.get('matched_topic_count', 0))}</strong></article>
<article class="metric"><span>Archives</span><strong>{esc(recall.get('matched_archive_count', 0))}</strong></article>
<article class="metric"><span>Vault</span><strong>{esc(recall.get('matched_vault_note_count', 0))}</strong></article>
</div>
<p><a href="{esc(_relative_href(Path(recall.get('surface', 'reports/product/memory-query.html'))))}">memory recall 열기</a></p>
<h2>약한 부분</h2>
<ul>{recall_weak_items}</ul>
<h2>이어갈 질문</h2>
<ul>{recall_question_items}</ul>
</section>
<section class="section">
<h2>오늘 결과를 만든 경로</h2>
<p><strong>{esc(trace.get('status', 'missing'))} · run {esc(trace.get('run_id', 'missing'))}</strong></p>
<p>TraceAgent식 관측 패턴을 daily loop에 채택한 요약입니다. 오늘 결과를 만든 입력, 빠진 단계, 오래된 단계, 외부효과 flag를 한 화면에서 먼저 봅니다.</p>
<div class="metrics">
<article class="metric"><span>Proof</span><strong>{esc(trace.get('proof_status', 'missing'))}</strong></article>
<article class="metric"><span>Steps</span><strong>{esc(trace.get('step_count', 0))}</strong></article>
<article class="metric"><span>Fresh</span><strong>{esc(trace.get('fresh_count', 0))}</strong></article>
<article class="metric"><span>Flags</span><strong>{esc(trace.get('external_effect_flag_count', 0))}</strong></article>
</div>
<p><a href="{esc(_relative_href(Path(trace.get('surface', 'reports/product/run-trace.html'))))}">run trace 열기</a></p>
<h2>영향 요약</h2>
<ul>{trace_influence_items}</ul>
<h2>약한 부분</h2>
<ul>{trace_weak_items}</ul>
<h2>문제 확인 순서</h2>
	<ul>{trace_debug_items}</ul>
	</section>
	<section class="section">
	<h2>근거 신선도 intake</h2>
	<div class="grid">
	<article class="metric"><span>Status</span><strong>{esc(intake.get('status', 'missing'))}</strong></article>
	<article class="metric"><span>Weak</span><strong>{esc(intake.get('stale_or_sample_source_count', 0))}</strong></article>
	<article class="metric"><span>Blocked live</span><strong>{esc(intake.get('blocked_live_candidate_count', 0))}</strong></article>
	<article class="metric"><span>Scope</span><strong>{esc(intake.get('approval_scope', ''))}</strong></article>
	</div>
	<p>{esc(intake.get('next_action', 'source freshness intake를 먼저 생성하세요.'))}</p>
	{f"<code>{esc(intake_response)}</code>" if intake_response else "<p>지금 복사할 source refresh 승인 응답은 없습니다.</p>"}
	<p><a href="{esc(_relative_href(Path(intake.get('surface', 'reports/product/source-freshness-intake.html'))))}">source freshness intake 열기</a></p>
	</section>
	<section class="section">
	<h2>오늘의 방식 Scout</h2>
	<p><strong>{esc(pattern.get('title', '다음 local-only 방식 실험 없음'))}</strong></p>
	<p>{esc(pattern.get('why_now', ''))}</p>
	<div class="metrics">
	<article class="metric"><span>Proof</span><strong>{esc(pattern.get('proof_status', 'missing'))}</strong></article>
	<article class="metric"><span>Scope</span><strong>{esc(pattern.get('approval_scope', ''))}</strong></article>
	<article class="metric"><span>Decision</span><strong>{esc('필요' if pattern.get('operator_decision_needed') else '불필요')}</strong></article>
	<article class="metric"><span>Watch</span><strong>{esc(len(pattern.get('deferred_watchlist', [])))}</strong></article>
	</div>
	<p><a href="{esc(_relative_href(Path(pattern.get('surface', 'reports/product/pattern-radar.html'))))}">pattern radar 열기</a> · <a href="{esc(_relative_href(Path(pattern.get('proof_surface', 'reports/product/pattern-dry-run.html'))))}">dry-run proof 열기</a></p>
	<h2>Done when</h2>
	<ul>{pattern_done_items}</ul>
    <h2>방법론 intake</h2>
    <p>새로 발견한 Hermes/OpenClaw/투자 에이전트 사례를 바로 도입하지 않고, 이미 검증됨/신규 local 후보/승인 필요/차단으로 분류합니다.</p>
    <div class="metrics">
    <article class="metric"><span>Status</span><strong>{esc(pattern_evidence.get('status', 'missing'))}</strong></article>
    <article class="metric"><span>Local</span><strong>{esc(pattern_evidence.get('local_candidate_count', 0))}</strong></article>
    <article class="metric"><span>Verified</span><strong>{esc(pattern_evidence.get('already_verified_count', 0))}</strong></article>
    <article class="metric"><span>Gated</span><strong>{esc(pattern_evidence.get('approval_gated_count', 0))}</strong></article>
    </div>
    <p><a href="{esc(_relative_href(Path(pattern_evidence.get('surface', 'reports/product/pattern-evidence-intake.html'))))}">pattern evidence intake 열기</a></p>
	<h2>보류 중인 방식</h2>
	<ul>{pattern_watch_items}</ul>
	<h2>넘지 않을 경계</h2>
	<ul>{pattern_boundary_items}</ul>
	</section>
	<section class="section">
	<h2>오늘 볼 순서</h2>
<div class="route-grid">{route_cards}</div>
</section>
<section class="section">
<h2>복사할 수 있는 로컬 응답</h2>
<div class="commands">{command_cards}</div>
</section>
<section class="section">
<h2>접근과 알림</h2>
<p>접근 경로: {esc(access.get('recommended_path', ''))} · private URL: {esc(access.get('private_phone_url', ''))}</p>
<p>알림 상태: {esc(notification.get('delivery_status', ''))} · dry-run: {esc(notification.get('dry_run', True))}</p>
</section>
<section class="section">
<h2>빠른 링크</h2>
<div class="links">{link_cards}</div>
</section>
<section class="section">
<h2>증거 파일</h2>
<table><thead><tr><th>Artifact</th><th>Exists</th><th>Status</th></tr></thead><tbody>{artifact_rows}</tbody></table>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 홈은 기존 로컬 파일만 읽습니다. task 실행, live network, 알림 전송, host write, credential, 계좌 접근, 주문 실행을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_morning_control_packet(payload: dict[str, Any]) -> str:
    read_first = payload.get("read_first", {})
    task_state = payload.get("task_state", {})
    runtime = payload.get("runtime", {})
    decision_cards = "".join(
        "<article class='card warn'>"
        f"<span>{esc(decision.get('id', 'decision'))} · {esc(decision.get('risk_level', 'risk'))}</span>"
        f"<h2>{esc(decision.get('title', '승인 필요'))}</h2>"
        f"<p>{esc(decision.get('why', ''))}</p>"
        f"<code>{esc(decision.get('copy_ready_response', ''))}</code>"
        f"<small>{esc(decision.get('stale_context_guard', ''))}</small>"
        "</article>"
        for decision in payload.get("pending_decisions", [])
    ) or "<p>지금 사람이 승인해야 할 외부효과 결정은 없습니다.</p>"
    task_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(task.get('task_id', ''))} · {esc(task.get('status', ''))} · {esc(task.get('priority', ''))}</span>"
        f"<h2>{esc(task.get('title', ''))}</h2>"
        f"<p>{esc(task.get('operator_note', task.get('why', '')))}</p>"
        "</article>"
        for task in task_state.get("top_tasks", [])
    ) or "<p>오늘 표시할 analyst task가 없습니다.</p>"
    command_cards = "".join(
        "<article class='command'>"
        f"<span>{esc(item.get('label', 'command'))}</span>"
        f"<code>{esc(item.get('command', ''))}</code>"
        f"<small>{esc(item.get('effect', 'local only'))}</small>"
        "</article>"
        for item in payload.get("command_bar", [])
    ) or "<p>오늘 복사할 로컬 응답 명령이 없습니다.</p>"
    links = payload.get("phone_links", {})
    link_cards = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in links.items()
        if path and label != "morning"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Morning Control</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:28px 0 16px; }}
.eyebrow,.card span,.command span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.card,.command {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.stack {{ display:grid; grid-template-columns:1fr; gap:10px; }}
.card,.command {{ background:white; padding:14px; min-width:0; }}
.warn {{ border-color:#d7b36a; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin-top:12px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .grid,.metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Morning · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>아침 analyst 관제판</h1>
<p>오늘 무엇을 먼저 읽고, 무엇을 승인하지 말아야 하며, 어떤 짧은 응답으로 작업 상태를 닫을지 보는 운영면입니다.</p>
</header>
<section class="hero">
<span class="eyebrow">먼저 볼 것</span>
<h2>{esc(read_first.get('title', '오늘 브리프'))}</h2>
<p>{esc(read_first.get('reason', ''))}</p>
<div class="metrics">
<article class="metric"><span>Status</span><strong>{esc(payload.get('status', 'ready'))}</strong></article>
<article class="metric"><span>Carried</span><strong>{esc(task_state.get('carried', 0))}</strong></article>
<article class="metric"><span>Blocked</span><strong>{esc(task_state.get('blocked', 0))}</strong></article>
<article class="metric"><span>Runtime</span><strong>{esc(runtime.get('runtime_doctor_status', 'missing'))}</strong></article>
</div>
</section>
<section class="section">
<h2>결정 필요</h2>
<div class="stack">{decision_cards}</div>
</section>
<section class="section">
<h2>오늘 닫을 analyst 작업</h2>
<div class="grid">{task_cards}</div>
</section>
<section class="section">
<h2>복사 가능한 응답</h2>
<div class="stack">{command_cards}</div>
</section>
<section class="section">
<h2>폰에서 열기</h2>
<div class="links">{link_cards}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 관제판은 기존 산출물을 읽고 표시할 뿐입니다. queued task 실행, live network, host write, notification send, 계좌/주문/일임 행위는 별도 승인 게이트 없이는 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def validate_task_status_apply_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != ANALYST_TASK_STATUS_APPLY_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    allowed = {"completed", "carried", "deferred", "blocked_by_operator"}
    for index, response in enumerate(payload.get("applied", [])):
        if response.get("status") not in allowed:
            errors.append(f"applied[{index}] invalid status {response.get('status')}")
        if not response.get("task_id", "").startswith("AT-"):
            errors.append(f"applied[{index}] invalid task_id")
    if "does_not_execute_tasks" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_execute_tasks")
    return errors


def validate_task_status_apply_file(path: str | Path) -> list[str]:
    return validate_task_status_apply_payload(load_json(path))


def validate_analyst_task_ledger_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != ANALYST_TASK_LEDGER_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    entries = payload.get("entries", [])
    if payload.get("entry_count", 0) != len(entries):
        errors.append("entry_count must match entries length")
    if not entries:
        errors.append("entries must not be empty")
    allowed_statuses = {"ready_for_local_work", "carried", "blocked_requires_approval", "retired_not_in_current_queue", "completed", "deferred", "blocked_by_operator"}
    for index, entry in enumerate(entries):
        for field in ["ledger_id", "task_id", "fingerprint", "role", "title", "priority", "status", "first_seen_at", "last_seen_at", "operator_note", "local_completion"]:
            if field not in entry:
                errors.append(f"entries[{index}] missing {field}")
        if entry.get("status") not in allowed_statuses:
            errors.append(f"entries[{index}] invalid status {entry.get('status')}")
        if entry.get("external_effect_allowed") is True and entry.get("requires_operator_approval") is not True:
            errors.append(f"entries[{index}] external effects require operator approval")
        completion = entry.get("local_completion", {})
        for field in ["status", "required_count", "present_count", "missing_count", "artifacts", "external_effect_performed"]:
            if field not in completion:
                errors.append(f"entries[{index}].local_completion missing {field}")
        if completion.get("external_effect_performed") is not False:
            errors.append(f"entries[{index}].local_completion.external_effect_performed must be false")
        if entry.get("status") == "completed" and entry.get("operator_override") == {} and completion.get("status") != "satisfied":
            errors.append(f"entries[{index}] auto-completed task must have satisfied local_completion")
    if "does_not_execute_tasks" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_execute_tasks")
    if "completion_inferred_from_local_artifact_presence_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include completion_inferred_from_local_artifact_presence_only")
    return errors


def validate_analyst_task_ledger_file(path: str | Path) -> list[str]:
    return validate_analyst_task_ledger_payload(load_json(path))


def render_analyst_task_ledger(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    cards = "".join(
        "<article class='entry'>"
        f"<span>{esc(entry.get('status', ''))} · {esc(entry.get('role', ''))} · {esc(entry.get('priority', ''))}</span>"
        f"<h2>{esc(entry.get('title', ''))}</h2>"
        f"<p>{esc(entry.get('operator_note', ''))}</p>"
        f"<p>local proof: {esc(entry.get('local_completion', {}).get('status', 'missing'))} · present {esc(entry.get('local_completion', {}).get('present_count', 0))}/{esc(entry.get('local_completion', {}).get('required_count', 0))}</p>"
        f"<small>first: {esc(_short_date(entry.get('first_seen_at', '')))} · last: {esc(_short_date(entry.get('last_seen_at', '')))} · scope: {esc(entry.get('approval_scope', ''))}</small>"
        "</article>"
        for entry in payload.get("entries", [])
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Task Ledger</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
.eyebrow,.entry span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.entry {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric,.entry {{ background:white; padding:14px; }}
.metric strong {{ display:block; font-size:24px; }}
.stack {{ display:grid; grid-template-columns:1fr; gap:10px; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Task Ledger · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>analyst 작업 이력</h1>
<p>오늘 queue가 어제와 어떻게 이어지는지, 무엇이 이월되고 무엇이 승인 대기인지 보는 기록입니다.</p>
</header>
<section class="hero">
<div class="metrics">
<article class="metric"><span>Total</span><strong>{esc(payload.get('entry_count', 0))}</strong></article>
<article class="metric"><span>Ready</span><strong>{esc(summary.get('ready_for_local_work', 0))}</strong></article>
<article class="metric"><span>Carried</span><strong>{esc(summary.get('carried', 0))}</strong></article>
<article class="metric"><span>Done</span><strong>{esc(summary.get('completed', 0))}</strong></article>
<article class="metric"><span>Blocked</span><strong>{esc(summary.get('blocked_requires_approval', 0) + summary.get('blocked_by_operator', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>상태별 작업</h2>
<div class="stack">{cards}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 ledger는 상태만 기록합니다. queued task 실행, live network, host write, notification send, 계좌/주문/일임 행위는 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def build_memory_index(
    *,
    memory_path: str | Path = "reports/memory/topic-memory.json",
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = "reports/evidence/daily-evidence-catalog.json",
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
) -> dict[str, Any]:
    memory = load_json(memory_path)
    evidence = load_json(evidence_path) if Path(evidence_path).exists() else {}
    vault = load_json(vault_path) if Path(vault_path).exists() else {}
    archive_manifests = []
    for manifest_path in sorted(Path(archive_root).glob("*/manifest.json"), reverse=True):
        try:
            archive_manifests.append(load_json(manifest_path))
        except json.JSONDecodeError:
            continue
    topic_rows = []
    for topic in memory.get("topics", []):
        topic_rows.append({
            "topic_id": topic.get("topic_id", ""),
            "name": topic.get("name", ""),
            "latest_summary": topic.get("latest_summary", ""),
            "daily_questions": topic.get("daily_questions", []),
            "latest_titles": topic.get("latest_titles", []),
            "source_names": topic.get("source_names", []),
            "collection_gaps": topic.get("collection_gaps", []),
            "changed_since_previous": topic.get("changed_since_previous", False),
        })
    return {
        "schema_version": MEMORY_INDEX_SCHEMA_VERSION,
        "generated_at": _now(),
        "memory_path": Path(memory_path).as_posix(),
        "archive_root": Path(archive_root).as_posix(),
        "run_count": memory.get("run_count", 0),
        "topic_count": len(topic_rows),
        "topics": topic_rows,
        "recent_runs": list(reversed(memory.get("runs", [])[-10:])),
        "archives": archive_manifests[:12],
        "source_relevance": [
            {
                "source_name": row.get("source_name", ""),
                "freshness_status": row.get("freshness_status", ""),
                "relevance_score": row.get("relevance_score", "0.00"),
                "relevance_label": row.get("relevance_label", "unscored"),
                "item_count": row.get("item_count", "0"),
            }
            for row in evidence.get("source_status", [])
        ],
        "vault_path": Path(vault_path).as_posix(),
        "vault_notes": _vault_notes_for_memory(vault),
        "policy": "research_only",
    }


def write_memory_surface(
    *,
    memory_path: str | Path = "reports/memory/topic-memory.json",
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = "reports/evidence/daily-evidence-catalog.json",
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    index_output_path: str | Path = DEFAULT_MEMORY_INDEX_OUTPUT,
    output_path: str | Path = DEFAULT_MEMORY_OUTPUT,
) -> Path:
    index = build_memory_index(memory_path=memory_path, archive_root=archive_root, evidence_path=evidence_path, vault_path=vault_path)
    write_json(index, index_output_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_memory_surface(index), encoding="utf-8")
    return target


def build_memory_query(
    *,
    query: str,
    memory_path: str | Path = "reports/memory/topic-memory.json",
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = "reports/evidence/daily-evidence-catalog.json",
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    limit: int = 5,
) -> dict[str, Any]:
    index = build_memory_index(memory_path=memory_path, archive_root=archive_root, evidence_path=evidence_path, vault_path=vault_path)
    tokens = _query_tokens(query)
    matched_topics = []
    for topic in index.get("topics", []):
        haystacks = [
            topic.get("name", ""),
            topic.get("latest_summary", ""),
            " ".join(topic.get("daily_questions", [])),
            " ".join(topic.get("latest_titles", [])),
            " ".join(topic.get("source_names", [])),
            " ".join(topic.get("collection_gaps", [])),
        ]
        score = _match_score(tokens, haystacks)
        if score > 0:
            matched_topics.append({
                "topic_id": topic.get("topic_id", ""),
                "name": topic.get("name", ""),
                "score": round(score, 3),
                "summary": topic.get("latest_summary", ""),
                "source_names": topic.get("source_names", []),
                "latest_titles": topic.get("latest_titles", [])[:5],
                "questions": topic.get("daily_questions", [])[:4],
                "why_matched": _match_reasons(tokens, haystacks),
            })
    matched_topics.sort(key=lambda row: (-row["score"], row["name"]))

    matched_archives = []
    for manifest in index.get("archives", []):
        haystacks = [
            manifest.get("run_id", ""),
            manifest.get("generated_at", ""),
            " ".join(str(value) for value in manifest.get("artifacts", {}).values()),
        ]
        score = _match_score(tokens, haystacks)
        if score > 0 or matched_topics:
            matched_archives.append({
                "run_id": manifest.get("run_id", ""),
                "generated_at": manifest.get("generated_at", ""),
                "score": round(score, 3),
                "archive_dir": manifest.get("archive_dir", ""),
                "artifacts": manifest.get("artifacts", {}),
            })
    matched_archives.sort(key=lambda row: (row["score"], row.get("generated_at", "")), reverse=True)

    matched_vault_notes = []
    for note in index.get("vault_notes", []):
        haystacks = [
            note.get("title", ""),
            note.get("topic_name", ""),
            note.get("source_path", ""),
            note.get("wiki_path", ""),
            " ".join(note.get("key_takeaways", [])),
        ]
        score = _match_score(tokens, haystacks)
        if score > 0:
            matched_vault_notes.append({
                "title": note.get("title", ""),
                "topic_name": note.get("topic_name", ""),
                "score": round(score, 3),
                "source_path": note.get("source_path", ""),
                "wiki_path": note.get("wiki_path", ""),
                "key_takeaways": note.get("key_takeaways", [])[:5],
                "why_matched": _match_reasons(tokens, haystacks),
            })
    matched_vault_notes.sort(key=lambda row: (-row["score"], row["title"]))

    selected_topics = matched_topics[:limit]
    selected_archives = matched_archives[:limit]
    selected_vault_notes = matched_vault_notes[:limit]
    status = "matched" if selected_topics or selected_archives or selected_vault_notes else "no_direct_match"
    evidence_bundles = _query_evidence_bundles(
        topics=selected_topics,
        vault_notes=selected_vault_notes,
        archives=selected_archives,
        source_relevance=index.get("source_relevance", []),
    )
    weak_spots = _query_weak_spots(
        status=status,
        topics=selected_topics,
        vault_notes=selected_vault_notes,
        archives=selected_archives,
        source_relevance=index.get("source_relevance", []),
    )
    next_questions = _query_next_questions(query=query, topics=selected_topics, status=status)
    return {
        "schema_version": MEMORY_QUERY_SCHEMA_VERSION,
        "generated_at": _now(),
        "query": query,
        "status": status,
        "recall_quality": _query_recall_quality(
            status=status,
            topic_count=len(selected_topics),
            archive_count=len(selected_archives),
            vault_note_count=len(selected_vault_notes),
            weak_spot_count=len(weak_spots),
        ),
        "matched_topic_count": len(selected_topics),
        "matched_archive_count": len(selected_archives),
        "matched_vault_note_count": len(selected_vault_notes),
        "matched_topics": selected_topics,
        "matched_archives": selected_archives,
        "matched_vault_notes": selected_vault_notes,
        "evidence_bundles": evidence_bundles,
        "weak_spots": weak_spots,
        "reading_order": _query_reading_order(
            topics=selected_topics,
            vault_notes=selected_vault_notes,
            archives=selected_archives,
            evidence_bundles=evidence_bundles,
            weak_spots=weak_spots,
        ),
        "source_relevance": index.get("source_relevance", []),
        "next_questions": next_questions,
        "policy": "research_only",
        "limitations": [
            "This is deterministic local retrieval, not a model-generated answer.",
            "Use the linked artifacts to inspect original context before relying on a conclusion.",
        ],
    }


def write_memory_query(
    *,
    query: str,
    memory_path: str | Path = "reports/memory/topic-memory.json",
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = "reports/evidence/daily-evidence-catalog.json",
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    output_path: str | Path = DEFAULT_MEMORY_QUERY_OUTPUT,
    surface_path: str | Path = DEFAULT_MEMORY_QUERY_SURFACE,
    limit: int = 5,
) -> Path:
    payload = build_memory_query(
        query=query,
        memory_path=memory_path,
        archive_root=archive_root,
        evidence_path=evidence_path,
        vault_path=vault_path,
        limit=limit,
    )
    write_json(payload, output_path)
    target = Path(surface_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_memory_query_surface(payload), encoding="utf-8")
    return target


def validate_memory_query_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != MEMORY_QUERY_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"matched", "no_direct_match"}:
        errors.append(f"invalid status {payload.get('status')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not str(payload.get("query", "")).strip():
        errors.append("query must not be empty")
    quality = payload.get("recall_quality", {})
    for field in ["level", "coverage_label", "confidence", "summary"]:
        if field not in quality:
            errors.append(f"recall_quality missing {field}")
    if not payload.get("reading_order"):
        errors.append("reading_order must not be empty")
    if "weak_spots" not in payload:
        errors.append("weak_spots must be present")
    if "next_questions" not in payload:
        errors.append("next_questions must be present")
    for field in ["matched_topic_count", "matched_archive_count", "matched_vault_note_count"]:
        if not isinstance(payload.get(field), int):
            errors.append(f"{field} must be an integer")
    return errors


def validate_memory_query_file(path: str | Path) -> list[str]:
    return validate_memory_query_payload(load_json(path))


def build_memory_audit(
    *,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    daily_review_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    index = build_memory_index(memory_path=memory_path, archive_root=archive_root, evidence_path=evidence_path, vault_path=vault_path)
    review = _load_optional_json(daily_review_path)
    risks = _memory_audit_risks(index=index, review=review)
    high_count = sum(1 for risk in risks if risk.get("severity") == "high")
    medium_count = sum(1 for risk in risks if risk.get("severity") == "medium")
    status = "blocked" if high_count else ("needs_attention" if medium_count else "ready")
    return {
        "schema_version": MEMORY_AUDIT_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "status": status,
        "audit_mode": "local_memory_and_vault_audit",
        "summary": {
            "topic_count": index.get("topic_count", 0),
            "run_count": index.get("run_count", 0),
            "archive_count": len(index.get("archives", [])),
            "vault_note_count": len(index.get("vault_notes", [])),
            "source_count": len(index.get("source_relevance", [])),
            "risk_count": len(risks),
            "high_risk_count": high_count,
            "medium_risk_count": medium_count,
            "review_response_count": int(review.get("summary", {}).get("response_count", 0) or 0),
        },
        "coverage": _memory_audit_coverage(index=index),
        "risks": risks,
        "next_questions": _memory_audit_next_questions(index=index, risks=risks),
        "operator_reading_order": [
            "summary",
            "risks",
            "coverage",
            "next_questions",
            "linked_surfaces",
        ],
        "linked_surfaces": {
            "memory": DEFAULT_MEMORY_OUTPUT.as_posix(),
            "memory_query": DEFAULT_MEMORY_QUERY_SURFACE.as_posix(),
            "vault": DEFAULT_VAULT_SURFACE_OUTPUT.as_posix(),
            "review": DEFAULT_DAILY_REVIEW_SURFACE.as_posix(),
            "review_prompt": DEFAULT_REVIEW_PROMPT_SURFACE.as_posix(),
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
        },
        "inputs": {
            "memory": Path(memory_path).as_posix(),
            "archive_root": Path(archive_root).as_posix(),
            "evidence": Path(evidence_path).as_posix(),
            "vault": Path(vault_path).as_posix(),
            "daily_review": Path(daily_review_path).as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "does_not_use_credentials",
            "no_account_access",
            "no_live_trading",
            "no_discretionary_management",
        ],
    }


def write_memory_audit(
    *,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    daily_review_path: str | Path = DEFAULT_DAILY_REVIEW_OUTPUT,
    output_path: str | Path = DEFAULT_MEMORY_AUDIT_OUTPUT,
    surface_path: str | Path = DEFAULT_MEMORY_AUDIT_SURFACE,
) -> Path:
    payload = build_memory_audit(
        memory_path=memory_path,
        archive_root=archive_root,
        evidence_path=evidence_path,
        vault_path=vault_path,
        daily_review_path=daily_review_path,
    )
    write_json(payload, output_path)
    target = Path(surface_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_memory_audit_surface(payload), encoding="utf-8")
    return target


def validate_memory_audit_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != MEMORY_AUDIT_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"ready", "needs_attention", "blocked"}:
        errors.append("status must be ready, needs_attention, or blocked")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("coverage"):
        errors.append("coverage must not be empty")
    if not payload.get("next_questions"):
        errors.append("next_questions must not be empty")
    for index, risk in enumerate(payload.get("risks", [])):
        for field in ["risk_id", "severity", "title", "evidence", "recommended_local_action"]:
            if field not in risk:
                errors.append(f"risks[{index}] missing {field}")
        if risk.get("severity") not in {"high", "medium", "low"}:
            errors.append(f"risks[{index}] invalid severity")
    if "reads_local_artifacts_only" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include reads_local_artifacts_only")
    return errors


def validate_memory_audit_file(path: str | Path) -> list[str]:
    return validate_memory_audit_payload(load_json(path))


def _memory_audit_coverage(index: dict[str, Any]) -> list[dict[str, Any]]:
    source_rows = index.get("source_relevance", [])
    topics = index.get("topics", [])
    vault_notes = index.get("vault_notes", [])
    archives = index.get("archives", [])
    covered_topics = [topic for topic in topics if topic.get("source_names")]
    changed_topics = [topic for topic in topics if topic.get("changed_since_previous")]
    return [
        {
            "name": "topic_source_coverage",
            "status": "ready" if len(covered_topics) == len(topics) and topics else "needs_attention",
            "value": f"{len(covered_topics)}/{len(topics)} topics have source names",
            "why_it_matters": "초보자용 브리프가 특정 주제를 반복할 때 어떤 원천이 받치는지 보여야 합니다.",
        },
        {
            "name": "vault_compounding",
            "status": "ready" if vault_notes else "needs_attention",
            "value": f"{len(vault_notes)} compiled vault notes",
            "why_it_matters": "개인 애널리스트는 매일 새로 시작하지 않고 원천 노트가 누적돼야 합니다.",
        },
        {
            "name": "archive_history",
            "status": "ready" if archives else "needs_attention",
            "value": f"{len(archives)} archive manifests",
            "why_it_matters": "과거 브리프와 판단이 남아야 같은 결론을 반복하는지 감사할 수 있습니다.",
        },
        {
            "name": "source_freshness",
            "status": "needs_attention" if any(row.get("freshness_status") in {"stale", "unknown"} for row in source_rows) else "ready",
            "value": f"{len(source_rows)} source rows",
            "why_it_matters": "오래된 근거가 매일 브리프를 지배하면 개인화가 아니라 편향 누적이 됩니다.",
        },
        {
            "name": "change_detection",
            "status": "ready" if changed_topics else "needs_attention",
            "value": f"{len(changed_topics)} changed topics",
            "why_it_matters": "매일 무엇이 달라졌는지 보여야 시장 공부 루프가 누적됩니다.",
        },
    ]


def _memory_audit_risks(*, index: dict[str, Any], review: dict[str, Any]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    topics = index.get("topics", [])
    source_rows = index.get("source_relevance", [])
    vault_notes = index.get("vault_notes", [])
    archives = index.get("archives", [])
    if not vault_notes:
        risks.append({
            "risk_id": "MA-001",
            "severity": "medium",
            "title": "vault 원천 노트가 아직 누적되지 않았습니다",
            "evidence": "compiled vault note count is 0",
            "recommended_local_action": "research-vault/raw에 읽은 자료를 넣고 appliance vault compile 또는 appliance run을 실행합니다.",
        })
    no_source_topics = [topic.get("name", "") for topic in topics if not topic.get("source_names")]
    if no_source_topics:
        risks.append({
            "risk_id": "MA-002",
            "severity": "medium",
            "title": "일부 주제가 source 이름 없이 반복됩니다",
            "evidence": ", ".join(no_source_topics[:4]),
            "recommended_local_action": "source-refresh-plan과 evidence catalog를 읽어 주제별 원천 누락을 확인합니다.",
        })
    weak_sources = [
        row.get("source_name", "source")
        for row in source_rows
        if row.get("freshness_status") in {"stale", "unknown"} or row.get("relevance_label") in {"weak", "unscored"}
    ]
    if weak_sources:
        risks.append({
            "risk_id": "MA-003",
            "severity": "medium",
            "title": "약하거나 오래된 source가 남아 있습니다",
            "evidence": ", ".join(weak_sources[:5]),
            "recommended_local_action": "live 실행 전에는 source-refresh 화면에서 승인 필요 항목과 dry-run 항목을 분리해 읽습니다.",
        })
    if not archives:
        risks.append({
            "risk_id": "MA-004",
            "severity": "high",
            "title": "archive manifest가 없어 과거 판단을 추적할 수 없습니다",
            "evidence": "archive manifest count is 0",
            "recommended_local_action": "appliance run을 실행해 오늘 산출물과 archive manifest를 생성합니다.",
        })
    if int(review.get("summary", {}).get("response_count", 0) or 0) == 0:
        risks.append({
            "risk_id": "MA-005",
            "severity": "low",
            "title": "operator review가 없어 다음 주제 선택이 개인 피드백을 거의 반영하지 못합니다",
            "evidence": "daily review response count is 0",
            "recommended_local_action": "review-prompt에서 복사한 review-response-apply 한 줄을 남깁니다.",
        })
    if not risks:
        risks.append({
            "risk_id": "MA-000",
            "severity": "low",
            "title": "치명적인 memory audit risk는 보이지 않습니다",
            "evidence": "vault, archive, source rows, review inputs are present enough for local study",
            "recommended_local_action": "오늘 브리프를 읽고 review-response-apply로 다음 루프 피드백을 남깁니다.",
        })
    return risks


def _memory_audit_next_questions(*, index: dict[str, Any], risks: list[dict[str, Any]]) -> list[str]:
    topics = index.get("topics", [])
    top_topic = topics[0].get("name", "오늘 주제") if topics else "오늘 주제"
    questions = [
        f"{top_topic}에 대해 최근 3일 archive에서 같은 결론이 반복되고 있나?",
        "오늘 브리프의 가장 약한 source는 무엇이고 왜 약한가?",
        "vault 원천 노트와 오늘 evidence가 서로 보강하는가, 아니면 충돌하는가?",
    ]
    if any(risk.get("risk_id") == "MA-005" for risk in risks):
        questions.insert(0, "내가 오늘 실제로 읽은 주제는 무엇이며 내일 더 보고 싶은가?")
    return questions[:4]


def render_memory_audit_surface(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    risk_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(risk.get('risk_id', 'MA'))} · {esc(risk.get('severity', 'low'))}</span>"
        f"<h2>{esc(risk.get('title', ''))}</h2>"
        f"<p>{esc(risk.get('evidence', ''))}</p>"
        f"<small>{esc(risk.get('recommended_local_action', ''))}</small>"
        "</article>"
        for risk in payload.get("risks", [])
    )
    coverage_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(row.get('status', ''))}</span>"
        f"<h2>{esc(row.get('name', ''))}</h2>"
        f"<p>{esc(row.get('value', ''))}</p>"
        f"<small>{esc(row.get('why_it_matters', ''))}</small>"
        "</article>"
        for row in payload.get("coverage", [])
    )
    questions = "".join(f"<li>{esc(question)}</li>" for question in payload.get("next_questions", []))
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("linked_surfaces", {}).items()
        if path
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Memory Audit</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:28px 0 16px; }}
.eyebrow,.card span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small,li {{ color:var(--muted); overflow-wrap:anywhere; }}
.hero,.section,.card {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics,.grid,.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.metric,.card,.links a {{ background:white; border:1px solid var(--line); border-radius:8px; padding:14px; min-width:0; }}
.metric strong {{ display:block; font-size:26px; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.grid,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Memory Audit · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>개인 애널리스트 메모리 감사</h1>
<p>매일 쌓이는 메모리, vault, archive, source 상태가 신뢰 가능한 공부 루프를 만들고 있는지 점검합니다.</p>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<h2>{esc(payload.get('status', 'needs_attention'))}</h2>
<div class="metrics">
<article class="metric"><span>Runs</span><strong>{esc(summary.get('run_count', 0))}</strong></article>
<article class="metric"><span>Vault</span><strong>{esc(summary.get('vault_note_count', 0))}</strong></article>
<article class="metric"><span>Archives</span><strong>{esc(summary.get('archive_count', 0))}</strong></article>
<article class="metric"><span>Risks</span><strong>{esc(summary.get('risk_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>감사 리스크</h2>
<div class="grid">{risk_cards}</div>
</section>
<section class="section">
<h2>커버리지</h2>
<div class="grid">{coverage_cards}</div>
</section>
<section class="section">
<h2>내일 확인할 질문</h2>
<ul>{questions}</ul>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 감사는 로컬 산출물만 읽습니다. live network, 알림 전송, host write, credential, 계좌 접근, 주문 실행을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_memory_surface(index: dict[str, Any]) -> str:
    topic_cards = "".join(
        "<article class='card'>"
        f"<span>{esc('새 변화' if topic.get('changed_since_previous') else '누적')}</span>"
        f"<h3>{esc(topic.get('name', ''))}</h3>"
        f"<p>{esc(topic.get('latest_summary', ''))}</p>"
        f"<small>{esc(', '.join(topic.get('source_names', [])) or 'source 없음')}</small>"
        "</article>"
        for topic in index.get("topics", [])
    ) or "<p>아직 topic memory가 없습니다.</p>"
    source_rows = "".join(
        "<tr>"
        f"<td>{esc(row.get('source_name', ''))}</td>"
        f"<td>{esc(row.get('relevance_label', 'unscored'))}</td>"
        f"<td>{esc(row.get('relevance_score', '0.00'))}</td>"
        f"<td>{esc(row.get('freshness_status', 'unknown'))}</td>"
        "</tr>"
        for row in index.get("source_relevance", [])
    ) or "<tr><td colspan='4'>아직 source relevance가 없습니다.</td></tr>"
    archive_cards = "".join(
        "<article class='archive'>"
        f"<strong>{esc(manifest.get('generated_at', '')[:10])}</strong>"
        f"<span>{esc(manifest.get('run_id', ''))}</span>"
        f"<a href='{esc(manifest.get('archive_dir', ''))}/today.html'>today</a>"
        f"<a href='{esc(manifest.get('archive_dir', ''))}/market-brief.html'>brief</a>"
        "</article>"
        for manifest in index.get("archives", [])
    ) or "<p>아직 archive manifest가 없습니다.</p>"
    vault_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(note.get('topic_name', ''))}</span>"
        f"<h3>{esc(note.get('title', ''))}</h3>"
        f"<p>{esc(note.get('source_path', ''))}</p>"
        f"<small>{esc(' · '.join(note.get('key_takeaways', [])[:2]))}</small>"
        f"<p><a href='{esc(note.get('wiki_path', ''))}'>wiki note</a></p>"
        "</article>"
        for note in index.get("vault_notes", [])[:8]
    ) or "<p>아직 컴파일된 vault note가 없습니다.</p>"
    run_items = "".join(
        f"<li><strong>{esc(run.get('run_id', ''))}</strong><span>{esc(run.get('generated_at', ''))} · changed {esc(', '.join(run.get('changed_topics', [])) or 'none')}</span></li>"
        for run in index.get("recent_runs", [])
    ) or "<li>아직 run history가 없습니다.</li>"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Memory</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ max-width:860px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:26px 0 16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p,small,li span {{ color:var(--muted); }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.section,.card,.archive {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.section {{ margin:14px 0; padding:16px; }}
.card,.archive {{ padding:14px; background:white; }}
.card span,.archive span {{ display:block; color:var(--blue); font-size:12px; font-weight:900; }}
.metrics {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.metric {{ padding:14px; border:1px solid var(--line); border-radius:8px; background:white; }}
.metric strong {{ display:block; font-size:24px; }}
table {{ width:100%; border-collapse:collapse; overflow:hidden; border-radius:8px; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; }}
ul {{ padding-left:18px; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .grid,.metrics {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Memory · {esc(index.get('generated_at', '')[:10])}</span>
<h1>내가 매일 쌓아온 시장 이해</h1>
<p>오늘 브리프가 끝이 아니라, 주제별 기억과 과거 브리프가 계속 누적되는 개인 리서치 노트입니다.</p>
</header>
<section class="metrics">
<article class="metric"><span>Memory runs</span><strong>{esc(index.get('run_count', 0))}</strong></article>
<article class="metric"><span>Topics</span><strong>{esc(index.get('topic_count', 0))}</strong></article>
<article class="metric"><span>Vault notes</span><strong>{esc(len(index.get('vault_notes', [])))}</strong></article>
</section>
<section class="section">
<h2>주제별 누적 기억</h2>
<div class="grid">{topic_cards}</div>
</section>
<section class="section">
<h2>근거 품질 추적</h2>
<table><thead><tr><th>Source</th><th>Label</th><th>Score</th><th>Freshness</th></tr></thead><tbody>{source_rows}</tbody></table>
</section>
<section class="section">
<h2>Vault 원천 노트</h2>
<div class="grid">{vault_cards}</div>
</section>
<section class="section">
<h2>최근 실행</h2>
<ul>{run_items}</ul>
</section>
<section class="section">
<h2>아카이브</h2>
<div class="grid">{archive_cards}</div>
</section>
</main>
</body>
</html>
"""


def render_memory_query_surface(payload: dict[str, Any]) -> str:
    recall_quality = payload.get("recall_quality", {})
    quality_items = "".join(
        "<article class='metric'>"
        f"<span>{esc(label)}</span>"
        f"<strong>{esc(value)}</strong>"
        "</article>"
        for label, value in [
            ("Quality", recall_quality.get("level", "unknown")),
            ("Coverage", recall_quality.get("coverage_label", "unknown")),
            ("Confidence", recall_quality.get("confidence", "low")),
        ]
    )
    bundle_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(bundle.get('bundle_type', 'context'))} · {esc(bundle.get('strength', ''))}</span>"
        f"<h3>{esc(bundle.get('title', ''))}</h3>"
        f"<p>{esc(bundle.get('why_it_matters', ''))}</p>"
        f"<small>{esc(' · '.join(bundle.get('source_names', [])) or bundle.get('artifact_path', ''))}</small>"
        "</article>"
        for bundle in payload.get("evidence_bundles", [])
    ) or "<p>묶을 수 있는 근거가 아직 부족합니다.</p>"
    weak_cards = "".join(
        "<article class='card warn'>"
        f"<span>{esc(item.get('severity', 'review'))}</span>"
        f"<h3>{esc(item.get('title', ''))}</h3>"
        f"<p>{esc(item.get('why', ''))}</p>"
        f"<small>{esc(item.get('next_check', ''))}</small>"
        "</article>"
        for item in payload.get("weak_spots", [])
    ) or "<p>현재 query에서 별도 약점은 발견되지 않았습니다.</p>"
    reading_items = "".join(
        "<li>"
        f"<strong>{esc(item.get('label', '읽기'))}</strong>"
        f"<span>{esc(item.get('why', ''))}</span>"
        f"<small>{esc(item.get('path', ''))}</small>"
        "</li>"
        for item in payload.get("reading_order", [])
    ) or "<li>먼저 오늘 브리프와 memory surface를 실행하세요.</li>"
    topic_cards = "".join(
        "<article class='card'>"
        f"<span>관련도 {esc(topic.get('score', 0))}</span>"
        f"<h3>{esc(topic.get('name', ''))}</h3>"
        f"<p>{esc(topic.get('summary', ''))}</p>"
        f"<small>{esc(', '.join(topic.get('why_matched', [])) or 'matched context')}</small>"
        "</article>"
        for topic in payload.get("matched_topics", [])
    ) or "<p>직접 매칭된 주제 기억이 없습니다. 질문을 더 넓게 바꾸거나 오늘 브리프를 먼저 실행하세요.</p>"
    archive_cards = "".join(
        "<article class='archive'>"
        f"<strong>{esc(archive.get('generated_at', '')[:10])}</strong>"
        f"<span>{esc(archive.get('run_id', ''))}</span>"
        f"<a href='{esc(archive.get('artifacts', {}).get('today', ''))}'>today</a>"
        f"<a href='{esc(archive.get('artifacts', {}).get('brief', ''))}'>brief</a>"
        "</article>"
        for archive in payload.get("matched_archives", [])
    ) or "<p>연결할 아카이브가 아직 없습니다.</p>"
    vault_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(note.get('topic_name', ''))} · 관련도 {esc(note.get('score', 0))}</span>"
        f"<h3>{esc(note.get('title', ''))}</h3>"
        f"<p>{esc(note.get('source_path', ''))}</p>"
        f"<small>{esc(' · '.join(note.get('why_matched', [])) or 'matched note')}</small>"
        f"<p><a href='{esc(note.get('wiki_path', ''))}'>wiki note</a></p>"
        "</article>"
        for note in payload.get("matched_vault_notes", [])
    ) or "<p>연결된 vault note가 없습니다.</p>"
    questions = "".join(f"<li>{esc(question)}</li>" for question in payload.get("next_questions", []))
    source_rows = "".join(
        "<tr>"
        f"<td>{esc(row.get('source_name', ''))}</td>"
        f"<td>{esc(row.get('relevance_label', 'unscored'))}</td>"
        f"<td>{esc(row.get('freshness_status', 'unknown'))}</td>"
        "</tr>"
        for row in payload.get("source_relevance", [])[:6]
    ) or "<tr><td colspan='3'>source context 없음</td></tr>"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Memory Query</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ max-width:860px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:26px 0 16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:32px; line-height:1.1; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p,small,li {{ color:var(--muted); }}
.section,.card,.archive {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.section {{ margin:14px 0; padding:16px; }}
.metrics {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:14px; }}
.metric strong {{ display:block; font-size:24px; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.card,.archive {{ padding:14px; background:white; }}
.card span,.archive span {{ display:block; color:var(--blue); font-size:12px; font-weight:900; }}
.warn {{ border-color:#d7b36a; }}
table {{ width:100%; border-collapse:collapse; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; }}
li small,li span {{ display:block; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:28px; }} .grid,.metrics {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Memory Query · {esc(payload.get('generated_at', '')[:10])}</span>
<h1>{esc(payload.get('query', ''))}</h1>
<p>누적 메모리와 아카이브에서 다시 꺼내본 맥락입니다. 결론이 아니라 다음 탐색의 출발점입니다.</p>
</header>
<section class="section">
<h2>Recall 품질</h2>
<div class="metrics">{quality_items}</div>
<p>{esc(recall_quality.get('summary', '로컬 기억을 더 쌓으면 recall 품질이 좋아집니다.'))}</p>
</section>
<section class="section">
<h2>먼저 읽을 순서</h2>
<ul>{reading_items}</ul>
</section>
<section class="section">
<h2>연결된 주제 기억</h2>
<div class="grid">{topic_cards}</div>
</section>
<section class="section">
<h2>근거 묶음</h2>
<div class="grid">{bundle_cards}</div>
</section>
<section class="section">
<h2>아직 약한 부분</h2>
<div class="grid">{weak_cards}</div>
</section>
<section class="section">
<h2>다음에 확인할 질문</h2>
<ul>{questions}</ul>
</section>
<section class="section">
<h2>관련 아카이브</h2>
<div class="grid">{archive_cards}</div>
</section>
<section class="section">
<h2>관련 Vault 노트</h2>
<div class="grid">{vault_cards}</div>
</section>
<section class="section">
<h2>자료 상태</h2>
<table><thead><tr><th>Source</th><th>Relevance</th><th>Freshness</th></tr></thead><tbody>{source_rows}</tbody></table>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 교육과 리서치, 시뮬레이션용입니다. 계좌 연결, 주문 실행, 일임 운용, 근거 없는 개인화 추천을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def write_notification_payload(
    *,
    provider: str,
    today_url: str,
    today_path: str | Path,
    scenario_path: str | Path,
    verdict_path: str | Path,
    output_path: str | Path = DEFAULT_NOTIFICATION_OUTPUT,
    dry_run: bool = True,
) -> Path:
    scenario = load_json(scenario_path)
    verdict = load_json(verdict_path)
    primary = verdict.get("primary_next_step") or {}
    payload = {
        "schema_version": NOTIFICATION_SCHEMA_VERSION,
        "generated_at": _now(),
        "provider": provider,
        "dry_run": dry_run,
        "title": "MyBroker 오늘의 시장 브리프",
        "message": primary.get("title", "오늘 브리프가 준비되었습니다."),
        "url": today_url,
        "local_path": Path(today_path).as_posix(),
        "required_env": _provider_env(provider),
        "run_id": scenario.get("run_id", ""),
        "policy": "research_only",
        "delivery_status": "dry_run_ready" if dry_run else "prepared_requires_sender",
    }
    return write_json(payload, output_path)


def send_notification_payload(path: str | Path) -> dict[str, Any]:
    payload = load_json(path)
    provider = payload.get("provider", "")
    if provider == "telegram":
        result = _send_telegram(payload)
    elif provider == "pushover":
        result = _send_pushover(payload)
    else:
        raise ValueError(f"unsupported notification provider: {provider}")
    payload["dry_run"] = False
    payload["delivery_status"] = "sent" if result.get("ok") else "send_failed"
    payload["sent_at"] = _now()
    payload["send_result"] = result
    write_json(payload, path)
    return payload


def write_launchd_assets(
    *,
    project_root: str | Path,
    output_dir: str | Path = DEFAULT_LOCAL_OPS_DIR,
    hour: int = 7,
    minute: int = 30,
    python_bin: str = "python3",
) -> dict[str, str]:
    root = Path(project_root).resolve()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    script_path = out / "run-daily-analyst.sh"
    plist_path = out / "com.mybroker.daily-analyst.plist"
    log_dir = root / "reports" / "runtime"
    script = f"""#!/bin/sh
set -eu
cd "{root.as_posix()}"
mkdir -p reports/runtime
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src {python_bin} -m mybroker appliance run \\
  --topics config/topics.json \\
  --profile examples/profiles/beginner-conservative.json \\
  ${{MYBROKER_EVIDENCE_SOURCES:-}} \\
  --today-url "${{MYBROKER_TODAY_URL:-http://localhost:8787/reports/product/today.html}}" \\
  --notification-provider "${{MYBROKER_NOTIFICATION_PROVIDER:-telegram}}" \\
  --dry-run
"""
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.mybroker.daily-analyst</string>
  <key>ProgramArguments</key>
  <array>
    <string>{script_path.resolve().as_posix()}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>{root.as_posix()}</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>{hour}</integer>
    <key>Minute</key>
    <integer>{minute}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>{(log_dir / "daily-analyst.out.log").as_posix()}</string>
  <key>StandardErrorPath</key>
  <string>{(log_dir / "daily-analyst.err.log").as_posix()}</string>
</dict>
</plist>
"""
    script_path.write_text(script, encoding="utf-8")
    script_path.chmod(0o755)
    plist_path.write_text(plist, encoding="utf-8")
    return {"script": script_path.as_posix(), "plist": plist_path.as_posix()}


def _provider_env(provider: str) -> list[str]:
    if provider == "pushover":
        return ["PUSHOVER_USER_KEY", "PUSHOVER_APP_TOKEN"]
    if provider == "telegram":
        return ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    return []


def _send_telegram(payload: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": f"{payload.get('title')}\n{payload.get('message')}\n{payload.get('url')}",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    return _post_form(url, data)


def _send_pushover(payload: dict[str, Any]) -> dict[str, Any]:
    user_key = os.environ.get("PUSHOVER_USER_KEY")
    app_token = os.environ.get("PUSHOVER_APP_TOKEN")
    if not user_key or not app_token:
        raise RuntimeError("PUSHOVER_USER_KEY and PUSHOVER_APP_TOKEN are required")
    data = urllib.parse.urlencode({
        "token": app_token,
        "user": user_key,
        "title": payload.get("title", "MyBroker"),
        "message": payload.get("message", ""),
        "url": payload.get("url", ""),
    }).encode("utf-8")
    return _post_form("https://api.pushover.net/1/messages.json", data)


def _post_form(url: str, data: bytes) -> dict[str, Any]:
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(request, timeout=15) as response:
        body = response.read().decode("utf-8")
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        parsed = {"body": body}
    parsed.setdefault("ok", 200 <= getattr(response, "status", 200) < 300)
    return parsed


def _daily_questions(
    memory_topics: list[dict[str, Any]],
    evidence: dict[str, Any],
    vault_notes: list[dict[str, Any]] | None = None,
    scout_recommendations: list[dict[str, Any]] | None = None,
) -> list[str]:
    questions = []
    for recommendation in (scout_recommendations or [])[:2]:
        question = recommendation.get("next_question", "")
        if question:
            questions.append(question)
    for topic in memory_topics[:3]:
        daily = topic.get("daily_questions", [])
        if daily:
            questions.append(daily[0])
    for note in (vault_notes or [])[:2]:
        title = note.get("title", "")
        if title:
            questions.append(f"Vault 노트 '{title}'의 원천 근거가 오늘 자료와 같은 방향을 가리키나요?")
    if evidence.get("collection_gaps"):
        questions.append("오늘 부족한 근거가 결론의 강도를 얼마나 낮추나요?")
    questions.append("이 브리프가 틀렸다고 판단할 가장 빠른 반대 신호는 무엇인가요?")
    deduped = []
    for question in questions:
        if question not in deduped:
            deduped.append(question)
    return deduped[:5]


def _dedupe_texts(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = " ".join(str(value).split())
        key = normalized.casefold()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def _learning_concepts(
    *,
    primary: dict[str, Any],
    focus: dict[str, Any],
    market_map: dict[str, Any],
    beginner_explanations: list[Any],
) -> list[dict[str, str]]:
    concepts: list[dict[str, str]] = []
    headline = focus.get("title") or primary.get("title")
    rationale = focus.get("rationale") or primary.get("rationale") or market_map.get("beginner_summary")
    if headline or rationale:
        concepts.append({
            "kind": "핵심 흐름",
            "title": str(headline or "오늘의 시장 흐름"),
            "explanation": str(rationale or "오늘은 결론보다 흐름을 먼저 이해합니다."),
            "why_beginner_cares": "초보자는 먼저 무엇이 가격보다 앞서 움직이는지 배워야 합니다.",
        })
    for item in beginner_explanations[:3]:
        if isinstance(item, dict):
            title = item.get("term") or item.get("title") or item.get("name") or "배울 개념"
            explanation = item.get("explanation") or item.get("summary") or item.get("why") or ""
        else:
            title = "배울 개념"
            explanation = str(item)
        if explanation:
            concepts.append({
                "kind": "초보자 설명",
                "title": str(title),
                "explanation": str(explanation),
                "why_beginner_cares": "이 단어를 이해하면 브리프의 원인-결과를 더 천천히 따라갈 수 있습니다.",
            })
    if not concepts:
        concepts.append({
            "kind": "시작점",
            "title": "오늘 브리프를 먼저 읽기",
            "explanation": "아직 추출된 개념이 약합니다. 오늘 브리프와 journal에서 먼저 배울 문장을 고릅니다.",
            "why_beginner_cares": "자료가 얇을 때는 결론을 만들지 않고 질문을 남기는 것이 더 중요합니다.",
        })
    return concepts[:4]


def _learning_ledger_status(*, concepts: list[dict[str, str]], questions: list[str], source_gaps: list[str]) -> str:
    if not concepts or not questions:
        return "thin"
    if source_gaps:
        return "review"
    return "ready"


def _journal_status(*, source_rows: list[dict[str, Any]], memory_topics: list[dict[str, Any]]) -> str:
    if not source_rows:
        return "blocked_no_sources"
    weak_count = sum(
        1 for row in source_rows
        if row.get("freshness_status") in {"stale", "unknown"} or row.get("relevance_label") in {"weak", "unscored"}
    )
    changed_count = sum(1 for topic in memory_topics if topic.get("changed_since_previous"))
    if weak_count >= len(source_rows):
        return "weak_needs_refresh"
    if changed_count:
        return "changed_review_first"
    return "stable_monitor"


def _journal_skeptic_note(*, evidence: dict[str, Any], memory_topics: list[dict[str, Any]]) -> str:
    gaps = evidence.get("collection_gaps", [])
    if gaps:
        return f"아직 {', '.join(_gap_label(gap) for gap in gaps[:3])} 문제가 있어 확신을 낮춰야 합니다."
    stale_topics = [topic.get("name", "") for topic in memory_topics if topic.get("collection_gaps")]
    if stale_topics:
        return f"{', '.join(stale_topics[:3])} 주제는 추가 근거 없이는 방향 판단이 약합니다."
    return "현재 근거는 학습용 시뮬레이션에는 충분하지만 투자 행동 결론에는 부족합니다."


def _journal_follow_up_questions(
    *,
    recommended: dict[str, Any],
    memory_topics: list[dict[str, Any]],
    scenario: dict[str, Any],
) -> list[str]:
    questions = []
    next_question = recommended.get("next_question", "")
    if next_question:
        questions.append(next_question)
    for topic in memory_topics:
        for question in topic.get("daily_questions", []):
            if question not in questions:
                questions.append(question)
            if len(questions) >= 5:
                break
        if len(questions) >= 5:
            break
    for candidate in scenario.get("action_candidates", [])[:2]:
        title = candidate.get("title", "")
        if title:
            questions.append(f"{title} 후보가 성립하려면 어떤 반대 근거를 먼저 확인해야 하나요?")
    if not questions:
        questions.append("오늘 시장을 이해하기 전에 먼저 확인해야 할 원천 자료는 무엇인가요?")
    return questions[:6]


def _task_source_scout_why(*, collection_gaps: list[str], weak_count: int) -> str:
    parts = []
    if collection_gaps:
        parts.append(f"자료 gap: {', '.join(_gap_label(gap) for gap in collection_gaps[:3])}")
    if weak_count:
        parts.append(f"약하거나 오래된 source {weak_count}개")
    if not parts:
        parts.append("오늘 source 상태가 안정적이지만 다음 run 전에 refresh 계획을 확인합니다.")
    return " · ".join(parts)


def _task_skeptic_why(*, journal: dict[str, Any]) -> str:
    changed = journal.get("what_changed", [])
    if changed:
        return f"{changed[0].get('name', '오늘 변화')} 변화가 실제 근거 변화인지 반복 관찰인지 구분합니다."
    stable = journal.get("stable_observations", [])
    if stable:
        return f"{stable[0].get('name', '반복 관찰')}은 새 변화가 없으므로 결론 강도를 낮춰 읽습니다."
    return "오늘 journal의 가장 강한 문장을 반대 근거로 검토합니다."


def _maybe_live_refresh_task(*, journal: dict[str, Any]) -> dict[str, Any] | None:
    gaps = set(journal.get("source_posture", {}).get("collection_gaps", []))
    if "live_refresh" not in gaps:
        return None
    return {
        "task_id": "AT-999",
        "role": "operator_gate",
        "title": "live source execution 승인 여부 결정",
        "why": "live_refresh gap이 남아 있지만 실제 live network 실행은 별도 승인과 preflight 통과 없이는 수행하지 않습니다.",
        "priority": "high",
        "status": "queued",
        "autonomy_level": "requires_human_approval",
        "approval_scope": "live_network_refresh",
        "external_effect_allowed": False,
        "requires_operator_approval": True,
        "inputs": [
            "reports/daily/source-refresh-live-gate.json",
            "reports/daily/source-refresh-live-run.json",
            "reports/daily/source-refresh-live-preflight.json",
        ],
        "suggested_command": "Review /today live refresh gate; do not execute without explicit approval.",
        "stop_condition": "operator_decision_recorded_or_deferred",
    }


def _task_fingerprint(task: dict[str, Any]) -> str:
    return "|".join([
        str(task.get("role", "")),
        str(task.get("title", "")),
        str(task.get("approval_scope", "")),
    ])


def _resolve_local_artifact_path(raw_path: str, *, base_path: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    if path.exists():
        return path
    base_candidate = base_path / path
    if base_candidate.exists():
        return base_candidate
    return path


def _local_task_completion_evidence(*, task: dict[str, Any], task_queue_path: str | Path) -> dict[str, Any]:
    inputs = [str(item) for item in task.get("inputs", []) if str(item).strip()]
    if task.get("requires_operator_approval") or task.get("external_effect_allowed"):
        return {
            "status": "approval_required",
            "required_count": len(inputs),
            "present_count": 0,
            "missing_count": len(inputs),
            "artifacts": [],
            "reason": "approval-gated task cannot be auto-completed",
            "external_effect_performed": False,
        }
    if not inputs:
        return {
            "status": "not_checked",
            "required_count": 0,
            "present_count": 0,
            "missing_count": 0,
            "artifacts": [],
            "reason": "task has no local artifact inputs",
            "external_effect_performed": False,
        }
    base_path = Path(task_queue_path).parent
    artifacts = []
    for raw_path in inputs:
        resolved = _resolve_local_artifact_path(raw_path, base_path=base_path)
        artifacts.append({
            "path": raw_path,
            "resolved_path": resolved.as_posix(),
            "exists": resolved.exists(),
            "is_local": not resolved.as_posix().startswith(("http://", "https://")),
        })
    present_count = sum(1 for artifact in artifacts if artifact.get("exists"))
    missing_count = len(artifacts) - present_count
    return {
        "status": "satisfied" if artifacts and missing_count == 0 else "missing_artifacts",
        "required_count": len(artifacts),
        "present_count": present_count,
        "missing_count": missing_count,
        "artifacts": artifacts,
        "reason": "all declared local artifact inputs exist" if missing_count == 0 else "one or more declared local artifact inputs are missing",
        "external_effect_performed": False,
    }


def _ledger_status_for_task(*, task: dict[str, Any], prior: dict[str, Any], completion: dict[str, Any] | None = None) -> str:
    if task.get("requires_operator_approval"):
        return "blocked_requires_approval"
    if completion and completion.get("status") == "satisfied":
        return "completed"
    if prior:
        return "carried"
    return "ready_for_local_work"


def _ledger_note_for_task(*, task: dict[str, Any], status: str, completion: dict[str, Any] | None = None) -> str:
    if status == "blocked_requires_approval":
        return "명시 승인 없이는 진행하지 않습니다. gate와 preflight를 먼저 확인하세요."
    if status == "completed" and completion and completion.get("status") == "satisfied":
        return f"로컬 산출물 {completion.get('present_count', 0)}개가 확인되어 자동 완료로 닫았습니다."
    if status == "carried":
        return "이전 run에서도 남아 있던 작업입니다. 오늘 완료할지, 계속 이월할지 판단하세요."
    return "로컬에서 외부 효과 없이 수행 가능한 작업입니다."


def _ledger_summary(entries: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "ready_for_local_work": 0,
        "carried": 0,
        "blocked_requires_approval": 0,
        "retired_not_in_current_queue": 0,
        "completed": 0,
        "deferred": 0,
        "blocked_by_operator": 0,
    }
    for entry in entries:
        status = entry.get("status", "")
        if status in summary:
            summary[status] += 1
    return summary


def _load_task_responses(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    responses = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        responses.append(json.loads(line))
    return responses


def _task_status_overrides(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if payload.get("schema_version") != ANALYST_TASK_STATUS_APPLY_SCHEMA_VERSION:
        return {}
    return {item.get("task_id", ""): item for item in payload.get("applied", []) if item.get("task_id")}


def _load_optional_json(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {}
    try:
        return load_json(target)
    except json.JSONDecodeError:
        return {}


def _run_trace_step(
    *,
    name: str,
    path: str | Path,
    stage: str,
    influence: str,
    required: bool,
    now: datetime,
) -> dict[str, Any]:
    target = Path(path)
    payload = _load_optional_json(target)
    exists = target.exists()
    age_hours = _readiness_age_hours(target, payload=payload, now=now) if exists else None
    freshness_status = "missing"
    if exists and age_hours is not None:
        freshness_status = "fresh" if age_hours <= 24 else "stale"
    return {
        "name": name,
        "stage": stage,
        "path": target.as_posix(),
        "required": required,
        "exists": exists,
        "status": payload.get("status", "present" if exists else "missing"),
        "freshness_status": freshness_status,
        "age_hours": round(age_hours, 2) if age_hours is not None else None,
        "generated_at": payload.get("generated_at", "") if payload else "",
        "schema_version": payload.get("schema_version", "") if payload else "",
        "influence": influence,
    }


def _run_trace_run_id(payloads: dict[str, dict[str, Any]]) -> str:
    for name in ["scenario_report", "daily_scout", "analyst_journal", "topic_memory"]:
        value = payloads.get(name, {}).get("run_id")
        if value:
            return str(value)
    return "local-daily-loop"


def _run_trace_influences(payloads: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    scout = payloads.get("daily_scout", {})
    evidence = payloads.get("evidence_catalog", {})
    memory = payloads.get("topic_memory", {})
    verdict = payloads.get("verdict", {})
    pattern = payloads.get("pattern_radar", {})
    review = payloads.get("daily_review", {})
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    primary = verdict.get("primary_next_step", {}) if verdict else {}
    pattern_summary = pattern.get("summary", {})
    review_summary = review.get("summary", {})
    return [
        {
            "label": "오늘 먼저 볼 주제",
            "value": recommended.get("name", primary.get("title", "없음")),
            "source": "daily_scout",
        },
        {
            "label": "근거 개수",
            "value": str(len(evidence.get("items", []))),
            "source": "evidence_catalog",
        },
        {
            "label": "누적 실행",
            "value": f"{memory.get('run_count', 0)}회",
            "source": "topic_memory",
        },
        {
            "label": "다음 안전 후보",
            "value": pattern_summary.get("top_next_pattern", "pattern review"),
            "source": "pattern_radar",
        },
        {
            "label": "review 응답",
            "value": f"{review_summary.get('response_count', 0)}개",
            "source": "daily_review",
        },
    ]


def _run_trace_external_flags(payloads: dict[str, dict[str, Any]]) -> list[str]:
    flags: list[str] = []
    for name, payload in payloads.items():
        if payload.get("external_effect_performed") is True:
            flags.append(f"{name}.external_effect_performed")
        if payload.get("host_write_performed") is True:
            flags.append(f"{name}.host_write_performed")
    return flags


def _run_trace_weak_spots(
    *,
    trace_steps: list[dict[str, Any]],
    payloads: dict[str, dict[str, Any]],
    external_flags: list[str],
) -> list[str]:
    weak: list[str] = []
    missing_required = [step["name"] for step in trace_steps if step["required"] and step["status"] == "missing"]
    if missing_required:
        weak.append(f"필수 trace step 누락: {', '.join(missing_required)}")
    stale = [step["name"] for step in trace_steps if step["freshness_status"] == "stale"]
    if stale:
        weak.append(f"오래된 trace step: {', '.join(stale[:5])}")
    evidence = payloads.get("evidence_catalog", {})
    source_rows = evidence.get("source_status", [])
    weak_sources = [
        row.get("source_name", "source")
        for row in source_rows
        if row.get("freshness_status") in {"stale", "unknown"} or row.get("relevance_label") in {"weak", "unscored"}
    ]
    if weak_sources:
        weak.append(f"약하거나 오래된 근거 source: {', '.join(weak_sources[:5])}")
    if external_flags:
        weak.append(f"외부효과 flag 확인 필요: {', '.join(external_flags)}")
    return weak


def _daily_handoff_canonical_run(run_ledger: dict[str, Any]) -> dict[str, Any]:
    if run_ledger.get("schema_version") != DAILY_RUN_LEDGER_SCHEMA_VERSION:
        return {}
    canonical_id = run_ledger.get("canonical_entry_id", "")
    for entry in run_ledger.get("entries", []):
        if entry.get("entry_id") == canonical_id or entry.get("canonical_status") == "canonical":
            return {
                "entry_id": entry.get("entry_id", ""),
                "run_id": entry.get("run_id", ""),
                "local_day": entry.get("local_day", ""),
                "run_status": entry.get("run_status", ""),
                "today_path": entry.get("today_path", ""),
                "archive_manifest": entry.get("archive_manifest", ""),
                "recorded_at": entry.get("recorded_at", ""),
            }
    return {}


def _daily_handoff_carried_items(
    *,
    journal: dict[str, Any],
    task_ledger: dict[str, Any],
    daily_review: dict[str, Any],
    review_effect: dict[str, Any],
    council: dict[str, Any],
    memory_audit: dict[str, Any],
    scout: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    match_text = _daily_handoff_match_text(scout=scout, review_effect=review_effect, daily_review=daily_review)
    for index, question in enumerate(journal.get("follow_up_questions", [])[:6], start=1):
        reflected = _text_overlaps(question, match_text)
        items.append({
            "id": f"DH-Q{index:02d}",
            "kind": "follow_up_question",
            "title": question,
            "source": "analyst_journal",
            "reflected_today": reflected,
            "evidence": "오늘 scout/review 문맥과 연결됩니다." if reflected else "오늘 scout/review 문맥에서 직접 연결을 찾지 못했습니다.",
            "next_action": "오늘 브리프를 읽을 때 이 질문이 해소됐는지 확인하세요." if reflected else "review-prompt에서 이 질문을 tomorrow focus로 남기세요.",
        })
    for entry in task_ledger.get("entries", [])[:8]:
        status = entry.get("status", "")
        if status in {"completed", "retired_not_in_current_queue"}:
            continue
        reflected = status in {"ready_for_local_work", "carried"} and _text_overlaps(entry.get("title", ""), match_text)
        items.append({
            "id": f"DH-{entry.get('task_id', 'TASK')}",
            "kind": "task",
            "title": entry.get("title", "local analyst task"),
            "source": "analyst_task_ledger",
            "reflected_today": reflected,
            "evidence": f"task status: {status or 'missing'}",
            "next_action": entry.get("operator_note") or entry.get("suggested_command") or "완료, 이월, 보류 중 하나로 task status response를 남기세요.",
        })
    if review_effect.get("schema_version") == OPERATOR_REVIEW_EFFECT_SCHEMA_VERSION:
        reflected = review_effect.get("status") == "applied"
        items.append({
            "id": "DH-REVIEW",
            "kind": "operator_feedback",
            "title": "어제/이전 review feedback이 오늘 scout scoring에 반영됐는지",
            "source": "review_effect",
            "reflected_today": reflected,
            "evidence": review_effect.get("interpretation", f"review effect status: {review_effect.get('status', 'missing')}"),
            "next_action": "반영됐으면 오늘 결과를 읽고, 아니면 review-response-apply 명령으로 선호를 다시 남기세요.",
        })
    if council.get("schema_version") == ANALYST_COUNCIL_SCHEMA_VERSION and council.get("status") != "ready_to_read":
        items.append({
            "id": "DH-COUNCIL",
            "kind": "council_warning",
            "title": "analyst council이 오늘 브리프를 주의해서 읽으라고 표시했습니다.",
            "source": "analyst_council",
            "reflected_today": False,
            "evidence": council.get("decision", {}).get("rationale", f"council status: {council.get('status', 'missing')}"),
            "next_action": "council.html에서 역할별 caution/blocker를 먼저 읽고 오늘 결론 강도를 낮추세요.",
        })
    risk_count = int(memory_audit.get("summary", {}).get("risk_count", 0) or 0)
    if risk_count:
        items.append({
            "id": "DH-MEMORY",
            "kind": "memory_warning",
            "title": "누적 기억 품질 경고가 남아 있습니다.",
            "source": "memory_audit",
            "reflected_today": False,
            "evidence": f"memory audit risk {risk_count}개",
            "next_action": "memory-audit.html에서 약한 source, vault gap, coverage gap을 먼저 확인하세요.",
        })
    if not items:
        items.append({
            "id": "DH-START",
            "kind": "startup",
            "title": "아직 이월 항목이 없습니다.",
            "source": "daily_handoff",
            "reflected_today": True,
            "evidence": "journal/task/review/council/memory artifact에서 남은 항목을 찾지 못했습니다.",
            "next_action": "오늘 브리프를 읽은 뒤 review-prompt의 짧은 응답을 남기면 내일 handoff가 생깁니다.",
        })
    return items


def _daily_handoff_study_closure(
    *,
    unresolved: list[dict[str, Any]],
    council: dict[str, Any],
    memory_audit: dict[str, Any],
    scout: dict[str, Any],
) -> dict[str, Any]:
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    topic = recommended.get("name", "오늘 브리프")
    items: list[dict[str, Any]] = []
    for item in unresolved:
        kind = item.get("kind", "handoff")
        title = item.get("title", "남은 질문")
        if kind == "follow_up_question":
            command = f"PYTHONPATH=src python3 -m mybroker appliance review-response-apply {shlex.quote(f'more \"{topic}\" \"handoff question: {title}\"')}"
            linked_surface = DEFAULT_REVIEW_PROMPT_SURFACE.as_posix()
            beginner_question = title
            why = "이 질문을 오늘 브리프와 연결해 읽으면 내일 scout가 무엇을 더 볼지 배웁니다."
            done_when = "오늘 브리프나 evidence에서 답이 되는 문장 하나와 아직 부족한 근거 하나를 말할 수 있습니다."
            severity = "study"
        elif kind == "council_warning":
            caution = council.get("decision", {}).get("operator_action", title)
            command = f"PYTHONPATH=src python3 -m mybroker appliance council-response-apply {shlex.quote(f'more \"{topic}\" \"council: {caution}\"')}"
            linked_surface = DEFAULT_ANALYST_COUNCIL_SURFACE.as_posix()
            beginner_question = "역할별 council 중 어떤 역할이 오늘 결론을 가장 약하게 만들었나요?"
            why = "council caution은 결론을 금지하는 신호가 아니라, 어떤 조건을 먼저 확인할지 알려주는 안전장치입니다."
            done_when = "caution 역할 하나와 그 역할이 요구한 다음 확인 항목 하나를 고릅니다."
            severity = "caution"
        elif kind == "memory_warning":
            question = memory_audit.get("next_questions", [title])[0] if memory_audit.get("next_questions") else title
            command = f"PYTHONPATH=src python3 -m mybroker appliance review-response-apply {shlex.quote(f'confusing \"{topic}\" \"memory: {question}\"')}"
            linked_surface = DEFAULT_MEMORY_AUDIT_SURFACE.as_posix()
            beginner_question = question
            why = "기억 품질 경고는 오늘 결론보다 누적 노트와 archive가 제대로 이어지는지 먼저 확인하라는 신호입니다."
            done_when = "vault/archive/source 중 어떤 기억 근거가 약한지 하나를 고릅니다."
            severity = "memory"
        else:
            command = f"PYTHONPATH=src python3 -m mybroker appliance handoff-response-apply {shlex.quote(f'more \"{topic}\" \"handoff: {title}\"')}"
            linked_surface = DEFAULT_DAILY_HANDOFF_SURFACE.as_posix()
            beginner_question = title
            why = "남은 handoff 항목을 local feedback으로 넘기면 다음 run이 같은 맥락을 잃지 않습니다."
            done_when = "이 항목을 내일 이어볼지, 오늘 충분한지 한 줄로 남깁니다."
            severity = "study"
        items.append({
            "id": f"SC-{item.get('id', len(items) + 1)}",
            "source_item_id": item.get("id", ""),
            "kind": kind,
            "title": title,
            "beginner_question": beginner_question,
            "why_it_matters": why,
            "source": item.get("source", "handoff"),
            "linked_surface": linked_surface,
            "copy_ready_command": command,
            "done_when": done_when,
            "severity": severity,
            "external_effect_performed": False,
            "host_write_performed": False,
        })
    return {
        "status": "queued" if items else "clear",
        "item_count": len(items),
        "items": items,
        "operator_rule": "남은 질문과 caution은 예측/추천이 아니라 오늘 공부로 닫습니다. 읽은 뒤 복사 가능한 local 응답 한 줄만 남깁니다.",
        "external_effect_performed": False,
        "host_write_performed": False,
    }


def _daily_handoff_match_text(*, scout: dict[str, Any], review_effect: dict[str, Any], daily_review: dict[str, Any]) -> str:
    parts: list[str] = []
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    parts.extend([recommended.get("name", ""), recommended.get("why", ""), recommended.get("next_question", "")])
    for recommendation in scout.get("recommendations", [])[:5]:
        parts.extend([recommendation.get("name", ""), recommendation.get("why", ""), recommendation.get("next_question", "")])
    for effect in review_effect.get("topic_effects", [])[:8]:
        parts.extend([effect.get("topic", ""), effect.get("effect", ""), effect.get("evidence", "")])
    for signal in daily_review.get("signals", [])[:8]:
        parts.extend([signal.get("topic", ""), signal.get("operator_note", ""), signal.get("reason", "")])
    return " ".join(str(part) for part in parts if part)


def _daily_handoff_commands(*, unresolved: list[dict[str, Any]], scout: dict[str, Any]) -> list[dict[str, Any]]:
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    topic = recommended.get("name", "오늘 브리프")
    question_items = [item for item in unresolved if item.get("kind") == "follow_up_question"]
    commands = [
        {
            "label": "오늘 읽음 기록",
            "command": f"PYTHONPATH=src python3 -m mybroker appliance handoff-response-apply {shlex.quote(f'more \"{topic}\" \"오늘 읽고 더 보고 싶은 부분을 기록\"')}",
            "why": "handoff-response-apply가 review/scout/effect/handoff proof를 같은 local run에서 갱신합니다.",
            "external_effect_performed": False,
        }
    ]
    if question_items:
        response = f'more "{topic}" "{question_items[0].get("title", "남은 질문")}"'
        commands.append({
            "label": "남은 질문 강조",
            "command": f"PYTHONPATH=src python3 -m mybroker appliance handoff-response-apply {shlex.quote(response)}",
            "why": "가장 중요한 unresolved 질문을 내일 우선순위로 넘깁니다.",
            "external_effect_performed": False,
        })
    task_items = [item for item in unresolved if item.get("kind") == "task" and item.get("id", "").startswith("DH-AT-")]
    if task_items:
        task_id = task_items[0].get("id", "DH-AT-001").replace("DH-", "")
        response = f'{task_id} carry "handoff에서 아직 남은 task로 확인"'
        commands.append({
            "label": "task 이월 기록",
            "command": f"PYTHONPATH=src python3 -m mybroker appliance handoff-response-apply {shlex.quote(response)}",
            "why": "task 상태를 로컬 응답으로 남기고 task ledger와 handoff proof를 다시 생성합니다.",
            "external_effect_performed": False,
        })
    commands.append({
        "label": "먼저 볼 화면",
        "command": "open reports/product/handoff.html reports/product/morning.html reports/product/today.html",
        "why": "로컬 파일 열기만 수행합니다. 외부 효과는 없습니다.",
        "external_effect_performed": False,
    })
    return commands


def _text_overlaps(value: str, haystack: str) -> bool:
    tokens = [
        token.strip(".,:;!?()[]{}\"'").lower()
        for token in value.split()
        if len(token.strip(".,:;!?()[]{}\"'")) >= 4
    ]
    if not tokens or not haystack:
        return False
    haystack_lower = haystack.lower()
    return any(token in haystack_lower for token in tokens[:12])


def _daily_run_ledger_entry(
    *,
    generated: datetime,
    trace: dict[str, Any],
    morning: dict[str, Any],
    readiness: dict[str, Any],
    scheduler: dict[str, Any],
    archive: dict[str, Any],
    archive_path: Path | None,
    run_trace_path: str | Path,
    morning_path: str | Path,
    readiness_path: str | Path,
    scheduler_operations_path: str | Path,
) -> dict[str, Any]:
    run_id = trace.get("run_id") or morning.get("run_id") or archive.get("run_id") or "daily-research"
    generated_at = trace.get("generated_at") or archive.get("generated_at") or generated.isoformat()
    local_day = _short_date(generated_at)
    artifacts = archive.get("artifacts", {}) if archive.get("schema_version") == ARCHIVE_SCHEMA_VERSION else {}
    entry_id = f"{local_day}:{run_id}:{generated.isoformat()}"
    trace_external = bool(trace.get("external_effect_performed"))
    morning_external = bool(morning.get("external_effect_performed"))
    readiness_external = bool(readiness.get("external_effect_performed"))
    scheduler_external = bool(scheduler.get("external_effect_performed"))
    trace_host = bool(trace.get("host_write_performed"))
    morning_host = bool(morning.get("host_write_performed"))
    readiness_host = bool(readiness.get("host_write_performed"))
    scheduler_host = bool(scheduler.get("host_write_performed"))
    return {
        "entry_id": entry_id,
        "local_day": local_day,
        "run_id": str(run_id),
        "generated_at": generated_at,
        "recorded_at": generated.isoformat(),
        "canonical_status": "candidate",
        "run_status": trace.get("status", morning.get("status", readiness.get("status", "review"))),
        "morning_status": morning.get("status", "missing"),
        "readiness_status": readiness.get("status", "missing"),
        "scheduler_status": scheduler.get("status", "missing"),
        "archive_manifest": archive_path.as_posix() if archive_path else "",
        "archive_dir": archive.get("archive_dir", ""),
        "today_path": artifacts.get("today", DEFAULT_TODAY_OUTPUT.as_posix()),
        "morning_path": Path(morning_path).as_posix(),
        "readiness_path": Path(readiness_path).as_posix(),
        "run_trace_path": Path(run_trace_path).as_posix(),
        "scheduler_operations_path": Path(scheduler_operations_path).as_posix(),
        "source_count": _ledger_source_count(trace=trace, readiness=readiness),
        "external_effect_performed": trace_external or morning_external or readiness_external or scheduler_external,
        "host_write_performed": trace_host or morning_host or readiness_host or scheduler_host,
        "operator_note": _daily_run_ledger_note(trace=trace, readiness=readiness, scheduler=scheduler),
    }


def _daily_run_ledger_entries(
    *,
    previous_entries: list[dict[str, Any]],
    current_entry: dict[str, Any],
) -> list[dict[str, Any]]:
    entries = [dict(entry) for entry in previous_entries if entry.get("entry_id") != current_entry["entry_id"]]
    entries.append(current_entry)
    return sorted(entries, key=lambda entry: entry.get("recorded_at", entry.get("generated_at", "")), reverse=True)


def _daily_run_ledger_canonical_entry_id(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return ""
    return sorted(entries, key=lambda entry: entry.get("recorded_at", entry.get("generated_at", "")), reverse=True)[0].get("entry_id", "")


def _daily_run_ledger_note(*, trace: dict[str, Any], readiness: dict[str, Any], scheduler: dict[str, Any]) -> str:
    if readiness.get("status") in {"blocked", "stale"}:
        return "필수 산출물 freshness를 먼저 확인한 뒤 today를 읽으세요."
    if trace.get("status") == "blocked":
        return "trace에 필수 단계 누락이 있습니다. run-trace를 먼저 확인하세요."
    if scheduler.get("status") in {"not_ready", "blocked", "missing"}:
        return "자동 실행 증거가 약합니다. scheduler 화면에서 run-once/preflight 상태를 확인하세요."
    return "오늘 canonical run으로 읽어도 됩니다. 외부효과는 수행되지 않았습니다."


def _ledger_source_count(*, trace: dict[str, Any], readiness: dict[str, Any]) -> int:
    for influence in trace.get("what_shaped_today", []):
        if influence.get("label") == "근거 개수":
            try:
                return int(str(influence.get("value", "0")).split()[0])
            except ValueError:
                return 0
    return int(readiness.get("summary", {}).get("fresh_required_count", 0) or 0)


def _drift_review_signals(
    *,
    trace: dict[str, Any],
    pattern: dict[str, Any],
    readiness: dict[str, Any],
    source_refresh: dict[str, Any],
    ledger: dict[str, Any],
    review: dict[str, Any],
) -> list[dict[str, str]]:
    trace_summary = trace.get("summary", {})
    pattern_summary = pattern.get("summary", {})
    readiness_summary = readiness.get("summary", {})
    ledger_summary = ledger.get("summary", {})
    review_summary = review.get("summary", {})
    return [
        {
            "name": "trace_health",
            "value": trace.get("status", "missing"),
            "interpretation": f"missing required {trace_summary.get('missing_required_count', 'unknown')}, stale {trace_summary.get('stale_count', 'unknown')}",
        },
        {
            "name": "pattern_next",
            "value": pattern_summary.get("top_next_pattern", "missing"),
            "interpretation": "다음 slice 후보가 pattern radar에 남아 있는지 확인합니다.",
        },
        {
            "name": "readiness",
            "value": readiness.get("status", "missing"),
            "interpretation": f"fresh required {readiness_summary.get('fresh_required_count', 'unknown')}, stale required {readiness_summary.get('stale_required_count', 'unknown')}",
        },
        {
            "name": "source_authority",
            "value": source_refresh.get("status", "missing"),
            "interpretation": "live source 실행이 필요한 상태라면 별도 승인 gate가 필요합니다.",
        },
        {
            "name": "task_pressure",
            "value": str(ledger_summary.get("blocked_requires_approval", 0) + ledger_summary.get("blocked_by_operator", 0)),
            "interpretation": "blocked task가 많으면 새 기능보다 운영 정리가 먼저입니다.",
        },
        {
            "name": "operator_feedback",
            "value": str(review_summary.get("response_count", 0)),
            "interpretation": "operator review가 적으면 방향 판단 confidence를 낮춥니다.",
        },
    ]


def _drift_review_decision(*, signals: list[dict[str, str]]) -> dict[str, str]:
    values = {signal["name"]: signal["value"] for signal in signals}
    if values.get("trace_health") in {"missing", "blocked"}:
        return {
            "status": "blocked",
            "recommended_branch": "repair_trace_inputs",
            "rationale": "trace proof 자체가 없거나 필수 단계가 누락되어 다음 작업 방향을 믿기 어렵습니다.",
            "confidence": "high",
        }
    if values.get("source_authority") in {"approval_required", "preflight_required", "ready_to_execute"}:
        return {
            "status": "approval_required",
            "recommended_branch": "hold_external_effect_until_scoped_approval",
            "rationale": "근거 새로고침 쪽은 별도 승인 gate가 필요하므로 로컬-only 작업과 분리해야 합니다.",
            "confidence": "high",
        }
    if values.get("readiness") in {"stale", "blocked"}:
        return {
            "status": "inspect",
            "recommended_branch": "refresh_local_artifacts_before_new_work",
            "rationale": "준비 상태가 오래되었거나 막혀 있어 새 slice보다 로컬 산출물 재생성이 먼저입니다.",
            "confidence": "medium",
        }
    if values.get("pattern_next") in {"missing", ""}:
        return {
            "status": "inspect",
            "recommended_branch": "refresh_pattern_radar",
            "rationale": "다음 안전 slice 후보가 명확하지 않아 pattern radar 갱신이 필요합니다.",
            "confidence": "medium",
        }
    return {
        "status": "aligned",
        "recommended_branch": values.get("pattern_next", "continue_local_loop"),
        "rationale": "trace, readiness, pattern radar가 모두 로컬-only 다음 작업을 지지합니다.",
        "confidence": "medium",
    }


def _drift_review_next_steps(*, decision: dict[str, str], signals: list[dict[str, str]]) -> list[str]:
    branch = decision.get("recommended_branch", "")
    steps = [
        f"추천 branch를 확인합니다: {branch}",
        "새 외부효과 작업은 source/host/notification approval gate와 분리합니다.",
    ]
    if decision.get("status") == "aligned":
        steps.append("다음 로컬-only slice를 Flyhigh direction review와 merge gate에 올립니다.")
    elif decision.get("status") == "approval_required":
        steps.append("operator가 명시 승인하기 전까지 live/source/host 작업은 진행하지 않습니다.")
    elif decision.get("status") == "blocked":
        steps.append("누락된 trace input을 먼저 재생성하고 validate-drift-review를 다시 실행합니다.")
    else:
        steps.append("readiness, trace, pattern radar 중 약한 신호를 먼저 확인합니다.")
    if any(signal["name"] == "operator_feedback" and signal["value"] == "0" for signal in signals):
        steps.append("operator review 응답이 없으므로 review prompt에서 복사 가능한 피드백을 남깁니다.")
    else:
        steps.append("operator review effect에서 피드백이 scout score에 반영됐는지 확인합니다.")
    return steps


def _morning_pending_decisions(
    *,
    live_gate: dict[str, Any],
    live_run: dict[str, Any],
    preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    decisions = []
    if live_gate.get("status") == "approval_required":
        for decision in live_gate.get("decisions", []):
            decisions.append({
                "id": decision.get("id", "live_network_refresh"),
                "title": "live source refresh 승인 여부",
                "why": "무료 공개 자료 live refresh 후보가 있지만 실제 네트워크 호출은 별도 승인 전까지 실행하지 않습니다.",
                "approval_scope": decision.get("approval_scope", ""),
                "risk_level": decision.get("risk_level", "medium"),
                "reversibility": decision.get("reversibility", ""),
                "copy_ready_response": decision.get("copy_ready_response", ""),
                "agent_will_run": decision.get("agent_will_run", []),
                "agent_will_not_run": decision.get("agent_will_not_run", []),
                "stale_context_guard": decision.get("stale_context_guard", ""),
                "approval_required": True,
            })
    execution = live_run.get("execution", {})
    if execution.get("status") in {"blocked", "not_requested"} and live_run.get("approval_status") == "missing":
        for blocker in execution.get("blockers", []):
            if blocker == "live_network_refresh_not_approved" and not decisions:
                decisions.append({
                    "id": "live_network_refresh",
                    "title": "live source refresh 승인 누락",
                    "why": live_run.get("next_step", "approval response is missing"),
                    "approval_scope": "live_network_refresh",
                    "risk_level": "medium",
                    "reversibility": "cache_artifact_can_be_deleted",
                    "copy_ready_response": "approve live_network_refresh live_network_refresh",
                    "agent_will_run": execution.get("proposed_commands", []),
                    "agent_will_not_run": ["paid API calls", "credentialed sources", "notification send", "host-level writes"],
                    "stale_context_guard": "Regenerate live-run proof before approval if source plan changed.",
                    "approval_required": True,
                })
    if preflight.get("status") == "blocked" and preflight.get("blockers"):
        decisions.append({
            "id": "live_refresh_preflight",
            "title": "live execution preflight 차단",
            "why": "; ".join(preflight.get("blockers", [])[:3]),
            "approval_scope": "live_network_refresh",
            "risk_level": "medium",
            "reversibility": "no external effect performed",
            "copy_ready_response": "rerun preflight after exact approval and confirmation",
            "agent_will_run": [],
            "agent_will_not_run": ["network execution until preflight passes"],
            "stale_context_guard": "Preflight must be regenerated after any approval or source change.",
            "approval_required": True,
        })
    return decisions


def _morning_top_tasks(*, ledger: dict[str, Any], queue: dict[str, Any]) -> list[dict[str, Any]]:
    entries = ledger.get("entries", [])
    if not entries:
        return queue.get("tasks", [])[:4]
    rank = {
        "blocked_requires_approval": 0,
        "blocked_by_operator": 1,
        "ready_for_local_work": 2,
        "carried": 3,
        "deferred": 4,
        "completed": 5,
        "retired_not_in_current_queue": 6,
    }
    return sorted(entries, key=lambda item: (rank.get(item.get("status", ""), 9), item.get("priority", ""), item.get("task_id", "")))[:4]


def _morning_command_bar(*, ledger: dict[str, Any], pending_decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    commands = []
    actionable = [
        entry for entry in ledger.get("entries", [])
        if entry.get("status") in {"ready_for_local_work", "carried", "deferred"}
        and entry.get("requires_operator_approval") is not True
    ]
    for entry in actionable[:3]:
        task_id = entry.get("task_id", "")
        commands.append({
            "label": f"{task_id} 완료 표시",
            "command": f"{task_id} complete \"오늘 확인 완료\"",
            "effect": "local task status response only",
            "external_effect_performed": False,
        })
        commands.append({
            "label": f"{task_id} 이월 표시",
            "command": f"{task_id} carry \"내일 계속 확인\"",
            "effect": "local task status response only",
            "external_effect_performed": False,
        })
        if len(commands) >= 4:
            break
    for decision in pending_decisions[:2]:
        commands.append({
            "label": f"{decision.get('id', 'decision')} 승인 응답",
            "command": decision.get("copy_ready_response", ""),
            "effect": "approval response only; separate apply/preflight still required",
            "external_effect_performed": False,
        })
    if not commands:
        commands.append({
            "label": "오늘 홈 열기",
            "command": "open reports/product/daily-home.html reports/product/handoff.html",
            "effect": "local file open only",
            "external_effect_performed": False,
        })
    return commands[:6]


def _morning_status(
    *,
    pending_decisions: list[dict[str, Any]],
    ledger_summary: dict[str, Any],
    doctor: dict[str, Any],
) -> str:
    if doctor.get("fail_count", 0):
        return "blocked"
    if pending_decisions or ledger_summary.get("blocked_requires_approval", 0) or ledger_summary.get("blocked_by_operator", 0):
        return "operator_review"
    return "ready"


def _today_vault_notes(*, vault_notes: list[dict[str, Any]], memory_topics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    topic_ids = {topic.get("topic_id", "") for topic in memory_topics[:5]}
    topic_names = {topic.get("name", "").lower() for topic in memory_topics[:5]}
    matched = []
    fallback = []
    for note in vault_notes:
        fallback.append(note)
        if note.get("topic_id") in topic_ids or note.get("topic_name", "").lower() in topic_names:
            matched.append(note)
    return matched or fallback


def _vault_notes_for_memory(vault: dict[str, Any]) -> list[dict[str, Any]]:
    if vault.get("schema_version") != "knowledge_vault_compile.v1":
        return []
    notes = []
    for note in vault.get("compiled_notes", []):
        notes.append({
            "title": note.get("title", ""),
            "topic_id": note.get("topic_id", ""),
            "topic_name": note.get("topic_name", ""),
            "source_path": note.get("source_path", ""),
            "wiki_path": note.get("wiki_path", ""),
            "source_hash": note.get("source_hash", ""),
            "key_takeaways": note.get("key_takeaways", []),
        })
    return notes


def _query_tokens(query: str) -> list[str]:
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in query)
    tokens = [token for token in normalized.split() if len(token) >= 2]
    compact = normalized.replace(" ", "")
    if compact and compact not in tokens:
        tokens.append(compact)
    return tokens or [query.strip().lower()]


def _match_score(tokens: list[str], haystacks: list[str]) -> float:
    text = " ".join(haystacks).lower()
    if not text:
        return 0.0
    hits = 0
    weighted = 0.0
    for token in tokens:
        if token and token in text:
            hits += 1
            weighted += min(1.0, max(0.2, len(token) / 12))
    if not tokens:
        return 0.0
    coverage = hits / len(tokens)
    return min(1.0, (coverage * 0.65) + (weighted / max(1, len(tokens)) * 0.35))


def _match_reasons(tokens: list[str], haystacks: list[str]) -> list[str]:
    text = " ".join(haystacks).lower()
    reasons = [f"'{token}' 포함" for token in tokens if token and token in text]
    return reasons[:5]


def _query_next_questions(*, query: str, topics: list[dict[str, Any]], status: str) -> list[str]:
    if status == "no_direct_match":
        return [
            f"'{query}'를 더 넓은 주제명이나 쉬운 키워드로 다시 물어볼까요?",
            "오늘 브리프를 먼저 실행해 최신 메모리를 만든 뒤 다시 검색할까요?",
            "이 질문에 필요한 무료 공개 자료원이 무엇인지 먼저 확인할까요?",
        ]
    questions = []
    for topic in topics:
        questions.extend(topic.get("questions", [])[:2])
    questions.append(f"'{query}'에 대해 최근 아카이브의 설명이 오늘도 유효한지 확인할까요?")
    questions.append("반대 근거가 쌓인 source가 있는지 먼저 볼까요?")
    return questions[:5]


def _query_recall_quality(
    *,
    status: str,
    topic_count: int,
    archive_count: int,
    vault_note_count: int,
    weak_spot_count: int,
) -> dict[str, Any]:
    coverage_score = min(1.0, (topic_count * 0.35) + (archive_count * 0.2) + (vault_note_count * 0.25))
    if status == "no_direct_match":
        level = "weak"
        confidence = "low"
        coverage_label = "직접 매칭 없음"
        summary = "질문과 직접 연결되는 누적 기억이 부족합니다. 먼저 넓은 키워드로 다시 묻거나 오늘 루프를 실행하세요."
    elif coverage_score >= 0.85 and weak_spot_count <= 1:
        level = "strong"
        confidence = "medium"
        coverage_label = "주제, 아카이브, vault가 함께 연결됨"
        summary = "누적 주제 기억, 과거 실행, 원천 노트가 함께 잡혔습니다. 그래도 원문과 최신성은 확인해야 합니다."
    elif coverage_score >= 0.45:
        level = "usable"
        confidence = "medium-low"
        coverage_label = "일부 기억 연결"
        summary = "답의 출발점으로는 충분하지만, 약한 source나 빠진 원천 노트를 먼저 확인해야 합니다."
    else:
        level = "thin"
        confidence = "low"
        coverage_label = "부분 매칭"
        summary = "연결은 있으나 근거가 얇습니다. 결론보다 추가 자료 확인 질문으로 사용하세요."
    return {
        "level": level,
        "confidence": confidence,
        "coverage_score": round(coverage_score, 3),
        "coverage_label": coverage_label,
        "summary": summary,
    }


def _query_evidence_bundles(
    *,
    topics: list[dict[str, Any]],
    vault_notes: list[dict[str, Any]],
    archives: list[dict[str, Any]],
    source_relevance: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    bundles: list[dict[str, Any]] = []
    for topic in topics[:3]:
        bundles.append({
            "bundle_type": "topic_memory",
            "title": topic.get("name", "주제 기억"),
            "strength": _bundle_strength(topic.get("score", 0), len(topic.get("source_names", []))),
            "why_it_matters": topic.get("summary", "누적 주제 기억이 질문과 연결됩니다."),
            "source_names": topic.get("source_names", [])[:4],
            "artifact_path": "reports/memory/topic-memory.json",
        })
    for note in vault_notes[:3]:
        bundles.append({
            "bundle_type": "vault_note",
            "title": note.get("title", "Vault note"),
            "strength": _bundle_strength(note.get("score", 0), len(note.get("key_takeaways", []))),
            "why_it_matters": " · ".join(note.get("key_takeaways", [])[:2]) or "원천 노트가 질문과 연결됩니다.",
            "source_names": [note.get("topic_name", "")] if note.get("topic_name") else [],
            "artifact_path": note.get("wiki_path", note.get("source_path", "")),
        })
    if archives:
        latest = archives[0]
        bundles.append({
            "bundle_type": "archive",
            "title": f"최근 실행 {latest.get('generated_at', '')[:10]}",
            "strength": "context",
            "why_it_matters": "과거 daily loop 산출물과 연결해 오늘 질문이 반복되는지 확인합니다.",
            "source_names": list(latest.get("artifacts", {}).keys())[:5],
            "artifact_path": latest.get("archive_dir", ""),
        })
    strong_sources = [
        row for row in source_relevance
        if row.get("relevance_label") in {"strong", "medium"} and row.get("freshness_status") not in {"stale", "unknown"}
    ]
    if strong_sources:
        bundles.append({
            "bundle_type": "source_posture",
            "title": "상대적으로 쓸 수 있는 source",
            "strength": "supporting",
            "why_it_matters": "신선도와 관련도 기준에서 먼저 확인할 source 후보입니다.",
            "source_names": [row.get("source_name", "") for row in strong_sources[:5]],
            "artifact_path": "reports/evidence/daily-evidence-catalog.json",
        })
    return bundles[:8]


def _query_weak_spots(
    *,
    status: str,
    topics: list[dict[str, Any]],
    vault_notes: list[dict[str, Any]],
    archives: list[dict[str, Any]],
    source_relevance: list[dict[str, Any]],
) -> list[dict[str, str]]:
    weak: list[dict[str, str]] = []
    if status == "no_direct_match":
        weak.append({
            "severity": "high",
            "title": "직접 매칭 부족",
            "why": "현재 질문을 설명할 누적 주제 기억이나 vault note가 부족합니다.",
            "next_check": "넓은 키워드로 다시 묻거나 raw vault에 관련 자료를 넣고 compile하세요.",
        })
    if not vault_notes:
        weak.append({
            "severity": "medium",
            "title": "원천 노트 부족",
            "why": "topic memory는 있어도 사용자가 직접 모은 원천 노트가 연결되지 않았습니다.",
            "next_check": "관련 글이나 보고서를 research-vault/raw에 넣고 appliance run을 다시 실행하세요.",
        })
    stale_sources = [
        row for row in source_relevance
        if row.get("freshness_status") in {"stale", "unknown"} or row.get("relevance_label") in {"weak", "unscored"}
    ]
    if stale_sources:
        weak.append({
            "severity": "medium",
            "title": "source 신선도/관련도 약함",
            "why": f"{len(stale_sources)}개 source가 오래됐거나 관련도가 약합니다.",
            "next_check": "source refresh page에서 승인 없이 가능한 로컬/샘플 확인부터 보세요.",
        })
    if not archives:
        weak.append({
            "severity": "low",
            "title": "과거 실행 연결 부족",
            "why": "관련 archive가 없어 같은 질문이 반복되는지 확인하기 어렵습니다.",
            "next_check": "며칠간 daily loop를 쌓은 뒤 같은 질문을 다시 비교하세요.",
        })
    if topics and all(float(topic.get("score", 0)) < 0.5 for topic in topics):
        weak.append({
            "severity": "medium",
            "title": "낮은 topic match",
            "why": "매칭된 주제는 있지만 점수가 낮아 우연한 단어 겹침일 수 있습니다.",
            "next_check": "topic 이름, 관련 기업/섹터, 쉬운 키워드를 섞어 다시 질문하세요.",
        })
    return weak[:5]


def _query_reading_order(
    *,
    topics: list[dict[str, Any]],
    vault_notes: list[dict[str, Any]],
    archives: list[dict[str, Any]],
    evidence_bundles: list[dict[str, Any]],
    weak_spots: list[dict[str, str]],
) -> list[dict[str, str]]:
    order: list[dict[str, str]] = []
    if topics:
        order.append({
            "label": f"1. {topics[0].get('name', 'matched topic')}",
            "why": "먼저 누적 주제 기억의 요약과 질문을 읽어 현재 맥락을 잡습니다.",
            "path": "reports/memory/topic-memory.json",
        })
    if vault_notes:
        order.append({
            "label": f"2. {vault_notes[0].get('title', 'vault note')}",
            "why": "사용자가 직접 쌓은 원천 노트에서 왜 이 주제가 남았는지 확인합니다.",
            "path": vault_notes[0].get("wiki_path", vault_notes[0].get("source_path", "")),
        })
    if archives:
        order.append({
            "label": "3. 최근 archive today/brief",
            "why": "과거 daily loop의 설명과 오늘 질문이 이어지는지 비교합니다.",
            "path": archives[0].get("archive_dir", ""),
        })
    if evidence_bundles:
        order.append({
            "label": "4. 근거 묶음",
            "why": "topic, vault, archive, source posture를 한 번에 비교합니다.",
            "path": evidence_bundles[0].get("artifact_path", ""),
        })
    if weak_spots:
        order.append({
            "label": "5. 약점 먼저 확인",
            "why": weak_spots[0].get("why", "결론 전에 약한 부분을 확인합니다."),
            "path": "reports/product/source-refresh.html",
        })
    return order[:5]


def _bundle_strength(score: Any, support_count: int) -> str:
    try:
        numeric = float(score)
    except (TypeError, ValueError):
        numeric = 0.0
    if numeric >= 0.75 and support_count >= 2:
        return "strong"
    if numeric >= 0.45 or support_count >= 2:
        return "usable"
    return "thin"


def _doctor_check_path(
    name: str,
    path: Path | None,
    missing_level: str,
    message: str,
    *,
    executable: bool = False,
    freshness_hours: int | None = None,
) -> dict[str, Any]:
    if not path or not path.exists():
        return {
            "name": name,
            "status": missing_level,
            "message": f"{message} Missing: {path.as_posix() if path else 'not_found'}",
            "path": path.as_posix() if path else "",
        }
    details: dict[str, Any] = {
        "name": name,
        "status": "pass",
        "message": message,
        "path": path.as_posix(),
    }
    if executable and not os.access(path, os.X_OK):
        details["status"] = "fail"
        details["message"] = f"{message} File is not executable."
    if freshness_hours is not None:
        age = _file_age_hours(path)
        details["age_hours"] = round(age, 2)
        if age > freshness_hours:
            details["status"] = "warn"
            details["message"] = f"{message} Artifact is older than {freshness_hours} hours."
    return details


def _doctor_check_notification(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "name": "notification_payload",
            "status": "warn",
            "message": "Notification payload has not been generated yet.",
            "path": path.as_posix(),
        }
    payload = load_json(path)
    required_env = payload.get("required_env", [])
    missing_env = [key for key in required_env if not os.environ.get(key)]
    status = "pass" if payload.get("dry_run") or not missing_env else "warn"
    message = "Notification payload exists."
    if payload.get("dry_run"):
        message = "Notification payload is dry-run ready; real send remains explicitly gated."
    elif missing_env:
        message = "Notification send is configured but provider environment variables are missing."
    return {
        "name": "notification_payload",
        "status": status,
        "message": message,
        "path": path.as_posix(),
        "provider": payload.get("provider", ""),
        "delivery_status": payload.get("delivery_status", ""),
        "missing_env": missing_env,
    }


def _doctor_check_launchd(plist_path: Path, *, require_launchd_loaded: bool) -> dict[str, Any]:
    launchd = _launchd_state()
    if launchd.get("inspect_error"):
        return {
            "name": "launchd_loaded",
            "status": "fail" if require_launchd_loaded else "warn",
            "message": f"Could not inspect launchd state: {launchd['inspect_error']}",
            "plist": plist_path.as_posix(),
            "loaded": False,
        }
    loaded = bool(launchd["loaded"])
    if loaded:
        status = "pass"
        message = "LaunchAgent is loaded for the current user."
    else:
        status = "fail" if require_launchd_loaded else "warn"
        message = "LaunchAgent is not loaded yet; install remains a host-level explicit step."
    return {
        "name": "launchd_loaded",
        "status": status,
        "message": message,
        "plist": plist_path.as_posix(),
        "loaded": loaded,
        "command": launchd["command"],
    }


def _launchd_state() -> dict[str, Any]:
    command = ["launchctl", "print", f"gui/{os.getuid()}/{LAUNCHD_LABEL}"]
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=8, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "loaded": False,
            "command": " ".join(command),
            "returncode": None,
            "inspect_error": str(exc),
        }
    return {
        "loaded": result.returncode == 0,
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout_excerpt": result.stdout[:500],
        "stderr_excerpt": result.stderr[:500],
    }


def _scheduler_status(*, source_plist: Path, source_script: Path, installed_plist: Path, loaded: bool) -> str:
    if loaded:
        return "loaded"
    if installed_plist.exists():
        return "installed_not_loaded"
    if source_plist.exists() and source_script.exists() and os.access(source_script, os.X_OK):
        return "assets_ready"
    return "not_ready"


def _scheduler_commands(*, source_plist: Path, installed_plist: Path) -> dict[str, str]:
    return {
        "prepare_assets": "PYTHONPATH=src python3 -m mybroker appliance init --project-root .",
        "install": f"mkdir -p ~/Library/LaunchAgents && cp {source_plist.as_posix()} {installed_plist.as_posix()}",
        "load": f"launchctl bootstrap gui/$(id -u) {installed_plist.as_posix()}",
        "start_now": f"launchctl kickstart -k gui/$(id -u)/{LAUNCHD_LABEL}",
        "status": f"launchctl print gui/$(id -u)/{LAUNCHD_LABEL}",
        "unload": f"launchctl bootout gui/$(id -u)/{LAUNCHD_LABEL}",
        "uninstall": f"rm {installed_plist.as_posix()}",
    }


def _scheduler_next_actions(*, source_plist: Path, source_script: Path, installed_plist: Path, loaded: bool) -> list[str]:
    if not source_plist.exists() or not source_script.exists() or not os.access(source_script, os.X_OK):
        return ["Run `PYTHONPATH=src python3 -m mybroker appliance init --project-root .` to prepare scheduler assets."]
    if not installed_plist.exists():
        return ["Review reports/runtime/scheduler-status.json, then run the install and load commands if you want the daily schedule active."]
    if not loaded:
        return ["The LaunchAgent plist is installed but not loaded. Run the load command, then `appliance scheduler status` again."]
    return ["Scheduler is loaded. Use the start_now command for an immediate proof run, then inspect reports/runtime logs and tomorrow's archive."]


def _scheduler_apply_actions(
    *,
    source_plist: Path,
    installed_plist: Path,
    install: bool,
    load: bool,
    start_now: bool,
    unload: bool,
    uninstall: bool,
) -> list[dict[str, Any]]:
    actions = []
    if install:
        actions.append({
            "name": "install",
            "kind": "copy_plist",
            "source": source_plist.as_posix(),
            "target": installed_plist.as_posix(),
            "command": f"mkdir -p {installed_plist.parent.as_posix()} && cp {source_plist.as_posix()} {installed_plist.as_posix()}",
        })
    if load:
        actions.append({
            "name": "load",
            "kind": "launchctl",
            "command": f"launchctl bootstrap gui/{os.getuid()} {installed_plist.as_posix()}",
        })
    if start_now:
        actions.append({
            "name": "start_now",
            "kind": "launchctl",
            "command": f"launchctl kickstart -k gui/{os.getuid()}/{LAUNCHD_LABEL}",
        })
    if unload:
        actions.append({
            "name": "unload",
            "kind": "launchctl",
            "command": f"launchctl bootout gui/{os.getuid()}/{LAUNCHD_LABEL}",
        })
    if uninstall:
        actions.append({
            "name": "uninstall",
            "kind": "remove_file",
            "target": installed_plist.as_posix(),
            "command": f"rm {installed_plist.as_posix()}",
        })
    return actions


def _execute_scheduler_action(action: dict[str, Any]) -> dict[str, Any]:
    result = dict(action)
    result["executed"] = True
    try:
        if action["kind"] == "copy_plist":
            source = Path(action["source"])
            target = Path(action["target"])
            if not source.exists():
                raise FileNotFoundError(source.as_posix())
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            result["status"] = "ok"
            return result
        if action["kind"] == "remove_file":
            target = Path(action["target"])
            if target.exists():
                target.unlink()
            result["status"] = "ok"
            return result
        completed = subprocess.run(action["command"].split(), text=True, capture_output=True, timeout=30, check=False)
        result["returncode"] = completed.returncode
        result["stdout_excerpt"] = completed.stdout[:500]
        result["stderr_excerpt"] = completed.stderr[:500]
        result["status"] = "ok" if completed.returncode == 0 else "failed"
    except Exception as exc:  # pragma: no cover - defensive host-level guard
        result["status"] = "failed"
        result["error"] = str(exc)
    return result


def _preflight_artifact_check(
    name: str,
    path: Path,
    *,
    expected_schema: str,
    max_age_hours: int,
    predicate: Any,
    message: str,
) -> dict[str, Any]:
    if not path.exists():
        return {
            "name": name,
            "status": "fail",
            "message": f"Missing artifact: {path.as_posix()}",
            "path": path.as_posix(),
        }
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return {
            "name": name,
            "status": "fail",
            "message": f"Invalid JSON: {exc}",
            "path": path.as_posix(),
        }
    if payload.get("schema_version") != expected_schema:
        return {
            "name": name,
            "status": "fail",
            "message": f"Unexpected schema_version: {payload.get('schema_version')}",
            "path": path.as_posix(),
        }
    age_hours = _artifact_age_hours(path, payload)
    status = "pass"
    reason = message
    if age_hours > max_age_hours:
        status = "warn"
        reason = f"{message} Artifact is older than {max_age_hours} hours."
    if not predicate(payload):
        status = "fail"
        reason = f"{message} Required condition was not met."
    return {
        "name": name,
        "status": status,
        "message": reason,
        "path": path.as_posix(),
        "age_hours": round(age_hours, 2),
    }


def _activation_verify_check(name: str, condition: bool, message: str, *, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pass" if condition else "fail",
        "message": message if condition else f"Required condition not met: {message}",
        "evidence": evidence,
    }


def _scheduler_activation_decision(*, preflight: dict[str, Any], verify: dict[str, Any]) -> dict[str, Any]:
    preflight_ready = preflight.get("status") in {"ready", "already_active"}
    active_verified = verify.get("status") == "active_verified"
    readiness = "ready" if preflight_ready and not active_verified else "pending"
    if not preflight_ready:
        readiness = "blocked"
    if active_verified:
        readiness = "complete"
    return {
        "id": "scheduler_activation",
        "title": "Activate daily scheduler",
        "approval_scope": "confirmed_host_write",
        "readiness": readiness,
        "current_state": {
            "preflight_status": preflight.get("status", "missing"),
            "verify_status": verify.get("status", "missing"),
            "preflight_blockers": preflight.get("blockers", []),
            "verify_blockers": verify.get("blockers", []),
        },
        "operator_can_say": "approve scheduler_activation confirmed_host_write",
        "agent_will_run": [
            "PYTHONPATH=src python3 -m mybroker appliance scheduler apply --install --load --start-now --confirm-host-write",
            "PYTHONPATH=src python3 -m mybroker appliance scheduler activation-verify",
        ],
        "risk": "Installs and loads a LaunchAgent for the current macOS user and starts the local runner.",
        "reversibility": "partially_reversible",
        "rollback_command": "PYTHONPATH=src python3 -m mybroker appliance scheduler apply --unload --uninstall --confirm-host-write",
    }


def _notification_send_decision(*, notification: dict[str, Any]) -> dict[str, Any]:
    required_env = notification.get("required_env", [])
    missing_env = [key for key in required_env if not os.environ.get(key)]
    dry_run_ready = notification.get("dry_run") is True and notification.get("delivery_status") == "dry_run_ready"
    readiness = "ready" if dry_run_ready and not missing_env else "blocked"
    return {
        "id": "notification_send",
        "title": "Send phone notification",
        "approval_scope": "send_notification",
        "readiness": readiness,
        "current_state": {
            "provider": notification.get("provider", "missing"),
            "delivery_status": notification.get("delivery_status", "missing"),
            "dry_run": notification.get("dry_run"),
            "missing_env": missing_env,
        },
        "operator_can_say": "approve notification_send send_notification",
        "agent_will_run": [
            "PYTHONPATH=src python3 -m mybroker appliance notify --provider <provider> --send",
        ],
        "risk": "Sends one message through the configured provider using local environment secrets.",
        "reversibility": "not_reversible",
        "rollback_command": "",
    }


def _private_phone_access_decision(*, phone_access: dict[str, Any]) -> dict[str, Any]:
    enable_commands = _phone_access_enable_commands(phone_access=phone_access)
    rollback_command = _phone_access_rollback_command(phone_access=phone_access)
    readiness = "ready" if phone_access.get("schema_version") == PHONE_ACCESS_SCHEMA_VERSION and enable_commands else "blocked"
    return {
        "id": "private_phone_access",
        "title": "Enable private phone access",
        "approval_scope": "private_network_exposure",
        "readiness": readiness,
        "current_state": {
            "recommended_path": phone_access.get("recommended_path", "missing"),
            "local_url": phone_access.get("local_url", ""),
            "private_phone_url": phone_access.get("private_phone_url", ""),
        },
        "operator_can_say": "approve private_phone_access private_network_exposure",
        "agent_will_run": enable_commands,
        "risk": "Starts local/private serving so the phone can read the daily brief. Public exposure remains out of scope.",
        "reversibility": "reversible",
        "rollback_command": rollback_command,
    }


def _phone_access_enable_commands(*, phone_access: dict[str, Any]) -> list[str]:
    enable_commands = []
    for item in phone_access.get("commands", []):
        command = item.get("command", "")
        purpose = item.get("purpose", "")
        if not command or _phone_access_command_is_rollback(command=command, purpose=purpose):
            continue
        enable_commands.append(command)
    return enable_commands


def _phone_access_rollback_command(*, phone_access: dict[str, Any]) -> str:
    for item in phone_access.get("commands", []):
        command = item.get("command", "")
        purpose = item.get("purpose", "")
        if command and _phone_access_command_is_rollback(command=command, purpose=purpose):
            return command
    return "tailscale serve reset"


def _phone_access_command_is_rollback(*, command: str, purpose: str) -> bool:
    normalized = f"{purpose} {command}".lower()
    return "stop" in normalized or "reset" in normalized or "unserve" in normalized


def _parse_operator_approval_response(response: str) -> dict[str, str]:
    parts = response.strip().split()
    if len(parts) != 3:
        return {
            "action": "",
            "decision_id": "",
            "approval_scope": "",
            "parse_status": "invalid",
            "parse_error": "Expected response shape: approve <decision_id> <approval_scope>",
        }
    action, decision_id, approval_scope = parts
    return {
        "action": action,
        "decision_id": decision_id,
        "approval_scope": approval_scope,
        "parse_status": "parsed",
        "parse_error": "",
    }


def _find_packet_decision(*, packet: dict[str, Any], decision_id: str) -> dict[str, Any] | None:
    for decision in packet.get("decisions", []):
        if decision.get("id") == decision_id:
            return decision
    return None


def _operator_decision_apply_blockers(*, parsed: dict[str, str], decision: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if parsed.get("parse_status") != "parsed":
        blockers.append(parsed.get("parse_error", "operator response could not be parsed"))
        return blockers
    if parsed.get("action") != "approve":
        blockers.append("Only approve responses can create an apply plan.")
    if decision is None:
        blockers.append(f"Decision not found in packet: {parsed.get('decision_id', '')}")
        return blockers
    if parsed.get("approval_scope") != decision.get("approval_scope"):
        blockers.append(
            f"Approval scope mismatch: expected {decision.get('approval_scope')}, got {parsed.get('approval_scope')}"
        )
    if decision.get("readiness") != "ready":
        blockers.append(f"Decision readiness is {decision.get('readiness')}, not ready.")
    if not decision.get("agent_will_run"):
        blockers.append("Decision has no runnable command plan.")
    return blockers


def _operator_decision_apply_next_action(*, blockers: list[str], decision: dict[str, Any] | None) -> str:
    if blockers:
        return "Fix the blocker or regenerate the operator decision packet before asking the agent to execute anything."
    return (
        "Review the commands and rollback_command. The artifact did not execute anything; external execution still requires "
        f"explicit scoped approval for {decision.get('approval_scope') if decision else 'unknown'}."
    )


def _same_file_contents(left: Path, right: Path) -> bool:
    if not left.exists() or not right.exists():
        return False
    return left.read_bytes() == right.read_bytes()


def _path_fresh(path: Path | None, freshness_hours: int) -> bool:
    if not path or not path.exists():
        return False
    return _file_age_hours(path) <= freshness_hours


def _dry_run_apply_is_activation_plan(payload: dict[str, Any]) -> bool:
    requested = payload.get("requested", {})
    actions = payload.get("actions", [])
    action_names = {action.get("name") for action in actions}
    action_statuses = {action.get("status") for action in actions}
    return (
        payload.get("dry_run") is True
        and payload.get("host_write_performed") is False
        and requested.get("install") is True
        and requested.get("load") is True
        and requested.get("start_now") is True
        and {"install", "load", "start_now"}.issubset(action_names)
        and action_statuses == {"planned"}
    )


def _artifact_age_hours(path: Path, payload: dict[str, Any]) -> float:
    generated_at = payload.get("generated_at")
    if isinstance(generated_at, str) and generated_at:
        try:
            generated = datetime.fromisoformat(generated_at)
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - generated.astimezone(timezone.utc)).total_seconds() / 3600
        except ValueError:
            pass
    return _file_age_hours(path)


def _timeout_output_excerpt(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")[-2000:]
    return value[-2000:]


def _doctor_next_actions(checks: list[dict[str, Any]]) -> list[str]:
    actions = []
    names = {check["name"]: check for check in checks}
    if names.get("runner_script", {}).get("status") == "fail" or names.get("launchd_plist", {}).get("status") == "fail":
        actions.append("Run `PYTHONPATH=src python3 -m mybroker appliance init --project-root .` to regenerate local runner assets.")
    if names.get("today_surface", {}).get("status") != "pass":
        actions.append("Run `PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --profile examples/profiles/beginner-conservative.json --dry-run` to refresh daily artifacts.")
    if names.get("phone_access_plan", {}).get("status") != "pass":
        actions.append("Run `PYTHONPATH=src python3 -m mybroker appliance access` to write private phone access guidance.")
    if names.get("launchd_loaded", {}).get("status") != "pass":
        actions.append("Install the LaunchAgent manually only after reviewing reports/runtime/local-runtime-doctor.json.")
    if not actions:
        actions.append("Local runtime evidence is ready; keep the Mac powered and review tomorrow's archive after the scheduled run.")
    return actions


def _latest_archive_manifest(archive_root: Path) -> Path | None:
    manifests = sorted(archive_root.glob("*/manifest.json"), reverse=True)
    return manifests[0] if manifests else None


def _file_age_hours(path: Path) -> float:
    modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return (datetime.now(timezone.utc) - modified).total_seconds() / 3600


def _agenda_topic_card(
    *,
    recommendation: dict[str, Any],
    evidence_items: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    memory_topic: dict[str, Any],
    vault_notes: list[dict[str, Any]],
) -> dict[str, Any]:
    latest_titles = set(recommendation.get("latest_titles", []))
    source_names = set(recommendation.get("source_names", []))
    supporting = [
        item
        for item in evidence_items
        if item.get("title") in latest_titles or item.get("source_name") in source_names
    ][:5]
    linked_vault = recommendation.get("linked_vault_notes", [])
    if not linked_vault:
        linked_vault = [
            {
                "title": note.get("title", ""),
                "source_path": note.get("source_path", ""),
                "wiki_path": note.get("wiki_path", ""),
            }
            for note in vault_notes
            if note.get("topic_id") == recommendation.get("topic_id")
        ][:3]
    source_family_count = len(source_names)
    weak_points = list(dict.fromkeys(recommendation.get("missing_evidence", []) + memory_topic.get("collection_gaps", [])))
    operator_brief = recommendation.get("operator_brief", {})
    return {
        "topic_id": recommendation.get("topic_id", ""),
        "name": recommendation.get("name", ""),
        "priority_rank": recommendation.get("priority_rank", 0),
        "action": recommendation.get("action", "monitor"),
        "confidence": recommendation.get("confidence", ""),
        "why_today": operator_brief.get("why_today", recommendation.get("why", "")),
        "headline": operator_brief.get("headline", ""),
        "beginner_focus": operator_brief.get("beginner_focus", recommendation.get("beginner_focus", "")),
        "confidence_note": operator_brief.get("confidence_note", ""),
        "missing_evidence_note": operator_brief.get("missing_evidence_note", ""),
        "next_question": recommendation.get("next_question", ""),
        "beginner_reading_order": recommendation.get("beginner_reading_order", []),
        "copy_ready_responses": recommendation.get("copy_ready_responses", []),
        "evidence_count": len(supporting),
        "source_family_count": source_family_count,
        "vault_note_count": len(linked_vault),
        "supporting_evidence": [
            {
                "source_name": item.get("source_name", ""),
                "title": item.get("title", ""),
                "freshness_status": item.get("freshness_status", ""),
                "entities": item.get("entities", [])[:5],
            }
            for item in supporting
        ],
        "source_status": [
            row
            for row in source_rows
            if row.get("source_name") in source_names
        ],
        "linked_vault_notes": linked_vault,
        "weak_points": weak_points,
        "readiness": _agenda_readiness(
            source_family_count=source_family_count,
            evidence_count=len(supporting),
            weak_points=weak_points,
        ),
    }


def _agenda_readiness(*, source_family_count: int, evidence_count: int, weak_points: list[str]) -> str:
    if source_family_count >= 3 and evidence_count >= 3 and not weak_points:
        return "meaningful"
    if source_family_count >= 2 and evidence_count >= 2:
        return "useful_but_verify"
    if evidence_count:
        return "weak"
    return "blocked"


def _agenda_weak_points(
    *,
    top_cards: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    evidence: dict[str, Any],
) -> list[str]:
    weak: list[str] = []
    for card in top_cards:
        weak.extend(card.get("weak_points", []))
        if card.get("readiness") in {"weak", "blocked"}:
            weak.append(f"{card.get('name', 'topic')} 근거 다양성이 약합니다.")
    weak.extend(evidence.get("collection_gaps", []))
    if len(source_rows) < 3:
        weak.append("source family가 3개 미만입니다.")
    if any(row.get("freshness_status") == "sample_cache" for row in source_rows):
        weak.append("일부 근거는 sample cache라 최신 시장 판단으로 바로 쓰면 안 됩니다.")
    return list(dict.fromkeys(weak))[:8]


def _agenda_study_sequence(*, primary: dict[str, Any], weak_points: list[str]) -> list[dict[str, Any]]:
    primary_name = primary.get("name", "오늘 추천 주제")
    reading_order = primary.get("beginner_reading_order", [])
    if reading_order:
        sequence = []
        minute_budget = [4, 5, 5, 4, 2]
        for index, item in enumerate(reading_order[:5], start=1):
            sequence.append({
                "step": index,
                "minutes": minute_budget[index - 1],
                "title": item.get("title", f"{primary_name} 읽기"),
                "operator_action": item.get("why", ""),
                "stop_condition": item.get("done_when", "다음 질문 하나를 남기면 이동합니다."),
            })
        return sequence
    return [
        {
            "step": 1,
            "minutes": 4,
            "title": f"{primary_name}를 왜 먼저 보는지 확인",
            "operator_action": primary.get("why_today", "Scout 추천 이유를 읽고 오늘의 질문을 하나 고릅니다."),
            "stop_condition": "왜 이 주제가 오늘 첫 번째인지 한 문장으로 설명할 수 있으면 다음으로 이동합니다.",
        },
        {
            "step": 2,
            "minutes": 6,
            "title": "근거가 서로 다른 출처에서 왔는지 확인",
            "operator_action": "GDELT/공시/가격/Vault 중 어떤 source family가 실제로 영향을 줬는지 봅니다.",
            "stop_condition": "출처가 하나뿐이거나 sample cache뿐이면 결론을 보류합니다.",
        },
        {
            "step": 3,
            "minutes": 6,
            "title": "시나리오를 낙관/base/downside로 나눠 읽기",
            "operator_action": "상승/기본/하락 경로를 비교하고, 어느 근거가 각 경로를 밀어주는지 체크합니다.",
            "stop_condition": "한쪽 시나리오만 강하게 보이면 skeptic task를 먼저 실행합니다.",
        },
        {
            "step": 4,
            "minutes": 4,
            "title": "오늘 남길 메모와 다음 질문 정하기",
            "operator_action": (weak_points[0] if weak_points else primary.get("next_question", "내일 다시 확인할 질문을 하나 남깁니다.")),
            "stop_condition": "매수/매도 결론이 아니라 다음 확인 질문으로 끝냅니다.",
        },
    ]


def _agenda_source_fanout(*, source_rows: list[dict[str, Any]], top_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top_source_names = {
        source.get("source_name", "")
        for card in top_cards
        for source in card.get("source_status", [])
    }
    rows = []
    for row in source_rows:
        source_name = row.get("source_name", "")
        rows.append({
            "source_name": source_name,
            "freshness_status": row.get("freshness_status", ""),
            "relevance_label": row.get("relevance_label", ""),
            "item_count": row.get("item_count", "0"),
            "role": _agenda_source_role(source_name=source_name),
            "influenced_top_topics": source_name in top_source_names,
        })
    return rows


def _agenda_source_role(*, source_name: str) -> str:
    roles = {
        "GDELT": "뉴스/이벤트 서사가 과열인지, 실제 사건인지 확인합니다.",
        "SEC EDGAR": "기업 공시로 서사가 실제 사업/위험 언어에 닿는지 확인합니다.",
        "Stooq": "가격 흐름이 서사와 같은 방향인지 넓은 시장 맥락을 확인합니다.",
    }
    return roles.get(source_name, "오늘 주제의 보조 근거로 사용합니다.")


def _agenda_role_brief(
    *,
    primary: dict[str, Any],
    weak_points: list[str],
    refresh_plan: dict[str, Any],
) -> list[dict[str, Any]]:
    primary_name = primary.get("name", "오늘 주제")
    blocked_refresh = [
        action.get("source_name", "")
        for action in refresh_plan.get("actions", [])
        if action.get("priority") == "high"
    ]
    return [
        {
            "role": "source_scout",
            "task": f"{primary_name}에 필요한 최신 근거 후보를 확인",
            "success_condition": "새 근거가 없으면 sample cache 기반이라는 점을 agenda에 남깁니다.",
        },
        {
            "role": "evidence_curator",
            "task": "근거 출처군, freshness, 중복 가능성을 점검",
            "success_condition": "source family와 weak point가 분리되어 표시됩니다.",
        },
        {
            "role": "market_mapper",
            "task": "주제-엔티티-이벤트가 어떤 market map을 만드는지 읽기 쉽게 정리",
            "success_condition": "초보자가 왜 이 주제가 시장 흐름과 연결되는지 이해합니다.",
        },
        {
            "role": "skeptic",
            "task": weak_points[0] if weak_points else "오늘 근거가 과도하게 한 방향으로 쏠렸는지 확인",
            "success_condition": "약한 근거가 있으면 투자 행동 후보가 아니라 추가 질문으로 남깁니다.",
        },
        {
            "role": "publisher",
            "task": "폰에서 읽을 순서와 다음 질문만 남기기",
            "success_condition": "오늘 output은 실행 지시가 아니라 학습/리서치 루틴으로 끝납니다.",
        },
        {
            "role": "refresh_gate",
            "task": f"필요한 live refresh 후보: {', '.join(blocked_refresh) or '없음'}",
            "success_condition": "live network refresh는 별도 승인 없이는 실행되지 않습니다.",
        },
    ]


def _agenda_questions(*, primary: dict[str, Any], weak_points: list[str]) -> list[str]:
    name = primary.get("name", "오늘 주제")
    question = primary.get("next_question") or f"오늘 {name}에서 초보자가 먼저 이해해야 할 변화는 무엇인가요?"
    questions = [
        question,
        f"{name}의 낙관/base/downside 경로를 가르는 핵심 근거는 무엇인가요?",
        "오늘 근거 중 sample cache 또는 stale 가능성이 있는 것은 무엇인가요?",
    ]
    if weak_points:
        questions.append(f"약한 근거 점검: {weak_points[0]}")
    return questions


def _readiness_artifact_check(
    *,
    root: Path,
    name: str,
    path: Path,
    kind: str,
    required: bool,
    freshness_hours: int,
    now: datetime,
) -> dict[str, Any]:
    full_path = path if path.is_absolute() else root / path
    exists = full_path.exists()
    payload: dict[str, Any] = {}
    age_hours: float | None = None
    if exists:
        if full_path.suffix == ".json":
            try:
                payload = load_json(full_path)
            except json.JSONDecodeError:
                payload = {}
        age_hours = _readiness_age_hours(full_path, payload=payload, now=now)
    freshness_status = "missing"
    if exists and age_hours is not None:
        freshness_status = "fresh" if age_hours <= freshness_hours else "stale"
    display_path = full_path.as_posix()
    try:
        display_path = full_path.relative_to(root).as_posix()
    except ValueError:
        pass
    return {
        "name": name,
        "path": display_path,
        "kind": kind,
        "required": required,
        "exists": exists,
        "freshness_status": freshness_status,
        "age_hours": round(age_hours, 2) if age_hours is not None else None,
        "generated_at": payload.get("generated_at", "") if payload else "",
        "schema_version": payload.get("schema_version", "") if payload else "",
    }


def _readiness_age_hours(path: Path, *, payload: dict[str, Any], now: datetime) -> float:
    generated_at = payload.get("generated_at")
    if isinstance(generated_at, str) and generated_at:
        try:
            generated = datetime.fromisoformat(generated_at)
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=timezone.utc)
            return (now - generated.astimezone(timezone.utc)).total_seconds() / 3600
        except ValueError:
            pass
    modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return (now - modified).total_seconds() / 3600


def _source_refresh_brief_actions(
    *,
    refresh_plan: dict[str, Any],
    refresh_apply: dict[str, Any],
    live_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    plan_by_adapter = {item.get("adapter_id", ""): item for item in refresh_plan.get("actions", [])}
    blocked_by_adapter = {item.get("adapter_id", ""): item for item in live_gate.get("blocked_actions", [])}
    rows = []
    for result in refresh_apply.get("results", []):
        adapter_id = result.get("adapter_id", "")
        plan = plan_by_adapter.get(adapter_id, {})
        blocked = blocked_by_adapter.get(adapter_id, {})
        rows.append({
            "source_name": result.get("source_name", plan.get("source_name", "")),
            "adapter_id": adapter_id,
            "decision": result.get("decision", ""),
            "status": result.get("status", ""),
            "approval_required": result.get("approval_required", "none"),
            "reason": result.get("reason", plan.get("reason", "")),
            "command": result.get("command", plan.get("command", "")),
            "expected_artifact": result.get("expected_artifact", blocked.get("expected_artifact", "")),
            "cadence": plan.get("cadence", ""),
            "priority": plan.get("priority", ""),
        })
    if rows:
        return rows
    return [
        {
            "source_name": item.get("source_name", ""),
            "adapter_id": item.get("adapter_id", ""),
            "decision": "planned",
            "status": "not_applied",
            "approval_required": "operator_review" if item.get("adapter_id") in {"gdelt-live", "stooq-live"} else "none",
            "reason": item.get("reason", ""),
            "command": item.get("command", ""),
            "expected_artifact": item.get("expected_artifact", ""),
            "cadence": item.get("cadence", ""),
            "priority": item.get("priority", ""),
        }
        for item in refresh_plan.get("actions", [])
    ]


def _source_refresh_weak_evidence(*, evidence: dict[str, Any], scout: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for gap in evidence.get("collection_gaps", [])[:4]:
        rows.append({
            "kind": "catalog_gap",
            "title": _gap_label(gap),
            "why_it_matters": "브리프 확신도를 낮추는 evidence catalog gap입니다.",
        })
    for recommendation in scout.get("recommendations", [])[:3]:
        missing = recommendation.get("missing_evidence", []) or []
        for gap in missing[:2]:
            rows.append({
                "kind": recommendation.get("name", "topic"),
                "title": _gap_label(gap),
                "why_it_matters": recommendation.get("why", "오늘 주제 판단 전에 확인해야 할 약한 근거입니다."),
            })
    seen = set()
    deduped = []
    for row in rows:
        key = (row["kind"], row["title"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped[:6]


def _source_refresh_freshness_scorecard(*, evidence: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for source in evidence.get("source_status", []):
        freshness = source.get("freshness_status", "unknown")
        relevance = source.get("relevance_label", "unscored")
        if freshness in {"fresh", "live"} and relevance in {"strong", "usable"}:
            trust_state = "fresh_enough"
            operator_rule = "오늘 brief에 직접 영향을 줘도 되지만 반대 근거는 별도로 확인합니다."
        elif freshness in {"sample_cache", "live_error_fallback_sample"}:
            trust_state = "sample_or_fallback"
            operator_rule = "학습용 맥락으로만 읽고, 오늘의 최신 시장 판단에는 낮은 확신으로 반영합니다."
        else:
            trust_state = "weak_or_unknown"
            operator_rule = "결론을 보류하고 source refresh 또는 다른 출처군 확인을 먼저 검토합니다."
        rows.append({
            "source_name": source.get("source_name", ""),
            "source_id": source.get("source_id", ""),
            "freshness_status": freshness,
            "relevance_label": relevance,
            "relevance_score": source.get("relevance_score", "0.00"),
            "item_count": source.get("item_count", "0"),
            "trust_state": trust_state,
            "operator_rule": operator_rule,
        })
    if rows:
        return rows
    return [{
        "source_name": "missing",
        "source_id": "missing",
        "freshness_status": "missing",
        "relevance_label": "unscored",
        "relevance_score": "0.00",
        "item_count": "0",
        "trust_state": "weak_or_unknown",
        "operator_rule": "source catalog를 먼저 생성해야 합니다.",
    }]


def _source_refresh_brief_status(
    *,
    actions: list[dict[str, Any]],
    live_gate: dict[str, Any],
    live_run: dict[str, Any],
    preflight: dict[str, Any],
) -> str:
    if live_run.get("execution", {}).get("status") == "executed":
        return "executed"
    if preflight.get("status") == "passed":
        return "ready_to_execute"
    if live_run.get("approval_status") == "approved" and live_run.get("execution", {}).get("status") == "ready_to_execute":
        return "preflight_required"
    if live_gate.get("status") == "approval_required":
        return "approval_required"
    if any(action.get("decision") == "ready" for action in actions):
        return "local_ready"
    if not actions:
        return "no_refresh_needed"
    return "blocked"


def _source_refresh_operator_decision(
    *,
    live_gate: dict[str, Any],
    live_run: dict[str, Any],
    preflight: dict[str, Any],
) -> dict[str, Any]:
    decision = (live_gate.get("decisions") or [{}])[0]
    if live_gate.get("status") != "approval_required":
        return {
            "approval_required": False,
            "title": "live source refresh 승인 없음",
            "why": "현재 live refresh gate가 승인 요구 상태가 아닙니다.",
        }
    return {
        "approval_required": True,
        "id": decision.get("id", "live_network_refresh"),
        "title": "free/no-key live source refresh 승인",
        "why": "GDELT 또는 Stooq 같은 무료 공개 자료 live refresh 후보가 있지만 네트워크 호출이므로 별도 승인 전에는 실행하지 않습니다.",
        "approval_scope": decision.get("approval_scope", "live_network_refresh"),
        "risk_level": decision.get("risk_level", "medium"),
        "copy_ready_response": decision.get("copy_ready_response", "approve live_network_refresh live_network_refresh"),
        "stale_context_guard": decision.get("stale_context_guard", "Regenerate refresh artifacts if scout or source plan changed."),
        "approval_status": live_run.get("approval_status", "missing"),
        "preflight_status": preflight.get("status", "missing"),
    }


def _source_refresh_next_action(
    *,
    status: str,
    live_gate: dict[str, Any],
    live_run: dict[str, Any],
    preflight: dict[str, Any],
) -> str:
    if status == "executed":
        return "live evidence catalog가 생성됐습니다. validator를 통과한 뒤 daily loop를 다시 실행해 브리프에 반영하세요."
    if status == "ready_to_execute":
        return "preflight가 통과했습니다. 실제 live network 실행은 별도 최종 확인 후에만 진행하세요."
    if status == "preflight_required":
        return "승인 응답은 유효합니다. 실행 전 source-refresh-live-preflight를 실행해 source id, output path, confirmation을 확인하세요."
    if status == "approval_required":
        decision = (live_gate.get("decisions") or [{}])[0]
        return f"필요하면 다음 응답을 검토하세요: {decision.get('copy_ready_response', 'approve live_network_refresh live_network_refresh')}"
    if status == "local_ready":
        return "먼저 로컬/샘플/cache 작업을 검증하고, live refresh는 약한 근거가 계속 남을 때만 승인하세요."
    if status == "no_refresh_needed":
        return "오늘은 별도 source refresh가 필요하지 않습니다. agenda와 today brief를 먼저 읽으세요."
    blockers = preflight.get("blockers") or live_run.get("execution", {}).get("blockers", [])
    return "차단 이유를 먼저 해소하세요: " + (", ".join(blockers[:3]) if blockers else "refresh artifacts를 다시 생성하세요.")


def _source_freshness_intake_next_action(*, status: str, response: str) -> str:
    if status == "approval_packet_ready":
        return f"필요하면 이 응답을 복사해 local approval proof를 만드세요: {response}"
    if status == "ready_for_operator_review":
        return "source freshness와 blocked candidate를 읽고, live refresh가 필요한지 source-refresh 화면과 함께 판단하세요."
    if status == "no_intake_needed":
        return "오늘 source freshness intake에서 승인할 항목은 없습니다. daily home과 learning ledger를 먼저 읽으세요."
    return "source-refresh brief, live gate, live run, preflight artifact를 다시 생성한 뒤 intake를 재실행하세요."


def _scheduler_proof_artifact(
    *,
    name: str,
    path: Path,
    expected_schema: str,
    freshness_hours: int,
    now: datetime,
) -> dict[str, Any]:
    exists = path.exists()
    payload: dict[str, Any] = {}
    age_hours: float | None = None
    freshness_status = "missing"
    summary_status = "missing"
    if exists:
        try:
            payload = load_json(path)
            age_hours = _readiness_age_hours(path, payload=payload, now=now)
            freshness_status = "fresh" if age_hours <= freshness_hours else "stale"
            summary_status = str(payload.get("status", payload.get("delivery_status", "present")))
            if payload.get("schema_version") != expected_schema:
                freshness_status = "invalid_schema"
                summary_status = f"unexpected schema {payload.get('schema_version', '')}"
        except json.JSONDecodeError:
            freshness_status = "invalid_schema"
            summary_status = "invalid json"
    return {
        "name": name,
        "path": path.as_posix(),
        "exists": exists,
        "freshness_status": freshness_status,
        "age_hours": round(age_hours, 2) if age_hours is not None else None,
        "schema_version": payload.get("schema_version", ""),
        "summary_status": summary_status,
        "host_write_performed": payload.get("host_write_performed", False),
    }


def _scheduler_operations_status(
    *,
    install_state: dict[str, Any],
    local_run: dict[str, Any],
    activation_preflight: dict[str, Any],
    activation_verify: dict[str, Any],
    runtime: dict[str, Any],
    proof_artifacts: list[dict[str, Any]],
) -> str:
    if any(item.get("freshness_status") == "invalid_schema" for item in proof_artifacts):
        return "blocked"
    if activation_verify.get("status") == "active_verified" and install_state.get("loaded"):
        return "active_verified"
    if activation_preflight.get("status") in {"ready", "already_active"} and local_run.get("status") == "passed":
        return "activation_ready"
    if install_state.get("script_ready") and install_state.get("plist_ready") and runtime.get("doctor_status") == "ready":
        return "manual_ready"
    if not install_state.get("script_ready") or not install_state.get("plist_ready"):
        return "not_ready"
    return "blocked"


def _scheduler_operations_next_action(
    *,
    status: str,
    install_state: dict[str, Any],
    local_run: dict[str, Any],
    activation_preflight: dict[str, Any],
    runtime: dict[str, Any],
) -> str:
    if status == "active_verified":
        return "자동 실행이 확인됐습니다. 내일 archive와 log가 새로 생기는지 점검하세요."
    if status == "activation_ready":
        return "수동 run-once와 preflight가 통과했습니다. host scheduler 활성화는 별도 확인과 승인 후에만 진행하세요."
    if not install_state.get("script_ready") or not install_state.get("plist_ready"):
        return "먼저 appliance init으로 runner script와 LaunchAgent plist를 생성하세요."
    if runtime.get("doctor_status") != "ready":
        return "runtime doctor가 ready가 아닙니다. readiness와 doctor proof를 먼저 새로 생성하세요."
    if local_run.get("status") != "passed":
        return "host-level 활성화 전에 scheduler run-once를 실행해 로컬 runner가 끝까지 도는지 확인하세요."
    if activation_preflight.get("status") != "ready":
        return "dry-run apply, run-once, notification dry-run proof를 만든 뒤 activation-preflight를 다시 실행하세요."
    return "현재 상태를 확인하고 readiness, morning, scheduler 순서로 폰에서 검토하세요."


def _scheduler_operations_commands(*, overall_status: str) -> list[dict[str, Any]]:
    commands = [
        {
            "label": "scheduler assets 생성",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance init --project-root .",
            "why": "runner script와 LaunchAgent plist를 로컬 repo 안에 생성합니다.",
            "requires_separate_approval": False,
            "external_effect_performed": False,
        },
        {
            "label": "수동 run-once proof",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance scheduler run-once",
            "why": "host scheduler 설치 없이 같은 runner를 한 번 실행합니다.",
            "requires_separate_approval": False,
            "external_effect_performed": False,
        },
        {
            "label": "activation preflight",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance scheduler activation-preflight",
            "why": "host write 전에 필요한 proof가 충분한지 다시 검사합니다.",
            "requires_separate_approval": False,
            "external_effect_performed": False,
        },
    ]
    if overall_status == "activation_ready":
        commands.append({
            "label": "별도 승인 후 활성화",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance scheduler apply --install --load --start-now --confirm-host-write",
            "why": "현재 macOS 사용자 LaunchAgent를 설치/load/start합니다. 별도 승인 없이는 실행하지 않습니다.",
            "requires_separate_approval": True,
            "external_effect_performed": False,
        })
    return commands


def _readiness_scheduler_state(status_path: Path) -> dict[str, Any]:
    if not status_path.exists():
        return {
            "status": "missing",
            "loaded": False,
            "installed": False,
            "path": status_path.as_posix(),
            "message": "Scheduler status artifact is missing.",
        }
    payload = load_json(status_path)
    return {
        "status": payload.get("status", "unknown"),
        "loaded": bool(payload.get("launchd", {}).get("loaded")),
        "installed": bool(payload.get("installed_plist", {}).get("exists")),
        "path": status_path.as_posix(),
        "message": payload.get("next_actions", [""])[0] if payload.get("next_actions") else "",
    }


def _readiness_status(
    *,
    missing_required: list[dict[str, Any]],
    stale_required: list[dict[str, Any]],
) -> str:
    if missing_required:
        return "blocked"
    if stale_required:
        return "stale"
    return "ready"


def _readiness_next_actions(
    *,
    status: str,
    missing_required: list[dict[str, Any]],
    stale_required: list[dict[str, Any]],
    scheduler: dict[str, Any],
) -> list[str]:
    actions: list[str] = []
    if missing_required:
        names = ", ".join(item["name"] for item in missing_required)
        actions.append(f"필수 artifact가 없습니다: {names}. `appliance run --dry-run`을 먼저 실행하세요.")
    if stale_required:
        names = ", ".join(item["name"] for item in stale_required)
        actions.append(f"필수 artifact가 오래됐습니다: {names}. daily run을 다시 생성하세요.")
    if status == "ready":
        actions.append("필수 산출물은 freshness 기준을 통과했습니다. morning, today, agenda 순서로 읽어도 됩니다.")
    if not scheduler.get("loaded"):
        actions.append("자동 실행은 아직 활성 확인이 안 됐습니다. 필요하면 scheduler status와 activation-preflight를 검토하세요.")
    actions.append("외부 효과가 필요한 source refresh, 알림 전송, host scheduler 쓰기는 별도 승인 게이트에서만 실행하세요.")
    return actions


def _readiness_css(status: str) -> str:
    return status if status in {"fresh", "stale", "missing"} else "missing"


def _gap_label(value: str) -> str:
    labels = {
        "live_refresh_not_enabled": "실시간 새로고침은 아직 연결되지 않았습니다.",
        "source_license_review_pending": "소스 이용조건 검토가 남아 있습니다.",
        "less_than_three_source_families": "자료군이 3종 미만이라 근거 다양성이 약합니다.",
        "topic_filter_too_thin_used_full_sample_cache": "주제별 필터 결과가 얇아 전체 샘플 캐시를 보강 사용했습니다.",
    }
    return labels.get(value, value)


def _relative_href(path: Path | None) -> str:
    if not path:
        return ""
    return path.as_posix()


def _short_date(value: str) -> str:
    return value[:10] if value else datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _local_date_label(value: str) -> str:
    if not value:
        return datetime.now().astimezone().strftime("%Y-%m-%d local")
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone().strftime("%Y-%m-%d local")
    except ValueError:
        return _short_date(value)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
