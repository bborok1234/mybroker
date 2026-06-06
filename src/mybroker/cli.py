from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from mybroker.appliance import (
    DEFAULT_ARCHIVE_ROOT,
    DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    DEFAULT_ANALYST_JOURNAL_OUTPUT,
    DEFAULT_LEARNING_LEDGER_OUTPUT,
    DEFAULT_LEARNING_LEDGER_SURFACE,
    DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    DEFAULT_ANALYST_TASK_QUEUE_OUTPUT,
    DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    DEFAULT_ANALYST_TASK_LEDGER_OUTPUT,
    DEFAULT_ANALYST_TASK_RESPONSES,
    DEFAULT_ANALYST_TASK_STATUS_APPLY,
    DEFAULT_AGENT_PATTERN_RADAR_OUTPUT,
    DEFAULT_AGENT_PATTERN_RADAR_SURFACE,
    DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT,
    DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE,
    DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT,
    DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE,
    DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    DEFAULT_DAILY_BRIEF_AGENDA_SURFACE,
    DEFAULT_DAILY_HOME_OUTPUT,
    DEFAULT_DAILY_HOME_SURFACE,
    DEFAULT_DAILY_BRIEFING_PACKET_OUTPUT,
    DEFAULT_DAILY_BRIEFING_PACKET_SURFACE,
    DEFAULT_DAILY_READINESS_OUTPUT,
    DEFAULT_DAILY_READINESS_SURFACE,
    DEFAULT_DAILY_HANDOFF_OUTPUT,
    DEFAULT_DAILY_HANDOFF_SURFACE,
    DEFAULT_DAILY_REVIEW_RESPONSES,
    DEFAULT_DAILY_REVIEW_SURFACE,
    DEFAULT_DRIFT_REVIEW_OUTPUT,
    DEFAULT_DRIFT_REVIEW_SURFACE,
    DEFAULT_REVIEW_PROMPT_OUTPUT,
    DEFAULT_REVIEW_PROMPT_SURFACE,
    DEFAULT_REVIEW_EFFECT_OUTPUT,
    DEFAULT_REVIEW_EFFECT_SURFACE,
    DEFAULT_REVIEW_RESPONSE_APPLY_OUTPUT,
    DEFAULT_REVIEW_RESPONSE_APPLY_SURFACE,
    OPERATOR_REVIEW_RESPONSE_APPLY_SCHEMA_VERSION,
    DEFAULT_BRIEFING_RESPONSE_APPLY_OUTPUT,
    DEFAULT_BRIEFING_RESPONSE_APPLY_SURFACE,
    OPERATOR_BRIEFING_RESPONSE_APPLY_SCHEMA_VERSION,
    DEFAULT_COUNCIL_RESPONSE_APPLY_OUTPUT,
    DEFAULT_COUNCIL_RESPONSE_APPLY_SURFACE,
    OPERATOR_COUNCIL_RESPONSE_APPLY_SCHEMA_VERSION,
    DEFAULT_HANDOFF_RESPONSES,
    DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT,
    DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE,
    OPERATOR_HANDOFF_RESPONSE_APPLY_SCHEMA_VERSION,
    DEFAULT_LOCAL_OPS_DIR,
    DEFAULT_MEMORY_INDEX_OUTPUT,
    DEFAULT_MEMORY_QUERY_OUTPUT,
    DEFAULT_MEMORY_QUERY_SURFACE,
    DEFAULT_MEMORY_AUDIT_OUTPUT,
    DEFAULT_MEMORY_AUDIT_SURFACE,
    DEFAULT_ANALYST_COUNCIL_OUTPUT,
    DEFAULT_ANALYST_COUNCIL_SURFACE,
    DEFAULT_MEMORY_OUTPUT,
    DEFAULT_NOTIFICATION_OUTPUT,
    DEFAULT_OPERATOR_DECISION_APPLY_OUTPUT,
    DEFAULT_OPERATOR_DECISION_PACKET_OUTPUT,
    DEFAULT_MORNING_CONTROL_OUTPUT,
    DEFAULT_MORNING_CONTROL_SURFACE,
    DEFAULT_PHONE_ACCESS_OUTPUT,
    DEFAULT_PHONE_ACCESS_VERIFY_OUTPUT,
    DEFAULT_PHONE_ACCESS_VERIFY_SURFACE,
    DEFAULT_DAILY_RUN_LEDGER_OUTPUT,
    DEFAULT_DAILY_RUN_LEDGER_SURFACE,
    DEFAULT_RUN_TRACE_OUTPUT,
    DEFAULT_RUN_TRACE_SURFACE,
    DEFAULT_RUNTIME_PLAYBOOK_OUTPUT,
    DEFAULT_RUNTIME_DOCTOR_OUTPUT,
    DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT,
    DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT,
    DEFAULT_SCHEDULER_APPLY_OUTPUT,
    DEFAULT_SCHEDULER_OPERATIONS_OUTPUT,
    DEFAULT_SCHEDULER_OPERATIONS_SURFACE,
    DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT,
    DEFAULT_SCHEDULER_STATUS_OUTPUT,
    DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT,
    DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE,
    DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT,
    DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE,
    DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT,
    DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE,
    DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT,
    DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE,
    DEFAULT_TODAY_OUTPUT,
    add_archive_artifacts,
    archive_daily_run,
    parse_daily_review_response,
    send_notification_payload,
    write_agent_pattern_radar,
    write_pattern_evidence_intake,
    write_pattern_dry_run_proof,
    write_launchd_assets,
    write_analyst_council,
    write_analyst_journal,
    write_learning_ledger,
    write_analyst_task_queue,
    write_analyst_task_ledger,
    write_daily_brief_agenda,
    write_daily_operator_home,
    write_daily_briefing_packet,
    write_daily_readiness,
    write_daily_handoff,
    write_daily_review,
    write_drift_review,
    write_operator_review_prompt,
    write_operator_review_effect,
    write_operator_review_response_apply,
    write_operator_briefing_response_apply,
    write_operator_council_response_apply,
    write_operator_handoff_response_apply,
    build_task_status_apply,
    record_daily_review_response,
    record_handoff_response,
    record_task_status_response,
    write_morning_control_packet,
    write_memory_query,
    write_memory_audit,
    write_memory_surface,
    write_notification_payload,
    write_operator_decision_apply,
    write_operator_decision_packet,
    write_phone_access_plan,
    write_phone_access_verify,
    write_daily_run_ledger,
    write_run_trace,
    write_runtime_doctor,
    write_runtime_playbook,
    write_scheduler_activation_verify,
    write_scheduler_activation_preflight,
    write_scheduler_apply,
    write_scheduler_operations,
    write_scheduler_run_once,
    write_scheduler_status,
    write_source_refresh_brief,
    write_source_freshness_intake,
    write_source_refresh_execution_brief,
    write_handoff_study_resolution,
    write_today_surface,
    validate_analyst_journal_file,
    validate_learning_ledger_file,
    validate_analyst_council_file,
    validate_analyst_task_queue_file,
    validate_analyst_task_ledger_file,
    validate_agent_pattern_radar_file,
    validate_pattern_evidence_intake_file,
    validate_pattern_dry_run_proof_file,
    validate_daily_brief_agenda_file,
    validate_daily_operator_home_file,
    validate_daily_briefing_packet_file,
    validate_daily_readiness_file,
    validate_daily_handoff_file,
    validate_daily_review_file,
    validate_drift_review_file,
    validate_operator_review_prompt_file,
    validate_operator_review_effect_file,
    validate_operator_review_response_apply_file,
    validate_operator_briefing_response_apply_file,
    validate_operator_council_response_apply_file,
    validate_operator_handoff_response_apply_file,
    validate_task_status_apply_file,
    validate_morning_control_packet_file,
    validate_memory_query_file,
    validate_memory_audit_file,
    validate_daily_run_ledger_file,
    validate_run_trace_file,
    validate_scheduler_operations_file,
    validate_source_refresh_brief_file,
    validate_source_freshness_intake_file,
    validate_source_refresh_execution_brief_file,
    validate_handoff_study_resolution_file,
    validate_phone_access_verify_file,
)
from mybroker.data import load_price_csv
from mybroker.dashboard import build_report_rollup, write_dashboard, write_rollup
from mybroker.policy import classify_action
from mybroker.profile import validate_profile_file
from mybroker.product_brief import write_product_brief
from mybroker.public_evidence import (
    SOURCE_MATRIX,
    build_public_evidence_catalog,
    validate_public_evidence_catalog_file,
    write_public_evidence_catalog,
)
from mybroker.registry import default_registry
from mybroker.reports import report_to_dict, validate_report_file
from mybroker.runner import make_price_adapter, run_research_task
from mybroker.scenario import (
    build_verdict,
    run_market_simulation,
    scenario_report_to_dict,
    validate_scenario_file,
    validate_verdict_file,
    write_scenario_report,
    write_verdict,
)
from mybroker.signals import momentum_signals
from mybroker.topics import (
    DEFAULT_DAILY_EVIDENCE_OUTPUT,
    DEFAULT_DAILY_REVIEW_OUTPUT,
    DEFAULT_LIVE_EVIDENCE_OUTPUT,
    DEFAULT_DAILY_SCOUT_OUTPUT,
    DEFAULT_RESEARCH_PLAN_OUTPUT,
    DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    DEFAULT_TOPIC_MEMORY_OUTPUT,
    DEFAULT_TOPICS_PATH,
    add_interest,
    build_daily_scout,
    build_research_plan,
    build_source_refresh_apply,
    build_source_refresh_live_gate,
    build_source_refresh_live_preflight,
    build_source_refresh_live_run,
    build_source_refresh_plan,
    collect_topic_evidence,
    init_topic_config,
    load_topic_config,
    validate_daily_scout_file,
    validate_research_plan_file,
    validate_source_refresh_apply_file,
    validate_source_refresh_live_gate_file,
    validate_source_refresh_live_preflight_file,
    validate_source_refresh_live_run_file,
    validate_source_refresh_plan_file,
    validate_topic_config_file,
    validate_topic_memory_file,
)
from mybroker.vault import (
    DEFAULT_VAULT_COMPILE_OUTPUT,
    DEFAULT_VAULT_RAW_DIR,
    DEFAULT_VAULT_ROOT,
    DEFAULT_VAULT_SURFACE_OUTPUT,
    DEFAULT_VAULT_WIKI_DIR,
    compile_knowledge_vault,
    init_knowledge_vault,
    validate_knowledge_vault_compile_file,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mybroker")
    subcommands = parser.add_subparsers(dest="command", required=True)

    signals_parser = subcommands.add_parser("signals", help="Generate research signals from a local price CSV.")
    signals_parser.add_argument("csv_path")
    signals_parser.add_argument("--short-window", type=int, default=3)
    signals_parser.add_argument("--long-window", type=int, default=5)

    research_parser = subcommands.add_parser("research", help="Run a registered local research task and write a report artifact.")
    research_parser.add_argument("--source", action="append", help="Local price CSV file or directory. Repeat for multiple CSV files. Defaults to the bundled sample data.")
    research_parser.add_argument("--task", default="momentum_research_v1")
    research_parser.add_argument("--short-window", type=int)
    research_parser.add_argument("--long-window", type=int)
    research_parser.add_argument("--run-id", default="local-momentum-research")
    research_parser.add_argument("--output", default="reports/runs/local-momentum-research.json")

    subcommands.add_parser("tasks", help="List registered research tasks.")

    validate_parser = subcommands.add_parser("validate-report", help="Validate a research report artifact.")
    validate_parser.add_argument("report_path")

    dashboard_parser = subcommands.add_parser("dashboard", help="Build a local HTML dashboard from research report artifacts.")
    dashboard_parser.add_argument("--reports-dir", default="reports/runs")
    dashboard_parser.add_argument("--output", default="reports/dashboard.html")
    dashboard_parser.add_argument("--rollup-output", default="reports/report-rollup.json")

    scenario_parser = subcommands.add_parser("scenario", help="Run a beginner-first market scenario simulation from local seed files.")
    scenario_parser.add_argument("--seed", action="append", help="Local markdown/txt seed file or directory. Defaults to examples/seeds.")
    scenario_parser.add_argument("--run-id", default="beginner-market-sim")
    scenario_parser.add_argument("--profile", help="Optional beginner profile JSON. Adjusts explanation priority without creating trade instructions.")
    scenario_parser.add_argument("--evidence-catalog", help="Optional public_evidence_catalog.v1 JSON to include in the simulation.")
    scenario_parser.add_argument("--output", default="reports/scenarios/beginner-market-sim.json")
    scenario_parser.add_argument("--verdict-output", default="reports/scenarios/verdict.json")

    validate_scenario_parser = subcommands.add_parser("validate-scenario", help="Validate a scenario_report.v1 artifact.")
    validate_scenario_parser.add_argument("scenario_path")

    validate_verdict_parser = subcommands.add_parser("validate-verdict", help="Validate a market_verdict.v1 artifact.")
    validate_verdict_parser.add_argument("verdict_path")
    validate_vault_parser = subcommands.add_parser("validate-vault", help="Validate a knowledge_vault_compile.v1 artifact.")
    validate_vault_parser.add_argument("vault_path")

    validate_profile_parser = subcommands.add_parser("validate-profile", help="Validate a beginner profile JSON artifact.")
    validate_profile_parser.add_argument("profile_path")

    subcommands.add_parser("evidence-sources", help="Print the free/public evidence source feasibility matrix.")

    ingest_public_parser = subcommands.add_parser("ingest-public-evidence", help="Build a local public_evidence_catalog.v1 artifact from cached public-source samples.")
    ingest_public_parser.add_argument("--source", action="append", help="Public evidence adapter id. Repeat to select multiple sources. Defaults to no-key cached samples.")
    ingest_public_parser.add_argument("--output", default="reports/evidence/public-evidence-catalog.json")

    validate_public_parser = subcommands.add_parser("validate-public-evidence", help="Validate a public_evidence_catalog.v1 artifact.")
    validate_public_parser.add_argument("catalog_path")

    topics_parser = subcommands.add_parser("topics", help="Manage beginner-readable MyBroker research interests.")
    topics_subcommands = topics_parser.add_subparsers(dest="topics_command", required=True)
    topics_init_parser = topics_subcommands.add_parser("init", help="Initialize local topic/interest config.")
    topics_init_parser.add_argument("--output", default=DEFAULT_TOPICS_PATH.as_posix())
    topics_add_parser = topics_subcommands.add_parser("add", help="Add or update one research interest.")
    topics_add_parser.add_argument("name")
    topics_add_parser.add_argument("--description", default="")
    topics_add_parser.add_argument("--beginner-focus", default="")
    topics_add_parser.add_argument("--keyword", action="append", default=[])
    topics_add_parser.add_argument("--config", default=DEFAULT_TOPICS_PATH.as_posix())
    topics_list_parser = topics_subcommands.add_parser("list", help="List configured research interests.")
    topics_list_parser.add_argument("--config", default=DEFAULT_TOPICS_PATH.as_posix())

    research_plan_parser = subcommands.add_parser("research-plan", help="Generate a daily research plan from configured interests.")
    research_plan_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    research_plan_parser.add_argument("--output", default=DEFAULT_RESEARCH_PLAN_OUTPUT.as_posix())
    research_plan_parser.add_argument("--run-id", default="daily-research")

    collect_parser = subcommands.add_parser("collect-evidence", help="Collect cached free/public evidence for configured interests and update topic memory.")
    collect_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    collect_parser.add_argument("--plan", default=DEFAULT_RESEARCH_PLAN_OUTPUT.as_posix())
    collect_parser.add_argument("--output", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    collect_parser.add_argument("--memory-output", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    collect_parser.add_argument("--source", action="append", help="Public evidence adapter id. Defaults to no-key cached samples.")

    scout_parser = subcommands.add_parser("daily-scout", help="Rank configured interests for today's local analyst brief.")
    scout_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    scout_parser.add_argument("--plan", default=DEFAULT_RESEARCH_PLAN_OUTPUT.as_posix())
    scout_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    scout_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    scout_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    scout_parser.add_argument("--review", default=DEFAULT_DAILY_REVIEW_OUTPUT.as_posix())
    scout_parser.add_argument("--output", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    scout_parser.add_argument("--run-id", default="daily-research")

    refresh_plan_parser = subcommands.add_parser("source-refresh-plan", help="Plan local/dry-run source refresh actions from today's scout recommendation.")
    refresh_plan_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    refresh_plan_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    refresh_plan_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    refresh_plan_parser.add_argument("--output", default=DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT.as_posix())

    refresh_apply_parser = subcommands.add_parser("source-refresh-apply", help="Build a dry-run apply packet from a source_refresh_plan.v1 artifact.")
    refresh_apply_parser.add_argument("--refresh-plan", default=DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT.as_posix())
    refresh_apply_parser.add_argument("--output", default=DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT.as_posix())

    refresh_live_gate_parser = subcommands.add_parser("source-refresh-live-gate", help="Build an operator approval gate for blocked live source refresh actions.")
    refresh_live_gate_parser.add_argument("--refresh-apply", default=DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT.as_posix())
    refresh_live_gate_parser.add_argument("--output", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())

    refresh_live_run_parser = subcommands.add_parser("source-refresh-live-run", help="Write or execute a guarded live source refresh run proof.")
    refresh_live_run_parser.add_argument("--live-gate", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())
    refresh_live_run_parser.add_argument("--response", default="")
    refresh_live_run_parser.add_argument("--output", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    refresh_live_run_parser.add_argument("--evidence-output", default=DEFAULT_LIVE_EVIDENCE_OUTPUT.as_posix())
    refresh_live_run_parser.add_argument("--execute", action="store_true", help="Execute no-key live network refresh if approval and confirmation are present.")
    refresh_live_run_parser.add_argument("--confirm-live-network", action="store_true", help="Required with --execute to permit live network calls.")

    refresh_live_preflight_parser = subcommands.add_parser("source-refresh-live-preflight", help="Preflight a live source refresh run proof without calling the network.")
    refresh_live_preflight_parser.add_argument("--live-run", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    refresh_live_preflight_parser.add_argument("--output", default=DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix())
    refresh_live_preflight_parser.add_argument("--intend-execute", action="store_true", help="Declare that the operator intends to execute the approved live refresh.")
    refresh_live_preflight_parser.add_argument("--confirm-live-network", action="store_true", help="Required for a passed preflight before live network execution.")

    validate_topics_parser = subcommands.add_parser("validate-topics", help="Validate a topic_config.v1 artifact.")
    validate_topics_parser.add_argument("topics_path")
    validate_plan_parser = subcommands.add_parser("validate-research-plan", help="Validate a daily_research_plan.v1 artifact.")
    validate_plan_parser.add_argument("plan_path")
    validate_scout_parser = subcommands.add_parser("validate-daily-scout", help="Validate a daily_scout.v1 artifact.")
    validate_scout_parser.add_argument("scout_path")
    validate_agenda_parser = subcommands.add_parser("validate-daily-agenda", help="Validate a daily_brief_agenda.v1 artifact.")
    validate_agenda_parser.add_argument("agenda_path")
    validate_daily_home_parser = subcommands.add_parser("validate-daily-home", help="Validate a daily_operator_home.v1 artifact.")
    validate_daily_home_parser.add_argument("daily_home_path")
    validate_daily_briefing_parser = subcommands.add_parser("validate-daily-briefing-packet", help="Validate a daily_briefing_packet.v1 artifact.")
    validate_daily_briefing_parser.add_argument("briefing_packet_path")
    validate_phone_access_verify_parser = subcommands.add_parser("validate-phone-access-verify", help="Validate a phone_access_verify.v1 artifact.")
    validate_phone_access_verify_parser.add_argument("phone_access_verify_path")
    validate_readiness_parser = subcommands.add_parser("validate-daily-readiness", help="Validate a daily_readiness.v1 artifact.")
    validate_readiness_parser.add_argument("readiness_path")
    validate_refresh_plan_parser = subcommands.add_parser("validate-source-refresh-plan", help="Validate a source_refresh_plan.v1 artifact.")
    validate_refresh_plan_parser.add_argument("refresh_plan_path")
    validate_refresh_apply_parser = subcommands.add_parser("validate-source-refresh-apply", help="Validate a source_refresh_apply.v1 artifact.")
    validate_refresh_apply_parser.add_argument("refresh_apply_path")
    validate_refresh_live_gate_parser = subcommands.add_parser("validate-source-refresh-live-gate", help="Validate a source_refresh_live_gate.v1 artifact.")
    validate_refresh_live_gate_parser.add_argument("refresh_live_gate_path")
    validate_refresh_live_run_parser = subcommands.add_parser("validate-source-refresh-live-run", help="Validate a source_refresh_live_run.v1 artifact.")
    validate_refresh_live_run_parser.add_argument("refresh_live_run_path")
    validate_refresh_live_preflight_parser = subcommands.add_parser("validate-source-refresh-live-preflight", help="Validate a source_refresh_live_preflight.v1 artifact.")
    validate_refresh_live_preflight_parser.add_argument("refresh_live_preflight_path")
    validate_memory_parser = subcommands.add_parser("validate-topic-memory", help="Validate a topic_memory.v1 artifact.")
    validate_memory_parser.add_argument("memory_path")
    validate_review_parser = subcommands.add_parser("validate-daily-review", help="Validate a daily_review.v1 artifact.")
    validate_review_parser.add_argument("review_path")
    validate_review_prompt_parser = subcommands.add_parser("validate-review-prompt", help="Validate an operator_review_prompt.v1 artifact.")
    validate_review_prompt_parser.add_argument("review_prompt_path")
    validate_review_effect_parser = subcommands.add_parser("validate-review-effect", help="Validate an operator_review_effect.v1 artifact.")
    validate_review_effect_parser.add_argument("review_effect_path")
    validate_review_response_apply_parser = subcommands.add_parser("validate-review-response-apply", help="Validate an operator_review_response_apply.v1 artifact.")
    validate_review_response_apply_parser.add_argument("review_response_apply_path")
    validate_briefing_response_apply_parser = subcommands.add_parser("validate-briefing-response-apply", help="Validate an operator_briefing_response_apply.v1 artifact.")
    validate_briefing_response_apply_parser.add_argument("briefing_response_apply_path")
    validate_council_response_apply_parser = subcommands.add_parser("validate-council-response-apply", help="Validate an operator_council_response_apply.v1 artifact.")
    validate_council_response_apply_parser.add_argument("council_response_apply_path")
    validate_handoff_response_apply_parser = subcommands.add_parser("validate-handoff-response-apply", help="Validate an operator_handoff_response_apply.v1 artifact.")
    validate_handoff_response_apply_parser.add_argument("handoff_response_apply_path")
    validate_memory_query_parser = subcommands.add_parser("validate-memory-query", help="Validate a personal_memory_query.v1 artifact.")
    validate_memory_query_parser.add_argument("memory_query_path")
    validate_memory_audit_parser = subcommands.add_parser("validate-memory-audit", help="Validate a personal_memory_audit.v1 artifact.")
    validate_memory_audit_parser.add_argument("memory_audit_path")
    validate_council_parser = subcommands.add_parser("validate-analyst-council", help="Validate an analyst_council.v1 artifact.")
    validate_council_parser.add_argument("council_path")
    validate_pattern_radar_parser = subcommands.add_parser("validate-agent-pattern-radar", help="Validate an agent_pattern_radar.v1 artifact.")
    validate_pattern_radar_parser.add_argument("pattern_radar_path")
    validate_pattern_evidence_parser = subcommands.add_parser("validate-pattern-evidence-intake", help="Validate a pattern_evidence_intake.v1 artifact.")
    validate_pattern_evidence_parser.add_argument("pattern_evidence_intake_path")
    validate_pattern_proof_parser = subcommands.add_parser("validate-pattern-dry-run-proof", help="Validate a pattern_dry_run_proof.v1 artifact.")
    validate_pattern_proof_parser.add_argument("pattern_proof_path")
    validate_journal_parser = subcommands.add_parser("validate-analyst-journal", help="Validate a personal_analyst_journal.v1 artifact.")
    validate_journal_parser.add_argument("journal_path")
    validate_learning_parser = subcommands.add_parser("validate-learning-ledger", help="Validate a personal_learning_ledger.v1 artifact.")
    validate_learning_parser.add_argument("learning_ledger_path")
    validate_tasks_parser = subcommands.add_parser("validate-analyst-task-queue", help="Validate a personal_analyst_task_queue.v1 artifact.")
    validate_tasks_parser.add_argument("task_queue_path")
    validate_task_ledger_parser = subcommands.add_parser("validate-analyst-task-ledger", help="Validate a personal_analyst_task_ledger.v1 artifact.")
    validate_task_ledger_parser.add_argument("task_ledger_path")
    validate_task_apply_parser = subcommands.add_parser("validate-analyst-task-status-apply", help="Validate a personal_analyst_task_status_apply.v1 artifact.")
    validate_task_apply_parser.add_argument("task_status_apply_path")
    validate_morning_parser = subcommands.add_parser("validate-morning-control", help="Validate a morning_control_packet.v1 artifact.")
    validate_morning_parser.add_argument("morning_control_path")
    validate_run_trace_parser = subcommands.add_parser("validate-run-trace", help="Validate a local_run_trace.v1 artifact.")
    validate_run_trace_parser.add_argument("run_trace_path")
    validate_run_ledger_parser = subcommands.add_parser("validate-daily-run-ledger", help="Validate a daily_run_ledger.v1 artifact.")
    validate_run_ledger_parser.add_argument("run_ledger_path")
    validate_handoff_parser = subcommands.add_parser("validate-daily-handoff", help="Validate a daily_handoff.v1 artifact.")
    validate_handoff_parser.add_argument("handoff_path")
    validate_handoff_study_parser = subcommands.add_parser("validate-handoff-study-resolution", help="Validate a handoff_study_resolution.v1 artifact.")
    validate_handoff_study_parser.add_argument("handoff_study_resolution_path")
    validate_drift_review_parser = subcommands.add_parser("validate-drift-review", help="Validate a local_drift_review.v1 artifact.")
    validate_drift_review_parser.add_argument("drift_review_path")
    validate_scheduler_operations_parser = subcommands.add_parser("validate-scheduler-operations", help="Validate a local_scheduler_operations.v1 artifact.")
    validate_scheduler_operations_parser.add_argument("scheduler_operations_path")
    validate_source_refresh_brief_parser = subcommands.add_parser("validate-source-refresh-brief", help="Validate a source_refresh_brief.v1 artifact.")
    validate_source_refresh_brief_parser.add_argument("source_refresh_brief_path")
    validate_source_freshness_intake_parser = subcommands.add_parser("validate-source-freshness-intake", help="Validate a source_freshness_intake.v1 artifact.")
    validate_source_freshness_intake_parser.add_argument("source_freshness_intake_path")
    validate_source_refresh_execution_parser = subcommands.add_parser("validate-source-refresh-execution-brief", help="Validate a source_refresh_execution_brief.v1 artifact.")
    validate_source_refresh_execution_parser.add_argument("source_refresh_execution_brief_path")

    brief_parser = subcommands.add_parser("brief", help="Build a user-facing MyBroker product brief from scenario and verdict artifacts.")
    brief_parser.add_argument("--scenario", required=True, help="scenario_report.v1 artifact path.")
    brief_parser.add_argument("--verdict", required=True, help="market_verdict.v1 artifact path.")
    brief_parser.add_argument("--output", default="reports/product/market-brief.html")

    daily_parser = subcommands.add_parser("daily-research", help="Run topic planning, free/public evidence collection, memory update, scenario, dashboard, and product brief.")
    daily_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    daily_parser.add_argument("--profile", help="Optional beginner profile JSON.")
    daily_parser.add_argument("--run-id", default="daily-research")
    daily_parser.add_argument("--plan-output", default=DEFAULT_RESEARCH_PLAN_OUTPUT.as_posix())
    daily_parser.add_argument("--scout-output", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    daily_parser.add_argument("--refresh-plan-output", default=DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT.as_posix())
    daily_parser.add_argument("--refresh-apply-output", default=DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT.as_posix())
    daily_parser.add_argument("--refresh-live-gate-output", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())
    daily_parser.add_argument("--refresh-live-run-output", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    daily_parser.add_argument("--refresh-live-preflight-output", default=DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix())
    daily_parser.add_argument("--evidence-output", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    daily_parser.add_argument("--memory-output", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    daily_parser.add_argument("--scenario-output", default="reports/scenarios/daily-research-sim.json")
    daily_parser.add_argument("--verdict-output", default="reports/scenarios/daily-research-verdict.json")
    daily_parser.add_argument("--dashboard-output", default="reports/dashboard.html")
    daily_parser.add_argument("--rollup-output", default="reports/report-rollup.json")
    daily_parser.add_argument("--brief-output", default="reports/product/market-brief.html")
    daily_parser.add_argument("--source", action="append", help="Public evidence adapter id. Use gdelt-live/stooq-live for no-key live refresh with cache fallback.")

    appliance_parser = subcommands.add_parser("appliance", help="Run MyBroker as a local personal analyst appliance.")
    appliance_subcommands = appliance_parser.add_subparsers(dest="appliance_command", required=True)
    appliance_plan_parser = appliance_subcommands.add_parser("playbook", help="Write the local analyst runtime playbook artifact.")
    appliance_plan_parser.add_argument("--output", default=DEFAULT_RUNTIME_PLAYBOOK_OUTPUT.as_posix())
    appliance_init_parser = appliance_subcommands.add_parser("init", help="Write launchd-compatible local runner assets.")
    appliance_init_parser.add_argument("--project-root", default=".")
    appliance_init_parser.add_argument("--output-dir", default=DEFAULT_LOCAL_OPS_DIR.as_posix())
    appliance_init_parser.add_argument("--hour", type=int, default=7)
    appliance_init_parser.add_argument("--minute", type=int, default=30)
    appliance_init_parser.add_argument("--python", default="python3")
    appliance_access_parser = appliance_subcommands.add_parser("access", help="Write private phone access guidance for local /today.")
    appliance_access_parser.add_argument("--output", default=DEFAULT_PHONE_ACCESS_OUTPUT.as_posix())
    appliance_access_parser.add_argument("--port", type=int, default=8787)
    appliance_access_parser.add_argument("--tailnet-host", default="mybroker-mac")
    appliance_access_verify_parser = appliance_subcommands.add_parser("access-verify", help="Verify local phone access readiness without starting services.")
    appliance_access_verify_parser.add_argument("--project-root", default=".")
    appliance_access_verify_parser.add_argument("--phone-access", default=DEFAULT_PHONE_ACCESS_OUTPUT.as_posix())
    appliance_access_verify_parser.add_argument("--daily-home", default=DEFAULT_DAILY_HOME_SURFACE.as_posix())
    appliance_access_verify_parser.add_argument("--today", default=DEFAULT_TODAY_OUTPUT.as_posix())
    appliance_access_verify_parser.add_argument("--port", type=int, default=8787)
    appliance_access_verify_parser.add_argument("--artifact-output", default=DEFAULT_PHONE_ACCESS_VERIFY_OUTPUT.as_posix())
    appliance_access_verify_parser.add_argument("--output", default=DEFAULT_PHONE_ACCESS_VERIFY_SURFACE.as_posix())
    appliance_decision_parser = appliance_subcommands.add_parser("decision-packet", help="Write pending operator decisions for external-effect appliance gates.")
    appliance_decision_parser.add_argument("--project-root", default=".")
    appliance_decision_parser.add_argument("--output", default=DEFAULT_OPERATOR_DECISION_PACKET_OUTPUT.as_posix())
    appliance_decision_workflow_parser = appliance_subcommands.add_parser("decision", help="Validate and apply operator decision responses without executing external effects.")
    appliance_decision_subcommands = appliance_decision_workflow_parser.add_subparsers(dest="decision_command", required=True)
    appliance_decision_apply_parser = appliance_decision_subcommands.add_parser("apply", help="Turn an operator approval response into a dry-run command plan.")
    appliance_decision_apply_parser.add_argument("--response", required=True, help="Example: approve private_phone_access private_network_exposure")
    appliance_decision_apply_parser.add_argument("--project-root", default=".")
    appliance_decision_apply_parser.add_argument("--packet", default=DEFAULT_OPERATOR_DECISION_PACKET_OUTPUT.as_posix())
    appliance_decision_apply_parser.add_argument("--output", default=DEFAULT_OPERATOR_DECISION_APPLY_OUTPUT.as_posix())
    appliance_doctor_parser = appliance_subcommands.add_parser("doctor", help="Write a local runtime readiness proof without installing host services.")
    appliance_doctor_parser.add_argument("--project-root", default=".")
    appliance_doctor_parser.add_argument("--output", default=DEFAULT_RUNTIME_DOCTOR_OUTPUT.as_posix())
    appliance_doctor_parser.add_argument("--freshness-hours", type=int, default=36)
    appliance_doctor_parser.add_argument("--require-launchd-loaded", action="store_true")
    appliance_scheduler_parser = appliance_subcommands.add_parser("scheduler", help="Inspect scheduler status and host-level commands without installing.")
    appliance_scheduler_subcommands = appliance_scheduler_parser.add_subparsers(dest="scheduler_command", required=True)
    appliance_scheduler_status_parser = appliance_scheduler_subcommands.add_parser("status", help="Write launchd scheduler status proof.")
    appliance_scheduler_status_parser.add_argument("--project-root", default=".")
    appliance_scheduler_status_parser.add_argument("--output", default=DEFAULT_SCHEDULER_STATUS_OUTPUT.as_posix())
    appliance_scheduler_apply_parser = appliance_scheduler_subcommands.add_parser("apply", help="Plan or execute launchd scheduler host-level actions.")
    appliance_scheduler_apply_parser.add_argument("--project-root", default=".")
    appliance_scheduler_apply_parser.add_argument("--output", default=DEFAULT_SCHEDULER_APPLY_OUTPUT.as_posix())
    appliance_scheduler_apply_parser.add_argument("--install", action="store_true")
    appliance_scheduler_apply_parser.add_argument("--load", action="store_true")
    appliance_scheduler_apply_parser.add_argument("--start-now", action="store_true")
    appliance_scheduler_apply_parser.add_argument("--unload", action="store_true")
    appliance_scheduler_apply_parser.add_argument("--uninstall", action="store_true")
    appliance_scheduler_apply_parser.add_argument("--confirm-host-write", action="store_true")
    appliance_scheduler_run_once_parser = appliance_scheduler_subcommands.add_parser("run-once", help="Execute the local scheduler runner once without host-level launchd writes.")
    appliance_scheduler_run_once_parser.add_argument("--project-root", default=".")
    appliance_scheduler_run_once_parser.add_argument("--output", default=DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT.as_posix())
    appliance_scheduler_run_once_parser.add_argument("--timeout-seconds", type=int, default=240)
    appliance_scheduler_preflight_parser = appliance_scheduler_subcommands.add_parser("activation-preflight", help="Check whether scheduler activation has enough local proof before host-level writes.")
    appliance_scheduler_preflight_parser.add_argument("--project-root", default=".")
    appliance_scheduler_preflight_parser.add_argument("--output", default=DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT.as_posix())
    appliance_scheduler_preflight_parser.add_argument("--max-proof-age-hours", type=int, default=24)
    appliance_scheduler_verify_parser = appliance_scheduler_subcommands.add_parser("activation-verify", help="Verify a confirmed scheduler activation without performing host-level writes.")
    appliance_scheduler_verify_parser.add_argument("--project-root", default=".")
    appliance_scheduler_verify_parser.add_argument("--output", default=DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT.as_posix())
    appliance_scheduler_verify_parser.add_argument("--freshness-hours", type=int, default=36)
    appliance_scheduler_summary_parser = appliance_scheduler_subcommands.add_parser("summary", help="Render scheduler operations summary without host-level writes.")
    appliance_scheduler_summary_parser.add_argument("--project-root", default=".")
    appliance_scheduler_summary_parser.add_argument("--freshness-hours", type=int, default=24)
    appliance_scheduler_summary_parser.add_argument("--artifact-output", default=DEFAULT_SCHEDULER_OPERATIONS_OUTPUT.as_posix())
    appliance_scheduler_summary_parser.add_argument("--output", default=DEFAULT_SCHEDULER_OPERATIONS_SURFACE.as_posix())
    appliance_today_parser = appliance_subcommands.add_parser("today", help="Render the mobile-first /today product surface.")
    appliance_today_parser.add_argument("--scenario", default="reports/scenarios/daily-research-sim.json")
    appliance_today_parser.add_argument("--verdict", default="reports/scenarios/daily-research-verdict.json")
    appliance_today_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--refresh-plan", default=DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--refresh-apply", default=DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--refresh-live-gate", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--refresh-live-run", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--refresh-live-preflight", default=DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--agenda", default=DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--agenda-surface", default=DEFAULT_DAILY_BRIEF_AGENDA_SURFACE.as_posix())
    appliance_today_parser.add_argument("--source-refresh-surface", default=DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix())
    appliance_today_parser.add_argument("--pattern-radar-surface", default=DEFAULT_AGENT_PATTERN_RADAR_SURFACE.as_posix())
    appliance_today_parser.add_argument("--run-trace-surface", default=DEFAULT_RUN_TRACE_SURFACE.as_posix())
    appliance_today_parser.add_argument("--drift-review-surface", default=DEFAULT_DRIFT_REVIEW_SURFACE.as_posix())
    appliance_today_parser.add_argument("--brief", default="reports/product/market-brief.html")
    appliance_today_parser.add_argument("--output", default=DEFAULT_TODAY_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--archive-manifest")
    appliance_today_parser.add_argument("--memory-surface")
    appliance_today_parser.add_argument("--journal-surface")
    appliance_today_parser.add_argument("--task-queue-surface")
    appliance_today_parser.add_argument("--task-ledger-surface")
    appliance_home_parser = appliance_subcommands.add_parser("home", help="Render the phone-first daily operating home from existing local artifacts.")
    appliance_home_parser.add_argument("--today", default=DEFAULT_TODAY_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--morning", default=DEFAULT_MORNING_CONTROL_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--readiness", default=DEFAULT_DAILY_READINESS_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--handoff", default=DEFAULT_DAILY_HANDOFF_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--handoff-study-resolution", default=DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--handoff-apply", default=DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--run-ledger", default=DEFAULT_DAILY_RUN_LEDGER_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--run-trace", default=DEFAULT_RUN_TRACE_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--task-ledger", default=DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT.as_posix())
    appliance_home_parser.add_argument("--scheduler-operations", default=DEFAULT_SCHEDULER_OPERATIONS_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--phone-access", default=DEFAULT_PHONE_ACCESS_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--phone-access-verify", default=DEFAULT_PHONE_ACCESS_VERIFY_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--notification", default=DEFAULT_NOTIFICATION_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--source-freshness-intake", default=DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--source-refresh-execution", default=DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--memory-query", default=DEFAULT_MEMORY_QUERY_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--memory-audit", default=DEFAULT_MEMORY_AUDIT_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--learning-ledger", default=DEFAULT_LEARNING_LEDGER_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--pattern-radar", default=DEFAULT_AGENT_PATTERN_RADAR_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--pattern-dry-run-proof", default=DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--pattern-evidence-intake", default=DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--artifact-output", default=DEFAULT_DAILY_HOME_OUTPUT.as_posix())
    appliance_home_parser.add_argument("--output", default=DEFAULT_DAILY_HOME_SURFACE.as_posix())
    appliance_briefing_parser = appliance_subcommands.add_parser("briefing", help="Render the phone/message-ready daily briefing packet from existing local artifacts.")
    appliance_briefing_parser.add_argument("--daily-home", default=DEFAULT_DAILY_HOME_OUTPUT.as_posix())
    appliance_briefing_parser.add_argument("--today", default=DEFAULT_TODAY_OUTPUT.as_posix())
    appliance_briefing_parser.add_argument("--readiness", default=DEFAULT_DAILY_READINESS_OUTPUT.as_posix())
    appliance_briefing_parser.add_argument("--run-ledger", default=DEFAULT_DAILY_RUN_LEDGER_OUTPUT.as_posix())
    appliance_briefing_parser.add_argument("--handoff-study-resolution", default=DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT.as_posix())
    appliance_briefing_parser.add_argument("--learning-ledger", default=DEFAULT_LEARNING_LEDGER_OUTPUT.as_posix())
    appliance_briefing_parser.add_argument("--memory-query", default=DEFAULT_MEMORY_QUERY_OUTPUT.as_posix())
    appliance_briefing_parser.add_argument("--notification", default=DEFAULT_NOTIFICATION_OUTPUT.as_posix())
    appliance_briefing_parser.add_argument("--artifact-output", default=DEFAULT_DAILY_BRIEFING_PACKET_OUTPUT.as_posix())
    appliance_briefing_parser.add_argument("--output", default=DEFAULT_DAILY_BRIEFING_PACKET_SURFACE.as_posix())
    appliance_agenda_parser = appliance_subcommands.add_parser("agenda", help="Render the phone-first daily study agenda from scout and evidence artifacts.")
    appliance_agenda_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_agenda_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_agenda_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_agenda_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_agenda_parser.add_argument("--refresh-plan", default=DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT.as_posix())
    appliance_agenda_parser.add_argument("--artifact-output", default=DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT.as_posix())
    appliance_agenda_parser.add_argument("--output", default=DEFAULT_DAILY_BRIEF_AGENDA_SURFACE.as_posix())
    appliance_source_refresh_parser = appliance_subcommands.add_parser("source-refresh", help="Render the phone-first source refresh briefing from refresh artifacts.")
    appliance_source_refresh_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_source_refresh_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_source_refresh_parser.add_argument("--refresh-plan", default=DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT.as_posix())
    appliance_source_refresh_parser.add_argument("--refresh-apply", default=DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT.as_posix())
    appliance_source_refresh_parser.add_argument("--refresh-live-gate", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())
    appliance_source_refresh_parser.add_argument("--refresh-live-run", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    appliance_source_refresh_parser.add_argument("--refresh-live-preflight", default=DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix())
    appliance_source_refresh_parser.add_argument("--artifact-output", default=DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT.as_posix())
    appliance_source_refresh_parser.add_argument("--output", default=DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix())
    appliance_source_freshness_intake_parser = appliance_subcommands.add_parser("source-freshness-intake", help="Render the source freshness approval intake packet from local artifacts.")
    appliance_source_freshness_intake_parser.add_argument("--source-refresh-brief", default=DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT.as_posix())
    appliance_source_freshness_intake_parser.add_argument("--refresh-live-gate", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())
    appliance_source_freshness_intake_parser.add_argument("--refresh-live-run", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    appliance_source_freshness_intake_parser.add_argument("--refresh-live-preflight", default=DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix())
    appliance_source_freshness_intake_parser.add_argument("--artifact-output", default=DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT.as_posix())
    appliance_source_freshness_intake_parser.add_argument("--output", default=DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE.as_posix())
    appliance_source_refresh_execution_parser = appliance_subcommands.add_parser("source-refresh-execution", help="Render the final-confirmation proof before any live source refresh execution.")
    appliance_source_refresh_execution_parser.add_argument("--source-refresh-brief", default=DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT.as_posix())
    appliance_source_refresh_execution_parser.add_argument("--refresh-live-gate", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())
    appliance_source_refresh_execution_parser.add_argument("--refresh-live-run", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    appliance_source_refresh_execution_parser.add_argument("--refresh-live-preflight", default=DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix())
    appliance_source_refresh_execution_parser.add_argument("--artifact-output", default=DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT.as_posix())
    appliance_source_refresh_execution_parser.add_argument("--output", default=DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE.as_posix())
    appliance_source_refresh_response_parser = appliance_subcommands.add_parser("source-refresh-response", help="Apply a source refresh approval response into local proof artifacts without live network execution.")
    appliance_source_refresh_response_parser.add_argument("response", help='Example: approve live_network_refresh live_network_refresh')
    appliance_source_refresh_response_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--refresh-plan", default=DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--refresh-apply", default=DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--refresh-live-gate", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--refresh-live-run-output", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--refresh-live-preflight-output", default=DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--evidence-output", default=DEFAULT_LIVE_EVIDENCE_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--intend-execute", action="store_true", help="Record operator intent for preflight only; does not execute live network.")
    appliance_source_refresh_response_parser.add_argument("--confirm-live-network", action="store_true", help="Record live-network confirmation for preflight only; does not execute live network.")
    appliance_source_refresh_response_parser.add_argument("--artifact-output", default=DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--output", default=DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix())
    appliance_source_refresh_response_parser.add_argument("--source-refresh-execution-output", default=DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT.as_posix())
    appliance_source_refresh_response_parser.add_argument("--source-refresh-execution-surface", default=DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE.as_posix())
    appliance_readiness_parser = appliance_subcommands.add_parser("readiness", help="Render daily freshness and next-run readiness for phone review.")
    appliance_readiness_parser.add_argument("--project-root", default=".")
    appliance_readiness_parser.add_argument("--freshness-hours", type=int, default=24)
    appliance_readiness_parser.add_argument("--artifact-output", default=DEFAULT_DAILY_READINESS_OUTPUT.as_posix())
    appliance_readiness_parser.add_argument("--output", default=DEFAULT_DAILY_READINESS_SURFACE.as_posix())
    appliance_memory_parser = appliance_subcommands.add_parser("memory", help="Render the mobile-friendly accumulated memory and archive surface.")
    appliance_memory_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_memory_parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT.as_posix())
    appliance_memory_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_memory_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_memory_parser.add_argument("--index-output", default=DEFAULT_MEMORY_INDEX_OUTPUT.as_posix())
    appliance_memory_parser.add_argument("--output", default=DEFAULT_MEMORY_OUTPUT.as_posix())
    appliance_journal_parser = appliance_subcommands.add_parser("journal", help="Render today's personal analyst journal from daily artifacts.")
    appliance_journal_parser.add_argument("--scenario", default="reports/scenarios/daily-research-sim.json")
    appliance_journal_parser.add_argument("--verdict", default="reports/scenarios/daily-research-verdict.json")
    appliance_journal_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_journal_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_journal_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_journal_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_journal_parser.add_argument("--archive-manifest")
    appliance_journal_parser.add_argument("--artifact-output", default=DEFAULT_ANALYST_JOURNAL_ARTIFACT.as_posix())
    appliance_journal_parser.add_argument("--output", default=DEFAULT_ANALYST_JOURNAL_OUTPUT.as_posix())
    appliance_learning_parser = appliance_subcommands.add_parser("learning", help="Render the beginner learning ledger from today's local analyst artifacts.")
    appliance_learning_parser.add_argument("--scenario", default="reports/scenarios/daily-research-sim.json")
    appliance_learning_parser.add_argument("--verdict", default="reports/scenarios/daily-research-verdict.json")
    appliance_learning_parser.add_argument("--journal", default=DEFAULT_ANALYST_JOURNAL_ARTIFACT.as_posix())
    appliance_learning_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_learning_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_learning_parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT.as_posix())
    appliance_learning_parser.add_argument("--artifact-output", default=DEFAULT_LEARNING_LEDGER_OUTPUT.as_posix())
    appliance_learning_parser.add_argument("--output", default=DEFAULT_LEARNING_LEDGER_SURFACE.as_posix())
    appliance_tasks_parser = appliance_subcommands.add_parser("tasks", help="Render the role-based analyst task queue from today's journal.")
    appliance_tasks_parser.add_argument("--journal", default=DEFAULT_ANALYST_JOURNAL_ARTIFACT.as_posix())
    appliance_tasks_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_tasks_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_tasks_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_tasks_parser.add_argument("--artifact-output", default=DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT.as_posix())
    appliance_tasks_parser.add_argument("--output", default=DEFAULT_ANALYST_TASK_QUEUE_OUTPUT.as_posix())
    appliance_task_ledger_parser = appliance_subcommands.add_parser("task-ledger", help="Render task state history from the current analyst task queue.")
    appliance_task_ledger_parser.add_argument("--task-queue", default=DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT.as_posix())
    appliance_task_ledger_parser.add_argument("--previous-ledger", default=DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT.as_posix())
    appliance_task_ledger_parser.add_argument("--status-apply", default=DEFAULT_ANALYST_TASK_STATUS_APPLY.as_posix())
    appliance_task_ledger_parser.add_argument("--artifact-output", default=DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT.as_posix())
    appliance_task_ledger_parser.add_argument("--output", default=DEFAULT_ANALYST_TASK_LEDGER_OUTPUT.as_posix())
    appliance_task_response_parser = appliance_subcommands.add_parser("task-response", help="Record one local operator task status response.")
    appliance_task_response_parser.add_argument("response", help='Example: AT-001 complete "checked source freshness"')
    appliance_task_response_parser.add_argument("--responses", default=DEFAULT_ANALYST_TASK_RESPONSES.as_posix())
    appliance_task_apply_parser = appliance_subcommands.add_parser("task-status-apply", help="Apply local task status responses to the task ledger.")
    appliance_task_apply_parser.add_argument("--ledger", default=DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT.as_posix())
    appliance_task_apply_parser.add_argument("--responses", default=DEFAULT_ANALYST_TASK_RESPONSES.as_posix())
    appliance_task_apply_parser.add_argument("--output", default=DEFAULT_ANALYST_TASK_STATUS_APPLY.as_posix())
    appliance_review_response_parser = appliance_subcommands.add_parser("review-response", help="Record one local daily review response for tomorrow's scout scoring.")
    appliance_review_response_parser.add_argument("response", help='Example: more "Semiconductors" "memory cycle is useful"')
    appliance_review_response_parser.add_argument("--responses", default=DEFAULT_DAILY_REVIEW_RESPONSES.as_posix())
    appliance_review_response_apply_parser = appliance_subcommands.add_parser("review-response-apply", help="Record one local review response and refresh review/scout/effect proof.")
    appliance_review_response_apply_parser.add_argument("response", help='Example: more "Semiconductors" "memory cycle is useful"')
    appliance_review_response_apply_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    appliance_review_response_apply_parser.add_argument("--plan", default=DEFAULT_RESEARCH_PLAN_OUTPUT.as_posix())
    appliance_review_response_apply_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_review_response_apply_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_review_response_apply_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_review_response_apply_parser.add_argument("--task-status-apply", default=DEFAULT_ANALYST_TASK_STATUS_APPLY.as_posix())
    appliance_review_response_apply_parser.add_argument("--responses", default=DEFAULT_DAILY_REVIEW_RESPONSES.as_posix())
    appliance_review_response_apply_parser.add_argument("--run-id", default="daily-research")
    appliance_review_response_apply_parser.add_argument("--daily-review-output", default=DEFAULT_DAILY_REVIEW_OUTPUT.as_posix())
    appliance_review_response_apply_parser.add_argument("--daily-review-surface", default=DEFAULT_DAILY_REVIEW_SURFACE.as_posix())
    appliance_review_response_apply_parser.add_argument("--scout-output", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_review_response_apply_parser.add_argument("--review-prompt-output", default=DEFAULT_REVIEW_PROMPT_OUTPUT.as_posix())
    appliance_review_response_apply_parser.add_argument("--review-prompt-surface", default=DEFAULT_REVIEW_PROMPT_SURFACE.as_posix())
    appliance_review_response_apply_parser.add_argument("--review-effect-output", default=DEFAULT_REVIEW_EFFECT_OUTPUT.as_posix())
    appliance_review_response_apply_parser.add_argument("--review-effect-surface", default=DEFAULT_REVIEW_EFFECT_SURFACE.as_posix())
    appliance_review_response_apply_parser.add_argument("--artifact-output", default=DEFAULT_REVIEW_RESPONSE_APPLY_OUTPUT.as_posix())
    appliance_review_response_apply_parser.add_argument("--output", default=DEFAULT_REVIEW_RESPONSE_APPLY_SURFACE.as_posix())
    appliance_briefing_response_apply_parser = appliance_subcommands.add_parser("briefing-response-apply", help="Record one daily briefing reply and refresh review/scout/effect/home/briefing proof.")
    appliance_briefing_response_apply_parser.add_argument("response", help='Example: more "Semiconductors" "오늘 브리핑을 더 보고 싶다"')
    appliance_briefing_response_apply_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--plan", default=DEFAULT_RESEARCH_PLAN_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--task-status-apply", default=DEFAULT_ANALYST_TASK_STATUS_APPLY.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--responses", default=DEFAULT_DAILY_REVIEW_RESPONSES.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--run-id", default="daily-research")
    appliance_briefing_response_apply_parser.add_argument("--daily-review-output", default=DEFAULT_DAILY_REVIEW_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--daily-review-surface", default=DEFAULT_DAILY_REVIEW_SURFACE.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--scout-output", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--review-prompt-output", default=DEFAULT_REVIEW_PROMPT_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--review-prompt-surface", default=DEFAULT_REVIEW_PROMPT_SURFACE.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--review-effect-output", default=DEFAULT_REVIEW_EFFECT_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--review-effect-surface", default=DEFAULT_REVIEW_EFFECT_SURFACE.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--source-briefing-packet", default=DEFAULT_DAILY_BRIEFING_PACKET_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--agenda", default=DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--today", default=DEFAULT_TODAY_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--morning", default=DEFAULT_MORNING_CONTROL_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--readiness", default=DEFAULT_DAILY_READINESS_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--handoff", default=DEFAULT_DAILY_HANDOFF_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--handoff-study-resolution", default=DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--handoff-apply", default=DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--run-ledger", default=DEFAULT_DAILY_RUN_LEDGER_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--run-trace", default=DEFAULT_RUN_TRACE_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--task-ledger", default=DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--scheduler-operations", default=DEFAULT_SCHEDULER_OPERATIONS_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--phone-access", default=DEFAULT_PHONE_ACCESS_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--phone-access-verify", default=DEFAULT_PHONE_ACCESS_VERIFY_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--notification", default=DEFAULT_NOTIFICATION_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--source-freshness-intake", default=DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--source-refresh-execution", default=DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--memory-query", default=DEFAULT_MEMORY_QUERY_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--memory-audit", default=DEFAULT_MEMORY_AUDIT_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--learning-ledger", default=DEFAULT_LEARNING_LEDGER_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--pattern-radar", default=DEFAULT_AGENT_PATTERN_RADAR_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--pattern-dry-run-proof", default=DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--pattern-evidence-intake", default=DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--daily-home-output", default=DEFAULT_DAILY_HOME_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--daily-home-surface", default=DEFAULT_DAILY_HOME_SURFACE.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--briefing-packet-output", default=DEFAULT_DAILY_BRIEFING_PACKET_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--briefing-packet-surface", default=DEFAULT_DAILY_BRIEFING_PACKET_SURFACE.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--artifact-output", default=DEFAULT_BRIEFING_RESPONSE_APPLY_OUTPUT.as_posix())
    appliance_briefing_response_apply_parser.add_argument("--output", default=DEFAULT_BRIEFING_RESPONSE_APPLY_SURFACE.as_posix())
    appliance_handoff_response_apply_parser = appliance_subcommands.add_parser("handoff-response-apply", help="Record one copied handoff response and refresh the affected local proofs.")
    appliance_handoff_response_apply_parser.add_argument("response", help='Example: more "Semiconductors" "continue this tomorrow" or AT-001 carry "still open"')
    appliance_handoff_response_apply_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--plan", default=DEFAULT_RESEARCH_PLAN_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--responses", default=DEFAULT_HANDOFF_RESPONSES.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--review-responses", default=DEFAULT_DAILY_REVIEW_RESPONSES.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--task-responses", default=DEFAULT_ANALYST_TASK_RESPONSES.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--task-queue", default=DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--task-ledger", default=DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--task-ledger-surface", default=DEFAULT_ANALYST_TASK_LEDGER_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--task-status-apply", default=DEFAULT_ANALYST_TASK_STATUS_APPLY.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--daily-review-output", default=DEFAULT_DAILY_REVIEW_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--daily-review-surface", default=DEFAULT_DAILY_REVIEW_SURFACE.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--scout-output", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--review-prompt-output", default=DEFAULT_REVIEW_PROMPT_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--review-prompt-surface", default=DEFAULT_REVIEW_PROMPT_SURFACE.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--review-effect-output", default=DEFAULT_REVIEW_EFFECT_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--review-effect-surface", default=DEFAULT_REVIEW_EFFECT_SURFACE.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--handoff-output", default=DEFAULT_DAILY_HANDOFF_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--handoff-surface", default=DEFAULT_DAILY_HANDOFF_SURFACE.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--artifact-output", default=DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--output", default=DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE.as_posix())
    appliance_handoff_response_apply_parser.add_argument("--run-id", default="daily-research")
    appliance_handoff_study_parser = appliance_subcommands.add_parser("handoff-study-resolution", help="Render answer candidates and stop conditions for unresolved handoff questions.")
    appliance_handoff_study_parser.add_argument("--handoff", default=DEFAULT_DAILY_HANDOFF_OUTPUT.as_posix())
    appliance_handoff_study_parser.add_argument("--learning-ledger", default=DEFAULT_LEARNING_LEDGER_OUTPUT.as_posix())
    appliance_handoff_study_parser.add_argument("--memory-query", default=DEFAULT_MEMORY_QUERY_OUTPUT.as_posix())
    appliance_handoff_study_parser.add_argument("--memory-audit", default=DEFAULT_MEMORY_AUDIT_OUTPUT.as_posix())
    appliance_handoff_study_parser.add_argument("--source-freshness-intake", default=DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT.as_posix())
    appliance_handoff_study_parser.add_argument("--analyst-council", default=DEFAULT_ANALYST_COUNCIL_OUTPUT.as_posix())
    appliance_handoff_study_parser.add_argument("--review-prompt", default=DEFAULT_REVIEW_PROMPT_OUTPUT.as_posix())
    appliance_handoff_study_parser.add_argument("--artifact-output", default=DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT.as_posix())
    appliance_handoff_study_parser.add_argument("--output", default=DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE.as_posix())
    appliance_council_response_apply_parser = appliance_subcommands.add_parser("council-response-apply", help="Record one local council response and refresh review/scout/effect/council proof.")
    appliance_council_response_apply_parser.add_argument("response")
    appliance_council_response_apply_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    appliance_council_response_apply_parser.add_argument("--plan", default=DEFAULT_RESEARCH_PLAN_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--responses", default=DEFAULT_DAILY_REVIEW_RESPONSES.as_posix())
    appliance_council_response_apply_parser.add_argument("--task-status-apply", default=DEFAULT_ANALYST_TASK_STATUS_APPLY.as_posix())
    appliance_council_response_apply_parser.add_argument("--daily-review-output", default=DEFAULT_DAILY_REVIEW_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--daily-review-surface", default=DEFAULT_DAILY_REVIEW_SURFACE.as_posix())
    appliance_council_response_apply_parser.add_argument("--scout-output", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--review-prompt-output", default=DEFAULT_REVIEW_PROMPT_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--review-prompt-surface", default=DEFAULT_REVIEW_PROMPT_SURFACE.as_posix())
    appliance_council_response_apply_parser.add_argument("--review-effect-output", default=DEFAULT_REVIEW_EFFECT_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--review-effect-surface", default=DEFAULT_REVIEW_EFFECT_SURFACE.as_posix())
    appliance_council_response_apply_parser.add_argument("--scenario", default="reports/scenarios/daily-research-sim.json")
    appliance_council_response_apply_parser.add_argument("--verdict", default="reports/scenarios/daily-research-verdict.json")
    appliance_council_response_apply_parser.add_argument("--journal", default=DEFAULT_ANALYST_JOURNAL_ARTIFACT.as_posix())
    appliance_council_response_apply_parser.add_argument("--memory-audit", default=DEFAULT_MEMORY_AUDIT_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--council-output", default=DEFAULT_ANALYST_COUNCIL_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--council-surface", default=DEFAULT_ANALYST_COUNCIL_SURFACE.as_posix())
    appliance_council_response_apply_parser.add_argument("--artifact-output", default=DEFAULT_COUNCIL_RESPONSE_APPLY_OUTPUT.as_posix())
    appliance_council_response_apply_parser.add_argument("--output", default=DEFAULT_COUNCIL_RESPONSE_APPLY_SURFACE.as_posix())
    appliance_council_response_apply_parser.add_argument("--run-id", default="daily-research")
    appliance_review_parser = appliance_subcommands.add_parser("review", help="Render daily review memory and scout scoring signals.")
    appliance_review_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_review_parser.add_argument("--task-status-apply", default=DEFAULT_ANALYST_TASK_STATUS_APPLY.as_posix())
    appliance_review_parser.add_argument("--responses", default=DEFAULT_DAILY_REVIEW_RESPONSES.as_posix())
    appliance_review_parser.add_argument("--artifact-output", default=DEFAULT_DAILY_REVIEW_OUTPUT.as_posix())
    appliance_review_parser.add_argument("--output", default=DEFAULT_DAILY_REVIEW_SURFACE.as_posix())
    appliance_review_prompt_parser = appliance_subcommands.add_parser("review-prompt", help="Render copy-ready local review prompts for phone feedback.")
    appliance_review_prompt_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_review_prompt_parser.add_argument("--daily-review", default=DEFAULT_DAILY_REVIEW_OUTPUT.as_posix())
    appliance_review_prompt_parser.add_argument("--drift-review", default=DEFAULT_DRIFT_REVIEW_OUTPUT.as_posix())
    appliance_review_prompt_parser.add_argument("--task-ledger", default=DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT.as_posix())
    appliance_review_prompt_parser.add_argument("--artifact-output", default=DEFAULT_REVIEW_PROMPT_OUTPUT.as_posix())
    appliance_review_prompt_parser.add_argument("--output", default=DEFAULT_REVIEW_PROMPT_SURFACE.as_posix())
    appliance_review_effect_parser = appliance_subcommands.add_parser("review-effect", help="Render proof that local review feedback shaped scout scoring.")
    appliance_review_effect_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_review_effect_parser.add_argument("--daily-review", default=DEFAULT_DAILY_REVIEW_OUTPUT.as_posix())
    appliance_review_effect_parser.add_argument("--review-prompt", default=DEFAULT_REVIEW_PROMPT_OUTPUT.as_posix())
    appliance_review_effect_parser.add_argument("--artifact-output", default=DEFAULT_REVIEW_EFFECT_OUTPUT.as_posix())
    appliance_review_effect_parser.add_argument("--output", default=DEFAULT_REVIEW_EFFECT_SURFACE.as_posix())
    appliance_pattern_radar_parser = appliance_subcommands.add_parser("pattern-radar", help="Render the workflow-pattern radar for local analyst evolution.")
    appliance_pattern_radar_parser.add_argument("--playbook", default=DEFAULT_RUNTIME_PLAYBOOK_OUTPUT.as_posix())
    appliance_pattern_radar_parser.add_argument("--pattern-proof", default=DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT.as_posix())
    appliance_pattern_radar_parser.add_argument("--artifact-output", default=DEFAULT_AGENT_PATTERN_RADAR_OUTPUT.as_posix())
    appliance_pattern_radar_parser.add_argument("--output", default=DEFAULT_AGENT_PATTERN_RADAR_SURFACE.as_posix())
    appliance_pattern_evidence_parser = appliance_subcommands.add_parser("pattern-evidence-intake", help="Render local evidence intake for workflow-pattern candidates.")
    appliance_pattern_evidence_parser.add_argument("--pattern-radar", default=DEFAULT_AGENT_PATTERN_RADAR_OUTPUT.as_posix())
    appliance_pattern_evidence_parser.add_argument("--pattern-proof", default=DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT.as_posix())
    appliance_pattern_evidence_parser.add_argument("--artifact-output", default=DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT.as_posix())
    appliance_pattern_evidence_parser.add_argument("--output", default=DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE.as_posix())
    appliance_pattern_proof_parser = appliance_subcommands.add_parser("pattern-dry-run", help="Render proof that local workflow-pattern candidates can be adopted safely.")
    appliance_pattern_proof_parser.add_argument("--pattern-radar", default=DEFAULT_AGENT_PATTERN_RADAR_OUTPUT.as_posix())
    appliance_pattern_proof_parser.add_argument("--artifact-output", default=DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT.as_posix())
    appliance_pattern_proof_parser.add_argument("--output", default=DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE.as_posix())
    appliance_trace_parser = appliance_subcommands.add_parser("trace", help="Render a compact local run trace proof from existing daily artifacts.")
    appliance_trace_parser.add_argument("--artifact-output", default=DEFAULT_RUN_TRACE_OUTPUT.as_posix())
    appliance_trace_parser.add_argument("--output", default=DEFAULT_RUN_TRACE_SURFACE.as_posix())
    appliance_run_ledger_parser = appliance_subcommands.add_parser("run-ledger", help="Render the daily run ledger and canonical run proof.")
    appliance_run_ledger_parser.add_argument("--artifact-output", default=DEFAULT_DAILY_RUN_LEDGER_OUTPUT.as_posix())
    appliance_run_ledger_parser.add_argument("--output", default=DEFAULT_DAILY_RUN_LEDGER_SURFACE.as_posix())
    appliance_run_ledger_parser.add_argument("--archive-manifest")
    appliance_handoff_parser = appliance_subcommands.add_parser("handoff", help="Render the cross-day handoff proof from existing local artifacts.")
    appliance_handoff_parser.add_argument("--artifact-output", default=DEFAULT_DAILY_HANDOFF_OUTPUT.as_posix())
    appliance_handoff_parser.add_argument("--output", default=DEFAULT_DAILY_HANDOFF_SURFACE.as_posix())
    appliance_drift_parser = appliance_subcommands.add_parser("drift-review", help="Render a trace-backed local direction drift review.")
    appliance_drift_parser.add_argument("--artifact-output", default=DEFAULT_DRIFT_REVIEW_OUTPUT.as_posix())
    appliance_drift_parser.add_argument("--output", default=DEFAULT_DRIFT_REVIEW_SURFACE.as_posix())
    appliance_morning_parser = appliance_subcommands.add_parser("morning", help="Render the morning analyst control packet from existing daily artifacts.")
    appliance_morning_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_morning_parser.add_argument("--journal", default=DEFAULT_ANALYST_JOURNAL_ARTIFACT.as_posix())
    appliance_morning_parser.add_argument("--task-queue", default=DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT.as_posix())
    appliance_morning_parser.add_argument("--task-ledger", default=DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT.as_posix())
    appliance_morning_parser.add_argument("--refresh-live-gate", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())
    appliance_morning_parser.add_argument("--refresh-live-run", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    appliance_morning_parser.add_argument("--refresh-live-preflight", default=DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix())
    appliance_morning_parser.add_argument("--notification", default=DEFAULT_NOTIFICATION_OUTPUT.as_posix())
    appliance_morning_parser.add_argument("--runtime-doctor", default=DEFAULT_RUNTIME_DOCTOR_OUTPUT.as_posix())
    appliance_morning_parser.add_argument("--scheduler-surface", default=DEFAULT_SCHEDULER_OPERATIONS_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--source-refresh-surface", default=DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--pattern-radar-surface", default=DEFAULT_AGENT_PATTERN_RADAR_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--pattern-dry-run-surface", default=DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--run-trace-surface", default=DEFAULT_RUN_TRACE_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--run-ledger-surface", default=DEFAULT_DAILY_RUN_LEDGER_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--handoff-surface", default=DEFAULT_DAILY_HANDOFF_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--handoff-apply-surface", default=DEFAULT_HANDOFF_RESPONSE_APPLY_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--drift-review-surface", default=DEFAULT_DRIFT_REVIEW_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--analyst-council-surface", default=DEFAULT_ANALYST_COUNCIL_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--memory-query-surface", default=DEFAULT_MEMORY_QUERY_SURFACE.as_posix())
    appliance_morning_parser.add_argument("--artifact-output", default=DEFAULT_MORNING_CONTROL_OUTPUT.as_posix())
    appliance_morning_parser.add_argument("--output", default=DEFAULT_MORNING_CONTROL_SURFACE.as_posix())
    appliance_query_parser = appliance_subcommands.add_parser("query", help="Search accumulated memory and archives for a beginner-readable question.")
    appliance_query_parser.add_argument("query")
    appliance_query_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_query_parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT.as_posix())
    appliance_query_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_query_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_query_parser.add_argument("--output", default=DEFAULT_MEMORY_QUERY_OUTPUT.as_posix())
    appliance_query_parser.add_argument("--surface-output", default=DEFAULT_MEMORY_QUERY_SURFACE.as_posix())
    appliance_query_parser.add_argument("--limit", type=int, default=5)
    appliance_audit_parser = appliance_subcommands.add_parser("audit", help="Audit local memory, vault, archives, source posture, and review feedback.")
    appliance_audit_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_audit_parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT.as_posix())
    appliance_audit_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_audit_parser.add_argument("--vault", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_audit_parser.add_argument("--daily-review", default=DEFAULT_DAILY_REVIEW_OUTPUT.as_posix())
    appliance_audit_parser.add_argument("--output", default=DEFAULT_MEMORY_AUDIT_OUTPUT.as_posix())
    appliance_audit_parser.add_argument("--surface-output", default=DEFAULT_MEMORY_AUDIT_SURFACE.as_posix())
    appliance_council_parser = appliance_subcommands.add_parser("council", help="Render role-specific analyst council review before reading today's brief.")
    appliance_council_parser.add_argument("--scenario", default="reports/scenarios/daily-research-sim.json")
    appliance_council_parser.add_argument("--verdict", default="reports/scenarios/daily-research-verdict.json")
    appliance_council_parser.add_argument("--journal", default=DEFAULT_ANALYST_JOURNAL_ARTIFACT.as_posix())
    appliance_council_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_council_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_council_parser.add_argument("--memory-audit", default=DEFAULT_MEMORY_AUDIT_OUTPUT.as_posix())
    appliance_council_parser.add_argument("--scout", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_council_parser.add_argument("--artifact-output", default=DEFAULT_ANALYST_COUNCIL_OUTPUT.as_posix())
    appliance_council_parser.add_argument("--output", default=DEFAULT_ANALYST_COUNCIL_SURFACE.as_posix())
    appliance_notify_parser = appliance_subcommands.add_parser("notify", help="Prepare a phone notification payload. Dry-run by default.")
    appliance_notify_parser.add_argument("--provider", choices=["telegram", "pushover"], default="telegram")
    appliance_notify_parser.add_argument("--today-url", default="http://localhost:8787/reports/product/today.html")
    appliance_notify_parser.add_argument("--today", default=DEFAULT_TODAY_OUTPUT.as_posix())
    appliance_notify_parser.add_argument("--scenario", default="reports/scenarios/daily-research-sim.json")
    appliance_notify_parser.add_argument("--verdict", default="reports/scenarios/daily-research-verdict.json")
    appliance_notify_parser.add_argument("--briefing-packet", default=DEFAULT_DAILY_BRIEFING_PACKET_OUTPUT.as_posix())
    appliance_notify_parser.add_argument("--output", default=DEFAULT_NOTIFICATION_OUTPUT.as_posix())
    appliance_notify_parser.add_argument("--dry-run", action="store_true", default=True)
    appliance_notify_parser.add_argument("--send", action="store_true", help="Send using provider environment variables instead of dry-run.")
    appliance_vault_parser = appliance_subcommands.add_parser("vault", help="Manage the local research vault inbox and wiki.")
    appliance_vault_subcommands = appliance_vault_parser.add_subparsers(dest="vault_command", required=True)
    appliance_vault_init_parser = appliance_vault_subcommands.add_parser("init", help="Create raw/wiki/output folders for the local research vault.")
    appliance_vault_init_parser.add_argument("--root", default=DEFAULT_VAULT_ROOT.as_posix())
    appliance_vault_compile_parser = appliance_vault_subcommands.add_parser("compile", help="Compile raw markdown/text notes into wiki notes and an index artifact.")
    appliance_vault_compile_parser.add_argument("--raw-dir", default=DEFAULT_VAULT_RAW_DIR.as_posix())
    appliance_vault_compile_parser.add_argument("--wiki-dir", default=DEFAULT_VAULT_WIKI_DIR.as_posix())
    appliance_vault_compile_parser.add_argument("--output", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_vault_compile_parser.add_argument("--surface-output", default=DEFAULT_VAULT_SURFACE_OUTPUT.as_posix())
    appliance_vault_compile_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    appliance_run_parser = appliance_subcommands.add_parser("run", help="Run the daily analyst loop, archive it, render /today, and prepare notification.")
    appliance_run_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    appliance_run_parser.add_argument("--profile", help="Optional beginner profile JSON.")
    appliance_run_parser.add_argument("--run-id", default="daily-research")
    appliance_run_parser.add_argument("--today-url", default="http://localhost:8787/reports/product/today.html")
    appliance_run_parser.add_argument("--notification-provider", choices=["telegram", "pushover"], default="telegram")
    appliance_run_parser.add_argument("--briefing-packet-output", default=DEFAULT_DAILY_BRIEFING_PACKET_OUTPUT.as_posix())
    appliance_run_parser.add_argument("--briefing-packet-surface", default=DEFAULT_DAILY_BRIEFING_PACKET_SURFACE.as_posix())
    appliance_run_parser.add_argument("--dry-run", action="store_true", default=True)
    appliance_run_parser.add_argument("--send", action="store_true", help="Send notification after writing payload. Requires provider environment variables.")
    appliance_run_parser.add_argument("--source", action="append", help="Public evidence adapter id. Use gdelt-live/stooq-live for no-key live refresh with cache fallback.")
    appliance_run_parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT.as_posix())
    appliance_run_parser.add_argument("--vault-raw-dir", default=DEFAULT_VAULT_RAW_DIR.as_posix())
    appliance_run_parser.add_argument("--vault-wiki-dir", default=DEFAULT_VAULT_WIKI_DIR.as_posix())
    appliance_run_parser.add_argument("--vault-output", default=DEFAULT_VAULT_COMPILE_OUTPUT.as_posix())
    appliance_run_parser.add_argument("--vault-surface-output", default=DEFAULT_VAULT_SURFACE_OUTPUT.as_posix())
    appliance_run_parser.add_argument("--skip-vault-compile", action="store_true", help="Do not auto-compile local raw vault notes before the daily scout.")
    appliance_run_parser.add_argument("--playbook-output", default=DEFAULT_RUNTIME_PLAYBOOK_OUTPUT.as_posix())
    appliance_run_parser.add_argument("--scout-output", default=DEFAULT_DAILY_SCOUT_OUTPUT.as_posix())
    appliance_run_parser.add_argument("--refresh-plan-output", default=DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT.as_posix())
    appliance_run_parser.add_argument("--refresh-apply-output", default=DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT.as_posix())
    appliance_run_parser.add_argument("--refresh-live-gate-output", default=DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT.as_posix())
    appliance_run_parser.add_argument("--refresh-live-run-output", default=DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT.as_posix())
    appliance_run_parser.add_argument("--refresh-live-preflight-output", default=DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT.as_posix())

    quality_parser = subcommands.add_parser("quality", help="Inspect local price dataset quality without writing a research report.")
    quality_parser.add_argument("--source", action="append", help="Local price CSV file or directory. Repeat for multiple CSV files. Defaults to the bundled sample data.")
    quality_parser.add_argument("--min-history", type=int, default=5)

    policy_parser = subcommands.add_parser("policy", help="Classify a proposed project action.")
    policy_parser.add_argument("--kind", required=True)

    args = parser.parse_args(argv)
    if args.command == "signals":
        bars = load_price_csv(args.csv_path)
        signals = momentum_signals(bars, short_window=args.short_window, long_window=args.long_window)
        print(json.dumps([asdict(signal) for signal in signals], indent=2, default=str))
        return 0
    if args.command == "research":
        report = run_research_task(
            source=args.source,
            task_id=args.task,
            short_window=args.short_window,
            long_window=args.long_window,
            run_id=args.run_id,
            output_path=args.output,
        )
        print(json.dumps(report_to_dict(report), indent=2, ensure_ascii=False))
        return 0
    if args.command == "tasks":
        tasks = [asdict(task) for task in default_registry().list_tasks()]
        print(json.dumps(tasks, indent=2))
        return 0
    if args.command == "validate-report":
        errors = validate_report_file(args.report_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "quality":
        adapter = make_price_adapter(args.source)
        dataset = adapter.load_dataset(min_history=args.min_history)
        print(json.dumps({
            "metadata": asdict(dataset.metadata),
            "data_quality": asdict(dataset.quality),
        }, indent=2, ensure_ascii=False))
        return 1 if dataset.quality.error_count else 0
    if args.command == "dashboard":
        rollup = build_report_rollup(args.reports_dir)
        dashboard_path = write_dashboard(rollup, args.output)
        rollup_path = write_rollup(rollup, args.rollup_output)
        print(json.dumps({
            "dashboard": dashboard_path.as_posix(),
            "rollup": rollup_path.as_posix(),
            "report_count": rollup["report_count"],
            "latest_valid": bool((rollup.get("latest_report") or {}).get("validation", {}).get("valid")),
        }, indent=2))
        return 0
    if args.command == "scenario":
        report = run_market_simulation(
            seed_sources=args.seed,
            profile_path=args.profile,
            evidence_catalog_path=args.evidence_catalog,
            run_id=args.run_id,
        )
        scenario_path = write_scenario_report(report, args.output)
        verdict_path = write_verdict(report, args.verdict_output)
        print(json.dumps({
            "scenario_report": scenario_path.as_posix(),
            "verdict": verdict_path.as_posix(),
            "run_id": report.run_id,
            "entities": len(report.market_map.entities),
            "scenarios": len(report.scenarios),
            "action_candidates": len(report.action_candidates),
            "output_boundary": report.output_boundary,
            "primary_next_step": build_verdict(report)["primary_next_step"]["title"],
            "report": scenario_report_to_dict(report),
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "evidence-sources":
        print(json.dumps(SOURCE_MATRIX, indent=2, ensure_ascii=False))
        return 0
    if args.command == "ingest-public-evidence":
        catalog = build_public_evidence_catalog(args.source)
        catalog_path = write_public_evidence_catalog(catalog, args.output)
        print(json.dumps({
            "catalog": catalog_path.as_posix(),
            "schema_version": catalog["schema_version"],
            "mode": catalog["mode"],
            "source_count": len(catalog["source_status"]),
            "item_count": len(catalog["items"]),
            "feasibility": catalog["feasibility"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "validate-public-evidence":
        errors = validate_public_evidence_catalog_file(args.catalog_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "topics":
        if args.topics_command == "init":
            payload = init_topic_config(args.output)
            print(json.dumps({
                "topics": args.output,
                "schema_version": payload["schema_version"],
                "interest_count": len(payload["interests"]),
            }, indent=2, ensure_ascii=False))
            return 0
        if args.topics_command == "add":
            payload = add_interest(
                name=args.name,
                description=args.description,
                keywords=args.keyword,
                beginner_focus=args.beginner_focus,
                path=args.config,
            )
            print(json.dumps({
                "topics": args.config,
                "interest_count": len(payload["interests"]),
                "latest": payload["interests"][-1],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.topics_command == "list":
            payload = load_topic_config(args.config)
            print(json.dumps({
                "topics": args.config,
                "interest_count": len(payload.get("interests", [])),
                "interests": payload.get("interests", []),
                "policy": payload.get("policy", {}),
            }, indent=2, ensure_ascii=False))
            return 0
    if args.command == "research-plan":
        payload = build_research_plan(topics_path=args.topics, output_path=args.output, run_id=args.run_id)
        print(json.dumps({
            "research_plan": args.output,
            "schema_version": payload["schema_version"],
            "run_id": payload["run_id"],
            "topic_count": len(payload["plan_items"]),
            "next_step": payload["next_step"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "collect-evidence":
        payload = collect_topic_evidence(
            topics_path=args.topics,
            plan_path=args.plan,
            output_path=args.output,
            memory_path=args.memory_output,
            source_ids=args.source,
        )
        print(json.dumps({
            "catalog": args.output,
            "memory": args.memory_output,
            "schema_version": payload["schema_version"],
            "mode": payload["mode"],
            "item_count": len(payload["items"]),
            "topic_count": len(payload.get("configured_interests", [])),
            "feasibility": payload["feasibility"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "daily-scout":
        payload = build_daily_scout(
            topics_path=args.topics,
            plan_path=args.plan,
            evidence_path=args.evidence,
            memory_path=args.memory,
            vault_path=args.vault,
            review_path=args.review,
            output_path=args.output,
            run_id=args.run_id,
        )
        top = payload.get("recommended_topic", {})
        print(json.dumps({
            "daily_scout": args.output,
            "schema_version": payload["schema_version"],
            "recommended_topic": top.get("name", ""),
            "action": top.get("action", ""),
            "score": top.get("score", 0),
            "recommendation_count": payload["recommendation_count"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "source-refresh-plan":
        payload = build_source_refresh_plan(
            scout_path=args.scout,
            evidence_path=args.evidence,
            vault_path=args.vault,
            output_path=args.output,
        )
        print(json.dumps({
            "source_refresh_plan": args.output,
            "schema_version": payload["schema_version"],
            "action_count": len(payload["actions"]),
            "selected_live_sources": payload["selected_live_sources"],
            "external_effect_performed": payload["external_effect_performed"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "source-refresh-apply":
        payload = build_source_refresh_apply(
            refresh_plan_path=args.refresh_plan,
            output_path=args.output,
        )
        print(json.dumps({
            "source_refresh_apply": args.output,
            "schema_version": payload["schema_version"],
            "execution_mode": payload["execution_mode"],
            "external_effect_performed": payload["external_effect_performed"],
            "ready_count": payload["summary"]["ready_count"],
            "blocked_count": payload["summary"]["blocked_count"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "source-refresh-live-gate":
        payload = build_source_refresh_live_gate(
            refresh_apply_path=args.refresh_apply,
            output_path=args.output,
        )
        print(json.dumps({
            "source_refresh_live_gate": args.output,
            "schema_version": payload["schema_version"],
            "status": payload["status"],
            "blocked_action_count": payload["blocked_action_count"],
            "proposed_command_count": payload["proposed_command_count"],
            "external_effect_performed": payload["external_effect_performed"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "source-refresh-live-run":
        payload = build_source_refresh_live_run(
            live_gate_path=args.live_gate,
            response=args.response,
            output_path=args.output,
            evidence_output_path=args.evidence_output,
            execute=args.execute,
            confirm_live_network=args.confirm_live_network,
        )
        print(json.dumps({
            "source_refresh_live_run": args.output,
            "schema_version": payload["schema_version"],
            "approval_status": payload["approval_status"],
            "execution_status": payload["execution"]["status"],
            "external_effect_performed": payload["external_effect_performed"],
            "blockers": payload["execution"]["blockers"],
            "next_step": payload["next_step"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "source-refresh-live-preflight":
        payload = build_source_refresh_live_preflight(
            live_run_path=args.live_run,
            output_path=args.output,
            intend_execute=args.intend_execute,
            confirm_live_network=args.confirm_live_network,
        )
        print(json.dumps({
            "source_refresh_live_preflight": args.output,
            "schema_version": payload["schema_version"],
            "status": payload["status"],
            "approval_status": payload["approval_status"],
            "live_run_status": payload["live_run_status"],
            "external_effect_performed": payload["external_effect_performed"],
            "blockers": payload["blockers"],
            "warnings": payload["warnings"],
            "next_step": payload["next_step"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "validate-topics":
        errors = validate_topic_config_file(args.topics_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-research-plan":
        errors = validate_research_plan_file(args.plan_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-daily-scout":
        errors = validate_daily_scout_file(args.scout_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-daily-agenda":
        errors = validate_daily_brief_agenda_file(args.agenda_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-daily-home":
        errors = validate_daily_operator_home_file(args.daily_home_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-daily-briefing-packet":
        errors = validate_daily_briefing_packet_file(args.briefing_packet_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-learning-ledger":
        errors = validate_learning_ledger_file(args.learning_ledger_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-phone-access-verify":
        errors = validate_phone_access_verify_file(args.phone_access_verify_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-daily-readiness":
        errors = validate_daily_readiness_file(args.readiness_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-source-refresh-plan":
        errors = validate_source_refresh_plan_file(args.refresh_plan_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-source-refresh-apply":
        errors = validate_source_refresh_apply_file(args.refresh_apply_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-source-refresh-live-gate":
        errors = validate_source_refresh_live_gate_file(args.refresh_live_gate_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-source-refresh-live-run":
        errors = validate_source_refresh_live_run_file(args.refresh_live_run_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-source-refresh-live-preflight":
        errors = validate_source_refresh_live_preflight_file(args.refresh_live_preflight_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-topic-memory":
        errors = validate_topic_memory_file(args.memory_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-daily-review":
        errors = validate_daily_review_file(args.review_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-review-prompt":
        errors = validate_operator_review_prompt_file(args.review_prompt_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-review-effect":
        errors = validate_operator_review_effect_file(args.review_effect_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-review-response-apply":
        errors = validate_operator_review_response_apply_file(args.review_response_apply_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-briefing-response-apply":
        errors = validate_operator_briefing_response_apply_file(args.briefing_response_apply_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-council-response-apply":
        errors = validate_operator_council_response_apply_file(args.council_response_apply_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-handoff-response-apply":
        errors = validate_operator_handoff_response_apply_file(args.handoff_response_apply_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-memory-query":
        errors = validate_memory_query_file(args.memory_query_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-memory-audit":
        errors = validate_memory_audit_file(args.memory_audit_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-analyst-council":
        errors = validate_analyst_council_file(args.council_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-agent-pattern-radar":
        errors = validate_agent_pattern_radar_file(args.pattern_radar_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-pattern-evidence-intake":
        errors = validate_pattern_evidence_intake_file(args.pattern_evidence_intake_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-pattern-dry-run-proof":
        errors = validate_pattern_dry_run_proof_file(args.pattern_proof_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-analyst-journal":
        errors = validate_analyst_journal_file(args.journal_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-analyst-task-queue":
        errors = validate_analyst_task_queue_file(args.task_queue_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-analyst-task-ledger":
        errors = validate_analyst_task_ledger_file(args.task_ledger_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-analyst-task-status-apply":
        errors = validate_task_status_apply_file(args.task_status_apply_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-morning-control":
        errors = validate_morning_control_packet_file(args.morning_control_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-run-trace":
        errors = validate_run_trace_file(args.run_trace_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-daily-run-ledger":
        errors = validate_daily_run_ledger_file(args.run_ledger_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-daily-handoff":
        errors = validate_daily_handoff_file(args.handoff_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-handoff-study-resolution":
        errors = validate_handoff_study_resolution_file(args.handoff_study_resolution_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-drift-review":
        errors = validate_drift_review_file(args.drift_review_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-scheduler-operations":
        errors = validate_scheduler_operations_file(args.scheduler_operations_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-source-refresh-brief":
        errors = validate_source_refresh_brief_file(args.source_refresh_brief_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-source-freshness-intake":
        errors = validate_source_freshness_intake_file(args.source_freshness_intake_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-source-refresh-execution-brief":
        errors = validate_source_refresh_execution_brief_file(args.source_refresh_execution_brief_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-vault":
        errors = validate_knowledge_vault_compile_file(args.vault_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "brief":
        path = write_product_brief(args.scenario, args.verdict, args.output)
        print(json.dumps({"product_brief": path.as_posix()}, indent=2, ensure_ascii=False))
        return 0
    if args.command == "daily-research":
        topics_path = args.topics
        if not Path(topics_path).exists():
            init_topic_config(topics_path)
        plan = build_research_plan(topics_path=topics_path, output_path=args.plan_output, run_id=args.run_id)
        catalog = collect_topic_evidence(
            topics_path=topics_path,
            plan_path=args.plan_output,
            output_path=args.evidence_output,
            memory_path=args.memory_output,
            source_ids=args.source,
        )
        scout = build_daily_scout(
            topics_path=topics_path,
            plan_path=args.plan_output,
            evidence_path=args.evidence_output,
            memory_path=args.memory_output,
            vault_path=DEFAULT_VAULT_COMPILE_OUTPUT,
            output_path=args.scout_output,
            run_id=args.run_id,
        )
        refresh_plan = build_source_refresh_plan(
            scout_path=args.scout_output,
            evidence_path=args.evidence_output,
            vault_path=DEFAULT_VAULT_COMPILE_OUTPUT,
            output_path=args.refresh_plan_output,
        )
        refresh_apply = build_source_refresh_apply(
            refresh_plan_path=args.refresh_plan_output,
            output_path=args.refresh_apply_output,
        )
        refresh_live_gate = build_source_refresh_live_gate(
            refresh_apply_path=args.refresh_apply_output,
            output_path=args.refresh_live_gate_output,
        )
        refresh_live_run = build_source_refresh_live_run(
            live_gate_path=args.refresh_live_gate_output,
            output_path=args.refresh_live_run_output,
        )
        refresh_live_preflight = build_source_refresh_live_preflight(
            live_run_path=args.refresh_live_run_output,
            output_path=args.refresh_live_preflight_output,
        )
        report = run_market_simulation(
            seed_sources=["examples/seeds"],
            profile_path=args.profile,
            evidence_catalog_path=args.evidence_output,
            run_id=args.run_id,
        )
        scenario_path = write_scenario_report(report, args.scenario_output)
        verdict_path = write_verdict(report, args.verdict_output)
        rollup = build_report_rollup("reports/runs")
        dashboard_path = write_dashboard(rollup, args.dashboard_output)
        rollup_path = write_rollup(rollup, args.rollup_output)
        brief_path = write_product_brief(scenario_path, verdict_path, args.brief_output)
        print(json.dumps({
            "topics": topics_path,
            "research_plan": args.plan_output,
            "daily_scout": args.scout_output,
            "source_refresh_plan": args.refresh_plan_output,
            "source_refresh_apply": args.refresh_apply_output,
            "source_refresh_live_gate": args.refresh_live_gate_output,
            "source_refresh_live_run": args.refresh_live_run_output,
            "source_refresh_live_preflight": args.refresh_live_preflight_output,
            "evidence_catalog": args.evidence_output,
            "topic_memory": args.memory_output,
            "scenario_report": scenario_path.as_posix(),
            "verdict": verdict_path.as_posix(),
            "dashboard": dashboard_path.as_posix(),
            "rollup": rollup_path.as_posix(),
            "product_brief": brief_path.as_posix(),
            "topic_count": len(plan["plan_items"]),
            "evidence_items": len(catalog["items"]),
            "recommended_topic": scout.get("recommended_topic", {}).get("name", ""),
            "refresh_action_count": len(refresh_plan["actions"]),
            "refresh_ready_count": refresh_apply["summary"]["ready_count"],
            "refresh_blocked_count": refresh_apply["summary"]["blocked_count"],
            "live_gate_status": refresh_live_gate["status"],
            "live_run_approval_status": refresh_live_run["approval_status"],
            "live_run_status": refresh_live_run["execution"]["status"],
            "live_preflight_status": refresh_live_preflight["status"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.command == "appliance":
        if args.appliance_command == "playbook":
            path = write_runtime_playbook(args.output)
            print(json.dumps({"playbook": path.as_posix()}, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "init":
            assets = write_launchd_assets(
                project_root=args.project_root,
                output_dir=args.output_dir,
                hour=args.hour,
                minute=args.minute,
                python_bin=args.python,
            )
            print(json.dumps(assets, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "access":
            path = write_phone_access_plan(output_path=args.output, port=args.port, tailnet_host=args.tailnet_host)
            print(json.dumps({"phone_access": path.as_posix()}, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "access-verify":
            path = write_phone_access_verify(
                project_root=args.project_root,
                phone_access_path=args.phone_access,
                daily_home_path=args.daily_home,
                today_path=args.today,
                port=args.port,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "phone_access_verify": args.artifact_output,
                "phone_access_surface": path.as_posix(),
                "status": payload["status"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "decision-packet":
            path = write_operator_decision_packet(project_root=args.project_root, output_path=args.output)
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            print(json.dumps({
                "operator_decision_packet": path.as_posix(),
                "status": payload["status"],
                "decision_count": payload["summary"]["decision_count"],
                "ready_count": payload["summary"]["ready_count"],
                "blocked_count": payload["summary"]["blocked_count"],
                "host_write_performed": payload["host_write_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "decision":
            if args.decision_command == "apply":
                path = write_operator_decision_apply(
                    response=args.response,
                    project_root=args.project_root,
                    packet_path=args.packet,
                    output_path=args.output,
                )
                payload = json.loads(Path(path).read_text(encoding="utf-8"))
                print(json.dumps({
                    "operator_decision_apply": path.as_posix(),
                    "status": payload["status"],
                    "decision_id": payload["decision_id"],
                    "approval_scope": payload["approval_scope"],
                    "command_count": len(payload["commands"]),
                    "external_effect_performed": payload["external_effect_performed"],
                    "blockers": payload["blockers"],
                }, indent=2, ensure_ascii=False))
                return 0
        if args.appliance_command == "doctor":
            path = write_runtime_doctor(
                project_root=args.project_root,
                output_path=args.output,
                freshness_hours=args.freshness_hours,
                require_launchd_loaded=args.require_launchd_loaded,
            )
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            print(json.dumps({
                "runtime_doctor": path.as_posix(),
                "status": payload["status"],
                "fail_count": payload["fail_count"],
                "warn_count": payload["warn_count"],
            }, indent=2, ensure_ascii=False))
            return 1 if payload["fail_count"] else 0
        if args.appliance_command == "scheduler":
            if args.scheduler_command == "status":
                path = write_scheduler_status(project_root=args.project_root, output_path=args.output)
                payload = json.loads(Path(path).read_text(encoding="utf-8"))
                print(json.dumps({
                    "scheduler_status": path.as_posix(),
                    "status": payload["status"],
                    "loaded": payload["launchd"]["loaded"],
                    "host_write_performed": payload["host_write_performed"],
                }, indent=2, ensure_ascii=False))
                return 0
            if args.scheduler_command == "apply":
                path = write_scheduler_apply(
                    project_root=args.project_root,
                    output_path=args.output,
                    install=args.install,
                    load=args.load,
                    start_now=args.start_now,
                    unload=args.unload,
                    uninstall=args.uninstall,
                    confirm_host_write=args.confirm_host_write,
                )
                payload = json.loads(Path(path).read_text(encoding="utf-8"))
                print(json.dumps({
                    "scheduler_apply": path.as_posix(),
                    "dry_run": payload["dry_run"],
                    "host_write_performed": payload["host_write_performed"],
                    "action_count": len(payload["actions"]),
                }, indent=2, ensure_ascii=False))
                return 1 if any(action.get("status") == "failed" for action in payload["actions"]) else 0
            if args.scheduler_command == "run-once":
                path = write_scheduler_run_once(
                    project_root=args.project_root,
                    output_path=args.output,
                    timeout_seconds=args.timeout_seconds,
                )
                payload = json.loads(Path(path).read_text(encoding="utf-8"))
                print(json.dumps({
                    "scheduler_run_once": path.as_posix(),
                    "status": payload["status"],
                    "returncode": payload["returncode"],
                    "host_write_performed": payload["host_write_performed"],
                    "duration_seconds": payload["duration_seconds"],
                }, indent=2, ensure_ascii=False))
                return 0 if payload["status"] == "passed" else 1
            if args.scheduler_command == "activation-preflight":
                path = write_scheduler_activation_preflight(
                    project_root=args.project_root,
                    output_path=args.output,
                    max_proof_age_hours=args.max_proof_age_hours,
                )
                payload = json.loads(Path(path).read_text(encoding="utf-8"))
                print(json.dumps({
                    "scheduler_activation_preflight": path.as_posix(),
                    "status": payload["status"],
                    "blocker_count": len(payload["blockers"]),
                    "warning_count": len(payload["warnings"]),
                    "host_write_performed": payload["host_write_performed"],
                    "next_action": payload["next_action"],
                }, indent=2, ensure_ascii=False))
                return 0 if payload["status"] in {"ready", "already_active"} else 1
            if args.scheduler_command == "activation-verify":
                path = write_scheduler_activation_verify(
                    project_root=args.project_root,
                    output_path=args.output,
                    freshness_hours=args.freshness_hours,
                )
                payload = json.loads(Path(path).read_text(encoding="utf-8"))
                print(json.dumps({
                    "scheduler_activation_verify": path.as_posix(),
                    "status": payload["status"],
                    "blocker_count": len(payload["blockers"]),
                    "warning_count": len(payload["warnings"]),
                    "host_write_performed": payload["host_write_performed"],
                    "next_action": payload["next_action"],
                }, indent=2, ensure_ascii=False))
                return 0 if payload["status"] == "active_verified" else 1
            if args.scheduler_command == "summary":
                path = write_scheduler_operations(
                    project_root=args.project_root,
                    freshness_hours=args.freshness_hours,
                    artifact_output_path=args.artifact_output,
                    surface_output_path=args.output,
                )
                payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
                print(json.dumps({
                    "scheduler_operations": args.artifact_output,
                    "surface": path.as_posix(),
                    "status": payload["status"],
                    "operator_next_action": payload["operator_next_action"],
                    "external_effect_performed": payload["external_effect_performed"],
                    "host_write_performed": payload["host_write_performed"],
                }, indent=2, ensure_ascii=False))
                return 0 if payload["status"] != "blocked" else 1
        if args.appliance_command == "today":
            path = write_today_surface(
                scenario_path=args.scenario,
                verdict_path=args.verdict,
                memory_path=args.memory,
                evidence_path=args.evidence,
                vault_path=args.vault,
                scout_path=args.scout,
                refresh_plan_path=args.refresh_plan,
                refresh_apply_path=args.refresh_apply,
                refresh_live_gate_path=args.refresh_live_gate,
                refresh_live_run_path=args.refresh_live_run,
                refresh_live_preflight_path=args.refresh_live_preflight,
                agenda_path=args.agenda,
                agenda_surface_path=args.agenda_surface,
                source_refresh_surface_path=args.source_refresh_surface,
                pattern_radar_surface_path=args.pattern_radar_surface,
                pattern_dry_run_surface_path=args.pattern_dry_run_surface,
                run_trace_surface_path=args.run_trace_surface,
                drift_review_surface_path=args.drift_review_surface,
                brief_path=args.brief,
                output_path=args.output,
                archive_manifest_path=args.archive_manifest,
                memory_surface_path=args.memory_surface,
                journal_surface_path=args.journal_surface,
                task_queue_surface_path=args.task_queue_surface,
                task_ledger_surface_path=args.task_ledger_surface,
            )
            print(json.dumps({"today": path.as_posix()}, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "home":
            path = write_daily_operator_home(
                today_path=args.today,
                morning_path=args.morning,
                readiness_path=args.readiness,
                handoff_path=args.handoff,
                handoff_study_resolution_path=args.handoff_study_resolution,
                handoff_apply_path=args.handoff_apply,
                run_ledger_path=args.run_ledger,
                run_trace_path=args.run_trace,
                task_ledger_path=args.task_ledger,
                scheduler_operations_path=args.scheduler_operations,
                phone_access_path=args.phone_access,
                phone_access_verify_path=args.phone_access_verify,
                notification_path=args.notification,
                source_freshness_intake_path=args.source_freshness_intake,
                source_refresh_execution_brief_path=args.source_refresh_execution,
                memory_query_path=args.memory_query,
                memory_audit_path=args.memory_audit,
                learning_ledger_path=args.learning_ledger,
                pattern_radar_path=args.pattern_radar,
                pattern_dry_run_proof_path=args.pattern_dry_run_proof,
                pattern_evidence_intake_path=args.pattern_evidence_intake,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "daily_home": args.artifact_output,
                "daily_home_surface": path.as_posix(),
                "status": payload["status"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "briefing":
            path = write_daily_briefing_packet(
                daily_home_path=args.daily_home,
                today_path=args.today,
                readiness_path=args.readiness,
                run_ledger_path=args.run_ledger,
                handoff_study_resolution_path=args.handoff_study_resolution,
                learning_ledger_path=args.learning_ledger,
                memory_query_path=args.memory_query,
                notification_path=args.notification,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "daily_briefing_packet": args.artifact_output,
                "daily_briefing_surface": path.as_posix(),
                "status": payload.get("status", ""),
                "topic": payload.get("topic", ""),
                "external_effect_performed": payload.get("external_effect_performed", False),
                "host_write_performed": payload.get("host_write_performed", False),
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "handoff-study-resolution":
            path = write_handoff_study_resolution(
                handoff_path=args.handoff,
                learning_ledger_path=args.learning_ledger,
                memory_query_path=args.memory_query,
                memory_audit_path=args.memory_audit,
                source_freshness_intake_path=args.source_freshness_intake,
                analyst_council_path=args.analyst_council,
                review_prompt_path=args.review_prompt,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "handoff_study_resolution": args.artifact_output,
                "handoff_study_resolution_surface": path.as_posix(),
                "status": payload["status"],
                "resolution_item_count": payload["summary"]["resolution_item_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "agenda":
            path = write_daily_brief_agenda(
                scout_path=args.scout,
                evidence_path=args.evidence,
                memory_path=args.memory,
                vault_path=args.vault,
                refresh_plan_path=args.refresh_plan,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            print(json.dumps({
                "daily_agenda": path.as_posix(),
                "artifact": args.artifact_output,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "source-refresh":
            path = write_source_refresh_brief(
                scout_path=args.scout,
                evidence_path=args.evidence,
                refresh_plan_path=args.refresh_plan,
                refresh_apply_path=args.refresh_apply,
                refresh_live_gate_path=args.refresh_live_gate,
                refresh_live_run_path=args.refresh_live_run,
                refresh_live_preflight_path=args.refresh_live_preflight,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "source_refresh": path.as_posix(),
                "artifact": args.artifact_output,
                "status": payload["status"],
                "next_action": payload["next_action"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "source-freshness-intake":
            path = write_source_freshness_intake(
                source_refresh_brief_path=args.source_refresh_brief,
                refresh_live_gate_path=args.refresh_live_gate,
                refresh_live_run_path=args.refresh_live_run,
                refresh_live_preflight_path=args.refresh_live_preflight,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "source_freshness_intake": path.as_posix(),
                "artifact": args.artifact_output,
                "status": payload["status"],
                "next_action": payload["next_action"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "source-refresh-execution":
            path = write_source_refresh_execution_brief(
                source_refresh_brief_path=args.source_refresh_brief,
                refresh_live_gate_path=args.refresh_live_gate,
                refresh_live_run_path=args.refresh_live_run,
                refresh_live_preflight_path=args.refresh_live_preflight,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "source_refresh_execution": path.as_posix(),
                "artifact": args.artifact_output,
                "status": payload["status"],
                "preflight_status": payload["summary"]["preflight_status"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "source-refresh-response":
            live_run = build_source_refresh_live_run(
                live_gate_path=args.refresh_live_gate,
                response=args.response,
                output_path=args.refresh_live_run_output,
                evidence_output_path=args.evidence_output,
                execute=False,
                confirm_live_network=False,
            )
            preflight = build_source_refresh_live_preflight(
                live_run_path=args.refresh_live_run_output,
                output_path=args.refresh_live_preflight_output,
                intend_execute=args.intend_execute,
                confirm_live_network=args.confirm_live_network,
            )
            path = write_source_refresh_brief(
                scout_path=args.scout,
                evidence_path=args.evidence,
                refresh_plan_path=args.refresh_plan,
                refresh_apply_path=args.refresh_apply,
                refresh_live_gate_path=args.refresh_live_gate,
                refresh_live_run_path=args.refresh_live_run_output,
                refresh_live_preflight_path=args.refresh_live_preflight_output,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            execution_surface = write_source_refresh_execution_brief(
                source_refresh_brief_path=args.artifact_output,
                refresh_live_gate_path=args.refresh_live_gate,
                refresh_live_run_path=args.refresh_live_run_output,
                refresh_live_preflight_path=args.refresh_live_preflight_output,
                artifact_output_path=args.source_refresh_execution_output,
                surface_output_path=args.source_refresh_execution_surface,
            )
            brief_payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "source_refresh_response": "applied",
                "source_refresh_live_run": args.refresh_live_run_output,
                "source_refresh_live_preflight": args.refresh_live_preflight_output,
                "source_refresh": path.as_posix(),
                "source_refresh_execution": execution_surface.as_posix(),
                "source_refresh_execution_artifact": args.source_refresh_execution_output,
                "artifact": args.artifact_output,
                "approval_status": live_run["approval_status"],
                "live_run_status": live_run["execution"]["status"],
                "preflight_status": preflight["status"],
                "brief_status": brief_payload["status"],
                "external_effect_performed": False,
                "next_action": brief_payload["next_action"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "readiness":
            path = write_daily_readiness(
                project_root=args.project_root,
                freshness_hours=args.freshness_hours,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "daily_readiness": path.as_posix(),
                "artifact": args.artifact_output,
                "status": payload["status"],
                "fresh_required_count": payload["summary"]["fresh_required_count"],
                "stale_required_count": payload["summary"]["stale_required_count"],
                "missing_required_count": payload["summary"]["missing_required_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "memory":
            path = write_memory_surface(
                memory_path=args.memory,
                archive_root=args.archive_root,
                evidence_path=args.evidence,
                vault_path=args.vault,
                index_output_path=args.index_output,
                output_path=args.output,
            )
            print(json.dumps({"memory": path.as_posix(), "index": args.index_output}, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "journal":
            path = write_analyst_journal(
                scenario_path=args.scenario,
                verdict_path=args.verdict,
                memory_path=args.memory,
                evidence_path=args.evidence,
                scout_path=args.scout,
                archive_manifest_path=args.archive_manifest,
                vault_path=args.vault,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            print(json.dumps({
                "journal": path.as_posix(),
                "artifact": args.artifact_output,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "learning":
            path = write_learning_ledger(
                scenario_path=args.scenario,
                verdict_path=args.verdict,
                journal_path=args.journal,
                memory_path=args.memory,
                evidence_path=args.evidence,
                archive_root=args.archive_root,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "learning": path.as_posix(),
                "artifact": args.artifact_output,
                "status": payload["status"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "tasks":
            path = write_analyst_task_queue(
                journal_path=args.journal,
                memory_path=args.memory,
                evidence_path=args.evidence,
                scout_path=args.scout,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            print(json.dumps({
                "tasks": path.as_posix(),
                "artifact": args.artifact_output,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "task-ledger":
            path = write_analyst_task_ledger(
                task_queue_path=args.task_queue,
                previous_ledger_path=args.previous_ledger,
                status_apply_path=args.status_apply,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            print(json.dumps({
                "task_ledger": path.as_posix(),
                "artifact": args.artifact_output,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "task-response":
            path = record_task_status_response(response=args.response, responses_path=args.responses)
            print(json.dumps({
                "responses": path.as_posix(),
                "external_effect_performed": False,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "task-status-apply":
            payload = build_task_status_apply(
                ledger_path=args.ledger,
                responses_path=args.responses,
                output_path=args.output,
            )
            print(json.dumps({
                "task_status_apply": args.output,
                "applied_count": payload["applied_count"],
                "ignored_count": payload["ignored_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "review-response":
            path = record_daily_review_response(response=args.response, responses_path=args.responses)
            print(json.dumps({
                "daily_review_responses": path.as_posix(),
                "external_effect_performed": False,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "review-response-apply":
            parsed_response = parse_daily_review_response(args.response)
            responses_path = record_daily_review_response(response=args.response, responses_path=args.responses)
            written_review = write_daily_review(
                scout_path=args.scout_output,
                task_status_apply_path=args.task_status_apply,
                responses_path=responses_path,
                artifact_output_path=args.daily_review_output,
                surface_output_path=args.daily_review_surface,
            )
            scout_payload = build_daily_scout(
                topics_path=args.topics,
                plan_path=args.plan,
                evidence_path=args.evidence,
                memory_path=args.memory,
                vault_path=args.vault,
                review_path=args.daily_review_output,
                output_path=args.scout_output,
                run_id=args.run_id,
            )
            written_prompt = write_operator_review_prompt(
                scout_path=args.scout_output,
                daily_review_path=args.daily_review_output,
                artifact_output_path=args.review_prompt_output,
                surface_output_path=args.review_prompt_surface,
            )
            written_effect = write_operator_review_effect(
                scout_path=args.scout_output,
                daily_review_path=args.daily_review_output,
                review_prompt_path=args.review_prompt_output,
                artifact_output_path=args.review_effect_output,
                surface_output_path=args.review_effect_surface,
            )
            review_payload = json.loads(Path(args.daily_review_output).read_text(encoding="utf-8"))
            effect_payload = json.loads(Path(args.review_effect_output).read_text(encoding="utf-8"))
            apply_payload = {
                "schema_version": OPERATOR_REVIEW_RESPONSE_APPLY_SCHEMA_VERSION,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "applied" if effect_payload.get("status") == "applied" else "blocked",
                "operator_response": args.response,
                "parsed_response": parsed_response,
                "responses_path": Path(responses_path).as_posix(),
                "daily_review": {
                    "path": args.daily_review_output,
                    "surface": written_review.as_posix(),
                    "response_count": review_payload.get("summary", {}).get("response_count", 0),
                    "signal_count": review_payload.get("summary", {}).get("signal_count", 0),
                },
                "daily_scout": {
                    "path": args.scout_output,
                    "recommended_topic": scout_payload.get("recommended_topic", {}).get("name", ""),
                    "review_response_count": scout_payload.get("review_context", {}).get("response_count", 0),
                    "review_signal_count": scout_payload.get("review_context", {}).get("signal_count", 0),
                },
                "review_prompt": {
                    "path": args.review_prompt_output,
                    "surface": written_prompt.as_posix(),
                },
                "review_effect": {
                    "path": args.review_effect_output,
                    "surface": written_effect.as_posix(),
                    "status": effect_payload.get("status", ""),
                    "applied_topic_count": effect_payload.get("summary", {}).get("applied_topic_count", 0),
                },
                "next_action": "피드백이 scout score에 반영됐습니다. review-effect 화면에서 topic-level 증거를 확인하세요." if effect_payload.get("status") == "applied" else "응답은 기록됐지만 effect proof가 applied가 아닙니다. review-effect 화면의 다음 행동을 확인하세요.",
                "external_effect_performed": False,
                "host_write_performed": False,
                "policy": "research_only",
                "safety_boundary": [
                    "local_review_response_apply_only",
                    "does_not_fetch_live_network",
                    "does_not_send_notifications",
                    "does_not_write_host_scheduler",
                    "does_not_use_credentials",
                    "no_account_access",
                    "no_live_trading",
                ],
            }
            written_apply = write_operator_review_response_apply(
                payload=apply_payload,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            print(json.dumps({
                "review_response_apply": args.artifact_output,
                "review_response_apply_surface": written_apply.as_posix(),
                "daily_review": args.daily_review_output,
                "daily_scout": args.scout_output,
                "review_effect": args.review_effect_output,
                "effect_status": effect_payload.get("status", ""),
                "external_effect_performed": False,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "briefing-response-apply":
            parsed_response = parse_daily_review_response(args.response)
            source_packet = json.loads(Path(args.source_briefing_packet).read_text(encoding="utf-8")) if Path(args.source_briefing_packet).exists() else {}
            responses_path = record_daily_review_response(response=args.response, responses_path=args.responses)
            written_review = write_daily_review(
                scout_path=args.scout_output,
                task_status_apply_path=args.task_status_apply,
                responses_path=responses_path,
                artifact_output_path=args.daily_review_output,
                surface_output_path=args.daily_review_surface,
            )
            scout_payload = build_daily_scout(
                topics_path=args.topics,
                plan_path=args.plan,
                evidence_path=args.evidence,
                memory_path=args.memory,
                vault_path=args.vault,
                review_path=args.daily_review_output,
                output_path=args.scout_output,
                run_id=args.run_id,
            )
            written_prompt = write_operator_review_prompt(
                scout_path=args.scout_output,
                daily_review_path=args.daily_review_output,
                artifact_output_path=args.review_prompt_output,
                surface_output_path=args.review_prompt_surface,
            )
            written_effect = write_operator_review_effect(
                scout_path=args.scout_output,
                daily_review_path=args.daily_review_output,
                review_prompt_path=args.review_prompt_output,
                artifact_output_path=args.review_effect_output,
                surface_output_path=args.review_effect_surface,
            )
            written_home = write_daily_operator_home(
                scout_path=args.scout_output,
                agenda_path=args.agenda,
                today_path=args.today,
                morning_path=args.morning,
                readiness_path=args.readiness,
                handoff_path=args.handoff,
                handoff_study_resolution_path=args.handoff_study_resolution,
                handoff_apply_path=args.handoff_apply,
                run_ledger_path=args.run_ledger,
                run_trace_path=args.run_trace,
                task_ledger_path=args.task_ledger,
                scheduler_operations_path=args.scheduler_operations,
                phone_access_path=args.phone_access,
                phone_access_verify_path=args.phone_access_verify,
                notification_path=args.notification,
                source_freshness_intake_path=args.source_freshness_intake,
                source_refresh_execution_brief_path=args.source_refresh_execution,
                memory_query_path=args.memory_query,
                memory_audit_path=args.memory_audit,
                learning_ledger_path=args.learning_ledger,
                pattern_radar_path=args.pattern_radar,
                pattern_dry_run_proof_path=args.pattern_dry_run_proof,
                pattern_evidence_intake_path=args.pattern_evidence_intake,
                artifact_output_path=args.daily_home_output,
                surface_output_path=args.daily_home_surface,
            )
            written_briefing = write_daily_briefing_packet(
                daily_home_path=args.daily_home_output,
                today_path=args.today,
                readiness_path=args.readiness,
                run_ledger_path=args.run_ledger,
                handoff_study_resolution_path=args.handoff_study_resolution,
                learning_ledger_path=args.learning_ledger,
                memory_query_path=args.memory_query,
                notification_path=args.notification,
                artifact_output_path=args.briefing_packet_output,
                surface_output_path=args.briefing_packet_surface,
            )
            review_payload = json.loads(Path(args.daily_review_output).read_text(encoding="utf-8"))
            effect_payload = json.loads(Path(args.review_effect_output).read_text(encoding="utf-8"))
            home_payload = json.loads(Path(args.daily_home_output).read_text(encoding="utf-8"))
            briefing_payload = json.loads(Path(args.briefing_packet_output).read_text(encoding="utf-8"))
            status = "applied" if effect_payload.get("status") == "applied" and briefing_payload.get("schema_version") == "daily_briefing_packet.v1" else "blocked"
            apply_payload = {
                "schema_version": OPERATOR_BRIEFING_RESPONSE_APPLY_SCHEMA_VERSION,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "operator_response": args.response,
                "parsed_response": parsed_response,
                "responses_path": Path(responses_path).as_posix(),
                "source_briefing_packet": {
                    "path": args.source_briefing_packet,
                    "status": source_packet.get("status", "missing"),
                    "topic": source_packet.get("topic", ""),
                    "generated_at": source_packet.get("generated_at", ""),
                },
                "daily_review": {
                    "path": args.daily_review_output,
                    "surface": written_review.as_posix(),
                    "response_count": review_payload.get("summary", {}).get("response_count", 0),
                    "signal_count": review_payload.get("summary", {}).get("signal_count", 0),
                },
                "daily_scout": {
                    "path": args.scout_output,
                    "recommended_topic": scout_payload.get("recommended_topic", {}).get("name", ""),
                    "review_response_count": scout_payload.get("review_context", {}).get("response_count", 0),
                    "review_signal_count": scout_payload.get("review_context", {}).get("signal_count", 0),
                },
                "review_prompt": {
                    "path": args.review_prompt_output,
                    "surface": written_prompt.as_posix(),
                },
                "review_effect": {
                    "path": args.review_effect_output,
                    "surface": written_effect.as_posix(),
                    "status": effect_payload.get("status", ""),
                    "applied_topic_count": effect_payload.get("summary", {}).get("applied_topic_count", 0),
                },
                "daily_home": {
                    "path": args.daily_home_output,
                    "surface": written_home.as_posix(),
                    "status": home_payload.get("status", ""),
                    "autonomous_topic": home_payload.get("summary", {}).get("autonomous_topic", ""),
                    "action_item_count": home_payload.get("summary", {}).get("action_item_count", 0),
                },
                "daily_briefing_packet": {
                    "path": args.briefing_packet_output,
                    "surface": written_briefing.as_posix(),
                    "status": briefing_payload.get("status", ""),
                    "topic": briefing_payload.get("topic", ""),
                    "copy_ready_message_length": len(briefing_payload.get("copy_ready_message", "")),
                },
                "phone_links": {
                    "briefing": args.briefing_packet_surface,
                    "daily_home": args.daily_home_surface,
                    "review_effect": args.review_effect_surface,
                    "review_prompt": args.review_prompt_surface,
                    "daily_review": args.daily_review_surface,
                },
                "next_action": "브리핑 답장이 로컬 리뷰 기억, 주제 선택, 반영 증거, 첫 화면, 오늘 브리핑에 반영됐습니다. daily-briefing과 review-effect를 다시 확인하세요." if status == "applied" else "응답은 기록됐지만 반영 증거 또는 브리핑 검증이 막혔습니다. review-effect와 daily-briefing validator를 확인하세요.",
                "external_effect_performed": False,
                "host_write_performed": False,
                "policy": "research_only",
                "safety_boundary": [
                    "local_briefing_response_apply_only",
                    "does_not_fetch_live_network",
                    "does_not_send_notifications",
                    "does_not_write_host_scheduler",
                    "does_not_use_credentials",
                    "no_account_access",
                    "no_live_trading",
                    "no_order_execution",
                    "research_only_not_personalized_advice",
                ],
            }
            written_apply = write_operator_briefing_response_apply(
                payload=apply_payload,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            print(json.dumps({
                "briefing_response_apply": args.artifact_output,
                "briefing_response_apply_surface": written_apply.as_posix(),
                "daily_home": args.daily_home_output,
                "daily_briefing_packet": args.briefing_packet_output,
                "review_effect": args.review_effect_output,
                "status": status,
                "external_effect_performed": False,
                "host_write_performed": False,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "handoff-response-apply":
            responses_path, handoff_response = record_handoff_response(response=args.response, responses_path=args.responses)
            route = handoff_response["route"]
            route_payload: dict[str, object] = {}
            if route == "daily_review":
                review_responses_path = record_daily_review_response(
                    response=args.response,
                    responses_path=args.review_responses,
                )
                written_review = write_daily_review(
                    scout_path=args.scout_output,
                    task_status_apply_path=args.task_status_apply,
                    responses_path=review_responses_path,
                    artifact_output_path=args.daily_review_output,
                    surface_output_path=args.daily_review_surface,
                )
                scout_payload = build_daily_scout(
                    topics_path=args.topics,
                    plan_path=args.plan,
                    evidence_path=args.evidence,
                    memory_path=args.memory,
                    vault_path=args.vault,
                    review_path=args.daily_review_output,
                    output_path=args.scout_output,
                    run_id=args.run_id,
                )
                written_prompt = write_operator_review_prompt(
                    scout_path=args.scout_output,
                    daily_review_path=args.daily_review_output,
                    artifact_output_path=args.review_prompt_output,
                    surface_output_path=args.review_prompt_surface,
                )
                written_effect = write_operator_review_effect(
                    scout_path=args.scout_output,
                    daily_review_path=args.daily_review_output,
                    review_prompt_path=args.review_prompt_output,
                    artifact_output_path=args.review_effect_output,
                    surface_output_path=args.review_effect_surface,
                )
                review_payload = json.loads(Path(args.daily_review_output).read_text(encoding="utf-8"))
                effect_payload = json.loads(Path(args.review_effect_output).read_text(encoding="utf-8"))
                route_status = "applied" if effect_payload.get("status") == "applied" else "blocked"
                route_payload = {
                    "daily_review": {
                        "path": args.daily_review_output,
                        "surface": written_review.as_posix(),
                        "response_count": review_payload.get("summary", {}).get("response_count", 0),
                        "signal_count": review_payload.get("summary", {}).get("signal_count", 0),
                    },
                    "daily_scout": {
                        "path": args.scout_output,
                        "recommended_topic": scout_payload.get("recommended_topic", {}).get("name", ""),
                        "review_response_count": scout_payload.get("review_context", {}).get("response_count", 0),
                        "review_signal_count": scout_payload.get("review_context", {}).get("signal_count", 0),
                    },
                    "review_prompt": {
                        "path": args.review_prompt_output,
                        "surface": written_prompt.as_posix(),
                    },
                    "review_effect": {
                        "path": args.review_effect_output,
                        "surface": written_effect.as_posix(),
                        "status": effect_payload.get("status", ""),
                        "applied_topic_count": effect_payload.get("summary", {}).get("applied_topic_count", 0),
                    },
                }
                next_action = "handoff 응답이 review/scout/effect에 반영됐습니다. handoff와 review-effect 화면에서 확인하세요."
            else:
                task_responses_path = record_task_status_response(
                    response=args.response,
                    responses_path=args.task_responses,
                )
                task_apply_payload = build_task_status_apply(
                    ledger_path=args.task_ledger,
                    responses_path=task_responses_path,
                    output_path=args.task_status_apply,
                )
                written_task_ledger = write_analyst_task_ledger(
                    task_queue_path=args.task_queue,
                    previous_ledger_path=args.task_ledger,
                    status_apply_path=args.task_status_apply,
                    artifact_output_path=args.task_ledger,
                    surface_output_path=args.task_ledger_surface,
                )
                written_review = write_daily_review(
                    scout_path=args.scout_output,
                    task_status_apply_path=args.task_status_apply,
                    responses_path=args.review_responses,
                    artifact_output_path=args.daily_review_output,
                    surface_output_path=args.daily_review_surface,
                )
                task_ledger_payload = json.loads(Path(args.task_ledger).read_text(encoding="utf-8"))
                review_payload = json.loads(Path(args.daily_review_output).read_text(encoding="utf-8"))
                route_status = "applied" if task_apply_payload.get("applied_count", 0) > 0 else "blocked"
                route_payload = {
                    "task_status_apply": {
                        "path": args.task_status_apply,
                        "applied_count": task_apply_payload.get("applied_count", 0),
                        "ignored_count": task_apply_payload.get("ignored_count", 0),
                    },
                    "task_ledger": {
                        "path": args.task_ledger,
                        "surface": written_task_ledger.as_posix(),
                        "entry_count": task_ledger_payload.get("entry_count", 0),
                        "completed": task_ledger_payload.get("summary", {}).get("completed", 0),
                        "carried": task_ledger_payload.get("summary", {}).get("carried", 0),
                    },
                    "daily_review": {
                        "path": args.daily_review_output,
                        "surface": written_review.as_posix(),
                        "response_count": review_payload.get("summary", {}).get("response_count", 0),
                        "completed_task_count": review_payload.get("summary", {}).get("completed_task_count", 0),
                    },
                }
                next_action = "handoff task 응답이 task ledger와 daily review에 반영됐습니다. handoff와 task ledger 화면에서 확인하세요."
            written_handoff = write_daily_handoff(
                task_ledger_path=args.task_ledger,
                daily_review_path=args.daily_review_output,
                review_effect_path=args.review_effect_output,
                scout_path=args.scout_output,
                artifact_output_path=args.handoff_output,
                surface_output_path=args.handoff_surface,
            )
            handoff_payload = json.loads(Path(args.handoff_output).read_text(encoding="utf-8"))
            apply_payload: dict[str, object] = {
                "schema_version": OPERATOR_HANDOFF_RESPONSE_APPLY_SCHEMA_VERSION,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": route_status,
                "route": route,
                "operator_response": args.response,
                "handoff_response": handoff_response,
                "responses_path": Path(responses_path).as_posix(),
                "daily_handoff": {
                    "path": args.handoff_output,
                    "surface": written_handoff.as_posix(),
                    "status": handoff_payload.get("status", ""),
                    "unresolved_count": handoff_payload.get("summary", {}).get("unresolved_count", 0),
                    "copy_ready_command_count": len(handoff_payload.get("copy_ready_commands", [])),
                },
                "next_action": next_action if route_status == "applied" else f"{next_action} 단, 현재 route proof는 blocked 상태입니다.",
                "external_effect_performed": False,
                "host_write_performed": False,
                "policy": "research_only",
                "safety_boundary": [
                    "local_handoff_response_apply_only",
                    "does_not_execute_tasks",
                    "does_not_fetch_live_network",
                    "does_not_send_notifications",
                    "does_not_write_host_scheduler",
                    "does_not_use_credentials",
                    "no_account_access",
                    "no_order_execution",
                ],
            }
            apply_payload.update(route_payload)
            written_apply = write_operator_handoff_response_apply(
                payload=apply_payload,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            print(json.dumps({
                "handoff_response_apply": args.artifact_output,
                "handoff_response_apply_surface": written_apply.as_posix(),
                "route": route,
                "status": route_status,
                "daily_handoff": args.handoff_output,
                "external_effect_performed": False,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "council-response-apply":
            parsed_response = parse_daily_review_response(args.response)
            responses_path = record_daily_review_response(response=args.response, responses_path=args.responses)
            written_review = write_daily_review(
                scout_path=args.scout_output,
                task_status_apply_path=args.task_status_apply,
                responses_path=responses_path,
                artifact_output_path=args.daily_review_output,
                surface_output_path=args.daily_review_surface,
            )
            scout_payload = build_daily_scout(
                topics_path=args.topics,
                plan_path=args.plan,
                evidence_path=args.evidence,
                memory_path=args.memory,
                vault_path=args.vault,
                review_path=args.daily_review_output,
                output_path=args.scout_output,
                run_id=args.run_id,
            )
            written_prompt = write_operator_review_prompt(
                scout_path=args.scout_output,
                daily_review_path=args.daily_review_output,
                artifact_output_path=args.review_prompt_output,
                surface_output_path=args.review_prompt_surface,
            )
            written_effect = write_operator_review_effect(
                scout_path=args.scout_output,
                daily_review_path=args.daily_review_output,
                review_prompt_path=args.review_prompt_output,
                artifact_output_path=args.review_effect_output,
                surface_output_path=args.review_effect_surface,
            )
            written_council = write_analyst_council(
                scenario_path=args.scenario,
                verdict_path=args.verdict,
                journal_path=args.journal,
                memory_path=args.memory,
                evidence_path=args.evidence,
                memory_audit_path=args.memory_audit,
                scout_path=args.scout_output,
                artifact_output_path=args.council_output,
                surface_output_path=args.council_surface,
            )
            review_payload = json.loads(Path(args.daily_review_output).read_text(encoding="utf-8"))
            effect_payload = json.loads(Path(args.review_effect_output).read_text(encoding="utf-8"))
            council_payload = json.loads(Path(args.council_output).read_text(encoding="utf-8"))
            apply_payload = {
                "schema_version": OPERATOR_COUNCIL_RESPONSE_APPLY_SCHEMA_VERSION,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "applied" if effect_payload.get("status") == "applied" else "blocked",
                "operator_response": args.response,
                "parsed_response": parsed_response,
                "responses_path": Path(responses_path).as_posix(),
                "daily_review": {
                    "path": args.daily_review_output,
                    "surface": written_review.as_posix(),
                    "response_count": review_payload.get("summary", {}).get("response_count", 0),
                    "signal_count": review_payload.get("summary", {}).get("signal_count", 0),
                },
                "daily_scout": {
                    "path": args.scout_output,
                    "recommended_topic": scout_payload.get("recommended_topic", {}).get("name", ""),
                    "review_response_count": scout_payload.get("review_context", {}).get("response_count", 0),
                    "review_signal_count": scout_payload.get("review_context", {}).get("signal_count", 0),
                },
                "review_prompt": {
                    "path": args.review_prompt_output,
                    "surface": written_prompt.as_posix(),
                },
                "review_effect": {
                    "path": args.review_effect_output,
                    "surface": written_effect.as_posix(),
                    "status": effect_payload.get("status", ""),
                    "applied_topic_count": effect_payload.get("summary", {}).get("applied_topic_count", 0),
                },
                "analyst_council": {
                    "path": args.council_output,
                    "surface": written_council.as_posix(),
                    "status": council_payload.get("status", ""),
                    "role_count": council_payload.get("summary", {}).get("role_count", 0),
                    "caution_count": council_payload.get("summary", {}).get("caution_count", 0),
                    "blocker_count": council_payload.get("summary", {}).get("blocker_count", 0),
                },
                "next_action": "council 응답이 review/scout/effect/council proof에 반영됐습니다. council과 review-effect 화면에서 반영 상태를 확인하세요." if effect_payload.get("status") == "applied" else "응답은 기록됐지만 effect proof가 applied가 아닙니다. review-effect와 council 화면의 다음 행동을 확인하세요.",
                "external_effect_performed": False,
                "host_write_performed": False,
                "policy": "research_only",
                "safety_boundary": [
                    "local_council_response_apply_only",
                    "does_not_fetch_live_network",
                    "does_not_send_notifications",
                    "does_not_write_host_scheduler",
                    "does_not_use_credentials",
                    "no_account_access",
                    "no_order_execution",
                ],
            }
            written_apply = write_operator_council_response_apply(
                payload=apply_payload,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            print(json.dumps({
                "council_response_apply": args.artifact_output,
                "council_response_apply_surface": written_apply.as_posix(),
                "daily_review": args.daily_review_output,
                "daily_scout": args.scout_output,
                "review_effect": args.review_effect_output,
                "analyst_council": args.council_output,
                "council_status": council_payload.get("status", ""),
                "effect_status": effect_payload.get("status", ""),
                "external_effect_performed": False,
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "review":
            path = write_daily_review(
                scout_path=args.scout,
                task_status_apply_path=args.task_status_apply,
                responses_path=args.responses,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "daily_review": args.artifact_output,
                "daily_review_surface": path.as_posix(),
                "response_count": payload["summary"]["response_count"],
                "signal_count": payload["summary"]["signal_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "review-prompt":
            path = write_operator_review_prompt(
                scout_path=args.scout,
                daily_review_path=args.daily_review,
                drift_review_path=args.drift_review,
                task_ledger_path=args.task_ledger,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "review_prompt": args.artifact_output,
                "review_prompt_surface": path.as_posix(),
                "prompt_count": payload["summary"]["prompt_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "review-effect":
            path = write_operator_review_effect(
                scout_path=args.scout,
                daily_review_path=args.daily_review,
                review_prompt_path=args.review_prompt,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "review_effect": args.artifact_output,
                "review_effect_surface": path.as_posix(),
                "status": payload["status"],
                "applied_topic_count": payload["summary"]["applied_topic_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "pattern-radar":
            path = write_agent_pattern_radar(
                playbook_path=args.playbook,
                pattern_proof_path=args.pattern_proof,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "agent_pattern_radar": args.artifact_output,
                "agent_pattern_radar_surface": path.as_posix(),
                "case_count": payload["summary"]["case_count"],
                "adopted_count": payload["summary"]["adopted_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "pattern-evidence-intake":
            path = write_pattern_evidence_intake(
                pattern_radar_path=args.pattern_radar,
                pattern_proof_path=args.pattern_proof,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "pattern_evidence_intake": args.artifact_output,
                "pattern_evidence_intake_surface": path.as_posix(),
                "status": payload["status"],
                "local_candidate_count": payload["summary"]["local_candidate_count"],
                "already_verified_count": payload["summary"]["already_verified_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "pattern-dry-run":
            path = write_pattern_dry_run_proof(
                pattern_radar_path=args.pattern_radar,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "pattern_dry_run_proof": args.artifact_output,
                "pattern_dry_run_proof_surface": path.as_posix(),
                "status": payload["status"],
                "passed_count": payload["summary"]["passed_count"],
                "approval_required_count": payload["summary"]["approval_required_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "trace":
            path = write_run_trace(
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "run_trace": args.artifact_output,
                "run_trace_surface": path.as_posix(),
                "status": payload["status"],
                "step_count": payload["summary"]["step_count"],
                "missing_required_count": payload["summary"]["missing_required_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "run-ledger":
            path = write_daily_run_ledger(
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
                archive_manifest_path=args.archive_manifest,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "daily_run_ledger": args.artifact_output,
                "daily_run_ledger_surface": path.as_posix(),
                "status": payload["status"],
                "today_run_count": payload["summary"]["today_run_count"],
                "duplicate_today_count": payload["summary"]["duplicate_today_count"],
                "canonical_entry_id": payload["canonical_entry_id"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "handoff":
            path = write_daily_handoff(
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "daily_handoff": args.artifact_output,
                "daily_handoff_surface": path.as_posix(),
                "status": payload["status"],
                "carried_item_count": payload["summary"]["carried_item_count"],
                "unresolved_count": payload["summary"]["unresolved_count"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "drift-review":
            path = write_drift_review(
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "drift_review": args.artifact_output,
                "drift_review_surface": path.as_posix(),
                "status": payload["status"],
                "recommended_branch": payload["decision"]["recommended_branch"],
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "morning":
            path = write_morning_control_packet(
                scout_path=args.scout,
                journal_path=args.journal,
                task_queue_path=args.task_queue,
                task_ledger_path=args.task_ledger,
                refresh_live_gate_path=args.refresh_live_gate,
                refresh_live_run_path=args.refresh_live_run,
                refresh_live_preflight_path=args.refresh_live_preflight,
                notification_path=args.notification,
                runtime_doctor_path=args.runtime_doctor,
                scheduler_surface_path=args.scheduler_surface,
                source_refresh_surface_path=args.source_refresh_surface,
                pattern_radar_surface_path=args.pattern_radar_surface,
                run_trace_surface_path=args.run_trace_surface,
                run_ledger_surface_path=args.run_ledger_surface,
                handoff_surface_path=args.handoff_surface,
                handoff_apply_surface_path=args.handoff_apply_surface,
                drift_review_surface_path=args.drift_review_surface,
                analyst_council_surface_path=args.analyst_council_surface,
                memory_query_surface_path=args.memory_query_surface,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            payload = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "morning": path.as_posix(),
                "artifact": args.artifact_output,
                "status": payload["status"],
                "pending_decision_count": len(payload["pending_decisions"]),
                "external_effect_performed": payload["external_effect_performed"],
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "query":
            path = write_memory_query(
                query=args.query,
                memory_path=args.memory,
                archive_root=args.archive_root,
                evidence_path=args.evidence,
                vault_path=args.vault,
                output_path=args.output,
                surface_path=args.surface_output,
                limit=args.limit,
            )
            print(json.dumps({
                "query": args.query,
                "query_artifact": args.output,
                "query_surface": path.as_posix(),
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "audit":
            path = write_memory_audit(
                memory_path=args.memory,
                archive_root=args.archive_root,
                evidence_path=args.evidence,
                vault_path=args.vault,
                daily_review_path=args.daily_review,
                output_path=args.output,
                surface_path=args.surface_output,
            )
            artifact = json.loads(Path(args.output).read_text(encoding="utf-8"))
            print(json.dumps({
                "memory_audit": args.output,
                "memory_audit_surface": path.as_posix(),
                "status": artifact.get("status", ""),
                "risk_count": artifact.get("summary", {}).get("risk_count", 0),
                "external_effect_performed": artifact.get("external_effect_performed", False),
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "council":
            path = write_analyst_council(
                scenario_path=args.scenario,
                verdict_path=args.verdict,
                journal_path=args.journal,
                memory_path=args.memory,
                evidence_path=args.evidence,
                memory_audit_path=args.memory_audit,
                scout_path=args.scout,
                artifact_output_path=args.artifact_output,
                surface_output_path=args.output,
            )
            artifact = json.loads(Path(args.artifact_output).read_text(encoding="utf-8"))
            print(json.dumps({
                "analyst_council": args.artifact_output,
                "analyst_council_surface": path.as_posix(),
                "status": artifact.get("status", ""),
                "role_count": artifact.get("summary", {}).get("role_count", 0),
                "blocker_count": artifact.get("summary", {}).get("blocker_count", 0),
                "external_effect_performed": artifact.get("external_effect_performed", False),
            }, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "notify":
            path = write_notification_payload(
                provider=args.provider,
                today_url=args.today_url,
                today_path=args.today,
                scenario_path=args.scenario,
                verdict_path=args.verdict,
                briefing_packet_path=args.briefing_packet,
                output_path=args.output,
                dry_run=not args.send,
            )
            result = {"notification": path.as_posix(), "dry_run": not args.send}
            if args.send:
                result["send_result"] = send_notification_payload(path).get("send_result", {})
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "vault":
            if args.vault_command == "init":
                payload = init_knowledge_vault(root=args.root)
                print(json.dumps(payload, indent=2, ensure_ascii=False))
                return 0
            if args.vault_command == "compile":
                payload = compile_knowledge_vault(
                    raw_dir=args.raw_dir,
                    wiki_dir=args.wiki_dir,
                    output_path=args.output,
                    surface_path=args.surface_output,
                    topics_path=args.topics,
                )
                print(json.dumps({
                    "vault_compile": args.output,
                    "surface": args.surface_output,
                    "compiled_count": payload["compiled_count"],
                    "topic_count": payload["topic_count"],
                    "policy": payload["policy"],
                }, indent=2, ensure_ascii=False))
                return 0
        if args.appliance_command == "run":
            topics_path = args.topics
            if not Path(topics_path).exists():
                init_topic_config(topics_path)
            plan_path = DEFAULT_RESEARCH_PLAN_OUTPUT
            scout_path = Path(args.scout_output)
            refresh_plan_path = Path(args.refresh_plan_output)
            refresh_apply_path = Path(args.refresh_apply_output)
            refresh_live_gate_path = Path(args.refresh_live_gate_output)
            refresh_live_run_path = Path(args.refresh_live_run_output)
            refresh_live_preflight_path = Path(args.refresh_live_preflight_output)
            evidence_path = DEFAULT_DAILY_EVIDENCE_OUTPUT
            memory_path = DEFAULT_TOPIC_MEMORY_OUTPUT
            scenario_path = Path("reports/scenarios/daily-research-sim.json")
            verdict_path = Path("reports/scenarios/daily-research-verdict.json")
            dashboard_path = Path("reports/dashboard.html")
            rollup_path = Path("reports/report-rollup.json")
            brief_path = Path("reports/product/market-brief.html")
            today_path = DEFAULT_TODAY_OUTPUT
            memory_surface_path = DEFAULT_MEMORY_OUTPUT
            journal_path = DEFAULT_ANALYST_JOURNAL_OUTPUT
            journal_artifact_path = DEFAULT_ANALYST_JOURNAL_ARTIFACT
            learning_ledger_path = DEFAULT_LEARNING_LEDGER_SURFACE
            learning_ledger_artifact_path = DEFAULT_LEARNING_LEDGER_OUTPUT
            task_queue_path = DEFAULT_ANALYST_TASK_QUEUE_OUTPUT
            task_queue_artifact_path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT
            task_ledger_path = DEFAULT_ANALYST_TASK_LEDGER_OUTPUT
            task_ledger_artifact_path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT
            task_status_apply_path = DEFAULT_ANALYST_TASK_STATUS_APPLY
            morning_path = DEFAULT_MORNING_CONTROL_SURFACE
            morning_artifact_path = DEFAULT_MORNING_CONTROL_OUTPUT
            agenda_artifact_path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT
            agenda_surface_path = DEFAULT_DAILY_BRIEF_AGENDA_SURFACE
            review_artifact_path = DEFAULT_DAILY_REVIEW_OUTPUT
            review_surface_path = DEFAULT_DAILY_REVIEW_SURFACE
            review_prompt_artifact_path = DEFAULT_REVIEW_PROMPT_OUTPUT
            review_prompt_surface_path = DEFAULT_REVIEW_PROMPT_SURFACE
            review_effect_artifact_path = DEFAULT_REVIEW_EFFECT_OUTPUT
            review_effect_surface_path = DEFAULT_REVIEW_EFFECT_SURFACE
            pattern_radar_artifact_path = DEFAULT_AGENT_PATTERN_RADAR_OUTPUT
            pattern_radar_surface_path = DEFAULT_AGENT_PATTERN_RADAR_SURFACE
            pattern_evidence_artifact_path = DEFAULT_PATTERN_EVIDENCE_INTAKE_OUTPUT
            pattern_evidence_surface_path = DEFAULT_PATTERN_EVIDENCE_INTAKE_SURFACE
            pattern_proof_artifact_path = DEFAULT_PATTERN_DRY_RUN_PROOF_OUTPUT
            pattern_proof_surface_path = DEFAULT_PATTERN_DRY_RUN_PROOF_SURFACE
            run_trace_artifact_path = DEFAULT_RUN_TRACE_OUTPUT
            run_trace_surface_path = DEFAULT_RUN_TRACE_SURFACE
            run_ledger_artifact_path = DEFAULT_DAILY_RUN_LEDGER_OUTPUT
            run_ledger_surface_path = DEFAULT_DAILY_RUN_LEDGER_SURFACE
            handoff_artifact_path = DEFAULT_DAILY_HANDOFF_OUTPUT
            handoff_surface_path = DEFAULT_DAILY_HANDOFF_SURFACE
            handoff_resolution_artifact_path = DEFAULT_HANDOFF_STUDY_RESOLUTION_OUTPUT
            handoff_resolution_surface_path = DEFAULT_HANDOFF_STUDY_RESOLUTION_SURFACE
            drift_review_artifact_path = DEFAULT_DRIFT_REVIEW_OUTPUT
            drift_review_surface_path = DEFAULT_DRIFT_REVIEW_SURFACE
            readiness_artifact_path = DEFAULT_DAILY_READINESS_OUTPUT
            readiness_surface_path = DEFAULT_DAILY_READINESS_SURFACE
            source_refresh_brief_artifact_path = DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT
            source_refresh_brief_surface_path = DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE
            source_freshness_intake_artifact_path = DEFAULT_SOURCE_FRESHNESS_INTAKE_OUTPUT
            source_freshness_intake_surface_path = DEFAULT_SOURCE_FRESHNESS_INTAKE_SURFACE
            source_refresh_execution_artifact_path = DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_OUTPUT
            source_refresh_execution_surface_path = DEFAULT_SOURCE_REFRESH_EXECUTION_BRIEF_SURFACE
            scheduler_operations_artifact_path = DEFAULT_SCHEDULER_OPERATIONS_OUTPUT
            scheduler_operations_surface_path = DEFAULT_SCHEDULER_OPERATIONS_SURFACE
            daily_home_artifact_path = DEFAULT_DAILY_HOME_OUTPUT
            daily_home_surface_path = DEFAULT_DAILY_HOME_SURFACE
            briefing_packet_artifact_path = Path(args.briefing_packet_output)
            briefing_packet_surface_path = Path(args.briefing_packet_surface)
            phone_access_verify_artifact_path = DEFAULT_PHONE_ACCESS_VERIFY_OUTPUT
            phone_access_verify_surface_path = DEFAULT_PHONE_ACCESS_VERIFY_SURFACE
            memory_query_artifact_path = DEFAULT_MEMORY_QUERY_OUTPUT
            memory_query_surface_path = DEFAULT_MEMORY_QUERY_SURFACE
            memory_audit_artifact_path = DEFAULT_MEMORY_AUDIT_OUTPUT
            memory_audit_surface_path = DEFAULT_MEMORY_AUDIT_SURFACE
            analyst_council_artifact_path = DEFAULT_ANALYST_COUNCIL_OUTPUT
            analyst_council_surface_path = DEFAULT_ANALYST_COUNCIL_SURFACE
            vault_compile_path = Path(args.vault_output)
            vault_surface_path = Path(args.vault_surface_output)
            playbook_path = write_runtime_playbook(args.playbook_output)
            phone_access_path = write_phone_access_plan(output_path=DEFAULT_PHONE_ACCESS_OUTPUT)
            written_pattern_radar = write_agent_pattern_radar(
                playbook_path=playbook_path,
                pattern_proof_path=pattern_proof_artifact_path,
                artifact_output_path=pattern_radar_artifact_path,
                surface_output_path=pattern_radar_surface_path,
            )
            written_pattern_evidence = write_pattern_evidence_intake(
                pattern_radar_path=pattern_radar_artifact_path,
                pattern_proof_path=pattern_proof_artifact_path,
                artifact_output_path=pattern_evidence_artifact_path,
                surface_output_path=pattern_evidence_surface_path,
            )
            vault_compile = None
            if not args.skip_vault_compile and Path(args.vault_raw_dir).exists():
                vault_compile = compile_knowledge_vault(
                    raw_dir=args.vault_raw_dir,
                    wiki_dir=args.vault_wiki_dir,
                    output_path=vault_compile_path,
                    surface_path=vault_surface_path,
                    topics_path=topics_path,
                )
            active_vault_path = vault_compile_path if vault_compile_path.exists() else DEFAULT_VAULT_COMPILE_OUTPUT
            active_vault_surface = vault_surface_path if vault_surface_path.exists() else DEFAULT_VAULT_SURFACE_OUTPUT
            plan = build_research_plan(topics_path=topics_path, output_path=plan_path, run_id=args.run_id)
            catalog = collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=evidence_path,
                memory_path=memory_path,
                source_ids=args.source,
            )
            scout = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=active_vault_path,
                review_path=review_artifact_path,
                output_path=scout_path,
                run_id=args.run_id,
            )
            refresh_plan = build_source_refresh_plan(
                scout_path=scout_path,
                evidence_path=evidence_path,
                vault_path=active_vault_path,
                output_path=refresh_plan_path,
            )
            refresh_apply = build_source_refresh_apply(
                refresh_plan_path=refresh_plan_path,
                output_path=refresh_apply_path,
            )
            refresh_live_gate = build_source_refresh_live_gate(
                refresh_apply_path=refresh_apply_path,
                output_path=refresh_live_gate_path,
            )
            refresh_live_run = build_source_refresh_live_run(
                live_gate_path=refresh_live_gate_path,
                output_path=refresh_live_run_path,
            )
            refresh_live_preflight = build_source_refresh_live_preflight(
                live_run_path=refresh_live_run_path,
                output_path=refresh_live_preflight_path,
            )
            written_source_refresh_brief = write_source_refresh_brief(
                scout_path=scout_path,
                evidence_path=evidence_path,
                refresh_plan_path=refresh_plan_path,
                refresh_apply_path=refresh_apply_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                artifact_output_path=source_refresh_brief_artifact_path,
                surface_output_path=source_refresh_brief_surface_path,
            )
            written_source_freshness_intake = write_source_freshness_intake(
                source_refresh_brief_path=source_refresh_brief_artifact_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                artifact_output_path=source_freshness_intake_artifact_path,
                surface_output_path=source_freshness_intake_surface_path,
            )
            written_source_refresh_execution = write_source_refresh_execution_brief(
                source_refresh_brief_path=source_refresh_brief_artifact_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                artifact_output_path=source_refresh_execution_artifact_path,
                surface_output_path=source_refresh_execution_surface_path,
            )
            written_agenda = write_daily_brief_agenda(
                scout_path=scout_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=active_vault_path,
                refresh_plan_path=refresh_plan_path,
                artifact_output_path=agenda_artifact_path,
                surface_output_path=agenda_surface_path,
            )
            report = run_market_simulation(
                seed_sources=["examples/seeds"],
                profile_path=args.profile,
                evidence_catalog_path=evidence_path,
                run_id=args.run_id,
            )
            written_scenario = write_scenario_report(report, scenario_path)
            written_verdict = write_verdict(report, verdict_path)
            rollup = build_report_rollup("reports/runs")
            written_dashboard = write_dashboard(rollup, dashboard_path)
            written_rollup = write_rollup(rollup, rollup_path)
            written_brief = write_product_brief(written_scenario, written_verdict, brief_path)
            provisional_journal = write_analyst_journal(
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                memory_path=memory_path,
                evidence_path=evidence_path,
                scout_path=scout_path,
                vault_path=active_vault_path,
                artifact_output_path=journal_artifact_path,
                surface_output_path=journal_path,
            )
            provisional_learning = write_learning_ledger(
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                journal_path=journal_artifact_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                archive_root=args.archive_root,
                artifact_output_path=learning_ledger_artifact_path,
                surface_output_path=learning_ledger_path,
            )
            provisional_task_queue = write_analyst_task_queue(
                journal_path=journal_artifact_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                scout_path=scout_path,
                artifact_output_path=task_queue_artifact_path,
                surface_output_path=task_queue_path,
            )
            provisional_task_ledger = write_analyst_task_ledger(
                task_queue_path=task_queue_artifact_path,
                previous_ledger_path=task_ledger_artifact_path,
                status_apply_path=task_status_apply_path,
                artifact_output_path=task_ledger_artifact_path,
                surface_output_path=task_ledger_path,
            )
            provisional_review = write_daily_review(
                scout_path=scout_path,
                task_status_apply_path=task_status_apply_path,
                artifact_output_path=review_artifact_path,
                surface_output_path=review_surface_path,
            )
            provisional_review_prompt = write_operator_review_prompt(
                scout_path=scout_path,
                daily_review_path=review_artifact_path,
                drift_review_path=drift_review_artifact_path,
                task_ledger_path=task_ledger_artifact_path,
                artifact_output_path=review_prompt_artifact_path,
                surface_output_path=review_prompt_surface_path,
            )
            provisional_review_effect = write_operator_review_effect(
                scout_path=scout_path,
                daily_review_path=review_artifact_path,
                review_prompt_path=review_prompt_artifact_path,
                artifact_output_path=review_effect_artifact_path,
                surface_output_path=review_effect_surface_path,
            )
            provisional_today = write_today_surface(
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                memory_path=memory_path,
                evidence_path=evidence_path,
                vault_path=active_vault_path,
                scout_path=scout_path,
                refresh_plan_path=refresh_plan_path,
                refresh_apply_path=refresh_apply_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                agenda_path=agenda_artifact_path,
                agenda_surface_path=written_agenda,
                source_refresh_surface_path=written_source_refresh_brief,
                review_surface_path=provisional_review,
                review_prompt_surface_path=provisional_review_prompt,
                review_effect_surface_path=provisional_review_effect,
                pattern_radar_surface_path=written_pattern_radar,
                run_trace_surface_path=run_trace_surface_path,
                drift_review_surface_path=drift_review_surface_path,
                brief_path=written_brief,
                output_path=today_path,
                journal_surface_path=provisional_journal,
                task_queue_surface_path=provisional_task_queue,
                task_ledger_surface_path=provisional_task_ledger,
            )
            archive_manifest = archive_daily_run(
                run_id=args.run_id,
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                evidence_path=evidence_path,
                memory_path=memory_path,
                brief_path=written_brief,
                today_path=provisional_today,
                refresh_plan_path=refresh_plan_path,
                refresh_apply_path=refresh_apply_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                journal_path=provisional_journal,
                task_queue_path=provisional_task_queue,
                task_ledger_path=provisional_task_ledger,
                daily_review_path=review_artifact_path,
                daily_review_surface_path=provisional_review,
                learning_ledger_path=learning_ledger_artifact_path,
                learning_ledger_surface_path=provisional_learning,
                review_prompt_path=review_prompt_artifact_path,
                review_prompt_surface_path=provisional_review_prompt,
                review_effect_path=review_effect_artifact_path,
                review_effect_surface_path=provisional_review_effect,
                pattern_radar_path=pattern_radar_artifact_path,
                pattern_radar_surface_path=written_pattern_radar,
                run_trace_path=run_trace_artifact_path,
                run_trace_surface_path=run_trace_surface_path,
                drift_review_path=drift_review_artifact_path,
                drift_review_surface_path=drift_review_surface_path,
                vault_compile_path=active_vault_path,
                vault_surface_path=active_vault_surface,
                agenda_path=agenda_artifact_path,
                agenda_surface_path=written_agenda,
                archive_root=args.archive_root,
            )
            written_memory = write_memory_surface(
                memory_path=memory_path,
                archive_root=args.archive_root,
                evidence_path=evidence_path,
                vault_path=active_vault_path,
                index_output_path=DEFAULT_MEMORY_INDEX_OUTPUT,
                output_path=memory_surface_path,
            )
            written_memory_audit = write_memory_audit(
                memory_path=memory_path,
                archive_root=args.archive_root,
                evidence_path=evidence_path,
                vault_path=active_vault_path,
                daily_review_path=review_artifact_path,
                output_path=memory_audit_artifact_path,
                surface_path=memory_audit_surface_path,
            )
            recall_query = scout.get("recommended_topic", {}).get("name") or scout.get("recommendations", [{}])[0].get("name", "today brief")
            written_memory_query = write_memory_query(
                query=recall_query,
                memory_path=memory_path,
                archive_root=args.archive_root,
                evidence_path=evidence_path,
                vault_path=active_vault_path,
                output_path=memory_query_artifact_path,
                surface_path=memory_query_surface_path,
            )
            written_journal = write_analyst_journal(
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                memory_path=memory_path,
                evidence_path=evidence_path,
                scout_path=scout_path,
                archive_manifest_path=archive_manifest,
                vault_path=active_vault_path,
                artifact_output_path=journal_artifact_path,
                surface_output_path=journal_path,
            )
            written_learning = write_learning_ledger(
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                journal_path=journal_artifact_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                archive_root=args.archive_root,
                artifact_output_path=learning_ledger_artifact_path,
                surface_output_path=learning_ledger_path,
            )
            written_analyst_council = write_analyst_council(
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                journal_path=journal_artifact_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                memory_audit_path=memory_audit_artifact_path,
                scout_path=scout_path,
                artifact_output_path=analyst_council_artifact_path,
                surface_output_path=analyst_council_surface_path,
            )
            written_task_queue = write_analyst_task_queue(
                journal_path=journal_artifact_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                scout_path=scout_path,
                artifact_output_path=task_queue_artifact_path,
                surface_output_path=task_queue_path,
            )
            written_task_ledger = write_analyst_task_ledger(
                task_queue_path=task_queue_artifact_path,
                previous_ledger_path=task_ledger_artifact_path,
                status_apply_path=task_status_apply_path,
                artifact_output_path=task_ledger_artifact_path,
                surface_output_path=task_ledger_path,
            )
            written_review = write_daily_review(
                scout_path=scout_path,
                task_status_apply_path=task_status_apply_path,
                artifact_output_path=review_artifact_path,
                surface_output_path=review_surface_path,
            )
            written_review_prompt = write_operator_review_prompt(
                scout_path=scout_path,
                daily_review_path=review_artifact_path,
                drift_review_path=drift_review_artifact_path,
                task_ledger_path=task_ledger_artifact_path,
                artifact_output_path=review_prompt_artifact_path,
                surface_output_path=review_prompt_surface_path,
            )
            written_review_effect = write_operator_review_effect(
                scout_path=scout_path,
                daily_review_path=review_artifact_path,
                review_prompt_path=review_prompt_artifact_path,
                artifact_output_path=review_effect_artifact_path,
                surface_output_path=review_effect_surface_path,
            )
            written_today = write_today_surface(
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                memory_path=memory_path,
                evidence_path=evidence_path,
                vault_path=active_vault_path,
                scout_path=scout_path,
                refresh_plan_path=refresh_plan_path,
                refresh_apply_path=refresh_apply_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                agenda_path=agenda_artifact_path,
                agenda_surface_path=written_agenda,
                source_refresh_surface_path=written_source_refresh_brief,
                review_surface_path=written_review,
                review_prompt_surface_path=written_review_prompt,
                review_effect_surface_path=written_review_effect,
                pattern_radar_surface_path=written_pattern_radar,
                run_trace_surface_path=run_trace_surface_path,
                drift_review_surface_path=drift_review_surface_path,
                brief_path=written_brief,
                output_path=today_path,
                archive_manifest_path=archive_manifest,
                memory_surface_path=written_memory,
                journal_surface_path=written_journal,
                task_queue_surface_path=written_task_queue,
                task_ledger_surface_path=written_task_ledger,
            )
            notification_path = write_notification_payload(
                provider=args.notification_provider,
                today_url=args.today_url,
                today_path=written_today,
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                dry_run=not args.send,
            )
            notification_status = "pending_packet_rewrite" if args.send else "dry_run_ready"
            write_scheduler_status(project_root=".", output_path=DEFAULT_SCHEDULER_STATUS_OUTPUT)
            written_scheduler_operations = write_scheduler_operations(
                project_root=".",
                artifact_output_path=scheduler_operations_artifact_path,
                surface_output_path=scheduler_operations_surface_path,
            )
            written_run_trace = write_run_trace(
                artifact_output_path=run_trace_artifact_path,
                surface_output_path=run_trace_surface_path,
                today_path=written_today,
                pattern_evidence_intake_path=pattern_evidence_artifact_path,
                source_freshness_intake_path=source_freshness_intake_artifact_path,
                source_refresh_execution_brief_path=source_refresh_execution_artifact_path,
                review_prompt_path=review_prompt_artifact_path,
                review_effect_path=review_effect_artifact_path,
                analyst_council_path=analyst_council_artifact_path,
                memory_query_path=memory_query_artifact_path,
                memory_audit_path=memory_audit_artifact_path,
                learning_ledger_path=learning_ledger_artifact_path,
                handoff_study_resolution_path=handoff_resolution_artifact_path,
                scheduler_operations_path=scheduler_operations_artifact_path,
            )
            written_pattern_proof = write_pattern_dry_run_proof(
                pattern_radar_path=pattern_radar_artifact_path,
                artifact_output_path=pattern_proof_artifact_path,
                surface_output_path=pattern_proof_surface_path,
            )
            written_pattern_evidence = write_pattern_evidence_intake(
                pattern_radar_path=pattern_radar_artifact_path,
                pattern_proof_path=pattern_proof_artifact_path,
                artifact_output_path=pattern_evidence_artifact_path,
                surface_output_path=pattern_evidence_surface_path,
            )
            written_drift_review = write_drift_review(
                artifact_output_path=drift_review_artifact_path,
                surface_output_path=drift_review_surface_path,
                run_trace_path=run_trace_artifact_path,
                pattern_radar_path=pattern_radar_artifact_path,
                source_refresh_brief_path=source_refresh_brief_artifact_path,
                task_ledger_path=task_ledger_artifact_path,
                daily_review_path=review_artifact_path,
            )
            written_morning = write_morning_control_packet(
                scout_path=scout_path,
                journal_path=journal_artifact_path,
                task_queue_path=task_queue_artifact_path,
                task_ledger_path=task_ledger_artifact_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                notification_path=notification_path,
                runtime_doctor_path=DEFAULT_RUNTIME_DOCTOR_OUTPUT,
                readiness_surface_path=readiness_surface_path,
                scheduler_surface_path=written_scheduler_operations,
                source_refresh_surface_path=written_source_refresh_brief,
                agenda_path=agenda_artifact_path,
                agenda_surface_path=written_agenda,
                review_surface_path=written_review,
                review_prompt_surface_path=written_review_prompt,
                review_effect_surface_path=written_review_effect,
                analyst_council_surface_path=written_analyst_council,
                memory_query_surface_path=written_memory_query,
                memory_audit_surface_path=written_memory_audit,
                pattern_radar_surface_path=written_pattern_radar,
                pattern_dry_run_surface_path=written_pattern_proof,
                run_trace_surface_path=written_run_trace,
                run_ledger_surface_path=run_ledger_surface_path,
                handoff_surface_path=handoff_surface_path,
                drift_review_surface_path=written_drift_review,
                artifact_output_path=morning_artifact_path,
                surface_output_path=morning_path,
            )
            written_readiness = write_daily_readiness(
                project_root=".",
                artifact_output_path=readiness_artifact_path,
                surface_output_path=readiness_surface_path,
            )
            written_drift_review = write_drift_review(
                artifact_output_path=drift_review_artifact_path,
                surface_output_path=drift_review_surface_path,
                run_trace_path=run_trace_artifact_path,
                pattern_radar_path=pattern_radar_artifact_path,
                readiness_path=readiness_artifact_path,
                source_refresh_brief_path=source_refresh_brief_artifact_path,
                task_ledger_path=task_ledger_artifact_path,
                daily_review_path=review_artifact_path,
            )
            written_review_prompt = write_operator_review_prompt(
                scout_path=scout_path,
                daily_review_path=review_artifact_path,
                drift_review_path=drift_review_artifact_path,
                task_ledger_path=task_ledger_artifact_path,
                artifact_output_path=review_prompt_artifact_path,
                surface_output_path=review_prompt_surface_path,
            )
            written_review_effect = write_operator_review_effect(
                scout_path=scout_path,
                daily_review_path=review_artifact_path,
                review_prompt_path=review_prompt_artifact_path,
                artifact_output_path=review_effect_artifact_path,
                surface_output_path=review_effect_surface_path,
            )
            written_run_ledger = write_daily_run_ledger(
                artifact_output_path=run_ledger_artifact_path,
                surface_output_path=run_ledger_surface_path,
                run_trace_path=run_trace_artifact_path,
                morning_path=morning_artifact_path,
                readiness_path=readiness_artifact_path,
                scheduler_operations_path=scheduler_operations_artifact_path,
                archive_manifest_path=archive_manifest,
            )
            written_handoff = write_daily_handoff(
                artifact_output_path=handoff_artifact_path,
                surface_output_path=handoff_surface_path,
                run_ledger_path=run_ledger_artifact_path,
                journal_path=journal_artifact_path,
                task_ledger_path=task_ledger_artifact_path,
                daily_review_path=review_artifact_path,
                review_effect_path=review_effect_artifact_path,
                analyst_council_path=analyst_council_artifact_path,
                memory_audit_path=memory_audit_artifact_path,
                scout_path=scout_path,
            )
            written_handoff_resolution = write_handoff_study_resolution(
                artifact_output_path=handoff_resolution_artifact_path,
                surface_output_path=handoff_resolution_surface_path,
                handoff_path=handoff_artifact_path,
                learning_ledger_path=learning_ledger_artifact_path,
                memory_query_path=memory_query_artifact_path,
                memory_audit_path=memory_audit_artifact_path,
                source_freshness_intake_path=source_freshness_intake_artifact_path,
                analyst_council_path=analyst_council_artifact_path,
                review_prompt_path=review_prompt_artifact_path,
            )
            written_run_trace = write_run_trace(
                artifact_output_path=run_trace_artifact_path,
                surface_output_path=run_trace_surface_path,
                today_path=written_today,
                pattern_evidence_intake_path=pattern_evidence_artifact_path,
                source_freshness_intake_path=source_freshness_intake_artifact_path,
                source_refresh_execution_brief_path=source_refresh_execution_artifact_path,
                review_prompt_path=review_prompt_artifact_path,
                review_effect_path=review_effect_artifact_path,
                analyst_council_path=analyst_council_artifact_path,
                memory_query_path=memory_query_artifact_path,
                memory_audit_path=memory_audit_artifact_path,
                learning_ledger_path=learning_ledger_artifact_path,
                handoff_study_resolution_path=handoff_resolution_artifact_path,
                scheduler_operations_path=scheduler_operations_artifact_path,
            )
            written_readiness = write_daily_readiness(
                project_root=".",
                artifact_output_path=readiness_artifact_path,
                surface_output_path=readiness_surface_path,
            )
            written_daily_home = write_daily_operator_home(
                artifact_output_path=daily_home_artifact_path,
                surface_output_path=daily_home_surface_path,
                today_path=written_today,
                morning_path=morning_artifact_path,
                readiness_path=readiness_artifact_path,
                handoff_path=handoff_artifact_path,
                handoff_study_resolution_path=handoff_resolution_artifact_path,
                handoff_apply_path=DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT,
                run_ledger_path=run_ledger_artifact_path,
                run_trace_path=run_trace_artifact_path,
                task_ledger_path=task_ledger_artifact_path,
                scheduler_operations_path=scheduler_operations_artifact_path,
                phone_access_path=phone_access_path,
                notification_path=notification_path,
                source_freshness_intake_path=source_freshness_intake_artifact_path,
                source_refresh_execution_brief_path=source_refresh_execution_artifact_path,
                memory_query_path=memory_query_artifact_path,
                memory_audit_path=memory_audit_artifact_path,
                learning_ledger_path=learning_ledger_artifact_path,
                pattern_evidence_intake_path=pattern_evidence_artifact_path,
                pattern_dry_run_proof_path=pattern_proof_artifact_path,
            )
            written_briefing_packet = write_daily_briefing_packet(
                artifact_output_path=briefing_packet_artifact_path,
                surface_output_path=briefing_packet_surface_path,
                daily_home_path=daily_home_artifact_path,
                today_path=written_today,
                readiness_path=readiness_artifact_path,
                run_ledger_path=run_ledger_artifact_path,
                handoff_study_resolution_path=handoff_resolution_artifact_path,
                learning_ledger_path=learning_ledger_artifact_path,
                memory_query_path=memory_query_artifact_path,
                notification_path=notification_path,
            )
            written_phone_access_verify = write_phone_access_verify(
                project_root=".",
                phone_access_path=phone_access_path,
                daily_home_path=daily_home_surface_path,
                today_path=written_today,
                artifact_output_path=phone_access_verify_artifact_path,
                surface_output_path=phone_access_verify_surface_path,
            )
            written_readiness = write_daily_readiness(
                project_root=".",
                artifact_output_path=readiness_artifact_path,
                surface_output_path=readiness_surface_path,
            )
            written_daily_home = write_daily_operator_home(
                artifact_output_path=daily_home_artifact_path,
                surface_output_path=daily_home_surface_path,
                today_path=written_today,
                morning_path=morning_artifact_path,
                readiness_path=readiness_artifact_path,
                handoff_path=handoff_artifact_path,
                handoff_study_resolution_path=handoff_resolution_artifact_path,
                handoff_apply_path=DEFAULT_HANDOFF_RESPONSE_APPLY_OUTPUT,
                run_ledger_path=run_ledger_artifact_path,
                run_trace_path=run_trace_artifact_path,
                task_ledger_path=task_ledger_artifact_path,
                scheduler_operations_path=scheduler_operations_artifact_path,
                phone_access_path=phone_access_path,
                notification_path=notification_path,
                source_freshness_intake_path=source_freshness_intake_artifact_path,
                source_refresh_execution_brief_path=source_refresh_execution_artifact_path,
                memory_query_path=memory_query_artifact_path,
                memory_audit_path=memory_audit_artifact_path,
                learning_ledger_path=learning_ledger_artifact_path,
                pattern_evidence_intake_path=pattern_evidence_artifact_path,
                pattern_dry_run_proof_path=pattern_proof_artifact_path,
            )
            written_briefing_packet = write_daily_briefing_packet(
                artifact_output_path=briefing_packet_artifact_path,
                surface_output_path=briefing_packet_surface_path,
                daily_home_path=daily_home_artifact_path,
                today_path=written_today,
                readiness_path=readiness_artifact_path,
                run_ledger_path=run_ledger_artifact_path,
                handoff_study_resolution_path=handoff_resolution_artifact_path,
                learning_ledger_path=learning_ledger_artifact_path,
                memory_query_path=memory_query_artifact_path,
                notification_path=notification_path,
            )
            written_phone_access_verify = write_phone_access_verify(
                project_root=".",
                phone_access_path=phone_access_path,
                daily_home_path=daily_home_surface_path,
                today_path=written_today,
                artifact_output_path=phone_access_verify_artifact_path,
                surface_output_path=phone_access_verify_surface_path,
            )
            written_briefing_packet = write_daily_briefing_packet(
                artifact_output_path=briefing_packet_artifact_path,
                surface_output_path=briefing_packet_surface_path,
                daily_home_path=daily_home_artifact_path,
                today_path=written_today,
                readiness_path=readiness_artifact_path,
                run_ledger_path=run_ledger_artifact_path,
                handoff_study_resolution_path=handoff_resolution_artifact_path,
                learning_ledger_path=learning_ledger_artifact_path,
                memory_query_path=memory_query_artifact_path,
                notification_path=notification_path,
            )
            notification_path = write_notification_payload(
                provider=args.notification_provider,
                today_url=args.today_url,
                today_path=written_today,
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                briefing_packet_path=briefing_packet_artifact_path,
                dry_run=not args.send,
            )
            if args.send:
                notification_status = send_notification_payload(notification_path).get("delivery_status", "unknown")
            else:
                notification_status = "dry_run_ready"
            add_archive_artifacts(
                manifest_path=archive_manifest,
                artifacts={
                    "daily_home": daily_home_artifact_path,
                    "daily_home_surface": written_daily_home,
                    "daily_briefing_packet": briefing_packet_artifact_path,
                    "daily_briefing_surface": written_briefing_packet,
                    "phone_access": phone_access_path,
                    "phone_access_verify": phone_access_verify_artifact_path,
                    "phone_access_verify_surface": written_phone_access_verify,
                    "source_refresh_brief": source_refresh_brief_artifact_path,
                    "source_refresh_brief_surface": written_source_refresh_brief,
                    "source_freshness_intake": source_freshness_intake_artifact_path,
                    "source_freshness_intake_surface": written_source_freshness_intake,
                    "source_refresh_execution_brief": source_refresh_execution_artifact_path,
                    "source_refresh_execution_surface": written_source_refresh_execution,
                    "scheduler_operations": scheduler_operations_artifact_path,
                    "scheduler_operations_surface": written_scheduler_operations,
                    "daily_readiness": readiness_artifact_path,
                    "daily_readiness_surface": written_readiness,
                    "daily_review": review_artifact_path,
                    "daily_review_surface": written_review,
                    "review_prompt": review_prompt_artifact_path,
                    "review_prompt_surface": written_review_prompt,
                    "review_effect": review_effect_artifact_path,
                    "review_effect_surface": written_review_effect,
                    "analyst_council": analyst_council_artifact_path,
                    "analyst_council_surface": written_analyst_council,
                    "memory_query": memory_query_artifact_path,
                    "memory_query_surface": written_memory_query,
                    "memory_audit": memory_audit_artifact_path,
                    "memory_audit_surface": written_memory_audit,
                    "learning_ledger": learning_ledger_artifact_path,
                    "learning_ledger_surface": written_learning,
                    "pattern_evidence_intake": pattern_evidence_artifact_path,
                    "pattern_evidence_intake_surface": written_pattern_evidence,
                    "pattern_dry_run_proof": pattern_proof_artifact_path,
                    "pattern_dry_run_proof_surface": written_pattern_proof,
                    "run_trace": run_trace_artifact_path,
                    "run_trace_surface": written_run_trace,
                    "daily_run_ledger": run_ledger_artifact_path,
                    "daily_run_ledger_surface": written_run_ledger,
                    "daily_handoff": handoff_artifact_path,
                    "daily_handoff_surface": written_handoff,
                    "handoff_study_resolution": handoff_resolution_artifact_path,
                    "handoff_study_resolution_surface": written_handoff_resolution,
                    "drift_review": drift_review_artifact_path,
                    "drift_review_surface": written_drift_review,
                    "today": written_today,
                },
            )
            print(json.dumps({
                "playbook": playbook_path.as_posix(),
                "phone_access": phone_access_path.as_posix(),
                "topics": topics_path,
                "research_plan": plan_path.as_posix(),
                "daily_scout": scout_path.as_posix(),
                "source_refresh_plan": refresh_plan_path.as_posix(),
                "source_refresh_apply": refresh_apply_path.as_posix(),
                "source_refresh_live_gate": refresh_live_gate_path.as_posix(),
                "source_refresh_live_run": refresh_live_run_path.as_posix(),
                "source_refresh_live_preflight": refresh_live_preflight_path.as_posix(),
                "daily_agenda": agenda_artifact_path.as_posix(),
                "daily_agenda_surface": written_agenda.as_posix(),
                "daily_home": daily_home_artifact_path.as_posix(),
                "daily_home_surface": written_daily_home.as_posix(),
                "daily_briefing_packet": briefing_packet_artifact_path.as_posix(),
                "daily_briefing_surface": written_briefing_packet.as_posix(),
                "phone_access_verify": phone_access_verify_artifact_path.as_posix(),
                "phone_access_verify_surface": written_phone_access_verify.as_posix(),
                "daily_readiness": readiness_artifact_path.as_posix(),
                "daily_readiness_surface": written_readiness.as_posix(),
                "daily_review": review_artifact_path.as_posix(),
                "daily_review_surface": written_review.as_posix(),
                "review_prompt": review_prompt_artifact_path.as_posix(),
                "review_prompt_surface": written_review_prompt.as_posix(),
                "review_effect": review_effect_artifact_path.as_posix(),
                "review_effect_surface": written_review_effect.as_posix(),
                "learning_ledger": learning_ledger_artifact_path.as_posix(),
                "learning_ledger_surface": written_learning.as_posix(),
                "agent_pattern_radar": pattern_radar_artifact_path.as_posix(),
                "agent_pattern_radar_surface": written_pattern_radar.as_posix(),
                "pattern_evidence_intake": pattern_evidence_artifact_path.as_posix(),
                "pattern_evidence_intake_surface": written_pattern_evidence.as_posix(),
                "pattern_dry_run_proof": pattern_proof_artifact_path.as_posix(),
                "pattern_dry_run_proof_surface": written_pattern_proof.as_posix(),
                "run_trace": run_trace_artifact_path.as_posix(),
                "run_trace_surface": written_run_trace.as_posix(),
                "daily_run_ledger": run_ledger_artifact_path.as_posix(),
                "daily_run_ledger_surface": written_run_ledger.as_posix(),
                "daily_handoff": handoff_artifact_path.as_posix(),
                "daily_handoff_surface": written_handoff.as_posix(),
                "handoff_study_resolution": handoff_resolution_artifact_path.as_posix(),
                "handoff_study_resolution_surface": written_handoff_resolution.as_posix(),
                "drift_review": drift_review_artifact_path.as_posix(),
                "drift_review_surface": written_drift_review.as_posix(),
                "source_refresh_brief": source_refresh_brief_artifact_path.as_posix(),
                "source_refresh_brief_surface": written_source_refresh_brief.as_posix(),
                "source_freshness_intake": source_freshness_intake_artifact_path.as_posix(),
                "source_freshness_intake_surface": written_source_freshness_intake.as_posix(),
                "source_refresh_execution_brief": source_refresh_execution_artifact_path.as_posix(),
                "source_refresh_execution_surface": written_source_refresh_execution.as_posix(),
                "scheduler_operations": scheduler_operations_artifact_path.as_posix(),
                "scheduler_operations_surface": written_scheduler_operations.as_posix(),
                "evidence_catalog": evidence_path.as_posix(),
                "topic_memory": memory_path.as_posix(),
                "scenario_report": written_scenario.as_posix(),
                "verdict": written_verdict.as_posix(),
                "dashboard": written_dashboard.as_posix(),
                "rollup": written_rollup.as_posix(),
                "product_brief": written_brief.as_posix(),
                "analyst_journal": written_journal.as_posix(),
                "analyst_journal_artifact": journal_artifact_path.as_posix(),
                "analyst_council": analyst_council_artifact_path.as_posix(),
                "analyst_council_surface": written_analyst_council.as_posix(),
                "analyst_tasks": written_task_queue.as_posix(),
                "analyst_tasks_artifact": task_queue_artifact_path.as_posix(),
                "analyst_task_ledger": written_task_ledger.as_posix(),
                "analyst_task_ledger_artifact": task_ledger_artifact_path.as_posix(),
                "today": written_today.as_posix(),
                "memory_surface": written_memory.as_posix(),
                "memory_query": memory_query_artifact_path.as_posix(),
                "memory_query_surface": written_memory_query.as_posix(),
                "memory_index": DEFAULT_MEMORY_INDEX_OUTPUT.as_posix(),
                "memory_audit": memory_audit_artifact_path.as_posix(),
                "memory_audit_surface": written_memory_audit.as_posix(),
                "vault_compile": active_vault_path.as_posix(),
                "vault_surface": active_vault_surface.as_posix(),
                "vault_compiled_count": vault_compile["compiled_count"] if vault_compile else 0,
                "morning_control": written_morning.as_posix(),
                "morning_control_artifact": morning_artifact_path.as_posix(),
                "archive_manifest": archive_manifest.as_posix(),
                "notification": notification_path.as_posix(),
                "notification_status": notification_status,
                "topic_count": len(plan["plan_items"]),
                "evidence_items": len(catalog["items"]),
                "recommended_topic": scout.get("recommended_topic", {}).get("name", ""),
                "refresh_action_count": len(refresh_plan["actions"]),
                "refresh_ready_count": refresh_apply["summary"]["ready_count"],
                "refresh_blocked_count": refresh_apply["summary"]["blocked_count"],
                "live_gate_status": refresh_live_gate["status"],
                "live_run_approval_status": refresh_live_run["approval_status"],
                "live_run_status": refresh_live_run["execution"]["status"],
                "live_preflight_status": refresh_live_preflight["status"],
            }, indent=2, ensure_ascii=False))
            return 0
    if args.command == "validate-profile":
        errors = validate_profile_file(args.profile_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-scenario":
        errors = validate_scenario_file(args.scenario_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "validate-verdict":
        errors = validate_verdict_file(args.verdict_path)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "errors": []}, indent=2))
        return 0
    if args.command == "policy":
        decision = classify_action(args.kind)
        print(json.dumps(asdict(decision), indent=2))
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
