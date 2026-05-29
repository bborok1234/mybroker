from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

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
