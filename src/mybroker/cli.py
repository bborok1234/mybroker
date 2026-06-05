from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from mybroker.appliance import (
    DEFAULT_ARCHIVE_ROOT,
    DEFAULT_LOCAL_OPS_DIR,
    DEFAULT_MEMORY_INDEX_OUTPUT,
    DEFAULT_MEMORY_QUERY_OUTPUT,
    DEFAULT_MEMORY_QUERY_SURFACE,
    DEFAULT_MEMORY_OUTPUT,
    DEFAULT_NOTIFICATION_OUTPUT,
    DEFAULT_PHONE_ACCESS_OUTPUT,
    DEFAULT_RUNTIME_PLAYBOOK_OUTPUT,
    DEFAULT_RUNTIME_DOCTOR_OUTPUT,
    DEFAULT_SCHEDULER_STATUS_OUTPUT,
    DEFAULT_TODAY_OUTPUT,
    archive_daily_run,
    send_notification_payload,
    write_launchd_assets,
    write_memory_query,
    write_memory_surface,
    write_notification_payload,
    write_phone_access_plan,
    write_runtime_doctor,
    write_runtime_playbook,
    write_scheduler_status,
    write_today_surface,
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
    DEFAULT_RESEARCH_PLAN_OUTPUT,
    DEFAULT_TOPIC_MEMORY_OUTPUT,
    DEFAULT_TOPICS_PATH,
    add_interest,
    build_research_plan,
    collect_topic_evidence,
    init_topic_config,
    load_topic_config,
    validate_research_plan_file,
    validate_topic_config_file,
    validate_topic_memory_file,
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

    validate_topics_parser = subcommands.add_parser("validate-topics", help="Validate a topic_config.v1 artifact.")
    validate_topics_parser.add_argument("topics_path")
    validate_plan_parser = subcommands.add_parser("validate-research-plan", help="Validate a daily_research_plan.v1 artifact.")
    validate_plan_parser.add_argument("plan_path")
    validate_memory_parser = subcommands.add_parser("validate-topic-memory", help="Validate a topic_memory.v1 artifact.")
    validate_memory_parser.add_argument("memory_path")

    brief_parser = subcommands.add_parser("brief", help="Build a user-facing MyBroker product brief from scenario and verdict artifacts.")
    brief_parser.add_argument("--scenario", required=True, help="scenario_report.v1 artifact path.")
    brief_parser.add_argument("--verdict", required=True, help="market_verdict.v1 artifact path.")
    brief_parser.add_argument("--output", default="reports/product/market-brief.html")

    daily_parser = subcommands.add_parser("daily-research", help="Run topic planning, free/public evidence collection, memory update, scenario, dashboard, and product brief.")
    daily_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    daily_parser.add_argument("--profile", help="Optional beginner profile JSON.")
    daily_parser.add_argument("--run-id", default="daily-research")
    daily_parser.add_argument("--plan-output", default=DEFAULT_RESEARCH_PLAN_OUTPUT.as_posix())
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
    appliance_today_parser = appliance_subcommands.add_parser("today", help="Render the mobile-first /today product surface.")
    appliance_today_parser.add_argument("--scenario", default="reports/scenarios/daily-research-sim.json")
    appliance_today_parser.add_argument("--verdict", default="reports/scenarios/daily-research-verdict.json")
    appliance_today_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--brief", default="reports/product/market-brief.html")
    appliance_today_parser.add_argument("--output", default=DEFAULT_TODAY_OUTPUT.as_posix())
    appliance_today_parser.add_argument("--archive-manifest")
    appliance_memory_parser = appliance_subcommands.add_parser("memory", help="Render the mobile-friendly accumulated memory and archive surface.")
    appliance_memory_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_memory_parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT.as_posix())
    appliance_memory_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_memory_parser.add_argument("--index-output", default=DEFAULT_MEMORY_INDEX_OUTPUT.as_posix())
    appliance_memory_parser.add_argument("--output", default=DEFAULT_MEMORY_OUTPUT.as_posix())
    appliance_query_parser = appliance_subcommands.add_parser("query", help="Search accumulated memory and archives for a beginner-readable question.")
    appliance_query_parser.add_argument("query")
    appliance_query_parser.add_argument("--memory", default=DEFAULT_TOPIC_MEMORY_OUTPUT.as_posix())
    appliance_query_parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT.as_posix())
    appliance_query_parser.add_argument("--evidence", default=DEFAULT_DAILY_EVIDENCE_OUTPUT.as_posix())
    appliance_query_parser.add_argument("--output", default=DEFAULT_MEMORY_QUERY_OUTPUT.as_posix())
    appliance_query_parser.add_argument("--surface-output", default=DEFAULT_MEMORY_QUERY_SURFACE.as_posix())
    appliance_query_parser.add_argument("--limit", type=int, default=5)
    appliance_notify_parser = appliance_subcommands.add_parser("notify", help="Prepare a phone notification payload. Dry-run by default.")
    appliance_notify_parser.add_argument("--provider", choices=["telegram", "pushover"], default="telegram")
    appliance_notify_parser.add_argument("--today-url", default="http://localhost:8787/reports/product/today.html")
    appliance_notify_parser.add_argument("--today", default=DEFAULT_TODAY_OUTPUT.as_posix())
    appliance_notify_parser.add_argument("--scenario", default="reports/scenarios/daily-research-sim.json")
    appliance_notify_parser.add_argument("--verdict", default="reports/scenarios/daily-research-verdict.json")
    appliance_notify_parser.add_argument("--output", default=DEFAULT_NOTIFICATION_OUTPUT.as_posix())
    appliance_notify_parser.add_argument("--dry-run", action="store_true", default=True)
    appliance_notify_parser.add_argument("--send", action="store_true", help="Send using provider environment variables instead of dry-run.")
    appliance_run_parser = appliance_subcommands.add_parser("run", help="Run the daily analyst loop, archive it, render /today, and prepare notification.")
    appliance_run_parser.add_argument("--topics", default=DEFAULT_TOPICS_PATH.as_posix())
    appliance_run_parser.add_argument("--profile", help="Optional beginner profile JSON.")
    appliance_run_parser.add_argument("--run-id", default="daily-research")
    appliance_run_parser.add_argument("--today-url", default="http://localhost:8787/reports/product/today.html")
    appliance_run_parser.add_argument("--notification-provider", choices=["telegram", "pushover"], default="telegram")
    appliance_run_parser.add_argument("--dry-run", action="store_true", default=True)
    appliance_run_parser.add_argument("--send", action="store_true", help="Send notification after writing payload. Requires provider environment variables.")
    appliance_run_parser.add_argument("--source", action="append", help="Public evidence adapter id. Use gdelt-live/stooq-live for no-key live refresh with cache fallback.")
    appliance_run_parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT.as_posix())
    appliance_run_parser.add_argument("--playbook-output", default=DEFAULT_RUNTIME_PLAYBOOK_OUTPUT.as_posix())

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
    if args.command == "validate-topic-memory":
        errors = validate_topic_memory_file(args.memory_path)
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
            "evidence_catalog": args.evidence_output,
            "topic_memory": args.memory_output,
            "scenario_report": scenario_path.as_posix(),
            "verdict": verdict_path.as_posix(),
            "dashboard": dashboard_path.as_posix(),
            "rollup": rollup_path.as_posix(),
            "product_brief": brief_path.as_posix(),
            "topic_count": len(plan["plan_items"]),
            "evidence_items": len(catalog["items"]),
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
        if args.appliance_command == "today":
            path = write_today_surface(
                scenario_path=args.scenario,
                verdict_path=args.verdict,
                memory_path=args.memory,
                evidence_path=args.evidence,
                brief_path=args.brief,
                output_path=args.output,
                archive_manifest_path=args.archive_manifest,
            )
            print(json.dumps({"today": path.as_posix()}, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "memory":
            path = write_memory_surface(
                memory_path=args.memory,
                archive_root=args.archive_root,
                evidence_path=args.evidence,
                index_output_path=args.index_output,
                output_path=args.output,
            )
            print(json.dumps({"memory": path.as_posix(), "index": args.index_output}, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "query":
            path = write_memory_query(
                query=args.query,
                memory_path=args.memory,
                archive_root=args.archive_root,
                evidence_path=args.evidence,
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
        if args.appliance_command == "notify":
            path = write_notification_payload(
                provider=args.provider,
                today_url=args.today_url,
                today_path=args.today,
                scenario_path=args.scenario,
                verdict_path=args.verdict,
                output_path=args.output,
                dry_run=not args.send,
            )
            result = {"notification": path.as_posix(), "dry_run": not args.send}
            if args.send:
                result["send_result"] = send_notification_payload(path).get("send_result", {})
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        if args.appliance_command == "run":
            topics_path = args.topics
            if not Path(topics_path).exists():
                init_topic_config(topics_path)
            plan_path = DEFAULT_RESEARCH_PLAN_OUTPUT
            evidence_path = DEFAULT_DAILY_EVIDENCE_OUTPUT
            memory_path = DEFAULT_TOPIC_MEMORY_OUTPUT
            scenario_path = Path("reports/scenarios/daily-research-sim.json")
            verdict_path = Path("reports/scenarios/daily-research-verdict.json")
            dashboard_path = Path("reports/dashboard.html")
            rollup_path = Path("reports/report-rollup.json")
            brief_path = Path("reports/product/market-brief.html")
            today_path = DEFAULT_TODAY_OUTPUT
            memory_surface_path = DEFAULT_MEMORY_OUTPUT
            playbook_path = write_runtime_playbook(args.playbook_output)
            plan = build_research_plan(topics_path=topics_path, output_path=plan_path, run_id=args.run_id)
            catalog = collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=evidence_path,
                memory_path=memory_path,
                source_ids=args.source,
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
            provisional_today = write_today_surface(
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                memory_path=memory_path,
                evidence_path=evidence_path,
                brief_path=written_brief,
                output_path=today_path,
            )
            archive_manifest = archive_daily_run(
                run_id=args.run_id,
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                evidence_path=evidence_path,
                memory_path=memory_path,
                brief_path=written_brief,
                today_path=provisional_today,
                archive_root=args.archive_root,
            )
            written_memory = write_memory_surface(
                memory_path=memory_path,
                archive_root=args.archive_root,
                evidence_path=evidence_path,
                index_output_path=DEFAULT_MEMORY_INDEX_OUTPUT,
                output_path=memory_surface_path,
            )
            written_today = write_today_surface(
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                memory_path=memory_path,
                evidence_path=evidence_path,
                brief_path=written_brief,
                output_path=today_path,
                archive_manifest_path=archive_manifest,
                memory_surface_path=written_memory,
            )
            notification_path = write_notification_payload(
                provider=args.notification_provider,
                today_url=args.today_url,
                today_path=written_today,
                scenario_path=written_scenario,
                verdict_path=written_verdict,
                dry_run=not args.send,
            )
            notification_status = "dry_run_ready"
            if args.send:
                notification_status = send_notification_payload(notification_path).get("delivery_status", "unknown")
            print(json.dumps({
                "playbook": playbook_path.as_posix(),
                "topics": topics_path,
                "research_plan": plan_path.as_posix(),
                "evidence_catalog": evidence_path.as_posix(),
                "topic_memory": memory_path.as_posix(),
                "scenario_report": written_scenario.as_posix(),
                "verdict": written_verdict.as_posix(),
                "dashboard": written_dashboard.as_posix(),
                "rollup": written_rollup.as_posix(),
                "product_brief": written_brief.as_posix(),
                "today": written_today.as_posix(),
                "memory_surface": written_memory.as_posix(),
                "memory_index": DEFAULT_MEMORY_INDEX_OUTPUT.as_posix(),
                "archive_manifest": archive_manifest.as_posix(),
                "notification": notification_path.as_posix(),
                "notification_status": notification_status,
                "topic_count": len(plan["plan_items"]),
                "evidence_items": len(catalog["items"]),
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
