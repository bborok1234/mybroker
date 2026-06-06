from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from mybroker.cli import main as cli_main
from mybroker.appliance import (
    archive_daily_run,
    send_notification_payload,
    build_task_status_apply,
    record_daily_review_response,
    record_task_status_response,
    write_agent_pattern_radar,
    write_pattern_dry_run_proof,
    write_analyst_journal,
    write_learning_ledger,
    write_analyst_council,
    write_analyst_task_queue,
    write_analyst_task_ledger,
    write_launchd_assets,
    write_morning_control_packet,
    write_daily_operator_home,
    write_memory_query,
    write_memory_audit,
    write_memory_surface,
    write_notification_payload,
    write_operator_decision_apply,
    write_operator_decision_packet,
    write_phone_access_plan,
    write_phone_access_verify,
    write_runtime_doctor,
    write_runtime_playbook,
    write_run_trace,
    write_daily_review,
    write_daily_run_ledger,
    write_daily_handoff,
    write_handoff_study_resolution,
    write_drift_review,
    write_operator_review_prompt,
    write_operator_review_effect,
    write_scheduler_activation_verify,
    write_scheduler_activation_preflight,
    write_scheduler_status,
    write_scheduler_apply,
    write_scheduler_operations,
    write_scheduler_run_once,
    write_source_refresh_brief,
    write_source_refresh_execution_brief,
    write_source_freshness_intake,
    write_today_surface,
    validate_morning_control_packet_file,
    validate_learning_ledger_file,
    validate_analyst_council_file,
    validate_analyst_task_ledger_file,
    validate_memory_query_file,
    validate_memory_audit_file,
    validate_run_trace_file,
    validate_agent_pattern_radar_file,
    validate_pattern_evidence_intake_file,
    validate_pattern_dry_run_proof_file,
    validate_daily_brief_agenda_file,
    validate_daily_brief_agenda_payload,
    validate_daily_operator_home_file,
    validate_daily_readiness_file,
    validate_daily_readiness_payload,
    validate_daily_review_file,
    validate_daily_review_payload,
    validate_daily_run_ledger_file,
    validate_daily_handoff_file,
    validate_handoff_study_resolution_file,
    validate_drift_review_file,
    validate_operator_review_prompt_file,
    validate_operator_review_effect_file,
    validate_operator_review_response_apply_file,
    validate_operator_council_response_apply_file,
    validate_operator_handoff_response_apply_file,
    validate_task_status_apply_file,
    validate_scheduler_operations_file,
    validate_scheduler_operations_payload,
    validate_source_refresh_brief_file,
    validate_source_refresh_brief_payload,
    validate_source_refresh_execution_brief_file,
    validate_source_refresh_execution_brief_payload,
    validate_source_freshness_intake_file,
    validate_handoff_study_resolution_payload,
    validate_phone_access_verify_file,
)
from mybroker.public_evidence import build_public_evidence_catalog, write_public_evidence_catalog
from mybroker.scenario import run_market_simulation, write_scenario_report, write_verdict
from mybroker.topics import (
    build_daily_scout,
    build_research_plan,
    build_source_refresh_apply,
    build_source_refresh_live_gate,
    build_source_refresh_live_preflight,
    build_source_refresh_live_run,
    build_source_refresh_plan,
    collect_topic_evidence,
    init_topic_config,
    validate_daily_scout_file,
    validate_source_refresh_live_preflight_file,
    validate_source_refresh_live_run_file,
)
from mybroker.vault import compile_knowledge_vault, init_knowledge_vault, validate_knowledge_vault_compile_file


class LocalApplianceTests(unittest.TestCase):
    def test_today_surface_archive_notification_and_runner_assets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            runtime_topics_path = root / "config" / "topics.json"
            plan_path = root / "research-plan.json"
            evidence_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            scenario_path = root / "scenario.json"
            verdict_path = root / "verdict.json"
            brief_path = root / "market-brief.html"
            journal_path = root / "journal.html"
            journal_artifact_path = root / "journal.json"
            learning_path = root / "learning.html"
            learning_artifact_path = root / "learning.json"
            tasks_path = root / "tasks.html"
            tasks_artifact_path = root / "tasks.json"
            ledger_path = root / "task-ledger.html"
            ledger_artifact_path = root / "task-ledger.json"
            today_path = root / "today.html"
            init_topic_config(topics_path)
            init_topic_config(runtime_topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="daily-test")
            collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=evidence_path,
                memory_path=memory_path,
            )
            report = run_market_simulation(
                seed_sources=["examples/seeds"],
                evidence_catalog_path=evidence_path,
                run_id="daily-test",
            )
            write_scenario_report(report, scenario_path)
            write_verdict(report, verdict_path)
            brief_path.write_text("<html>brief</html>", encoding="utf-8")
            journal = write_analyst_journal(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                scout_path=root / "missing-scout.json",
                artifact_output_path=journal_artifact_path,
                surface_output_path=journal_path,
            )
            learning = write_learning_ledger(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                journal_path=journal_artifact_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                archive_root=root / "archive",
                artifact_output_path=learning_artifact_path,
                surface_output_path=learning_path,
            )
            tasks = write_analyst_task_queue(
                journal_path=journal_artifact_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                scout_path=root / "missing-scout.json",
                artifact_output_path=tasks_artifact_path,
                surface_output_path=tasks_path,
            )
            ledger = write_analyst_task_ledger(
                task_queue_path=tasks_artifact_path,
                previous_ledger_path=root / "missing-ledger.json",
                artifact_output_path=ledger_artifact_path,
                surface_output_path=ledger_path,
            )

            today = write_today_surface(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                brief_path=brief_path,
                vault_path=root / "missing-vault.json",
                scout_path=root / "missing-scout.json",
                refresh_plan_path=root / "missing-refresh-plan.json",
                journal_surface_path=journal,
                task_queue_surface_path=tasks,
                task_ledger_surface_path=ledger,
                output_path=today_path,
            )
            refresh_plan_path = root / "source-refresh-plan.json"
            refresh_plan_path.write_text('{"schema_version":"source_refresh_plan.v1","actions":[]}', encoding="utf-8")
            refresh_apply_path = root / "source-refresh-apply.json"
            refresh_apply_path.write_text(
                '{"schema_version":"source_refresh_apply.v1","results":[{"decision":"ready","status":"dry_run_ready","source_name":"Local cache","adapter_id":"sample-cache","will_execute":false,"reason":"ready"}]}',
                encoding="utf-8",
            )
            refresh_live_gate_path = root / "source-refresh-live-gate.json"
            refresh_live_gate_path.write_text(
                '{"schema_version":"source_refresh_live_gate.v1","status":"no_live_refresh_requested","decisions":[],"blocked_actions":[],"blocked_action_count":0,"external_effect_performed":false}',
                encoding="utf-8",
            )
            refresh_live_run_path = root / "source-refresh-live-run.json"
            refresh_live_run_path.write_text(
                '{"schema_version":"source_refresh_live_run.v1","approval_status":"not_required","execution":{"status":"not_requested","blockers":[]},"external_effect_performed":false,"next_step":"no live refresh requested"}',
                encoding="utf-8",
            )
            refresh_live_preflight_path = root / "source-refresh-live-preflight.json"
            refresh_live_preflight_path.write_text(
                '{"schema_version":"source_refresh_live_preflight.v1","status":"not_required","approval_status":"not_required","live_run_status":"not_requested","requested_execution":{"intend_execute":false,"confirm_live_network":false},"source_ids":[],"proposed_commands":[],"blockers":[],"warnings":[],"external_effect_performed":false,"next_step":"no live refresh execution needed"}',
                encoding="utf-8",
            )
            source_refresh_brief = write_source_refresh_brief(
                scout_path=root / "missing-scout.json",
                evidence_path=root / "missing-evidence.json",
                refresh_plan_path=refresh_plan_path,
                refresh_apply_path=refresh_apply_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                artifact_output_path=root / "source-refresh-brief.json",
                surface_output_path=root / "source-refresh.html",
            )
            manifest = archive_daily_run(
                run_id="daily-test",
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                brief_path=brief_path,
                today_path=today,
                refresh_plan_path=refresh_plan_path,
                refresh_apply_path=refresh_apply_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                journal_path=journal,
                task_queue_path=tasks,
                task_ledger_path=ledger,
                archive_root=root / "archive",
            )
            today = write_today_surface(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                brief_path=brief_path,
                vault_path=root / "missing-vault.json",
                scout_path=root / "missing-scout.json",
                refresh_plan_path=root / "missing-refresh-plan.json",
                refresh_apply_path=root / "missing-refresh-apply.json",
                refresh_live_gate_path=root / "missing-refresh-live-gate.json",
                refresh_live_run_path=root / "missing-refresh-live-run.json",
                refresh_live_preflight_path=root / "missing-refresh-live-preflight.json",
                output_path=today_path,
                archive_manifest_path=manifest,
                journal_surface_path=journal,
                task_queue_surface_path=tasks,
                task_ledger_surface_path=ledger,
            )
            notification = write_notification_payload(
                provider="telegram",
                today_url="http://localhost:8787/today.html",
                today_path=today,
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                output_path=root / "notification.json",
            )
            access_plan = write_phone_access_plan(output_path=root / "phone-access.json", port=8787, tailnet_host="mybroker-mac")
            memory_surface = write_memory_surface(
                memory_path=memory_path,
                archive_root=root / "archive",
                evidence_path=evidence_path,
                index_output_path=root / "memory-index.json",
                output_path=root / "memory.html",
            )
            query_surface = write_memory_query(
                query="semiconductor cycle",
                memory_path=memory_path,
                archive_root=root / "archive",
                evidence_path=evidence_path,
                output_path=root / "memory-query.json",
                surface_path=root / "memory-query.html",
            )
            playbook = write_runtime_playbook(root / "playbook.json")
            assets = write_launchd_assets(project_root=root, output_dir=root / "ops" / "local", hour=7, minute=15)
            doctor = write_runtime_doctor(
                project_root=root,
                output_path=root / "runtime-doctor.json",
                freshness_hours=36,
            )
            scheduler = write_scheduler_status(
                project_root=root,
                output_path=root / "scheduler-status.json",
            )
            scheduler_apply = write_scheduler_apply(
                project_root=root,
                output_path=root / "scheduler-apply.json",
                install=True,
                load=True,
                start_now=True,
            )
            scheduler_operations = write_scheduler_operations(
                project_root=root,
                artifact_output_path=root / "scheduler-operations.json",
                surface_output_path=root / "scheduler.html",
            )

            html = today.read_text(encoding="utf-8")
            journal_html = journal.read_text(encoding="utf-8")
            journal_payload = json.loads(journal_artifact_path.read_text(encoding="utf-8"))
            learning_html = learning.read_text(encoding="utf-8")
            learning_payload = json.loads(learning_artifact_path.read_text(encoding="utf-8"))
            learning_errors = validate_learning_ledger_file(learning_artifact_path)
            tasks_html = tasks.read_text(encoding="utf-8")
            tasks_payload = json.loads(tasks_artifact_path.read_text(encoding="utf-8"))
            ledger_html = ledger.read_text(encoding="utf-8")
            ledger_payload = json.loads(ledger_artifact_path.read_text(encoding="utf-8"))
            memory_html = memory_surface.read_text(encoding="utf-8")
            query_payload = json.loads((root / "memory-query.json").read_text(encoding="utf-8"))
            query_html = query_surface.read_text(encoding="utf-8")
            notification_payload = json.loads(notification.read_text(encoding="utf-8"))
            access_payload = json.loads(access_plan.read_text(encoding="utf-8"))
            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
            playbook_payload = json.loads(playbook.read_text(encoding="utf-8"))
            doctor_payload = json.loads(doctor.read_text(encoding="utf-8"))
            scheduler_payload = json.loads(scheduler.read_text(encoding="utf-8"))
            scheduler_apply_payload = json.loads(scheduler_apply.read_text(encoding="utf-8"))
            scheduler_operations_payload = json.loads((root / "scheduler-operations.json").read_text(encoding="utf-8"))
            scheduler_operations_html = scheduler_operations.read_text(encoding="utf-8")
            source_refresh_brief_payload = json.loads((root / "source-refresh-brief.json").read_text(encoding="utf-8"))
            source_refresh_brief_html = source_refresh_brief.read_text(encoding="utf-8")
            source_freshness_intake = write_source_freshness_intake(
                source_refresh_brief_path=root / "source-refresh-brief.json",
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                artifact_output_path=root / "source-freshness-intake.json",
                surface_output_path=root / "source-freshness-intake.html",
            )
            source_freshness_intake_payload = json.loads((root / "source-freshness-intake.json").read_text(encoding="utf-8"))
            source_freshness_intake_html = source_freshness_intake.read_text(encoding="utf-8")
            source_freshness_intake_errors = validate_source_freshness_intake_file(root / "source-freshness-intake.json")
            script_exists = Path(assets["script"]).exists()
            plist_exists = Path(assets["plist"]).exists()
            morning = write_morning_control_packet(
                scout_path=root / "missing-scout.json",
                journal_path=journal_artifact_path,
                task_queue_path=tasks_artifact_path,
                task_ledger_path=ledger_artifact_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                notification_path=notification,
                runtime_doctor_path=doctor,
                artifact_output_path=root / "morning.json",
                surface_output_path=root / "morning.html",
            )
            morning_payload = json.loads((root / "morning.json").read_text(encoding="utf-8"))
            morning_html = morning.read_text(encoding="utf-8")
            morning_errors = validate_morning_control_packet_file(root / "morning.json")
            daily_home = write_daily_operator_home(
                today_path=today,
                morning_path=root / "morning.json",
                readiness_path=root / "missing-readiness.json",
                handoff_path=root / "missing-handoff.json",
                handoff_apply_path=root / "missing-handoff-apply.json",
                run_ledger_path=root / "missing-run-ledger.json",
                scheduler_operations_path=root / "scheduler-operations.json",
                phone_access_path=access_plan,
                notification_path=notification,
                source_freshness_intake_path=root / "source-freshness-intake.json",
                memory_audit_path=root / "missing-memory-audit.json",
                artifact_output_path=root / "reports" / "runtime" / "daily-home.json",
                surface_output_path=root / "reports" / "product" / "daily-home.html",
            )
            daily_home_payload = json.loads((root / "reports" / "runtime" / "daily-home.json").read_text(encoding="utf-8"))
            daily_home_html = daily_home.read_text(encoding="utf-8")
            daily_home_errors = validate_daily_operator_home_file(root / "reports" / "runtime" / "daily-home.json")
            for linked_path in daily_home_payload["phone_links"].values():
                candidate = Path(linked_path)
                if not candidate.is_absolute() and candidate.as_posix() not in {
                    "reports/product/daily-home.html",
                    "reports/product/phone-access.html",
                }:
                    linked_file = root / candidate
                    linked_file.parent.mkdir(parents=True, exist_ok=True)
                    linked_file.write_text("placeholder", encoding="utf-8")
            access_verify = write_phone_access_verify(
                project_root=root,
                phone_access_path=access_plan,
                daily_home_path=root / "reports" / "product" / "daily-home.html",
                today_path=today,
                artifact_output_path=root / "reports" / "runtime" / "phone-access-verify.json",
                surface_output_path=root / "reports" / "product" / "phone-access.html",
            )
            access_verify_payload = json.loads((root / "reports" / "runtime" / "phone-access-verify.json").read_text(encoding="utf-8"))
            access_verify_html = access_verify.read_text(encoding="utf-8")
            access_verify_errors = validate_phone_access_verify_file(root / "reports" / "runtime" / "phone-access-verify.json")

        self.assertIn("MyBroker Today", html)
        self.assertIn("오늘 시장 5분 브리프", html)
        self.assertIn("오늘의 analyst journal", html)
        self.assertIn("다음 analyst tasks", html)
        self.assertIn("task ledger", html)
        self.assertIn("근거 품질", html)
        self.assertIn("아카이브 manifest", html)
        self.assertIn("MyBroker Analyst Journal", journal_html)
        self.assertIn("역할별 메모", journal_html)
        self.assertIn("내일 이어갈 analyst tasks", journal_html)
        self.assertEqual(journal_payload["schema_version"], "personal_analyst_journal.v1")
        self.assertEqual(journal_payload["policy"], "research_only")
        self.assertIn("MyBroker Learning Ledger", learning_html)
        self.assertIn("오늘 배운 것의 누적 원장", learning_html)
        self.assertEqual(learning_payload["schema_version"], "personal_learning_ledger.v1")
        self.assertEqual(learning_errors, [])
        self.assertFalse(learning_payload["external_effect_performed"])
        self.assertIn("MyBroker Analyst Tasks", tasks_html)
        self.assertIn("역할별 큐", tasks_html)
        self.assertEqual(tasks_payload["schema_version"], "personal_analyst_task_queue.v1")
        self.assertGreaterEqual(tasks_payload["task_count"], 6)
        self.assertFalse(any(task["external_effect_allowed"] for task in tasks_payload["tasks"]))
        self.assertIn("MyBroker Task Ledger", ledger_html)
        self.assertIn("상태별 작업", ledger_html)
        self.assertEqual(ledger_payload["schema_version"], "personal_analyst_task_ledger.v1")
        self.assertEqual(ledger_payload["summary"]["completed"], ledger_payload["entry_count"])
        self.assertTrue(all(entry["local_completion"]["status"] == "satisfied" for entry in ledger_payload["entries"]))
        self.assertIn("MyBroker Memory", memory_html)
        self.assertIn("주제별 누적 기억", memory_html)
        self.assertIn("근거 품질 추적", memory_html)
        self.assertEqual(query_payload["schema_version"], "personal_memory_query.v1")
        self.assertEqual(query_payload["status"], "matched")
        self.assertGreaterEqual(query_payload["matched_topic_count"], 1)
        self.assertIn(query_payload["recall_quality"]["level"], {"usable", "strong", "thin"})
        self.assertGreaterEqual(len(query_payload["evidence_bundles"]), 1)
        self.assertGreaterEqual(len(query_payload["reading_order"]), 1)
        self.assertIn("weak_spots", query_payload)
        self.assertIn("MyBroker Memory Query", query_html)
        self.assertIn("Recall 품질", query_html)
        self.assertIn("근거 묶음", query_html)
        self.assertIn("먼저 읽을 순서", query_html)
        self.assertIn("다음에 확인할 질문", query_html)
        self.assertNotIn("schema_version", query_html)
        self.assertNotIn("schema_version", html)
        self.assertNotIn("Flyhigh", html)
        self.assertEqual(notification_payload["schema_version"], "notification_delivery.v1")
        self.assertEqual(notification_payload["delivery_status"], "dry_run_ready")
        self.assertIn("TELEGRAM_BOT_TOKEN", notification_payload["required_env"])
        self.assertEqual(access_payload["schema_version"], "phone_access_plan.v1")
        self.assertEqual(access_payload["recommended_path"], "tailscale_serve_private")
        self.assertEqual(access_payload["entrypoint"], "reports/product/daily-home.html")
        self.assertTrue(access_payload["local_url"].endswith("/reports/product/daily-home.html"))
        self.assertIn("tailscale serve --bg 8787", {item["command"] for item in access_payload["commands"]})
        self.assertEqual(manifest_payload["schema_version"], "daily_archive.v1")
        self.assertIn("source_refresh_plan", manifest_payload["artifacts"])
        self.assertIn("source_refresh_apply", manifest_payload["artifacts"])
        self.assertIn("source_refresh_live_gate", manifest_payload["artifacts"])
        self.assertIn("source_refresh_live_run", manifest_payload["artifacts"])
        self.assertIn("source_refresh_live_preflight", manifest_payload["artifacts"])
        self.assertIn("journal", manifest_payload["artifacts"])
        self.assertIn("tasks", manifest_payload["artifacts"])
        self.assertIn("task_ledger", manifest_payload["artifacts"])
        self.assertIn("Hermes Agent", {item["source"] for item in playbook_payload["absorbed_patterns"]})
        self.assertEqual(doctor_payload["schema_version"], "local_runtime_doctor.v1")
        self.assertEqual(doctor_payload["status"], "ready")
        self.assertEqual(doctor_payload["fail_count"], 0)
        self.assertIn("launchd_loaded", {item["name"] for item in doctor_payload["checks"]})
        self.assertTrue(doctor_payload["install_boundary"]["launchd_install_is_host_level"])
        self.assertEqual(scheduler_payload["schema_version"], "local_scheduler_status.v1")
        self.assertIn(scheduler_payload["status"], {"assets_ready", "installed_not_loaded", "loaded"})
        self.assertFalse(scheduler_payload["host_write_performed"])
        self.assertIn("install", scheduler_payload["commands"])
        self.assertEqual(scheduler_apply_payload["schema_version"], "local_scheduler_apply.v1")
        self.assertTrue(scheduler_apply_payload["dry_run"])
        self.assertFalse(scheduler_apply_payload["host_write_performed"])
        self.assertEqual({item["status"] for item in scheduler_apply_payload["actions"]}, {"planned"})
        self.assertIn("post_status", scheduler_apply_payload)
        self.assertTrue(scheduler_apply_payload["post_status_path"].startswith(root.resolve().as_posix()))
        self.assertEqual(scheduler_operations_payload["schema_version"], "local_scheduler_operations.v1")
        self.assertIn(scheduler_operations_payload["status"], {"manual_ready", "not_ready", "blocked", "activation_ready", "active_verified"})
        self.assertFalse(scheduler_operations_payload["external_effect_performed"])
        self.assertFalse(scheduler_operations_payload["host_write_performed"])
        self.assertEqual(validate_scheduler_operations_payload(scheduler_operations_payload), [])
        self.assertIn("자동 실행 준비 상태", scheduler_operations_html)
        self.assertNotIn("schema_version", scheduler_operations_html)
        self.assertEqual(source_refresh_brief_payload["schema_version"], "source_refresh_brief.v1")
        self.assertIn(source_refresh_brief_payload["status"], {"local_ready", "no_refresh_needed", "approval_required", "preflight_required", "ready_to_execute", "executed", "blocked"})
        self.assertFalse(source_refresh_brief_payload["external_effect_performed"])
        self.assertFalse(source_refresh_brief_payload["host_write_performed"])
        self.assertGreaterEqual(len(source_refresh_brief_payload["source_freshness"]), 1)
        self.assertTrue(any(row["trust_state"] in {"sample_or_fallback", "fresh_enough", "weak_or_unknown"} for row in source_refresh_brief_payload["source_freshness"]))
        self.assertEqual(validate_source_refresh_brief_payload(source_refresh_brief_payload), [])
        self.assertIn("오늘 근거 새로고침 판단", source_refresh_brief_html)
        self.assertIn("Source freshness", source_refresh_brief_html)
        self.assertNotIn("schema_version", source_refresh_brief_html)
        self.assertEqual(source_freshness_intake_payload["schema_version"], "source_freshness_intake.v1")
        self.assertIn(source_freshness_intake_payload["status"], {"approval_packet_ready", "ready_for_operator_review", "no_intake_needed"})
        self.assertFalse(source_freshness_intake_payload["external_effect_performed"])
        self.assertFalse(source_freshness_intake_payload["host_write_performed"])
        self.assertEqual(source_freshness_intake_errors, [])
        self.assertIn("승인 전 근거 신선도 확인", source_freshness_intake_html)
        self.assertIn("복사 가능한 승인 응답", source_freshness_intake_html)
        self.assertNotIn("schema_version", source_freshness_intake_html)
        self.assertTrue(script_exists)
        self.assertTrue(plist_exists)
        self.assertEqual(morning_payload["schema_version"], "morning_control_packet.v1")
        self.assertFalse(morning_payload["external_effect_performed"])
        self.assertFalse(morning_payload["host_write_performed"])
        self.assertIn(morning_payload["status"], {"ready", "operator_review"})
        self.assertIn("today", morning_payload["phone_links"])
        self.assertGreaterEqual(len(morning_payload["command_bar"]), 1)
        self.assertEqual(morning_errors, [])
        self.assertIn("MyBroker Morning Control", morning_html)
        self.assertIn("아침 analyst 관제판", morning_html)
        self.assertIn("복사 가능한 응답", morning_html)
        self.assertNotIn("schema_version", morning_html)
        self.assertNotIn("--send", morning_html)
        self.assertEqual(daily_home_payload["schema_version"], "daily_operator_home.v1")
        self.assertEqual(daily_home_errors, [])
        self.assertIn(daily_home_payload["status"], {"ready", "operator_review", "blocked"})
        self.assertFalse(daily_home_payload["external_effect_performed"])
        self.assertFalse(daily_home_payload["host_write_performed"])
        self.assertIn("daily_home_reads_existing_artifacts_only", daily_home_payload["safety_boundary"])
        self.assertIn("today", daily_home_payload["phone_links"])
        self.assertIn("morning", daily_home_payload["phone_links"])
        self.assertIn("readiness", daily_home_payload["phone_links"])
        self.assertIn("handoff", daily_home_payload["phone_links"])
        self.assertIn("handoff_apply", daily_home_payload["phone_links"])
        self.assertIn("trace", daily_home_payload["phone_links"])
        self.assertIn("source_freshness_intake", daily_home_payload["phone_links"])
        self.assertIn("pattern_radar", daily_home_payload["phone_links"])
        self.assertIn("pattern_dry_run", daily_home_payload["phone_links"])
        self.assertEqual(daily_home_payload["trace_observability_adoption"]["pattern_candidate_id"], "pattern-run-trace-observability")
        self.assertFalse(daily_home_payload["trace_observability_adoption"]["external_effect_performed"])
        self.assertFalse(daily_home_payload["trace_observability_adoption"]["host_write_performed"])
        self.assertEqual(daily_home_payload["source_freshness_intake_adoption"]["pattern_candidate_id"], "pattern-freshness-intake")
        self.assertFalse(daily_home_payload["source_freshness_intake_adoption"]["external_effect_performed"])
        self.assertFalse(daily_home_payload["source_freshness_intake_adoption"]["host_write_performed"])
        self.assertEqual(daily_home_payload["pattern_scout_adoption"]["pattern_candidate_id"], "pattern-freshness-intake")
        self.assertFalse(daily_home_payload["pattern_scout_adoption"]["operator_decision_needed"])
        self.assertFalse(daily_home_payload["pattern_scout_adoption"]["external_effect_performed"])
        self.assertFalse(daily_home_payload["pattern_scout_adoption"]["host_write_performed"])
        self.assertIn("operator_action_inbox", daily_home_payload)
        self.assertIn(daily_home_payload["operator_action_inbox"]["status"], {"clear", "needs_attention", "approval_review"})
        self.assertFalse(daily_home_payload["operator_action_inbox"]["external_effect_performed"])
        self.assertFalse(daily_home_payload["operator_action_inbox"]["host_write_performed"])
        self.assertGreaterEqual(len(daily_home_payload["daily_route"]), 6)
        self.assertIn("오늘의 개인 애널리스트 홈", daily_home_html)
        self.assertIn("오늘 닫을 것", daily_home_html)
        self.assertIn("오늘의 방식 Scout", daily_home_html)
        self.assertIn("근거 신선도 intake", daily_home_html)
        self.assertIn("오늘 볼 순서", daily_home_html)
        self.assertIn("복사할 수 있는 로컬 응답", daily_home_html)
        self.assertNotIn("schema_version", daily_home_html)
        self.assertNotIn("--send", daily_home_html)
        self.assertEqual(access_verify_payload["schema_version"], "phone_access_verify.v1")
        self.assertEqual(access_verify_errors, [])
        self.assertEqual(access_verify_payload["status"], "ready")
        self.assertFalse(access_verify_payload["external_effect_performed"])
        self.assertFalse(access_verify_payload["host_write_performed"])
        self.assertFalse(access_verify_payload["public_exposure_performed"])
        self.assertEqual(access_verify_payload["summary"]["missing_link_count"], 0)
        self.assertTrue(access_verify_payload["summary"]["daily_home_local_url"].endswith("/reports/product/daily-home.html"))
        self.assertIn("폰 접근 검증", access_verify_html)
        self.assertIn("수동 테스트 명령", access_verify_html)
        self.assertNotIn("schema_version", access_verify_html)

    def test_scheduler_run_once_executes_local_runner_without_host_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "ops" / "local" / "run-daily-analyst.sh"
            script.parent.mkdir(parents=True, exist_ok=True)
            script.write_text(
                "#!/bin/sh\n"
                "set -eu\n"
                "mkdir -p reports/runtime reports/product reports/archive/test\n"
                "printf 'runner ok\\n'\n",
                encoding="utf-8",
            )
            script.chmod(0o755)

            output = write_scheduler_run_once(
                project_root=root,
                output_path=root / "scheduler-run-once.json",
                timeout_seconds=5,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], "local_scheduler_run_once.v1")
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["returncode"], 0)
        self.assertFalse(payload["host_write_performed"])
        self.assertIn("runner ok", payload["stdout_excerpt"])
        self.assertTrue(payload["post_status_path"].endswith("reports/runtime/scheduler-status.json"))
        self.assertTrue(payload["doctor_path"].endswith("reports/runtime/local-runtime-doctor.json"))

    def test_scheduler_activation_preflight_requires_local_proofs_without_host_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config").mkdir(parents=True)
            (root / "config" / "topics.json").write_text("{}", encoding="utf-8")
            for path in [
                root / "reports" / "runtime" / "phone-access.json",
                root / "reports" / "product" / "today.html",
                root / "reports" / "product" / "memory.html",
                root / "reports" / "product" / "memory-query.html",
                root / "reports" / "archive" / "test" / "manifest.json",
            ]:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("ok", encoding="utf-8")
            (root / "reports" / "notifications").mkdir(parents=True, exist_ok=True)
            (root / "reports" / "notifications" / "latest.json").write_text(
                json.dumps({
                    "schema_version": "notification_delivery.v1",
                    "generated_at": "2026-06-05T00:00:00+00:00",
                    "provider": "telegram",
                    "dry_run": True,
                    "delivery_status": "dry_run_ready",
                    "required_env": [],
                }),
                encoding="utf-8",
            )
            script = root / "ops" / "local" / "run-daily-analyst.sh"
            script.parent.mkdir(parents=True, exist_ok=True)
            script.write_text("#!/bin/sh\nprintf 'runner ok\\n'\n", encoding="utf-8")
            script.chmod(0o755)
            (root / "ops" / "local" / "com.mybroker.daily-analyst.plist").write_text("<plist />", encoding="utf-8")

            write_scheduler_apply(
                project_root=root,
                output_path=root / "reports" / "runtime" / "scheduler-apply.json",
                install=True,
                load=True,
                start_now=True,
            )
            write_scheduler_run_once(
                project_root=root,
                output_path=root / "reports" / "runtime" / "scheduler-run-once.json",
                timeout_seconds=5,
            )
            output = write_scheduler_activation_preflight(
                project_root=root,
                output_path=root / "reports" / "runtime" / "scheduler-activation-preflight.json",
                max_proof_age_hours=24,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], "local_scheduler_activation_preflight.v1")
        self.assertEqual(payload["status"], "ready")
        self.assertFalse(payload["host_write_performed"])
        self.assertEqual(payload["blockers"], [])
        self.assertIn("--confirm-host-write", payload["activation_command"])
        self.assertTrue(payload["safety"]["requires_explicit_operator_approval"])

    def test_scheduler_activation_verify_blocks_until_launchd_is_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config").mkdir(parents=True)
            (root / "config" / "topics.json").write_text("{}", encoding="utf-8")
            for path in [
                root / "reports" / "runtime" / "phone-access.json",
                root / "reports" / "product" / "today.html",
                root / "reports" / "product" / "memory.html",
                root / "reports" / "product" / "memory-query.html",
                root / "reports" / "archive" / "test" / "manifest.json",
            ]:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("ok", encoding="utf-8")
            (root / "reports" / "notifications").mkdir(parents=True, exist_ok=True)
            (root / "reports" / "notifications" / "latest.json").write_text(
                json.dumps({
                    "schema_version": "notification_delivery.v1",
                    "provider": "telegram",
                    "dry_run": True,
                    "delivery_status": "dry_run_ready",
                    "required_env": [],
                }),
                encoding="utf-8",
            )
            script = root / "ops" / "local" / "run-daily-analyst.sh"
            script.parent.mkdir(parents=True, exist_ok=True)
            script.write_text("#!/bin/sh\nprintf 'runner ok\\n'\n", encoding="utf-8")
            script.chmod(0o755)
            (root / "ops" / "local" / "com.mybroker.daily-analyst.plist").write_text("<plist />", encoding="utf-8")

            output = write_scheduler_activation_verify(
                project_root=root,
                output_path=root / "reports" / "runtime" / "scheduler-activation-verify.json",
                freshness_hours=36,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], "local_scheduler_activation_verify.v1")
        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["host_write_performed"])
        self.assertGreaterEqual(len(payload["blockers"]), 1)
        self.assertIn("confirmed host-level activation", payload["next_action"])

    def test_operator_decision_packet_separates_external_effect_approvals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config").mkdir(parents=True)
            (root / "config" / "topics.json").write_text("{}", encoding="utf-8")
            write_phone_access_plan(output_path=root / "reports" / "runtime" / "phone-access.json")
            for path in [
                root / "reports" / "product" / "today.html",
                root / "reports" / "product" / "memory.html",
                root / "reports" / "product" / "memory-query.html",
                root / "reports" / "archive" / "test" / "manifest.json",
            ]:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("ok", encoding="utf-8")
            (root / "reports" / "notifications").mkdir(parents=True, exist_ok=True)
            (root / "reports" / "notifications" / "latest.json").write_text(
                json.dumps({
                    "schema_version": "notification_delivery.v1",
                    "generated_at": "2026-06-05T00:00:00+00:00",
                    "provider": "telegram",
                    "dry_run": True,
                    "delivery_status": "dry_run_ready",
                    "required_env": ["TELEGRAM_BOT_TOKEN"],
                }),
                encoding="utf-8",
            )
            script = root / "ops" / "local" / "run-daily-analyst.sh"
            script.parent.mkdir(parents=True, exist_ok=True)
            script.write_text("#!/bin/sh\nprintf 'runner ok\\n'\n", encoding="utf-8")
            script.chmod(0o755)
            (root / "ops" / "local" / "com.mybroker.daily-analyst.plist").write_text("<plist />", encoding="utf-8")
            write_scheduler_apply(
                project_root=root,
                output_path=root / "reports" / "runtime" / "scheduler-apply.json",
                install=True,
                load=True,
                start_now=True,
            )
            write_scheduler_run_once(
                project_root=root,
                output_path=root / "reports" / "runtime" / "scheduler-run-once.json",
                timeout_seconds=5,
            )

            output = write_operator_decision_packet(
                project_root=root,
                output_path=root / "reports" / "runtime" / "operator-decision-packet.json",
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], "operator_decision_packet.v1")
        self.assertEqual(payload["status"], "pending_operator_decision")
        self.assertFalse(payload["host_write_performed"])
        decision_ids = {decision["id"] for decision in payload["decisions"]}
        self.assertEqual(decision_ids, {"scheduler_activation", "notification_send", "private_phone_access"})
        self.assertIn("confirmed_host_write", {decision["approval_scope"] for decision in payload["decisions"]})
        self.assertGreaterEqual(payload["summary"]["blocked_count"], 1)
        phone_decision = next(decision for decision in payload["decisions"] if decision["id"] == "private_phone_access")
        self.assertIn("cd <mybroker-repo> && python3 -m http.server 8787", phone_decision["agent_will_run"])
        self.assertIn("tailscale serve --bg 8787", phone_decision["agent_will_run"])
        self.assertNotIn("tailscale serve reset", phone_decision["agent_will_run"])
        self.assertEqual(phone_decision["rollback_command"], "tailscale serve reset")

    def test_operator_decision_apply_validates_scoped_approvals_without_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet = root / "operator-decision-packet.json"
            packet.write_text(
                json.dumps({
                    "schema_version": "operator_decision_packet.v1",
                    "decisions": [
                        {
                            "id": "private_phone_access",
                            "approval_scope": "private_network_exposure",
                            "readiness": "ready",
                            "agent_will_run": [
                                "cd <mybroker-repo> && python3 -m http.server 8787",
                                "tailscale serve --bg 8787",
                            ],
                            "rollback_command": "tailscale serve reset",
                        },
                        {
                            "id": "notification_send",
                            "approval_scope": "send_notification",
                            "readiness": "blocked",
                            "agent_will_run": ["PYTHONPATH=src python3 -m mybroker appliance notify --send"],
                            "rollback_command": "",
                        },
                    ],
                }),
                encoding="utf-8",
            )

            valid_output = write_operator_decision_apply(
                response="approve private_phone_access private_network_exposure",
                project_root=root,
                packet_path=packet,
                output_path=root / "operator-decision-apply.json",
            )
            valid_payload = json.loads(valid_output.read_text(encoding="utf-8"))
            mismatch_output = write_operator_decision_apply(
                response="approve private_phone_access send_notification",
                project_root=root,
                packet_path=packet,
                output_path=root / "operator-decision-apply-mismatch.json",
            )
            mismatch_payload = json.loads(mismatch_output.read_text(encoding="utf-8"))
            blocked_output = write_operator_decision_apply(
                response="approve notification_send send_notification",
                project_root=root,
                packet_path=packet,
                output_path=root / "operator-decision-apply-blocked.json",
            )
            blocked_payload = json.loads(blocked_output.read_text(encoding="utf-8"))

        self.assertEqual(valid_payload["schema_version"], "operator_decision_apply.v1")
        self.assertEqual(valid_payload["status"], "ready_to_apply")
        self.assertFalse(valid_payload["external_effect_performed"])
        self.assertFalse(valid_payload["host_write_performed"])
        self.assertEqual(valid_payload["commands"], [
            "cd <mybroker-repo> && python3 -m http.server 8787",
            "tailscale serve --bg 8787",
        ])
        self.assertEqual(valid_payload["rollback_command"], "tailscale serve reset")
        self.assertEqual(mismatch_payload["status"], "blocked")
        self.assertEqual(mismatch_payload["commands"], [])
        self.assertIn("Approval scope mismatch", mismatch_payload["blockers"][0])
        self.assertEqual(blocked_payload["status"], "blocked")
        self.assertEqual(blocked_payload["commands"], [])
        self.assertIn("Decision readiness is blocked", blocked_payload["blockers"][0])

    def test_today_surface_can_use_public_catalog_without_topic_memory_leakage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence_path = write_public_evidence_catalog(build_public_evidence_catalog(), root / "evidence.json")
            memory_path = root / "memory.json"
            memory_path.write_text(
                json.dumps({
                    "schema_version": "topic_memory.v1",
                    "run_count": 1,
                    "topics": [],
                }),
                encoding="utf-8",
            )
            report = run_market_simulation(seed_sources=["examples/seeds"], evidence_catalog_path=evidence_path)
            scenario_path = write_scenario_report(report, root / "scenario.json")
            verdict_path = write_verdict(report, root / "verdict.json")
            brief_path = root / "brief.html"
            brief_path.write_text("<html>brief</html>", encoding="utf-8")

            today = write_today_surface(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                brief_path=brief_path,
                vault_path=root / "missing-vault.json",
                scout_path=root / "missing-scout.json",
                refresh_plan_path=root / "missing-refresh-plan.json",
                output_path=root / "today.html",
            )
            html = today.read_text(encoding="utf-8")

        self.assertIn("아직 누적 주제 기억이 없습니다", html)

    def test_notification_send_requires_provider_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = root / "notification.json"
            payload.write_text(
                json.dumps({
                    "schema_version": "notification_delivery.v1",
                    "provider": "telegram",
                    "title": "MyBroker",
                    "message": "ready",
                    "url": "http://localhost",
                }),
                encoding="utf-8",
            )

            with self.assertRaises(RuntimeError):
                send_notification_payload(payload)

    def test_knowledge_vault_compiles_raw_notes_into_wiki_and_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault_root = root / "research-vault"
            init_payload = init_knowledge_vault(root=vault_root)
            raw_note = vault_root / "raw" / "semiconductor-cycle.md"
            raw_note.write_text(
                "# Semiconductor cycle note\n\n"
                "AI demand is lifting chip suppliers.\n"
                "Memory pricing remains cyclical.\n"
                "Check source freshness before trusting the trend.\n",
                encoding="utf-8",
            )
            topics = init_topic_config(root / "topics.json")
            output = root / "reports" / "vault" / "compile.json"
            surface = root / "reports" / "product" / "vault.html"
            payload = compile_knowledge_vault(
                raw_dir=vault_root / "raw",
                wiki_dir=vault_root / "wiki",
                output_path=output,
                surface_path=surface,
                topics_path=root / "topics.json",
            )
            errors = validate_knowledge_vault_compile_file(output)
            note = payload["compiled_notes"][0]
            wiki_note_exists = Path(note["wiki_path"]).exists()
            surface_exists = surface.exists()
            surface_html = surface.read_text(encoding="utf-8")
            memory_path = root / "reports" / "memory" / "topic-memory.json"
            memory_path.parent.mkdir(parents=True, exist_ok=True)
            memory_path.write_text(
                json.dumps({
                    "schema_version": "topic_memory.v1",
                    "generated_at": "2026-06-05T00:00:00+00:00",
                    "run_count": 0,
                    "topics": [],
                    "runs": [],
                }),
                encoding="utf-8",
            )
            evidence_path = root / "reports" / "evidence" / "daily-evidence-catalog.json"
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text(json.dumps({"source_status": []}), encoding="utf-8")
            plan_path = root / "reports" / "daily" / "research-plan.json"
            plan = build_research_plan(topics_path=root / "topics.json", output_path=plan_path, run_id="vault-today")
            daily_evidence_path = root / "reports" / "evidence" / "scout-evidence.json"
            collect_topic_evidence(
                topics_path=root / "topics.json",
                plan_path=plan_path,
                output_path=daily_evidence_path,
                memory_path=memory_path,
            )
            scout_path = root / "reports" / "daily" / "scout.json"
            scout = build_daily_scout(
                topics_path=root / "topics.json",
                plan_path=plan_path,
                evidence_path=daily_evidence_path,
                memory_path=memory_path,
                vault_path=output,
                output_path=scout_path,
                run_id="vault-today",
            )
            refresh_plan_path = root / "reports" / "daily" / "source-refresh-plan.json"
            refresh_plan = build_source_refresh_plan(
                scout_path=scout_path,
                evidence_path=daily_evidence_path,
                vault_path=output,
                output_path=refresh_plan_path,
            )
            refresh_apply_path = root / "reports" / "daily" / "source-refresh-apply.json"
            refresh_apply = build_source_refresh_apply(
                refresh_plan_path=refresh_plan_path,
                output_path=refresh_apply_path,
            )
            refresh_live_gate_path = root / "reports" / "daily" / "source-refresh-live-gate.json"
            refresh_live_gate = build_source_refresh_live_gate(
                refresh_apply_path=refresh_apply_path,
                output_path=refresh_live_gate_path,
            )
            refresh_live_run_path = root / "reports" / "daily" / "source-refresh-live-run.json"
            refresh_live_run = build_source_refresh_live_run(
                live_gate_path=refresh_live_gate_path,
                output_path=refresh_live_run_path,
            )
            refresh_live_preflight_path = root / "reports" / "daily" / "source-refresh-live-preflight.json"
            refresh_live_preflight = build_source_refresh_live_preflight(
                live_run_path=refresh_live_run_path,
                output_path=refresh_live_preflight_path,
            )
            memory_surface = write_memory_surface(
                memory_path=memory_path,
                archive_root=root / "reports" / "archive",
                evidence_path=daily_evidence_path,
                vault_path=output,
                index_output_path=root / "reports" / "memory" / "index.json",
                output_path=root / "reports" / "product" / "memory.html",
            )
            query_surface = write_memory_query(
                query="memory pricing",
                memory_path=memory_path,
                archive_root=root / "reports" / "archive",
                evidence_path=daily_evidence_path,
                vault_path=output,
                output_path=root / "reports" / "memory" / "latest-query.json",
                surface_path=root / "reports" / "product" / "memory-query.html",
            )
            audit_surface = write_memory_audit(
                memory_path=memory_path,
                archive_root=root / "reports" / "archive",
                evidence_path=daily_evidence_path,
                vault_path=output,
                daily_review_path=root / "missing-review.json",
                output_path=root / "reports" / "memory" / "audit.json",
                surface_path=root / "reports" / "product" / "memory-audit.html",
            )
            scenario_report = run_market_simulation(seed_sources=["examples/seeds"], run_id="vault-today")
            scenario_path = write_scenario_report(scenario_report, root / "reports" / "scenario.json")
            verdict_path = write_verdict(scenario_report, root / "reports" / "verdict.json")
            journal_surface = write_analyst_journal(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                memory_path=memory_path,
                evidence_path=daily_evidence_path,
                scout_path=scout_path,
                vault_path=output,
                artifact_output_path=root / "reports" / "memory" / "journal.json",
                surface_output_path=root / "reports" / "product" / "journal.html",
            )
            council_surface = write_analyst_council(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                journal_path=root / "reports" / "memory" / "journal.json",
                memory_path=memory_path,
                evidence_path=daily_evidence_path,
                memory_audit_path=root / "reports" / "memory" / "audit.json",
                scout_path=scout_path,
                artifact_output_path=root / "reports" / "runtime" / "analyst-council.json",
                surface_output_path=root / "reports" / "product" / "council.html",
            )
            brief_path = root / "reports" / "product" / "market-brief.html"
            brief_path.parent.mkdir(parents=True, exist_ok=True)
            brief_path.write_text("<html>brief</html>", encoding="utf-8")
            today_surface = write_today_surface(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                memory_path=memory_path,
                evidence_path=daily_evidence_path,
                brief_path=brief_path,
                vault_path=output,
                scout_path=scout_path,
                refresh_plan_path=refresh_plan_path,
                refresh_apply_path=refresh_apply_path,
                refresh_live_gate_path=refresh_live_gate_path,
                refresh_live_run_path=refresh_live_run_path,
                refresh_live_preflight_path=refresh_live_preflight_path,
                output_path=root / "reports" / "product" / "today.html",
            )
            memory_index = json.loads((root / "reports" / "memory" / "index.json").read_text(encoding="utf-8"))
            query_payload = json.loads((root / "reports" / "memory" / "latest-query.json").read_text(encoding="utf-8"))
            audit_payload = json.loads((root / "reports" / "memory" / "audit.json").read_text(encoding="utf-8"))
            audit_errors = validate_memory_audit_file(root / "reports" / "memory" / "audit.json")
            council_payload = json.loads((root / "reports" / "runtime" / "analyst-council.json").read_text(encoding="utf-8"))
            council_errors = validate_analyst_council_file(root / "reports" / "runtime" / "analyst-council.json")
            memory_surface_html = memory_surface.read_text(encoding="utf-8")
            query_surface_html = query_surface.read_text(encoding="utf-8")
            audit_surface_html = audit_surface.read_text(encoding="utf-8")
            council_surface_html = council_surface.read_text(encoding="utf-8")
            journal_surface_html = journal_surface.read_text(encoding="utf-8")
            today_surface_html = today_surface.read_text(encoding="utf-8")

        self.assertEqual(init_payload["schema_version"], "knowledge_vault_init.v1")
        self.assertEqual(topics["schema_version"], "topic_config.v1")
        self.assertEqual(errors, [])
        self.assertEqual(payload["schema_version"], "knowledge_vault_compile.v1")
        self.assertEqual(payload["compiled_count"], 1)
        self.assertEqual(payload["topic_count"], 1)
        self.assertEqual(payload["policy"], "research_only")
        self.assertEqual(plan["schema_version"], "daily_research_plan.v1")
        self.assertEqual(scout["schema_version"], "daily_scout.v1")
        self.assertEqual(refresh_plan["schema_version"], "source_refresh_plan.v1")
        self.assertEqual(refresh_apply["schema_version"], "source_refresh_apply.v1")
        self.assertFalse(refresh_apply["external_effect_performed"])
        self.assertEqual(refresh_live_gate["schema_version"], "source_refresh_live_gate.v1")
        self.assertFalse(refresh_live_gate["external_effect_performed"])
        self.assertEqual(refresh_live_run["schema_version"], "source_refresh_live_run.v1")
        self.assertFalse(refresh_live_run["external_effect_performed"])
        self.assertEqual(refresh_live_preflight["schema_version"], "source_refresh_live_preflight.v1")
        self.assertFalse(refresh_live_preflight["external_effect_performed"])
        self.assertEqual(note["title"], "Semiconductor cycle note")
        self.assertIn("AI demand is lifting chip suppliers.", note["key_takeaways"])
        self.assertTrue(wiki_note_exists)
        self.assertTrue(surface_exists)
        self.assertIn("컴파일된 리서치 노트", surface_html)
        self.assertEqual(memory_index["vault_notes"][0]["title"], "Semiconductor cycle note")
        self.assertIn("Vault 원천 노트", memory_surface_html)
        self.assertEqual(query_payload["matched_vault_note_count"], 1)
        self.assertEqual(query_payload["matched_vault_notes"][0]["title"], "Semiconductor cycle note")
        self.assertEqual(audit_payload["schema_version"], "personal_memory_audit.v1")
        self.assertEqual(audit_errors, [])
        self.assertGreaterEqual(audit_payload["summary"]["vault_note_count"], 1)
        self.assertIn(audit_payload["status"], {"ready", "needs_attention", "blocked"})
        self.assertIn("관련 Vault 노트", query_surface_html)
        self.assertIn("개인 애널리스트 메모리 감사", audit_surface_html)
        self.assertIn("감사 리스크", audit_surface_html)
        self.assertEqual(council_payload["schema_version"], "analyst_council.v1")
        self.assertEqual(council_errors, [])
        self.assertFalse(council_payload["external_effect_performed"])
        self.assertFalse(council_payload["host_write_performed"])
        self.assertTrue(any(role["role"] == "skeptic" for role in council_payload["roles"]))
        self.assertIn(council_payload["status"], {"ready_to_read", "read_with_caution", "blocked"})
        self.assertTrue(any("council-response-apply" in command["command"] for command in council_payload["copy_ready_commands"]))
        self.assertIn("오늘 브리프 읽기 전 analyst council", council_surface_html)
        self.assertIn("복사 가능한 council 응답", council_surface_html)
        self.assertIn("오늘의 개인 애널리스트 작업일지", journal_surface_html)
        self.assertIn("오늘 Scout 추천", today_surface_html)
        self.assertIn("오늘 새로고침 계획", today_surface_html)
        self.assertIn("오늘 실행 판정", today_surface_html)
        self.assertIn("라이브 새로고침 게이트", today_surface_html)
        self.assertIn("라이브 실행 증거", today_surface_html)
        self.assertIn("라이브 실행 사전점검", today_surface_html)
        self.assertIn("Vault에서 다시 볼 원천 노트", today_surface_html)
        self.assertIn("Semiconductor cycle note", today_surface_html)
        self.assertIn("Vault 노트 &#x27;Semiconductor cycle note&#x27;가 오늘 근거와 같은 방향", today_surface_html)

    def test_appliance_run_auto_compiles_local_vault_before_daily_scout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "examples" / "seeds").mkdir(parents=True)
            (root / "examples" / "seeds" / "market.md").write_text(
                "# AI infrastructure demand\n\n"
                "AI data center demand keeps semiconductors and power in focus.\n",
                encoding="utf-8",
            )
            raw_dir = root / "research-vault" / "raw"
            raw_dir.mkdir(parents=True)
            (raw_dir / "semiconductor-cycle.md").write_text(
                "# Semiconductor cycle note\n\n"
                "AI demand is lifting chip suppliers.\n"
                "Memory pricing remains cyclical.\n"
                "Check source freshness before trusting the trend.\n",
                encoding="utf-8",
            )
            previous_cwd = Path.cwd()
            try:
                os.chdir(root)
                result = cli_main([
                    "appliance",
                    "run",
                    "--topics",
                    "config/topics.json",
                    "--vault-raw-dir",
                    "research-vault/raw",
                    "--vault-wiki-dir",
                    "research-vault/wiki",
                    "--vault-output",
                    "reports/vault/compile.json",
                    "--vault-surface-output",
                    "reports/product/vault.html",
                    "--dry-run",
                ])
            finally:
                os.chdir(previous_cwd)
            vault_payload = json.loads((root / "reports" / "vault" / "compile.json").read_text(encoding="utf-8"))
            scout_payload = json.loads((root / "reports" / "daily" / "scout.json").read_text(encoding="utf-8"))
            memory_index = json.loads((root / "reports" / "memory" / "index.json").read_text(encoding="utf-8"))
            memory_query_payload = json.loads((root / "reports" / "memory" / "latest-query.json").read_text(encoding="utf-8"))
            memory_query_errors = validate_memory_query_file(root / "reports" / "memory" / "latest-query.json")
            memory_audit_payload = json.loads((root / "reports" / "memory" / "audit.json").read_text(encoding="utf-8"))
            memory_audit_errors = validate_memory_audit_file(root / "reports" / "memory" / "audit.json")
            council_payload = json.loads((root / "reports" / "runtime" / "analyst-council.json").read_text(encoding="utf-8"))
            council_errors = validate_analyst_council_file(root / "reports" / "runtime" / "analyst-council.json")
            journal_payload = json.loads((root / "reports" / "memory" / "analyst-journal.json").read_text(encoding="utf-8"))
            learning_payload = json.loads((root / "reports" / "memory" / "learning-ledger.json").read_text(encoding="utf-8"))
            learning_errors = validate_learning_ledger_file(root / "reports" / "memory" / "learning-ledger.json")
            morning_payload = json.loads((root / "reports" / "runtime" / "morning-control.json").read_text(encoding="utf-8"))
            agenda_payload = json.loads((root / "reports" / "daily" / "brief-agenda.json").read_text(encoding="utf-8"))
            agenda_errors = validate_daily_brief_agenda_file(root / "reports" / "daily" / "brief-agenda.json")
            readiness_payload = json.loads((root / "reports" / "runtime" / "daily-readiness.json").read_text(encoding="utf-8"))
            readiness_errors = validate_daily_readiness_file(root / "reports" / "runtime" / "daily-readiness.json")
            daily_home_payload = json.loads((root / "reports" / "runtime" / "daily-home.json").read_text(encoding="utf-8"))
            daily_home_errors = validate_daily_operator_home_file(root / "reports" / "runtime" / "daily-home.json")
            access_verify_payload = json.loads((root / "reports" / "runtime" / "phone-access-verify.json").read_text(encoding="utf-8"))
            access_verify_errors = validate_phone_access_verify_file(root / "reports" / "runtime" / "phone-access-verify.json")
            source_refresh_brief_payload = json.loads((root / "reports" / "runtime" / "source-refresh-brief.json").read_text(encoding="utf-8"))
            source_refresh_brief_errors = validate_source_refresh_brief_file(root / "reports" / "runtime" / "source-refresh-brief.json")
            source_freshness_intake_payload = json.loads((root / "reports" / "runtime" / "source-freshness-intake.json").read_text(encoding="utf-8"))
            source_freshness_intake_errors = validate_source_freshness_intake_file(root / "reports" / "runtime" / "source-freshness-intake.json")
            source_refresh_execution_payload = json.loads((root / "reports" / "runtime" / "source-refresh-execution-brief.json").read_text(encoding="utf-8"))
            source_refresh_execution_errors = validate_source_refresh_execution_brief_file(root / "reports" / "runtime" / "source-refresh-execution-brief.json")
            pattern_radar_payload = json.loads((root / "reports" / "runtime" / "agent-pattern-radar.json").read_text(encoding="utf-8"))
            pattern_radar_errors = validate_agent_pattern_radar_file(root / "reports" / "runtime" / "agent-pattern-radar.json")
            pattern_evidence_payload = json.loads((root / "reports" / "runtime" / "pattern-evidence-intake.json").read_text(encoding="utf-8"))
            pattern_evidence_errors = validate_pattern_evidence_intake_file(root / "reports" / "runtime" / "pattern-evidence-intake.json")
            pattern_proof_payload = json.loads((root / "reports" / "runtime" / "pattern-dry-run-proof.json").read_text(encoding="utf-8"))
            pattern_proof_errors = validate_pattern_dry_run_proof_file(root / "reports" / "runtime" / "pattern-dry-run-proof.json")
            run_trace_payload = json.loads((root / "reports" / "runtime" / "run-trace.json").read_text(encoding="utf-8"))
            run_trace_errors = validate_run_trace_file(root / "reports" / "runtime" / "run-trace.json")
            run_ledger_payload = json.loads((root / "reports" / "runtime" / "daily-run-ledger.json").read_text(encoding="utf-8"))
            run_ledger_errors = validate_daily_run_ledger_file(root / "reports" / "runtime" / "daily-run-ledger.json")
            handoff_payload = json.loads((root / "reports" / "runtime" / "daily-handoff.json").read_text(encoding="utf-8"))
            handoff_errors = validate_daily_handoff_file(root / "reports" / "runtime" / "daily-handoff.json")
            handoff_resolution_payload = json.loads((root / "reports" / "runtime" / "handoff-study-resolution.json").read_text(encoding="utf-8"))
            handoff_resolution_errors = validate_handoff_study_resolution_file(root / "reports" / "runtime" / "handoff-study-resolution.json")
            drift_review_payload = json.loads((root / "reports" / "runtime" / "drift-review.json").read_text(encoding="utf-8"))
            drift_review_errors = validate_drift_review_file(root / "reports" / "runtime" / "drift-review.json")
            review_payload = json.loads((root / "reports" / "memory" / "daily-review.json").read_text(encoding="utf-8"))
            review_errors = validate_daily_review_file(root / "reports" / "memory" / "daily-review.json")
            review_prompt_payload = json.loads((root / "reports" / "runtime" / "review-prompt.json").read_text(encoding="utf-8"))
            review_prompt_errors = validate_operator_review_prompt_file(root / "reports" / "runtime" / "review-prompt.json")
            review_effect_payload = json.loads((root / "reports" / "runtime" / "review-effect.json").read_text(encoding="utf-8"))
            review_effect_errors = validate_operator_review_effect_file(root / "reports" / "runtime" / "review-effect.json")
            scheduler_operations_payload = json.loads((root / "reports" / "runtime" / "scheduler-operations.json").read_text(encoding="utf-8"))
            scheduler_operations_errors = validate_scheduler_operations_file(root / "reports" / "runtime" / "scheduler-operations.json")
            archive_manifests = sorted((root / "reports" / "archive").glob("*/manifest.json"))
            self.assertEqual(len(archive_manifests), 1)
            manifest_payload = json.loads(archive_manifests[0].read_text(encoding="utf-8"))
            today_html = (root / "reports" / "product" / "today.html").read_text(encoding="utf-8")
            morning_html = (root / "reports" / "product" / "morning.html").read_text(encoding="utf-8")
            agenda_html = (root / "reports" / "product" / "daily-agenda.html").read_text(encoding="utf-8")
            readiness_html = (root / "reports" / "product" / "readiness.html").read_text(encoding="utf-8")
            daily_home_html = (root / "reports" / "product" / "daily-home.html").read_text(encoding="utf-8")
            access_verify_html = (root / "reports" / "product" / "phone-access.html").read_text(encoding="utf-8")
            source_refresh_html = (root / "reports" / "product" / "source-refresh.html").read_text(encoding="utf-8")
            source_freshness_intake_html = (root / "reports" / "product" / "source-freshness-intake.html").read_text(encoding="utf-8")
            source_refresh_execution_html = (root / "reports" / "product" / "source-refresh-execution.html").read_text(encoding="utf-8")
            pattern_radar_html = (root / "reports" / "product" / "pattern-radar.html").read_text(encoding="utf-8")
            pattern_evidence_html = (root / "reports" / "product" / "pattern-evidence-intake.html").read_text(encoding="utf-8")
            pattern_proof_html = (root / "reports" / "product" / "pattern-dry-run.html").read_text(encoding="utf-8")
            run_trace_html = (root / "reports" / "product" / "run-trace.html").read_text(encoding="utf-8")
            run_ledger_html = (root / "reports" / "product" / "run-ledger.html").read_text(encoding="utf-8")
            handoff_html = (root / "reports" / "product" / "handoff.html").read_text(encoding="utf-8")
            handoff_resolution_html = (root / "reports" / "product" / "handoff-study-resolution.html").read_text(encoding="utf-8")
            drift_review_html = (root / "reports" / "product" / "drift-review.html").read_text(encoding="utf-8")
            review_html = (root / "reports" / "product" / "review.html").read_text(encoding="utf-8")
            review_prompt_html = (root / "reports" / "product" / "review-prompt.html").read_text(encoding="utf-8")
            review_effect_html = (root / "reports" / "product" / "review-effect.html").read_text(encoding="utf-8")
            scheduler_html = (root / "reports" / "product" / "scheduler.html").read_text(encoding="utf-8")
            memory_query_html = (root / "reports" / "product" / "memory-query.html").read_text(encoding="utf-8")
            memory_audit_html = (root / "reports" / "product" / "memory-audit.html").read_text(encoding="utf-8")
            learning_html = (root / "reports" / "product" / "learning.html").read_text(encoding="utf-8")
            council_html = (root / "reports" / "product" / "council.html").read_text(encoding="utf-8")
            vault_html = (root / "reports" / "product" / "vault.html").read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertEqual(vault_payload["schema_version"], "knowledge_vault_compile.v1")
        self.assertEqual(vault_payload["compiled_count"], 1)
        self.assertEqual(vault_payload["compiled_notes"][0]["title"], "Semiconductor cycle note")
        self.assertTrue(any(item.get("linked_vault_notes") for item in scout_payload["recommendations"]))
        self.assertEqual(memory_index["vault_notes"][0]["title"], "Semiconductor cycle note")
        self.assertEqual(memory_query_payload["schema_version"], "personal_memory_query.v1")
        self.assertEqual(memory_query_errors, [])
        self.assertEqual(memory_query_payload["query"], scout_payload["recommended_topic"]["name"])
        self.assertIn(memory_query_payload["recall_quality"]["level"], {"usable", "strong", "thin"})
        self.assertGreaterEqual(len(memory_query_payload["reading_order"]), 1)
        self.assertIn("vault note 1개", journal_payload["role_notes"][4]["finding"])
        self.assertEqual(learning_payload["schema_version"], "personal_learning_ledger.v1")
        self.assertEqual(learning_errors, [])
        self.assertIn("오늘 배운 것의 누적 원장", learning_html)
        self.assertGreaterEqual(learning_payload["summary"]["concept_count"], 1)
        self.assertGreaterEqual(learning_payload["summary"]["question_count"], 1)
        self.assertFalse(learning_payload["external_effect_performed"])
        self.assertIn("learning_ledger", manifest_payload["artifacts"])
        self.assertIn("vault", morning_payload["phone_links"])
        self.assertIn("memory_query", morning_payload["phone_links"])
        self.assertIn("agenda", morning_payload["phone_links"])
        self.assertIn("readiness", morning_payload["phone_links"])
        self.assertIn("scheduler", morning_payload["phone_links"])
        self.assertIn("source_refresh", morning_payload["phone_links"])
        self.assertIn("pattern_radar", morning_payload["phone_links"])
        self.assertIn("trace", morning_payload["phone_links"])
        self.assertIn("run_ledger", morning_payload["phone_links"])
        self.assertIn("handoff", morning_payload["phone_links"])
        self.assertIn("handoff_apply", morning_payload["phone_links"])
        self.assertIn("daily_home", morning_payload["phone_links"])
        self.assertIn("phone_access", morning_payload["phone_links"])
        self.assertIn("drift_review", morning_payload["phone_links"])
        self.assertIn("review", morning_payload["phone_links"])
        self.assertIn("review_prompt", morning_payload["phone_links"])
        self.assertIn("review_effect", morning_payload["phone_links"])
        self.assertIn("council", morning_payload["phone_links"])
        self.assertIn("memory_audit", morning_payload["phone_links"])
        self.assertEqual(memory_audit_payload["schema_version"], "personal_memory_audit.v1")
        self.assertEqual(memory_audit_errors, [])
        self.assertFalse(memory_audit_payload["external_effect_performed"])
        self.assertFalse(memory_audit_payload["host_write_performed"])
        self.assertGreaterEqual(memory_audit_payload["summary"]["vault_note_count"], 1)
        self.assertEqual(council_payload["schema_version"], "analyst_council.v1")
        self.assertEqual(council_errors, [])
        self.assertFalse(council_payload["external_effect_performed"])
        self.assertFalse(council_payload["host_write_performed"])
        self.assertIn(council_payload["status"], {"ready_to_read", "read_with_caution", "blocked"})
        self.assertGreaterEqual(council_payload["summary"]["role_count"], 6)
        self.assertTrue(any(role["role"] == "beginner_tutor" for role in council_payload["roles"]))
        self.assertTrue(any("council-response-apply" in command["command"] for command in council_payload["copy_ready_commands"]))
        self.assertEqual(agenda_payload["schema_version"], "daily_brief_agenda.v1")
        self.assertEqual(agenda_errors, [])
        self.assertEqual(validate_daily_brief_agenda_payload(agenda_payload), [])
        self.assertIn("phone_first_local_personal_analyst", agenda_payload["mode"])
        self.assertGreaterEqual(len(agenda_payload["copy_ready_responses"]), 1)
        self.assertIn("beginner_reading_order", agenda_payload["primary_topic"])
        self.assertGreaterEqual(len(agenda_payload["study_sequence"]), 4)
        self.assertTrue(any(role["role"] == "skeptic" for role in agenda_payload["role_brief"]))
        self.assertEqual(readiness_payload["schema_version"], "daily_readiness.v1")
        self.assertEqual(readiness_errors, [])
        self.assertEqual(validate_daily_readiness_payload(readiness_payload), [])
        self.assertFalse(readiness_payload["external_effect_performed"])
        self.assertIn(readiness_payload["status"], {"ready", "review", "stale", "blocked"})
        self.assertTrue(any(item["name"] == "daily_agenda" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "daily_home" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "daily_home_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "phone_access_verify" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "phone_access_verify_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "source_refresh_brief" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "source_freshness_intake" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "source_refresh_execution_brief" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "source_refresh_execution_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "pattern_evidence_intake" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "pattern_evidence_intake_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "scheduler_operations" for item in readiness_payload["artifacts"]))
        self.assertIn("source_refresh", readiness_payload["phone_links"])
        self.assertIn("source_freshness_intake", readiness_payload["phone_links"])
        self.assertIn("source_refresh_execution", readiness_payload["phone_links"])
        self.assertIn("scheduler", readiness_payload["phone_links"])
        self.assertIn("trace", readiness_payload["phone_links"])
        self.assertIn("run_ledger", readiness_payload["phone_links"])
        self.assertIn("handoff", readiness_payload["phone_links"])
        self.assertIn("handoff_study_resolution", readiness_payload["phone_links"])
        self.assertIn("handoff_apply", readiness_payload["phone_links"])
        self.assertIn("daily_home", readiness_payload["phone_links"])
        self.assertIn("phone_access", readiness_payload["phone_links"])
        self.assertIn("drift_review", readiness_payload["phone_links"])
        self.assertIn("review_prompt", readiness_payload["phone_links"])
        self.assertIn("review_effect", readiness_payload["phone_links"])
        self.assertIn("council", readiness_payload["phone_links"])
        self.assertIn("memory_query", readiness_payload["phone_links"])
        self.assertTrue(any(item["name"] == "memory_query" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "memory_query_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "memory_audit" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "memory_audit_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "learning_ledger" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "learning_ledger_surface" for item in readiness_payload["artifacts"]))
        self.assertIn("learning", readiness_payload["phone_links"])
        self.assertTrue(any(item["name"] == "analyst_council" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "analyst_council_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "run_trace" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "daily_handoff" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "daily_handoff_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "handoff_study_resolution" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "handoff_study_resolution_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "handoff_response_apply" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "handoff_response_apply_surface" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "drift_review" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "review_prompt" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "review_effect" for item in readiness_payload["artifacts"]))
        self.assertEqual(source_refresh_brief_payload["schema_version"], "source_refresh_brief.v1")
        self.assertEqual(source_refresh_brief_errors, [])
        self.assertFalse(source_refresh_brief_payload["external_effect_performed"])
        self.assertFalse(source_refresh_brief_payload["host_write_performed"])
        self.assertIn(source_refresh_brief_payload["status"], {"local_ready", "approval_required", "preflight_required", "ready_to_execute", "executed", "blocked", "no_refresh_needed"})
        self.assertGreaterEqual(len(source_refresh_brief_payload["source_freshness"]), 1)
        self.assertTrue(any(row["trust_state"] == "sample_or_fallback" for row in source_refresh_brief_payload["source_freshness"]))
        self.assertEqual(source_freshness_intake_payload["schema_version"], "source_freshness_intake.v1")
        self.assertEqual(source_freshness_intake_errors, [])
        self.assertFalse(source_freshness_intake_payload["external_effect_performed"])
        self.assertFalse(source_freshness_intake_payload["host_write_performed"])
        self.assertGreaterEqual(source_freshness_intake_payload["summary"]["source_count"], 1)
        self.assertIn("승인 전 근거 신선도 확인", source_freshness_intake_html)
        self.assertNotIn("schema_version", source_freshness_intake_html)
        self.assertEqual(source_refresh_execution_payload["schema_version"], "source_refresh_execution_brief.v1")
        self.assertEqual(source_refresh_execution_errors, [])
        self.assertFalse(source_refresh_execution_payload["external_effect_performed"])
        self.assertFalse(source_refresh_execution_payload["host_write_performed"])
        self.assertIn(source_refresh_execution_payload["status"], {"not_required", "approval_required", "preflight_required", "ready_for_final_confirmation", "executed", "blocked"})
        self.assertIn("execution_requires_separate_final_confirmation", source_refresh_execution_payload["safety_boundary"])
        self.assertEqual(validate_source_refresh_execution_brief_payload(source_refresh_execution_payload), [])
        self.assertIn("실행 전 최종 확인", source_refresh_execution_html)
        self.assertIn("멈춤 조건", source_refresh_execution_html)
        self.assertNotIn("schema_version", source_refresh_execution_html)
        self.assertFalse(source_refresh_execution_payload["final_confirmation"]["required"])
        self.assertEqual(pattern_radar_payload["schema_version"], "agent_pattern_radar.v1")
        self.assertEqual(pattern_radar_errors, [])
        self.assertFalse(pattern_radar_payload["external_effect_performed"])
        self.assertFalse(pattern_radar_payload["host_write_performed"])
        self.assertGreaterEqual(pattern_radar_payload["summary"]["adopted_count"], 5)
        self.assertGreaterEqual(pattern_radar_payload["summary"]["dry_run_candidate_count"], 3)
        self.assertEqual(pattern_radar_payload["pattern_scout"]["status"], "ready")
        self.assertEqual(pattern_radar_payload["pattern_scout"]["recommended_next"]["candidate_id"], "pattern-method-evidence-intake")
        self.assertEqual(pattern_radar_payload["pattern_scout"]["recommended_next"]["title"], "pattern evidence intake before workflow adoption")
        self.assertEqual(pattern_radar_payload["pattern_scout"]["recommended_next"]["approval_scope"], "local_dry_run_only")
        self.assertFalse(pattern_radar_payload["pattern_scout"]["external_effect_performed"])
        self.assertTrue(pattern_radar_payload["pattern_scout"]["deferred_watchlist"])
        self.assertTrue(pattern_radar_payload["pattern_scout"]["rejected_boundary"])
        self.assertTrue(any(candidate["candidate_id"] == "pattern-freshness-intake" and candidate["status"] == "ready" for candidate in pattern_radar_payload["dry_run_candidates"]))
        self.assertTrue(any(candidate["candidate_id"] == "pattern-method-evidence-intake" and candidate["status"] == "ready" for candidate in pattern_radar_payload["dry_run_candidates"]))
        self.assertTrue(any(candidate["candidate_id"] == "pattern-source-refresh-execution-confirmation" and candidate["status"] == "ready" for candidate in pattern_radar_payload["dry_run_candidates"]))
        self.assertTrue(any(candidate["candidate_id"] == "pattern-live-source-browser-gateway" and candidate["status"] == "requires_approval" for candidate in pattern_radar_payload["dry_run_candidates"]))
        self.assertIn("dry_run_to_adopted", pattern_radar_payload["adoption_gate"]["allowed_transitions"])
        self.assertTrue(any(case["source"] == "MiroFish" for case in pattern_radar_payload["cases"]))
        self.assertTrue(any(case["source"] == "Hermes Studio" for case in pattern_radar_payload["cases"]))
        self.assertTrue(any(case["source"] == "OpenClaw safety research" for case in pattern_radar_payload["cases"]))
        self.assertTrue(any(case["source"] == "SemaClaw" for case in pattern_radar_payload["cases"]))
        self.assertTrue(any(case["source"] == "work-buddy" for case in pattern_radar_payload["cases"]))
        self.assertTrue(any(case["source"] == "Dexter" for case in pattern_radar_payload["cases"]))
        self.assertTrue(any(case["source"] == "TraceAgent" for case in pattern_radar_payload["cases"]))
        self.assertTrue(any(case["source"] == "TaskWeaver" and case["decision"] == "defer" for case in pattern_radar_payload["cases"]))
        self.assertTrue(any(case["decision"] == "reject" for case in pattern_radar_payload["cases"]))
        self.assertEqual(pattern_evidence_payload["schema_version"], "pattern_evidence_intake.v1")
        self.assertEqual(pattern_evidence_errors, [])
        self.assertFalse(pattern_evidence_payload["external_effect_performed"])
        self.assertFalse(pattern_evidence_payload["host_write_performed"])
        self.assertGreaterEqual(pattern_evidence_payload["summary"]["candidate_count"], 5)
        self.assertGreaterEqual(pattern_evidence_payload["summary"]["already_verified_count"], 3)
        self.assertTrue(any(row["candidate_id"] == "pattern-method-evidence-intake" and row["intake_status"] == "already_verified" for row in pattern_evidence_payload["candidate_assessments"]))
        self.assertTrue(any(row["candidate_id"] == "pattern-live-source-browser-gateway" and row["intake_status"] == "approval_gated" for row in pattern_evidence_payload["candidate_assessments"]))
        self.assertIn("새 에이전트 방법론을 루프에 넣어도 되나", pattern_evidence_html)
        self.assertNotIn("schema_version", pattern_evidence_html)
        self.assertEqual(pattern_proof_payload["schema_version"], "pattern_dry_run_proof.v1")
        self.assertEqual(pattern_proof_errors, [])
        self.assertFalse(pattern_proof_payload["external_effect_performed"])
        self.assertFalse(pattern_proof_payload["host_write_performed"])
        self.assertGreaterEqual(pattern_proof_payload["summary"]["passed_count"], 1)
        self.assertTrue(any(row["candidate_id"] == "pattern-freshness-intake" and row["proof_status"] == "passed" for row in pattern_proof_payload["candidate_results"]))
        self.assertTrue(any(row["candidate_id"] == "pattern-method-evidence-intake" and row["proof_status"] == "passed" for row in pattern_proof_payload["candidate_results"]))
        self.assertTrue(any(row["candidate_id"] == "pattern-source-refresh-execution-confirmation" and row["proof_status"] == "passed" for row in pattern_proof_payload["candidate_results"]))
        self.assertTrue(any(row["candidate_id"] == "pattern-memory-recall-quality" and row["proof_status"] == "passed" for row in pattern_proof_payload["candidate_results"]))
        self.assertTrue(any(row["candidate_id"] == "pattern-run-trace-observability" and row["proof_status"] == "passed" for row in pattern_proof_payload["candidate_results"]))
        self.assertTrue(any(row["candidate_id"] == "pattern-live-source-browser-gateway" and row["proof_status"] == "approval_required" for row in pattern_proof_payload["candidate_results"]))
        self.assertTrue(any(row["candidate_id"] == "pattern-code-analytics-sandbox" and row["proof_status"] == "blocked" for row in pattern_proof_payload["candidate_results"]))
        self.assertTrue(any(item["decision"] == "adopted_proof_ready" for item in pattern_proof_payload["promotion_decisions"]))
        self.assertIn("does_not_execute_candidate_commands", pattern_proof_payload["safety_boundary"])
        self.assertEqual(run_trace_payload["schema_version"], "local_run_trace.v1")
        self.assertEqual(run_trace_errors, [])
        self.assertFalse(run_trace_payload["external_effect_performed"])
        self.assertFalse(run_trace_payload["host_write_performed"])
        self.assertGreaterEqual(run_trace_payload["summary"]["step_count"], 10)
        self.assertTrue(any(step["name"] == "daily_scout" for step in run_trace_payload["trace_steps"]))
        self.assertTrue(any(step["name"] == "analyst_council" for step in run_trace_payload["trace_steps"]))
        self.assertTrue(any(step["name"] == "memory_audit" for step in run_trace_payload["trace_steps"]))
        self.assertTrue(any(step["name"] == "learning_ledger" for step in run_trace_payload["trace_steps"]))
        self.assertTrue(any(step["name"] == "handoff_study_resolution" for step in run_trace_payload["trace_steps"]))
        self.assertTrue(any(step["name"] == "source_refresh_execution_brief" for step in run_trace_payload["trace_steps"]))
        self.assertTrue(any(step["name"] == "pattern_evidence_intake" for step in run_trace_payload["trace_steps"]))
        self.assertTrue(any(step["name"] == "today_surface" for step in run_trace_payload["trace_steps"]))
        self.assertEqual(run_ledger_payload["schema_version"], "daily_run_ledger.v1")
        self.assertEqual(run_ledger_errors, [])
        self.assertFalse(run_ledger_payload["external_effect_performed"])
        self.assertFalse(run_ledger_payload["host_write_performed"])
        self.assertEqual(run_ledger_payload["summary"]["today_run_count"], 1)
        self.assertEqual(run_ledger_payload["summary"]["duplicate_today_count"], 0)
        self.assertEqual(run_ledger_payload["entries"][0]["canonical_status"], "canonical")
        self.assertEqual(handoff_payload["schema_version"], "daily_handoff.v1")
        self.assertEqual(handoff_errors, [])
        self.assertFalse(handoff_payload["external_effect_performed"])
        self.assertFalse(handoff_payload["host_write_performed"])
        self.assertIn(handoff_payload["status"], {"ready", "review", "blocked"})
        self.assertGreaterEqual(handoff_payload["summary"]["carried_item_count"], 1)
        self.assertTrue(handoff_payload["copy_ready_commands"])
        self.assertIn("canonical_run", handoff_payload)
        self.assertEqual(handoff_resolution_payload["schema_version"], "handoff_study_resolution.v1")
        self.assertEqual(handoff_resolution_errors, [])
        self.assertEqual(validate_handoff_study_resolution_payload(handoff_resolution_payload), [])
        self.assertFalse(handoff_resolution_payload["external_effect_performed"])
        self.assertFalse(handoff_resolution_payload["host_write_performed"])
        self.assertGreaterEqual(handoff_resolution_payload["summary"]["resolution_item_count"], 1)
        self.assertGreaterEqual(handoff_resolution_payload["summary"]["copy_ready_response_count"], 1)
        self.assertTrue(handoff_resolution_payload["operator_rule"])
        self.assertTrue(all(item["evidence_refs"] for item in handoff_resolution_payload["items"]))
        self.assertIn("남은 질문을 공부로 닫기", handoff_resolution_html)
        self.assertNotIn("schema_version", handoff_resolution_html)
        self.assertEqual(daily_home_payload["schema_version"], "daily_operator_home.v1")
        self.assertEqual(daily_home_errors, [])
        self.assertFalse(daily_home_payload["external_effect_performed"])
        self.assertFalse(daily_home_payload["host_write_performed"])
        self.assertIn("daily_home_reads_existing_artifacts_only", daily_home_payload["safety_boundary"])
        self.assertTrue(daily_home_payload["summary"]["read_first"])
        self.assertEqual(daily_home_payload["autonomous_scout"]["mode"], "system_recommends_first_topic")
        self.assertFalse(daily_home_payload["autonomous_scout"]["operator_input_required"])
        self.assertTrue(daily_home_payload["autonomous_scout"]["why_today"])
        self.assertGreaterEqual(len(daily_home_payload["autonomous_scout"]["copy_ready_responses"]), 1)
        self.assertEqual(daily_home_payload["phone_links"]["today"], "reports/product/today.html")
        self.assertEqual(daily_home_payload["phone_links"]["daily_home"], "reports/product/daily-home.html")
        self.assertEqual(daily_home_payload["phone_links"]["phone_access"], "reports/product/phone-access.html")
        self.assertEqual(daily_home_payload["phone_links"]["memory_query"], "reports/product/memory-query.html")
        self.assertEqual(daily_home_payload["phone_links"]["learning"], "reports/product/learning.html")
        self.assertEqual(daily_home_payload["phone_links"]["source_freshness_intake"], "reports/product/source-freshness-intake.html")
        self.assertEqual(daily_home_payload["phone_links"]["source_refresh_execution"], "reports/product/source-refresh-execution.html")
        self.assertEqual(daily_home_payload["phone_links"]["handoff_study_resolution"], "reports/product/handoff-study-resolution.html")
        self.assertEqual(daily_home_payload["phone_links"]["pattern_evidence_intake"], "reports/product/pattern-evidence-intake.html")
        self.assertEqual(daily_home_payload["phone_links"]["pattern_dry_run"], "reports/product/pattern-dry-run.html")
        self.assertEqual(daily_home_payload["phone_links"]["trace"], "reports/product/run-trace.html")
        self.assertEqual(daily_home_payload["memory_recall_adoption"]["pattern_candidate_id"], "pattern-memory-recall-quality")
        self.assertEqual(daily_home_payload["memory_recall_adoption"]["proof_status"], "passed")
        self.assertEqual(daily_home_payload["memory_recall_adoption"]["query"], scout_payload["recommended_topic"]["name"])
        self.assertFalse(daily_home_payload["memory_recall_adoption"]["external_effect_performed"])
        self.assertEqual(daily_home_payload["trace_observability_adoption"]["pattern_candidate_id"], "pattern-run-trace-observability")
        self.assertEqual(daily_home_payload["trace_observability_adoption"]["proof_status"], "passed")
        self.assertEqual(daily_home_payload["trace_observability_adoption"]["status"], run_trace_payload["status"])
        self.assertEqual(daily_home_payload["trace_observability_adoption"]["run_id"], run_trace_payload["run_id"])
        self.assertGreaterEqual(daily_home_payload["trace_observability_adoption"]["step_count"], 10)
        self.assertGreaterEqual(len(daily_home_payload["trace_observability_adoption"]["what_shaped_today"]), 1)
        self.assertFalse(daily_home_payload["trace_observability_adoption"]["external_effect_performed"])
        self.assertFalse(daily_home_payload["trace_observability_adoption"]["host_write_performed"])
        self.assertEqual(daily_home_payload["source_freshness_intake_adoption"]["pattern_candidate_id"], "pattern-freshness-intake")
        self.assertFalse(daily_home_payload["source_freshness_intake_adoption"]["external_effect_performed"])
        self.assertFalse(daily_home_payload["source_freshness_intake_adoption"]["host_write_performed"])
        self.assertEqual(daily_home_payload["source_refresh_execution_adoption"]["pattern_candidate_id"], "pattern-source-refresh-final-confirmation")
        self.assertEqual(daily_home_payload["source_refresh_execution_adoption"]["status"], source_refresh_execution_payload["status"])
        self.assertFalse(daily_home_payload["source_refresh_execution_adoption"]["external_effect_performed"])
        self.assertFalse(daily_home_payload["source_refresh_execution_adoption"]["host_write_performed"])
        inbox = daily_home_payload["operator_action_inbox"]
        self.assertEqual(inbox["pattern_source"], "Hermes/OpenClaw operator handoff")
        self.assertIn(inbox["status"], {"needs_attention", "approval_review"})
        self.assertGreaterEqual(inbox["summary"]["priority_item_count"], 1)
        self.assertEqual(inbox["summary"]["pattern_scout_count"], 1)
        self.assertEqual(inbox["summary"]["pattern_scout_proof_ready_count"], 1)
        self.assertEqual(inbox["summary"]["pattern_evidence_intake_count"], 1)
        self.assertGreaterEqual(inbox["summary"]["pattern_evidence_already_verified_count"], 3)
        self.assertGreaterEqual(inbox["summary"]["unresolved_handoff_count"], 1)
        self.assertEqual(inbox["summary"]["handoff_resolution_count"], 1)
        self.assertGreaterEqual(inbox["summary"]["handoff_resolution_blocked_count"], 0)
        self.assertGreaterEqual(inbox["summary"]["carried_task_count"], 1)
        self.assertTrue(any(item["kind"] == "handoff_study_resolution" for item in inbox["priority_items"]))
        self.assertTrue(any(item["kind"] == "pattern_scout" and item["status"] == "local_proof_ready" for item in inbox["priority_items"]))
        self.assertEqual(daily_home_payload["pattern_scout_adoption"]["pattern_candidate_id"], "pattern-method-evidence-intake")
        self.assertEqual(daily_home_payload["pattern_scout_adoption"]["proof_status"], "passed")
        self.assertFalse(daily_home_payload["pattern_scout_adoption"]["operator_decision_needed"])
        self.assertEqual(daily_home_payload["pattern_evidence_intake_adoption"]["pattern_candidate_id"], "pattern-method-evidence-intake")
        self.assertEqual(daily_home_payload["pattern_evidence_intake_adoption"]["status"], pattern_evidence_payload["status"])
        self.assertGreaterEqual(daily_home_payload["pattern_evidence_intake_adoption"]["already_verified_count"], 3)
        self.assertFalse(daily_home_payload["pattern_evidence_intake_adoption"]["external_effect_performed"])
        self.assertFalse(daily_home_payload["pattern_evidence_intake_adoption"]["host_write_performed"])
        self.assertTrue(daily_home_payload["pattern_scout_adoption"]["done_when"])
        self.assertTrue(daily_home_payload["pattern_scout_adoption"]["deferred_watchlist"])
        self.assertTrue(daily_home_payload["pattern_scout_adoption"]["rejected_boundary"])
        self.assertFalse(inbox["external_effect_performed"])
        self.assertFalse(inbox["host_write_performed"])
        self.assertTrue(all(item["external_effect_performed"] is False for item in inbox["priority_items"]))
        self.assertGreaterEqual(len(daily_home_payload["daily_route"]), 6)
        self.assertTrue(any(step["title"] == "memory recall" for step in daily_home_payload["daily_route"]))
        self.assertTrue(any(step["title"] == "learning ledger" for step in daily_home_payload["daily_route"]))
        self.assertTrue(any(step["title"] == "run trace" for step in daily_home_payload["daily_route"]))
        self.assertTrue(any(step["title"] == "handoff study resolution" for step in daily_home_payload["daily_route"]))
        self.assertTrue(any(step["title"] == "source refresh execution" for step in daily_home_payload["daily_route"]))
        self.assertTrue(any(step["title"] == "pattern evidence intake" for step in daily_home_payload["daily_route"]))
        self.assertTrue(any(step["title"] == "pattern dry-run proof" for step in daily_home_payload["daily_route"]))
        self.assertEqual(access_verify_payload["schema_version"], "phone_access_verify.v1")
        self.assertEqual(access_verify_errors, [])
        self.assertEqual(access_verify_payload["status"], "ready")
        self.assertFalse(access_verify_payload["external_effect_performed"])
        self.assertFalse(access_verify_payload["host_write_performed"])
        self.assertFalse(access_verify_payload["live_network_performed"])
        self.assertFalse(access_verify_payload["public_exposure_performed"])
        self.assertEqual(access_verify_payload["summary"]["missing_link_count"], 0)
        self.assertTrue(access_verify_payload["summary"]["daily_home_local_url"].endswith("/reports/product/daily-home.html"))
        self.assertEqual(drift_review_payload["schema_version"], "local_drift_review.v1")
        self.assertEqual(drift_review_errors, [])
        self.assertFalse(drift_review_payload["external_effect_performed"])
        self.assertFalse(drift_review_payload["host_write_performed"])
        self.assertIn(drift_review_payload["status"], {"aligned", "inspect", "approval_required", "blocked"})
        self.assertIn("recommended_branch", drift_review_payload["decision"])
        self.assertEqual(review_payload["schema_version"], "daily_review.v1")
        self.assertEqual(review_errors, [])
        self.assertEqual(validate_daily_review_payload(review_payload), [])
        self.assertFalse(review_payload["external_effect_performed"])
        self.assertEqual(review_prompt_payload["schema_version"], "operator_review_prompt.v1")
        self.assertEqual(review_prompt_errors, [])
        self.assertFalse(review_prompt_payload["external_effect_performed"])
        self.assertFalse(review_prompt_payload["host_write_performed"])
        self.assertGreaterEqual(review_prompt_payload["summary"]["prompt_count"], 1)
        self.assertTrue(any("review-response-apply" in command["command"] for card in review_prompt_payload["prompt_cards"] for command in card["copy_ready_commands"]))
        self.assertEqual(review_effect_payload["schema_version"], "operator_review_effect.v1")
        self.assertEqual(review_effect_errors, [])
        self.assertFalse(review_effect_payload["external_effect_performed"])
        self.assertFalse(review_effect_payload["host_write_performed"])
        self.assertIn(review_effect_payload["status"], {"no_feedback", "applied", "not_applied", "missing_inputs"})
        self.assertEqual(scheduler_operations_payload["schema_version"], "local_scheduler_operations.v1")
        self.assertEqual(scheduler_operations_errors, [])
        self.assertFalse(scheduler_operations_payload["external_effect_performed"])
        self.assertFalse(scheduler_operations_payload["host_write_performed"])
        self.assertIn(scheduler_operations_payload["status"], {"manual_ready", "not_ready", "blocked", "activation_ready", "active_verified"})
        self.assertIn("vault_compile", manifest_payload["artifacts"])
        self.assertIn("vault", manifest_payload["artifacts"])
        self.assertIn("daily_agenda", manifest_payload["artifacts"])
        self.assertIn("daily_agenda_surface", manifest_payload["artifacts"])
        self.assertIn("daily_readiness", manifest_payload["artifacts"])
        self.assertIn("daily_readiness_surface", manifest_payload["artifacts"])
        self.assertIn("daily_review", manifest_payload["artifacts"])
        self.assertIn("daily_review_surface", manifest_payload["artifacts"])
        self.assertIn("review_prompt", manifest_payload["artifacts"])
        self.assertIn("review_prompt_surface", manifest_payload["artifacts"])
        self.assertIn("review_effect", manifest_payload["artifacts"])
        self.assertIn("review_effect_surface", manifest_payload["artifacts"])
        self.assertIn("analyst_council", manifest_payload["artifacts"])
        self.assertIn("analyst_council_surface", manifest_payload["artifacts"])
        self.assertIn("memory_query", manifest_payload["artifacts"])
        self.assertIn("memory_query_surface", manifest_payload["artifacts"])
        self.assertIn("memory_audit", manifest_payload["artifacts"])
        self.assertIn("memory_audit_surface", manifest_payload["artifacts"])
        self.assertIn("agent_pattern_radar", manifest_payload["artifacts"])
        self.assertIn("agent_pattern_radar_surface", manifest_payload["artifacts"])
        self.assertIn("pattern_dry_run_proof", manifest_payload["artifacts"])
        self.assertIn("pattern_dry_run_proof_surface", manifest_payload["artifacts"])
        self.assertIn("run_trace", manifest_payload["artifacts"])
        self.assertIn("run_trace_surface", manifest_payload["artifacts"])
        self.assertIn("daily_run_ledger", manifest_payload["artifacts"])
        self.assertIn("daily_run_ledger_surface", manifest_payload["artifacts"])
        self.assertIn("daily_handoff", manifest_payload["artifacts"])
        self.assertIn("daily_handoff_surface", manifest_payload["artifacts"])
        self.assertIn("daily_home", manifest_payload["artifacts"])
        self.assertIn("daily_home_surface", manifest_payload["artifacts"])
        self.assertIn("phone_access", manifest_payload["artifacts"])
        self.assertIn("phone_access_verify", manifest_payload["artifacts"])
        self.assertIn("phone_access_verify_surface", manifest_payload["artifacts"])
        self.assertIn("drift_review", manifest_payload["artifacts"])
        self.assertIn("drift_review_surface", manifest_payload["artifacts"])
        self.assertIn("source_refresh_brief", manifest_payload["artifacts"])
        self.assertIn("source_refresh_brief_surface", manifest_payload["artifacts"])
        self.assertIn("source_refresh_execution_brief", manifest_payload["artifacts"])
        self.assertIn("source_refresh_execution_surface", manifest_payload["artifacts"])
        self.assertIn("scheduler_operations", manifest_payload["artifacts"])
        self.assertIn("scheduler_operations_surface", manifest_payload["artifacts"])
        self.assertIn("오늘 20분 agenda", today_html)
        self.assertIn("오늘 review 기록", today_html)
        self.assertIn("오늘 피드백 가이드", today_html)
        self.assertIn("피드백 반영 확인", today_html)
        self.assertIn("방식 업데이트 레이더", today_html)
        self.assertIn("오늘 실행 trace", today_html)
        self.assertIn("방향 이탈 점검", today_html)
        self.assertIn("Semiconductor cycle note", today_html)
        self.assertIn("오늘 20분 시장 공부 순서", agenda_html)
        self.assertIn("아직 결론내리면 안 되는 이유", agenda_html)
        self.assertIn("짧게 남길 응답", agenda_html)
        self.assertIn("오늘 브리프 준비 상태", readiness_html)
        self.assertIn("Artifact freshness", readiness_html)
        self.assertIn("오늘의 개인 애널리스트 홈", daily_home_html)
        self.assertIn("오늘 닫을 것", daily_home_html)
        self.assertIn("action inbox", daily_home_html)
        self.assertIn("Scout가 먼저 고른 주제", daily_home_html)
        self.assertIn("오늘 기억 회상 품질", daily_home_html)
        self.assertIn("memory recall 열기", daily_home_html)
        self.assertIn("오늘 결과를 만든 경로", daily_home_html)
        self.assertIn("run trace 열기", daily_home_html)
        self.assertIn("방법론 intake", daily_home_html)
        self.assertIn("pattern evidence intake 열기", daily_home_html)
        self.assertIn("오늘 볼 순서", daily_home_html)
        self.assertIn("복사할 수 있는 로컬 응답", daily_home_html)
        self.assertNotIn("schema_version", daily_home_html)
        self.assertNotIn("--send", daily_home_html)
        self.assertIn("폰 접근 검증", access_verify_html)
        self.assertIn("오늘 첫 화면을 폰에서 열 준비", access_verify_html)
        self.assertNotIn("schema_version", access_verify_html)
        self.assertIn("오늘 근거 새로고침 판단", source_refresh_html)
        self.assertIn("Source actions", source_refresh_html)
        self.assertIn("개인 애널리스트 방식 업데이트", pattern_radar_html)
        self.assertIn("오늘의 방식 Scout", pattern_radar_html)
        self.assertIn("pattern evidence intake", pattern_radar_html)
        self.assertIn("넘지 않을 경계", pattern_radar_html)
        self.assertIn("Dry-run 승격 큐", pattern_radar_html)
        self.assertIn("채택 게이트", pattern_radar_html)
        self.assertIn("work-buddy", pattern_radar_html)
        self.assertIn("TraceAgent", pattern_radar_html)
        self.assertNotIn("schema_version", pattern_radar_html)
        self.assertIn("새 에이전트 패턴을 실제 루프에 넣어도 되는가", pattern_proof_html)
        self.assertIn("후보별 dry-run 증거", pattern_proof_html)
        self.assertIn("승격 가능한 후보", pattern_proof_html)
        self.assertNotIn("schema_version", pattern_proof_html)
        self.assertIn("오늘 실행 근거 추적", run_trace_html)
        self.assertIn("단계별 trace", run_trace_html)
        self.assertNotIn("schema_version", run_trace_html)
        self.assertIn("오늘 어떤 run을 믿을지", run_ledger_html)
        self.assertIn("Run history", run_ledger_html)
        self.assertNotIn("schema_version", run_ledger_html)
        self.assertIn("어제가 오늘에 반영됐나", handoff_html)
        self.assertIn("아직 남은 것", handoff_html)
        self.assertNotIn("schema_version", handoff_html)
        self.assertIn("오늘 방향 이탈 점검", drift_review_html)
        self.assertIn("판단 신호", drift_review_html)
        self.assertNotIn("schema_version", drift_review_html)
        self.assertIn("오늘 읽은 것과 내일 더 볼 것", review_html)
        self.assertIn("오늘 남길 피드백", review_prompt_html)
        self.assertIn("review-response-apply", review_prompt_html)
        self.assertIn("피드백 반영 확인", review_effect_html)
        self.assertIn("자동 실행 준비 상태", scheduler_html)
        self.assertIn("운영 증거", scheduler_html)
        self.assertIn("vault", morning_html)
        self.assertIn("readiness", morning_html)
        self.assertIn("source_refresh", morning_html)
        self.assertIn("trace", morning_html)
        self.assertIn("run_ledger", morning_html)
        self.assertIn("handoff", morning_html)
        self.assertIn("drift_review", morning_html)
        self.assertIn("review_prompt", morning_html)
        self.assertIn("review_effect", morning_html)
        self.assertIn("council", morning_html)
        self.assertIn("memory_audit", morning_html)
        self.assertIn("pattern_radar", morning_html)
        self.assertIn("pattern_dry_run", morning_html)
        self.assertIn("오늘의 방식 Scout", daily_home_html)
        self.assertIn("pattern evidence intake", daily_home_html)
        self.assertIn("scheduler", morning_html)
        self.assertIn("MyBroker Memory Query", memory_query_html)
        self.assertIn("Recall 품질", memory_query_html)
        self.assertNotIn("schema_version", memory_query_html)
        self.assertIn("개인 애널리스트 메모리 감사", memory_audit_html)
        self.assertIn("오늘 브리프 읽기 전 analyst council", council_html)
        self.assertIn("역할별 검토", council_html)
        self.assertIn("council-response-apply", council_html)
        self.assertIn("컴파일된 리서치 노트", vault_html)

    def test_daily_run_ledger_marks_latest_same_day_run_as_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trace_path = root / "run-trace.json"
            morning_path = root / "morning.json"
            readiness_path = root / "readiness.json"
            scheduler_path = root / "scheduler.json"
            archive_dir = root / "archive" / "2026-06-05"
            archive_dir.mkdir(parents=True)
            archive_path = archive_dir / "manifest.json"
            trace_path.write_text(json.dumps({
                "schema_version": "local_run_trace.v1",
                "generated_at": "2026-06-05T07:30:00+00:00",
                "status": "ready",
                "run_id": "daily-research",
                "what_shaped_today": [{"label": "근거 개수", "value": "5", "source": "evidence_catalog"}],
                "external_effect_performed": False,
                "host_write_performed": False,
            }), encoding="utf-8")
            morning_path.write_text(json.dumps({
                "schema_version": "morning_control_packet.v1",
                "generated_at": "2026-06-05T07:31:00+00:00",
                "status": "ready",
                "run_id": "daily-research",
                "external_effect_performed": False,
                "host_write_performed": False,
            }), encoding="utf-8")
            readiness_path.write_text(json.dumps({
                "schema_version": "daily_readiness.v1",
                "generated_at": "2026-06-05T07:32:00+00:00",
                "status": "ready",
                "summary": {"fresh_required_count": 8},
                "external_effect_performed": False,
                "host_write_performed": False,
            }), encoding="utf-8")
            scheduler_path.write_text(json.dumps({
                "schema_version": "local_scheduler_operations.v1",
                "generated_at": "2026-06-05T07:33:00+00:00",
                "status": "manual_ready",
                "external_effect_performed": False,
                "host_write_performed": False,
            }), encoding="utf-8")
            archive_path.write_text(json.dumps({
                "schema_version": "daily_archive.v1",
                "run_id": "daily-research",
                "generated_at": "2026-06-05T07:34:00+00:00",
                "archive_dir": archive_dir.as_posix(),
                "artifacts": {"today": "reports/product/today.html"},
                "policy": "research_only",
            }), encoding="utf-8")
            ledger_path = root / "daily-run-ledger.json"
            surface_path = root / "run-ledger.html"

            write_daily_run_ledger(
                artifact_output_path=ledger_path,
                surface_output_path=surface_path,
                run_trace_path=trace_path,
                morning_path=morning_path,
                readiness_path=readiness_path,
                scheduler_operations_path=scheduler_path,
                archive_manifest_path=archive_path,
                generated_at=datetime(2026, 6, 5, 7, 40, tzinfo=timezone.utc),
            )
            write_daily_run_ledger(
                artifact_output_path=ledger_path,
                surface_output_path=surface_path,
                run_trace_path=trace_path,
                morning_path=morning_path,
                readiness_path=readiness_path,
                scheduler_operations_path=scheduler_path,
                archive_manifest_path=archive_path,
                generated_at=datetime(2026, 6, 5, 8, 5, tzinfo=timezone.utc),
            )

            payload = json.loads(ledger_path.read_text(encoding="utf-8"))
            html = surface_path.read_text(encoding="utf-8")
            errors = validate_daily_run_ledger_file(ledger_path)

        self.assertEqual(errors, [])
        self.assertEqual(payload["summary"]["today_run_count"], 2)
        self.assertEqual(payload["summary"]["duplicate_today_count"], 1)
        self.assertEqual(sum(1 for entry in payload["entries"] if entry["canonical_status"] == "canonical"), 1)
        self.assertTrue(payload["entries"][0]["recorded_at"] > payload["entries"][1]["recorded_at"])
        self.assertEqual(payload["entries"][0]["canonical_status"], "canonical")
        self.assertEqual(payload["entries"][1]["canonical_status"], "duplicate_same_day")
        self.assertIn("canonical run", html)
        self.assertIn("Duplicates", html)

    def test_daily_handoff_summarizes_reflected_and_unresolved_carryover(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            journal_path = root / "journal.json"
            ledger_path = root / "task-ledger.json"
            review_path = root / "daily-review.json"
            effect_path = root / "review-effect.json"
            council_path = root / "council.json"
            audit_path = root / "memory-audit.json"
            scout_path = root / "scout.json"
            run_ledger_path = root / "daily-run-ledger.json"
            handoff_path = root / "daily-handoff.json"
            handoff_surface = root / "handoff.html"
            handoff_resolution_path = root / "handoff-study-resolution.json"
            handoff_resolution_surface = root / "handoff-study-resolution.html"
            learning_path = root / "learning-ledger.json"
            memory_query_path = root / "memory-query.json"
            freshness_path = root / "source-freshness-intake.json"
            review_prompt_path = root / "review-prompt.json"
            journal_path.write_text(json.dumps({
                "schema_version": "personal_analyst_journal.v1",
                "run_id": "daily-research",
                "follow_up_questions": [
                    "Semiconductors cycle에서 반대 근거는 무엇인가요?",
                    "Energy prices는 오늘 왜 약한가요?",
                ],
            }), encoding="utf-8")
            ledger_path.write_text(json.dumps({
                "schema_version": "personal_analyst_task_ledger.v1",
                "entries": [
                    {
                        "task_id": "AT-001",
                        "title": "Check Semiconductors source freshness",
                        "status": "carried",
                        "operator_note": "오늘 source freshness를 다시 확인하세요.",
                    },
                    {
                        "task_id": "AT-002",
                        "title": "Blocked live source execution",
                        "status": "blocked_requires_approval",
                    },
                ],
            }), encoding="utf-8")
            review_path.write_text(json.dumps({
                "schema_version": "daily_review.v1",
                "signals": [{"topic": "Semiconductors", "operator_note": "cycle이 중요"}],
                "summary": {"response_count": 1},
            }), encoding="utf-8")
            effect_path.write_text(json.dumps({
                "schema_version": "operator_review_effect.v1",
                "status": "applied",
                "interpretation": "review feedback shaped today's scout scoring",
                "topic_effects": [{"topic": "Semiconductors", "effect": "boosted"}],
            }), encoding="utf-8")
            council_path.write_text(json.dumps({
                "schema_version": "analyst_council.v1",
                "status": "read_with_caution",
                "decision": {"rationale": "source freshness remains weak"},
            }), encoding="utf-8")
            audit_path.write_text(json.dumps({
                "schema_version": "personal_memory_audit.v1",
                "summary": {"risk_count": 1},
                "next_questions": ["Semiconductors 기억이 최근 archive와 연결되나요?"],
            }), encoding="utf-8")
            scout_path.write_text(json.dumps({
                "schema_version": "daily_scout.v1",
                "run_id": "daily-research",
                "recommended_topic": {
                    "name": "Semiconductors",
                    "why": "cycle and source freshness are today's focus",
                    "next_question": "Semiconductors cycle에서 반대 근거는 무엇인가요?",
                },
                "recommendations": [],
            }), encoding="utf-8")
            run_ledger_path.write_text(json.dumps({
                "schema_version": "daily_run_ledger.v1",
                "canonical_entry_id": "entry-1",
                "summary": {"duplicate_today_count": 0},
                "entries": [
                    {
                        "entry_id": "entry-1",
                        "run_id": "daily-research",
                        "local_day": "2026-06-05",
                        "run_status": "ready",
                        "today_path": "reports/product/today.html",
                        "archive_manifest": "reports/archive/2026-06-05/manifest.json",
                        "recorded_at": "2026-06-05T07:40:00+00:00",
                        "canonical_status": "canonical",
                    }
                ],
            }), encoding="utf-8")
            learning_path.write_text(json.dumps({
                "schema_version": "personal_learning_ledger.v1",
                "status": "review",
                "questions": [{"question": "반도체 기대가 실제 수요 근거로 이어지나요?"}],
            }), encoding="utf-8")
            memory_query_path.write_text(json.dumps({
                "schema_version": "personal_memory_query.v1",
                "status": "ready",
                "recall_quality": {
                    "level": "usable",
                    "summary": "Semiconductors에 대한 로컬 기억이 일부 있습니다.",
                },
            }), encoding="utf-8")
            freshness_path.write_text(json.dumps({
                "schema_version": "source_freshness_intake.v1",
                "status": "approval_packet_ready",
                "summary": {
                    "stale_or_sample_source_count": 2,
                    "blocked_live_candidate_count": 1,
                },
            }), encoding="utf-8")
            review_prompt_path.write_text(json.dumps({
                "schema_version": "operator_review_prompt.v1",
                "prompt_cards": [{"title": "Semiconductors", "question": "오늘 더 볼 질문은?"}],
            }), encoding="utf-8")

            write_daily_handoff(
                artifact_output_path=handoff_path,
                surface_output_path=handoff_surface,
                journal_path=journal_path,
                task_ledger_path=ledger_path,
                daily_review_path=review_path,
                review_effect_path=effect_path,
                analyst_council_path=council_path,
                memory_audit_path=audit_path,
                scout_path=scout_path,
                run_ledger_path=run_ledger_path,
            )
            payload = json.loads(handoff_path.read_text(encoding="utf-8"))
            html = handoff_surface.read_text(encoding="utf-8")
            errors = validate_daily_handoff_file(handoff_path)
            write_handoff_study_resolution(
                artifact_output_path=handoff_resolution_path,
                surface_output_path=handoff_resolution_surface,
                handoff_path=handoff_path,
                learning_ledger_path=learning_path,
                memory_query_path=memory_query_path,
                memory_audit_path=audit_path,
                source_freshness_intake_path=freshness_path,
                analyst_council_path=council_path,
                review_prompt_path=review_prompt_path,
            )
            resolution_payload = json.loads(handoff_resolution_path.read_text(encoding="utf-8"))
            resolution_html = handoff_resolution_surface.read_text(encoding="utf-8")
            resolution_errors = validate_handoff_study_resolution_file(handoff_resolution_path)

        self.assertEqual(errors, [])
        self.assertEqual(payload["schema_version"], "daily_handoff.v1")
        self.assertEqual(payload["status"], "review")
        self.assertGreater(payload["summary"]["reflected_today_count"], 0)
        self.assertGreater(payload["summary"]["unresolved_count"], 0)
        self.assertGreater(payload["summary"]["study_closure_count"], 0)
        self.assertEqual(payload["summary"]["study_closure_count"], payload["study_closure"]["item_count"])
        self.assertTrue(any(item["kind"] == "follow_up_question" for item in payload["study_closure"]["items"]))
        self.assertTrue(any(item["kind"] == "council_warning" for item in payload["study_closure"]["items"]))
        self.assertTrue(all(item["external_effect_performed"] is False for item in payload["study_closure"]["items"]))
        self.assertTrue(any("review-response-apply" in item["copy_ready_command"] for item in payload["study_closure"]["items"]))
        self.assertTrue(any(item["kind"] == "operator_feedback" and item["reflected_today"] for item in payload["carried_forward"]))
        self.assertTrue(any(item["kind"] == "council_warning" for item in payload["unresolved"]))
        self.assertIn("어제가 오늘에 반영됐나", html)
        self.assertIn("오늘 공부로 닫을 항목", html)
        self.assertNotIn("schema_version", html)
        self.assertEqual(resolution_errors, [])
        self.assertEqual(resolution_payload["schema_version"], "handoff_study_resolution.v1")
        self.assertEqual(resolution_payload["status"], "review")
        self.assertGreaterEqual(resolution_payload["summary"]["resolution_item_count"], 1)
        self.assertGreaterEqual(resolution_payload["summary"]["study_with_freshness_caveat_count"], 1)
        self.assertEqual(resolution_payload["summary"]["blocked_by_source_freshness_count"], 0)
        self.assertTrue(any(item["status"] == "study_with_freshness_caveat" for item in resolution_payload["items"]))
        self.assertTrue(any(item["requires_live_refresh_to_finalize"] for item in resolution_payload["items"]))
        self.assertTrue(all(item["source_freshness_caveat"] for item in resolution_payload["items"]))
        self.assertTrue(all(item["evidence_refs"] for item in resolution_payload["items"]))
        self.assertIn("남은 질문을 공부로 닫기", resolution_html)
        self.assertIn("답변 후보", resolution_html)
        self.assertIn("근거 신선도 주의", resolution_html)
        self.assertNotIn("schema_version", resolution_html)

    def test_task_status_response_apply_updates_ledger_locally(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_queue = root / "tasks.json"
            ledger = root / "ledger.json"
            responses = root / "responses.jsonl"
            apply_path = root / "apply.json"
            updated_ledger = root / "ledger-updated.json"
            surface = root / "ledger.html"
            task_queue.write_text(
                json.dumps({
                    "schema_version": "personal_analyst_task_queue.v1",
                    "generated_at": "2026-06-05T00:00:00+00:00",
                    "run_id": "daily-test",
                    "status": "queued",
                    "source_journal": "journal.json",
                    "task_count": 1,
                    "tasks": [{
                        "task_id": "AT-001",
                        "role": "source_scout",
                        "title": "자료 신선도 확인",
                        "why": "gap 확인",
                        "priority": "high",
                        "status": "queued",
                        "autonomy_level": "autonomous_local",
                        "approval_scope": "local_dry_run_only",
                        "external_effect_allowed": False,
                        "requires_operator_approval": False,
                        "inputs": ["evidence.json"],
                        "suggested_command": "mybroker source-refresh-plan",
                        "stop_condition": "local_artifact_written",
                    }],
                    "reading_order": ["source_scout"],
                    "policy": "research_only",
                    "safety_boundary": ["queued_tasks_do_not_execute"],
                }),
                encoding="utf-8",
            )
            write_analyst_task_ledger(
                task_queue_path=task_queue,
                previous_ledger_path=root / "missing.json",
                status_apply_path=root / "missing-apply.json",
                artifact_output_path=ledger,
                surface_output_path=root / "initial.html",
            )
            record_task_status_response(
                response='AT-001 complete "checked dry-run source plan"',
                responses_path=responses,
            )
            apply_payload = build_task_status_apply(
                ledger_path=ledger,
                responses_path=responses,
                output_path=apply_path,
            )
            write_analyst_task_ledger(
                task_queue_path=task_queue,
                previous_ledger_path=ledger,
                status_apply_path=apply_path,
                artifact_output_path=updated_ledger,
                surface_output_path=surface,
            )
            updated = json.loads(updated_ledger.read_text(encoding="utf-8"))
            html = surface.read_text(encoding="utf-8")

        self.assertEqual(apply_payload["schema_version"], "personal_analyst_task_status_apply.v1")
        self.assertEqual(apply_payload["applied_count"], 1)
        self.assertFalse(apply_payload["external_effect_performed"])
        self.assertEqual(updated["entries"][0]["status"], "completed")
        self.assertEqual(updated["summary"]["completed"], 1)
        self.assertIn("checked dry-run source plan", html)

    def test_task_ledger_auto_completes_local_tasks_from_artifact_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_queue = root / "tasks.json"
            ledger = root / "ledger.json"
            surface = root / "ledger.html"
            evidence = root / "evidence.json"
            today = root / "today.html"
            handoff = root / "handoff.json"
            handoff_surface = root / "handoff.html"
            evidence.write_text('{"schema_version":"daily_evidence_catalog.v1"}', encoding="utf-8")
            today.write_text("<html>today</html>", encoding="utf-8")
            task_queue.write_text(
                json.dumps({
                    "schema_version": "personal_analyst_task_queue.v1",
                    "generated_at": "2026-06-05T00:00:00+00:00",
                    "run_id": "daily-test",
                    "status": "queued",
                    "source_journal": "journal.json",
                    "task_count": 1,
                    "tasks": [{
                        "task_id": "AT-001",
                        "role": "market_mapper",
                        "title": "오늘 초점 주제를 시장 지도에 다시 연결",
                        "why": "local artifacts already exist",
                        "priority": "high",
                        "status": "queued",
                        "autonomy_level": "autonomous_local",
                        "approval_scope": "local_render_only",
                        "external_effect_allowed": False,
                        "requires_operator_approval": False,
                        "inputs": [evidence.as_posix(), today.as_posix()],
                        "suggested_command": "mybroker appliance today",
                        "stop_condition": "write_or_refresh_local_artifact_without_external_effect",
                    }],
                    "reading_order": ["market_mapper"],
                    "policy": "research_only",
                    "safety_boundary": ["queued_tasks_do_not_execute"],
                }),
                encoding="utf-8",
            )
            write_analyst_task_ledger(
                task_queue_path=task_queue,
                previous_ledger_path=root / "missing.json",
                status_apply_path=root / "missing-apply.json",
                artifact_output_path=ledger,
                surface_output_path=surface,
            )
            write_daily_handoff(
                journal_path=root / "missing-journal.json",
                task_ledger_path=ledger,
                daily_review_path=root / "missing-review.json",
                review_effect_path=root / "missing-effect.json",
                analyst_council_path=root / "missing-council.json",
                memory_audit_path=root / "missing-audit.json",
                scout_path=root / "missing-scout.json",
                run_ledger_path=root / "missing-run-ledger.json",
                artifact_output_path=handoff,
                surface_output_path=handoff_surface,
            )
            payload = json.loads(ledger.read_text(encoding="utf-8"))
            handoff_payload = json.loads(handoff.read_text(encoding="utf-8"))
            html = surface.read_text(encoding="utf-8")
            ledger_errors = validate_analyst_task_ledger_file(ledger)
            handoff_errors = validate_daily_handoff_file(handoff)

        self.assertEqual(ledger_errors, [])
        self.assertEqual(handoff_errors, [])
        self.assertEqual(payload["summary"]["completed"], 1)
        self.assertEqual(payload["summary"]["carried"], 0)
        self.assertEqual(payload["entries"][0]["status"], "completed")
        self.assertEqual(payload["entries"][0]["local_completion"]["status"], "satisfied")
        self.assertEqual(payload["entries"][0]["local_completion"]["present_count"], 2)
        self.assertFalse(payload["entries"][0]["local_completion"]["external_effect_performed"])
        self.assertFalse(any(item.get("id") == "DH-AT-001" for item in handoff_payload["unresolved"]))
        self.assertIn("local proof: satisfied", html)

    def test_source_refresh_response_updates_local_proofs_without_network_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            plan_path = root / "research-plan.json"
            evidence_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            scout_path = root / "scout.json"
            refresh_plan_path = root / "source-refresh-plan.json"
            refresh_apply_path = root / "source-refresh-apply.json"
            refresh_live_gate_path = root / "source-refresh-live-gate.json"
            refresh_live_run_path = root / "source-refresh-live-run.json"
            refresh_live_preflight_path = root / "source-refresh-live-preflight.json"
            source_refresh_brief_path = root / "source-refresh-brief.json"
            source_refresh_surface_path = root / "source-refresh.html"
            source_refresh_execution_path = root / "source-refresh-execution-brief.json"
            source_refresh_execution_surface_path = root / "source-refresh-execution.html"

            init_topic_config(topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="approval-handoff")
            collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=evidence_path,
                memory_path=memory_path,
            )
            build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=root / "missing-vault.json",
                output_path=scout_path,
                run_id="approval-handoff",
            )
            build_source_refresh_plan(
                scout_path=scout_path,
                evidence_path=evidence_path,
                vault_path=root / "missing-vault.json",
                output_path=refresh_plan_path,
            )
            build_source_refresh_apply(
                refresh_plan_path=refresh_plan_path,
                output_path=refresh_apply_path,
            )
            gate = build_source_refresh_live_gate(
                refresh_apply_path=refresh_apply_path,
                output_path=refresh_live_gate_path,
            )
            response = gate["decisions"][0]["copy_ready_response"]

            result = cli_main([
                "appliance",
                "source-refresh-response",
                response,
                "--scout",
                scout_path.as_posix(),
                "--evidence",
                evidence_path.as_posix(),
                "--refresh-plan",
                refresh_plan_path.as_posix(),
                "--refresh-apply",
                refresh_apply_path.as_posix(),
                "--refresh-live-gate",
                refresh_live_gate_path.as_posix(),
                "--refresh-live-run-output",
                refresh_live_run_path.as_posix(),
                "--refresh-live-preflight-output",
                refresh_live_preflight_path.as_posix(),
                "--evidence-output",
                (root / "live-evidence.json").as_posix(),
                "--intend-execute",
                "--confirm-live-network",
                "--artifact-output",
                source_refresh_brief_path.as_posix(),
                "--output",
                source_refresh_surface_path.as_posix(),
                "--source-refresh-execution-output",
                source_refresh_execution_path.as_posix(),
                "--source-refresh-execution-surface",
                source_refresh_execution_surface_path.as_posix(),
            ])

            live_run = json.loads(refresh_live_run_path.read_text(encoding="utf-8"))
            preflight = json.loads(refresh_live_preflight_path.read_text(encoding="utf-8"))
            brief = json.loads(source_refresh_brief_path.read_text(encoding="utf-8"))
            execution_brief = json.loads(source_refresh_execution_path.read_text(encoding="utf-8"))
            html = source_refresh_surface_path.read_text(encoding="utf-8")
            execution_html = source_refresh_execution_surface_path.read_text(encoding="utf-8")
            live_run_errors = validate_source_refresh_live_run_file(refresh_live_run_path)
            preflight_errors = validate_source_refresh_live_preflight_file(refresh_live_preflight_path)
            brief_errors = validate_source_refresh_brief_file(source_refresh_brief_path)
            execution_errors = validate_source_refresh_execution_brief_file(source_refresh_execution_path)
            live_evidence_exists = (root / "live-evidence.json").exists()

        self.assertEqual(result, 0)
        self.assertEqual(live_run_errors, [])
        self.assertEqual(preflight_errors, [])
        self.assertEqual(brief_errors, [])
        self.assertEqual(execution_errors, [])
        self.assertEqual(live_run["approval_status"], "approved")
        self.assertEqual(live_run["execution"]["status"], "ready_to_execute")
        self.assertFalse(live_run["external_effect_performed"])
        self.assertEqual(preflight["status"], "passed")
        self.assertFalse(preflight["external_effect_performed"])
        self.assertEqual(brief["status"], "ready_to_execute")
        self.assertFalse(brief["external_effect_performed"])
        self.assertEqual(execution_brief["status"], "ready_for_final_confirmation")
        self.assertTrue(execution_brief["final_confirmation"]["required"])
        self.assertIn("--execute --confirm-live-network", execution_brief["final_confirmation"]["run_command_preview"])
        self.assertFalse(execution_brief["external_effect_performed"])
        self.assertFalse(execution_brief["host_write_performed"])
        self.assertEqual(validate_source_refresh_execution_brief_payload(execution_brief), [])
        self.assertIn("실행 전 최종 확인", html)
        self.assertIn("실행 전 최종 확인", execution_html)
        self.assertIn("Rollback / 재시도 원칙", execution_html)
        self.assertNotIn("schema_version", execution_html)
        self.assertFalse(live_evidence_exists)

    def test_daily_review_feedback_changes_scout_score_locally(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            plan_path = root / "research-plan.json"
            evidence_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            scout_before_path = root / "scout-before.json"
            scout_after_path = root / "scout-after.json"
            responses_path = root / "daily-review-responses.jsonl"
            review_path = root / "daily-review.json"
            review_surface_path = root / "review.html"
            review_prompt_path = root / "review-prompt.json"
            review_prompt_surface_path = root / "review-prompt.html"
            review_effect_path = root / "review-effect.json"
            review_effect_surface_path = root / "review-effect.html"

            init_topic_config(topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="review-loop")
            collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=evidence_path,
                memory_path=memory_path,
            )
            scout_before = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=root / "missing-vault.json",
                review_path=root / "missing-review.json",
                output_path=scout_before_path,
                run_id="review-loop",
            )
            topic_name = scout_before["recommended_topic"]["name"]
            record_daily_review_response(
                response=f'more "{topic_name}" "내일도 이 주제를 더 보고 싶다"',
                responses_path=responses_path,
            )
            review_surface = write_daily_review(
                scout_path=scout_before_path,
                task_status_apply_path=root / "missing-task-status.json",
                responses_path=responses_path,
                artifact_output_path=review_path,
                surface_output_path=review_surface_path,
            )
            review_prompt_surface = write_operator_review_prompt(
                scout_path=scout_before_path,
                daily_review_path=review_path,
                drift_review_path=root / "missing-drift-review.json",
                task_ledger_path=root / "missing-task-ledger.json",
                artifact_output_path=review_prompt_path,
                surface_output_path=review_prompt_surface_path,
            )
            scout_after = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=root / "missing-vault.json",
                review_path=review_path,
                output_path=scout_after_path,
                run_id="review-loop",
            )
            review_effect_surface = write_operator_review_effect(
                scout_path=scout_after_path,
                daily_review_path=review_path,
                review_prompt_path=review_prompt_path,
                artifact_output_path=review_effect_path,
                surface_output_path=review_effect_surface_path,
            )
            review_payload = json.loads(review_path.read_text(encoding="utf-8"))
            review_html = review_surface.read_text(encoding="utf-8")
            review_prompt_payload = json.loads(review_prompt_path.read_text(encoding="utf-8"))
            review_prompt_html = review_prompt_surface.read_text(encoding="utf-8")
            review_effect_payload = json.loads(review_effect_path.read_text(encoding="utf-8"))
            review_effect_html = review_effect_surface.read_text(encoding="utf-8")
            after_topic = next(row for row in scout_after["recommendations"] if row["name"] == topic_name)
            review_file_errors = validate_daily_review_file(review_path)
            review_payload_errors = validate_daily_review_payload(review_payload)
            review_prompt_errors = validate_operator_review_prompt_file(review_prompt_path)
            review_effect_errors = validate_operator_review_effect_file(review_effect_path)

        self.assertEqual(review_file_errors, [])
        self.assertEqual(review_payload_errors, [])
        self.assertEqual(review_prompt_errors, [])
        self.assertEqual(review_effect_errors, [])
        self.assertFalse(review_payload["external_effect_performed"])
        self.assertFalse(review_prompt_payload["external_effect_performed"])
        self.assertFalse(review_effect_payload["external_effect_performed"])
        self.assertEqual(review_prompt_payload["schema_version"], "operator_review_prompt.v1")
        self.assertEqual(review_effect_payload["schema_version"], "operator_review_effect.v1")
        self.assertEqual(review_effect_payload["status"], "applied")
        self.assertEqual(review_effect_payload["summary"]["applied_topic_count"], 1)
        self.assertEqual(review_payload["summary"]["signal_count"], 1)
        self.assertEqual(review_payload["topic_signals"][0]["latest_status"], "want_more")
        self.assertGreater(after_topic["review_signal"]["score_delta"], 0)
        self.assertTrue(any(factor["name"] == "operator_review" for factor in after_topic["score_factors"]))
        self.assertIn("오늘 읽은 것과 내일 더 볼 것", review_html)
        self.assertIn("오늘 남길 피드백", review_prompt_html)
        self.assertIn("review-response-apply", review_prompt_html)
        self.assertIn("피드백 반영 확인", review_effect_html)
        self.assertIn("피드백 반영됨", review_effect_html)
        self.assertIn(topic_name, review_html)
        self.assertIn(topic_name, review_prompt_html)
        self.assertIn(topic_name, review_effect_html)

    def test_daily_scout_rotation_guard_rotates_repeated_stale_topic_locally(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            plan_path = root / "research-plan.json"
            evidence_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            scout_path = root / "scout.json"
            home_path = root / "daily-home.json"
            home_surface_path = root / "daily-home.html"

            config = init_topic_config(topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="rotation-loop")
            evidence_path.write_text(json.dumps({
                "schema_version": "public_evidence_catalog.v1",
                "source_status": [],
                "collection_gaps": ["live_refresh_not_enabled"],
                "mode": "sample_cache",
            }), encoding="utf-8")
            topics = []
            for interest in config["interests"]:
                source_names = ["sample-cache", "local-vault"]
                latest_titles = [f"{interest['name']} note"]
                if interest["topic_id"] == "semiconductors":
                    source_names.append("macro-sample")
                    latest_titles.extend(["Semiconductors cycle", "AI chip supply"])
                topics.append({
                    "topic_id": interest["topic_id"],
                    "name": interest["name"],
                    "last_seen_item_ids": [f"{interest['topic_id']}-1"],
                    "latest_titles": latest_titles,
                    "source_names": source_names,
                    "new_evidence_count": 0,
                    "changed_since_previous": False,
                    "latest_summary": f"{interest['name']} stale sample",
                    "daily_questions": ["오늘 이 주제의 반대 근거는 무엇인가?"],
                    "collection_gaps": ["live_refresh_not_enabled"],
                })
            memory_path.write_text(json.dumps({
                "schema_version": "topic_memory.v1",
                "generated_at": "2026-06-06T00:00:00+00:00",
                "run_count": 67,
                "topics": topics,
                "runs": [],
                "policy": {"output_boundary": "research_only"},
            }), encoding="utf-8")

            scout = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=root / "missing-vault.json",
                review_path=root / "missing-review.json",
                output_path=scout_path,
                run_id="rotation-loop",
            )
            home_surface = write_daily_operator_home(
                scout_path=scout_path,
                artifact_output_path=home_path,
                surface_output_path=home_surface_path,
            )
            home_payload = json.loads(home_path.read_text(encoding="utf-8"))
            home_html = home_surface.read_text(encoding="utf-8")
            scout_errors = validate_daily_scout_file(scout_path)
            home_errors = validate_daily_operator_home_file(home_path)

        self.assertEqual(scout_errors, [])
        self.assertEqual(home_errors, [])
        self.assertTrue(scout["rotation_guard"]["rotated"])
        self.assertEqual(scout["rotation_guard"]["pre_rotation_topic"], "semiconductors")
        self.assertNotEqual(scout["recommended_topic"]["topic_id"], "semiconductors")
        self.assertTrue(any(factor["name"] == "coverage_rotation_guard" for factor in scout["recommended_topic"]["score_factors"]))
        self.assertEqual(home_payload["autonomous_scout"]["rotation_guard"]["status"], "rotated")
        self.assertIn("Rotation", home_html)
        self.assertIn("커버리지", home_html)

    def test_daily_scout_rotation_guard_respects_more_feedback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            plan_path = root / "research-plan.json"
            evidence_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            scout_path = root / "scout.json"
            responses_path = root / "responses.jsonl"
            review_path = root / "review.json"

            config = init_topic_config(topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="rotation-review")
            evidence_path.write_text(json.dumps({
                "schema_version": "public_evidence_catalog.v1",
                "source_status": [],
                "collection_gaps": ["live_refresh_not_enabled"],
                "mode": "sample_cache",
            }), encoding="utf-8")
            topics = []
            for interest in config["interests"]:
                source_names = ["sample-cache", "local-vault"]
                latest_titles = [f"{interest['name']} note"]
                if interest["topic_id"] == "semiconductors":
                    source_names.append("macro-sample")
                    latest_titles.extend(["Semiconductors cycle", "AI chip supply"])
                topics.append({
                    "topic_id": interest["topic_id"],
                    "name": interest["name"],
                    "last_seen_item_ids": [f"{interest['topic_id']}-1"],
                    "latest_titles": latest_titles,
                    "source_names": source_names,
                    "new_evidence_count": 0,
                    "changed_since_previous": False,
                    "latest_summary": f"{interest['name']} stale sample",
                    "daily_questions": ["오늘 이 주제의 반대 근거는 무엇인가?"],
                    "collection_gaps": ["live_refresh_not_enabled"],
                })
            memory_path.write_text(json.dumps({
                "schema_version": "topic_memory.v1",
                "generated_at": "2026-06-06T00:00:00+00:00",
                "run_count": 67,
                "topics": topics,
                "runs": [],
                "policy": {"output_boundary": "research_only"},
            }), encoding="utf-8")
            responses_path.write_text('more "Semiconductors" "아직 이 주제를 더 보고 싶다"\n', encoding="utf-8")
            review_path.write_text(json.dumps({
                "schema_version": "daily_review.v1",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary": {"response_count": 1, "signal_count": 1},
                "topic_signals": [{
                    "topic_id": "semiconductors",
                    "topic_name": "Semiconductors",
                    "latest_status": "want_more",
                    "score_delta": 1.2,
                    "reason": "operator daily review signal",
                    "responses": [{
                        "recorded_at": datetime.now(timezone.utc).isoformat(),
                        "action": "more",
                        "status": "want_more",
                        "topic": "Semiconductors",
                        "note": "아직 이 주제를 더 보고 싶다",
                        "external_effect_performed": False,
                    }],
                }],
                "external_effect_performed": False,
            }), encoding="utf-8")

            scout = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=root / "missing-vault.json",
                review_path=review_path,
                output_path=scout_path,
                run_id="rotation-review",
            )
            scout_errors = validate_daily_scout_file(scout_path)

        self.assertEqual(scout_errors, [])
        self.assertEqual(scout["rotation_guard"]["status"], "operator_override")
        self.assertFalse(scout["rotation_guard"]["rotated"])
        self.assertEqual(scout["recommended_topic"]["topic_id"], "semiconductors")
        self.assertTrue(any(factor["name"] == "operator_review" for factor in scout["recommended_topic"]["score_factors"]))

    def test_daily_scout_rotation_guard_expires_old_more_feedback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            plan_path = root / "research-plan.json"
            evidence_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            scout_path = root / "scout.json"
            review_path = root / "review.json"

            config = init_topic_config(topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="rotation-expiry")
            evidence_path.write_text(json.dumps({
                "schema_version": "public_evidence_catalog.v1",
                "source_status": [],
                "collection_gaps": ["live_refresh_not_enabled"],
                "mode": "sample_cache",
            }), encoding="utf-8")
            topics = []
            for interest in config["interests"]:
                source_names = ["sample-cache", "local-vault"]
                latest_titles = [f"{interest['name']} note"]
                if interest["topic_id"] == "semiconductors":
                    source_names.append("macro-sample")
                    latest_titles.extend(["Semiconductors cycle", "AI chip supply"])
                topics.append({
                    "topic_id": interest["topic_id"],
                    "name": interest["name"],
                    "last_seen_item_ids": [f"{interest['topic_id']}-1"],
                    "latest_titles": latest_titles,
                    "source_names": source_names,
                    "new_evidence_count": 0,
                    "changed_since_previous": False,
                    "latest_summary": f"{interest['name']} stale sample",
                    "daily_questions": ["오늘 이 주제의 반대 근거는 무엇인가?"],
                    "collection_gaps": ["live_refresh_not_enabled"],
                })
            memory_path.write_text(json.dumps({
                "schema_version": "topic_memory.v1",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "run_count": 67,
                "topics": topics,
                "runs": [],
                "policy": {"output_boundary": "research_only"},
            }), encoding="utf-8")
            review_path.write_text(json.dumps({
                "schema_version": "daily_review.v1",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary": {"response_count": 1, "signal_count": 1},
                "topic_signals": [{
                    "topic_id": "semiconductors",
                    "topic_name": "Semiconductors",
                    "latest_status": "want_more",
                    "score_delta": 1.2,
                    "reason": "operator daily review signal",
                    "responses": [{
                        "recorded_at": "2026-01-01T00:00:00+00:00",
                        "action": "more",
                        "status": "want_more",
                        "topic": "Semiconductors",
                        "note": "오래된 피드백",
                        "external_effect_performed": False,
                    }],
                }],
                "external_effect_performed": False,
            }), encoding="utf-8")

            scout = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=root / "missing-vault.json",
                review_path=review_path,
                output_path=scout_path,
                run_id="rotation-expiry",
            )
            scout_errors = validate_daily_scout_file(scout_path)

        self.assertEqual(scout_errors, [])
        self.assertEqual(scout["rotation_guard"]["status"], "rotated")
        self.assertNotEqual(scout["recommended_topic"]["topic_id"], "semiconductors")
        stale_topic = next(row for row in scout["recommendations"] if row["topic_id"] == "semiconductors")
        self.assertFalse(any(factor["name"] == "operator_review" for factor in stale_topic["score_factors"]))
        self.assertTrue(any(factor["name"] == "operator_review_expired" for factor in stale_topic["score_factors"]))

    def test_review_response_apply_refreshes_review_scout_and_effect_locally(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            plan_path = root / "research-plan.json"
            evidence_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            scout_path = root / "scout.json"
            responses_path = root / "daily-review-responses.jsonl"
            review_path = root / "daily-review.json"
            review_surface_path = root / "review.html"
            review_prompt_path = root / "review-prompt.json"
            review_prompt_surface_path = root / "review-prompt.html"
            review_effect_path = root / "review-effect.json"
            review_effect_surface_path = root / "review-effect.html"
            apply_path = root / "review-response-apply.json"
            apply_surface_path = root / "review-response-apply.html"

            init_topic_config(topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="review-apply")
            collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=evidence_path,
                memory_path=memory_path,
            )
            scout_before = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=root / "missing-vault.json",
                review_path=root / "missing-review.json",
                output_path=scout_path,
                run_id="review-apply",
            )
            topic_name = scout_before["recommended_topic"]["name"]
            result = cli_main([
                "appliance",
                "review-response-apply",
                f'more "{topic_name}" "이 주제를 내일도 더 보고 싶다"',
                "--topics",
                topics_path.as_posix(),
                "--plan",
                plan_path.as_posix(),
                "--evidence",
                evidence_path.as_posix(),
                "--memory",
                memory_path.as_posix(),
                "--vault",
                (root / "missing-vault.json").as_posix(),
                "--responses",
                responses_path.as_posix(),
                "--daily-review-output",
                review_path.as_posix(),
                "--daily-review-surface",
                review_surface_path.as_posix(),
                "--scout-output",
                scout_path.as_posix(),
                "--review-prompt-output",
                review_prompt_path.as_posix(),
                "--review-prompt-surface",
                review_prompt_surface_path.as_posix(),
                "--review-effect-output",
                review_effect_path.as_posix(),
                "--review-effect-surface",
                review_effect_surface_path.as_posix(),
                "--artifact-output",
                apply_path.as_posix(),
                "--output",
                apply_surface_path.as_posix(),
            ])

            review_payload = json.loads(review_path.read_text(encoding="utf-8"))
            scout_after = json.loads(scout_path.read_text(encoding="utf-8"))
            effect_payload = json.loads(review_effect_path.read_text(encoding="utf-8"))
            apply_payload = json.loads(apply_path.read_text(encoding="utf-8"))
            apply_html = apply_surface_path.read_text(encoding="utf-8")
            topic_after = next(row for row in scout_after["recommendations"] if row["name"] == topic_name)
            apply_errors = validate_operator_review_response_apply_file(apply_path)
            effect_errors = validate_operator_review_effect_file(review_effect_path)

        self.assertEqual(result, 0)
        self.assertEqual(apply_errors, [])
        self.assertEqual(effect_errors, [])
        self.assertEqual(review_payload["summary"]["response_count"], 1)
        self.assertEqual(scout_after["review_context"]["response_count"], 1)
        self.assertEqual(effect_payload["status"], "applied")
        self.assertEqual(apply_payload["status"], "applied")
        self.assertFalse(apply_payload["external_effect_performed"])
        self.assertFalse(apply_payload["host_write_performed"])
        self.assertTrue(any(factor["name"] == "operator_review" for factor in topic_after["score_factors"]))
        self.assertIn("피드백 응답 적용", apply_html)
        self.assertIn("응답 적용됨", apply_html)

    def test_handoff_response_apply_routes_review_feedback_and_refreshes_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            plan_path = root / "research-plan.json"
            evidence_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            scout_path = root / "scout.json"
            handoff_responses_path = root / "handoff-responses.jsonl"
            review_responses_path = root / "daily-review-responses.jsonl"
            review_path = root / "daily-review.json"
            review_surface_path = root / "review.html"
            review_prompt_path = root / "review-prompt.json"
            review_prompt_surface_path = root / "review-prompt.html"
            review_effect_path = root / "review-effect.json"
            review_effect_surface_path = root / "review-effect.html"
            handoff_path = root / "daily-handoff.json"
            handoff_surface_path = root / "handoff.html"
            apply_path = root / "handoff-response-apply.json"
            apply_surface_path = root / "handoff-response-apply.html"

            init_topic_config(topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="handoff-review-apply")
            collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=evidence_path,
                memory_path=memory_path,
            )
            scout_before = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=root / "missing-vault.json",
                review_path=root / "missing-review.json",
                output_path=scout_path,
                run_id="handoff-review-apply",
            )
            topic_name = scout_before["recommended_topic"]["name"]
            result = cli_main([
                "appliance",
                "handoff-response-apply",
                f'more "{topic_name}" "handoff에서 이어서 보고 싶다"',
                "--topics",
                topics_path.as_posix(),
                "--plan",
                plan_path.as_posix(),
                "--evidence",
                evidence_path.as_posix(),
                "--memory",
                memory_path.as_posix(),
                "--vault",
                (root / "missing-vault.json").as_posix(),
                "--responses",
                handoff_responses_path.as_posix(),
                "--review-responses",
                review_responses_path.as_posix(),
                "--daily-review-output",
                review_path.as_posix(),
                "--daily-review-surface",
                review_surface_path.as_posix(),
                "--scout-output",
                scout_path.as_posix(),
                "--review-prompt-output",
                review_prompt_path.as_posix(),
                "--review-prompt-surface",
                review_prompt_surface_path.as_posix(),
                "--review-effect-output",
                review_effect_path.as_posix(),
                "--review-effect-surface",
                review_effect_surface_path.as_posix(),
                "--handoff-output",
                handoff_path.as_posix(),
                "--handoff-surface",
                handoff_surface_path.as_posix(),
                "--artifact-output",
                apply_path.as_posix(),
                "--output",
                apply_surface_path.as_posix(),
                "--run-id",
                "handoff-review-apply",
            ])

            apply_payload = json.loads(apply_path.read_text(encoding="utf-8"))
            handoff_payload = json.loads(handoff_path.read_text(encoding="utf-8"))
            scout_after = json.loads(scout_path.read_text(encoding="utf-8"))
            apply_html = apply_surface_path.read_text(encoding="utf-8")
            apply_errors = validate_operator_handoff_response_apply_file(apply_path)
            handoff_errors = validate_daily_handoff_file(handoff_path)

        self.assertEqual(result, 0)
        self.assertEqual(apply_errors, [])
        self.assertEqual(handoff_errors, [])
        self.assertEqual(apply_payload["route"], "daily_review")
        self.assertEqual(apply_payload["status"], "applied")
        self.assertEqual(apply_payload["daily_review"]["response_count"], 1)
        self.assertEqual(apply_payload["review_effect"]["status"], "applied")
        self.assertEqual(scout_after["review_context"]["response_count"], 1)
        self.assertTrue(any("handoff-response-apply" in command["command"] for command in handoff_payload["copy_ready_commands"]))
        self.assertFalse(apply_payload["external_effect_performed"])
        self.assertFalse(apply_payload["host_write_performed"])
        self.assertIn("handoff 응답 적용", apply_html)

    def test_handoff_response_apply_routes_task_status_and_refreshes_task_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_queue_path = root / "task-queue.json"
            task_ledger_path = root / "task-ledger.json"
            task_ledger_surface_path = root / "task-ledger.html"
            task_responses_path = root / "task-responses.jsonl"
            handoff_responses_path = root / "handoff-responses.jsonl"
            task_apply_path = root / "task-status-apply.json"
            review_path = root / "daily-review.json"
            review_surface_path = root / "review.html"
            handoff_path = root / "daily-handoff.json"
            handoff_surface_path = root / "handoff.html"
            apply_path = root / "handoff-response-apply.json"
            apply_surface_path = root / "handoff-response-apply.html"
            task_queue = {
                "schema_version": "personal_analyst_task_queue.v1",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "run_id": "handoff-task-apply",
                "task_count": 1,
                "tasks": [{
                    "task_id": "AT-001",
                    "role": "beginner_tutor",
                    "title": "오늘 질문을 쉬운 언어로 풀기",
                    "priority": "high",
                    "approval_scope": "local_research_only",
                    "external_effect_allowed": False,
                    "requires_operator_approval": False,
                    "suggested_command": "local note",
                    "stop_condition": "설명이 기록됨",
                }],
                "external_effect_performed": False,
                "policy": "research_only",
            }
            task_queue_path.write_text(json.dumps(task_queue, ensure_ascii=False), encoding="utf-8")
            write_analyst_task_ledger(
                task_queue_path=task_queue_path,
                previous_ledger_path=root / "missing-ledger.json",
                status_apply_path=root / "missing-status-apply.json",
                artifact_output_path=task_ledger_path,
                surface_output_path=task_ledger_surface_path,
            )

            result = cli_main([
                "appliance",
                "handoff-response-apply",
                'AT-001 complete "폰에서 확인하고 완료"',
                "--responses",
                handoff_responses_path.as_posix(),
                "--task-responses",
                task_responses_path.as_posix(),
                "--task-queue",
                task_queue_path.as_posix(),
                "--task-ledger",
                task_ledger_path.as_posix(),
                "--task-ledger-surface",
                task_ledger_surface_path.as_posix(),
                "--task-status-apply",
                task_apply_path.as_posix(),
                "--daily-review-output",
                review_path.as_posix(),
                "--daily-review-surface",
                review_surface_path.as_posix(),
                "--handoff-output",
                handoff_path.as_posix(),
                "--handoff-surface",
                handoff_surface_path.as_posix(),
                "--artifact-output",
                apply_path.as_posix(),
                "--output",
                apply_surface_path.as_posix(),
            ])

            apply_payload = json.loads(apply_path.read_text(encoding="utf-8"))
            task_apply_payload = json.loads(task_apply_path.read_text(encoding="utf-8"))
            task_ledger_payload = json.loads(task_ledger_path.read_text(encoding="utf-8"))
            handoff_payload = json.loads(handoff_path.read_text(encoding="utf-8"))
            apply_errors = validate_operator_handoff_response_apply_file(apply_path)
            task_apply_errors = validate_task_status_apply_file(task_apply_path)
            task_ledger_errors = validate_analyst_task_ledger_file(task_ledger_path)
            handoff_errors = validate_daily_handoff_file(handoff_path)

        self.assertEqual(result, 0)
        self.assertEqual(apply_errors, [])
        self.assertEqual(task_apply_errors, [])
        self.assertEqual(task_ledger_errors, [])
        self.assertEqual(handoff_errors, [])
        self.assertEqual(apply_payload["route"], "task_status")
        self.assertEqual(apply_payload["status"], "applied")
        self.assertEqual(task_apply_payload["applied_count"], 1)
        self.assertEqual(task_ledger_payload["summary"]["completed"], 1)
        self.assertEqual(handoff_payload["artifact_inputs"]["task_ledger"], task_ledger_path.as_posix())
        self.assertFalse(apply_payload["external_effect_performed"])
        self.assertFalse(apply_payload["host_write_performed"])

    def test_council_response_apply_refreshes_review_scout_effect_and_council(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            plan_path = root / "research-plan.json"
            evidence_path = root / "evidence.json"
            memory_path = root / "memory.json"
            scout_path = root / "scout.json"
            scenario_path = root / "scenario.json"
            verdict_path = root / "verdict.json"
            journal_path = root / "journal.json"
            journal_surface_path = root / "journal.html"
            audit_path = root / "memory-audit.json"
            audit_surface_path = root / "memory-audit.html"
            council_path = root / "council.json"
            council_surface_path = root / "council.html"
            responses_path = root / "daily-review-responses.jsonl"
            review_path = root / "daily-review.json"
            review_surface_path = root / "review.html"
            review_prompt_path = root / "review-prompt.json"
            review_prompt_surface_path = root / "review-prompt.html"
            review_effect_path = root / "review-effect.json"
            review_effect_surface_path = root / "review-effect.html"
            apply_path = root / "council-response-apply.json"
            apply_surface_path = root / "council-response-apply.html"

            init_topic_config(topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="council-apply")
            collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=evidence_path,
                memory_path=memory_path,
            )
            scout_before = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                vault_path=root / "missing-vault.json",
                review_path=root / "missing-review.json",
                output_path=scout_path,
                run_id="council-apply",
            )
            scenario = run_market_simulation(seed_sources=["examples/seeds"], evidence_catalog_path=evidence_path, run_id="council-apply")
            write_scenario_report(scenario, scenario_path)
            write_verdict(scenario, verdict_path)
            write_analyst_journal(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                scout_path=scout_path,
                artifact_output_path=journal_path,
                surface_output_path=journal_surface_path,
            )
            write_memory_audit(
                memory_path=memory_path,
                archive_root=root / "archive",
                evidence_path=evidence_path,
                vault_path=root / "missing-vault.json",
                daily_review_path=root / "missing-review.json",
                output_path=audit_path,
                surface_path=audit_surface_path,
            )
            write_analyst_council(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                journal_path=journal_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                memory_audit_path=audit_path,
                scout_path=scout_path,
                artifact_output_path=council_path,
                surface_output_path=council_surface_path,
            )
            initial_council = json.loads(council_path.read_text(encoding="utf-8"))
            response = initial_council["copy_ready_commands"][0]["response"]
            result = cli_main([
                "appliance",
                "council-response-apply",
                response,
                "--topics",
                topics_path.as_posix(),
                "--plan",
                plan_path.as_posix(),
                "--evidence",
                evidence_path.as_posix(),
                "--memory",
                memory_path.as_posix(),
                "--vault",
                (root / "missing-vault.json").as_posix(),
                "--responses",
                responses_path.as_posix(),
                "--daily-review-output",
                review_path.as_posix(),
                "--daily-review-surface",
                review_surface_path.as_posix(),
                "--scout-output",
                scout_path.as_posix(),
                "--review-prompt-output",
                review_prompt_path.as_posix(),
                "--review-prompt-surface",
                review_prompt_surface_path.as_posix(),
                "--review-effect-output",
                review_effect_path.as_posix(),
                "--review-effect-surface",
                review_effect_surface_path.as_posix(),
                "--scenario",
                scenario_path.as_posix(),
                "--verdict",
                verdict_path.as_posix(),
                "--journal",
                journal_path.as_posix(),
                "--memory-audit",
                audit_path.as_posix(),
                "--council-output",
                council_path.as_posix(),
                "--council-surface",
                council_surface_path.as_posix(),
                "--artifact-output",
                apply_path.as_posix(),
                "--output",
                apply_surface_path.as_posix(),
                "--run-id",
                "council-apply",
            ])

            review_payload = json.loads(review_path.read_text(encoding="utf-8"))
            scout_after = json.loads(scout_path.read_text(encoding="utf-8"))
            effect_payload = json.loads(review_effect_path.read_text(encoding="utf-8"))
            council_payload = json.loads(council_path.read_text(encoding="utf-8"))
            apply_payload = json.loads(apply_path.read_text(encoding="utf-8"))
            apply_html = apply_surface_path.read_text(encoding="utf-8")
            topic_name = scout_before["recommended_topic"]["name"]
            topic_after = next(row for row in scout_after["recommendations"] if row["name"] == topic_name)
            apply_errors = validate_operator_council_response_apply_file(apply_path)
            council_errors = validate_analyst_council_file(council_path)

        self.assertEqual(result, 0)
        self.assertEqual(apply_errors, [])
        self.assertEqual(council_errors, [])
        self.assertEqual(review_payload["summary"]["response_count"], 1)
        self.assertEqual(scout_after["review_context"]["response_count"], 1)
        self.assertEqual(effect_payload["status"], "applied")
        self.assertEqual(apply_payload["status"], "applied")
        self.assertFalse(apply_payload["external_effect_performed"])
        self.assertFalse(apply_payload["host_write_performed"])
        self.assertIn(council_payload["status"], {"ready_to_read", "read_with_caution", "blocked"})
        self.assertTrue(any(factor["name"] == "operator_review" for factor in topic_after["score_factors"]))
        self.assertIn("council 응답 적용", apply_html)
        self.assertIn("갱신된 화면", apply_html)


if __name__ == "__main__":
    unittest.main()
