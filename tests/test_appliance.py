from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from mybroker.cli import main as cli_main
from mybroker.appliance import (
    archive_daily_run,
    send_notification_payload,
    build_task_status_apply,
    record_task_status_response,
    write_analyst_journal,
    write_analyst_task_queue,
    write_analyst_task_ledger,
    write_launchd_assets,
    write_morning_control_packet,
    write_memory_query,
    write_memory_surface,
    write_notification_payload,
    write_operator_decision_apply,
    write_operator_decision_packet,
    write_phone_access_plan,
    write_runtime_doctor,
    write_runtime_playbook,
    write_scheduler_activation_verify,
    write_scheduler_activation_preflight,
    write_scheduler_status,
    write_scheduler_apply,
    write_scheduler_operations,
    write_scheduler_run_once,
    write_source_refresh_brief,
    write_today_surface,
    validate_morning_control_packet_file,
    validate_daily_brief_agenda_file,
    validate_daily_brief_agenda_payload,
    validate_daily_readiness_file,
    validate_daily_readiness_payload,
    validate_scheduler_operations_file,
    validate_scheduler_operations_payload,
    validate_source_refresh_brief_file,
    validate_source_refresh_brief_payload,
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
        self.assertIn("MyBroker Analyst Tasks", tasks_html)
        self.assertIn("역할별 큐", tasks_html)
        self.assertEqual(tasks_payload["schema_version"], "personal_analyst_task_queue.v1")
        self.assertGreaterEqual(tasks_payload["task_count"], 6)
        self.assertFalse(any(task["external_effect_allowed"] for task in tasks_payload["tasks"]))
        self.assertIn("MyBroker Task Ledger", ledger_html)
        self.assertIn("상태별 작업", ledger_html)
        self.assertEqual(ledger_payload["schema_version"], "personal_analyst_task_ledger.v1")
        self.assertEqual(ledger_payload["summary"]["ready_for_local_work"], ledger_payload["entry_count"])
        self.assertIn("MyBroker Memory", memory_html)
        self.assertIn("주제별 누적 기억", memory_html)
        self.assertIn("근거 품질 추적", memory_html)
        self.assertEqual(query_payload["schema_version"], "personal_memory_query.v1")
        self.assertEqual(query_payload["status"], "matched")
        self.assertGreaterEqual(query_payload["matched_topic_count"], 1)
        self.assertIn("MyBroker Memory Query", query_html)
        self.assertIn("다음에 확인할 질문", query_html)
        self.assertNotIn("schema_version", query_html)
        self.assertNotIn("schema_version", html)
        self.assertNotIn("Flyhigh", html)
        self.assertEqual(notification_payload["schema_version"], "notification_delivery.v1")
        self.assertEqual(notification_payload["delivery_status"], "dry_run_ready")
        self.assertIn("TELEGRAM_BOT_TOKEN", notification_payload["required_env"])
        self.assertEqual(access_payload["schema_version"], "phone_access_plan.v1")
        self.assertEqual(access_payload["recommended_path"], "tailscale_serve_private")
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
        self.assertEqual(validate_source_refresh_brief_payload(source_refresh_brief_payload), [])
        self.assertIn("오늘 근거 새로고침 판단", source_refresh_brief_html)
        self.assertNotIn("schema_version", source_refresh_brief_html)
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
            scenario_report = run_market_simulation(seed_sources=["examples/seeds"], run_id="vault-today")
            scenario_path = write_scenario_report(scenario_report, root / "reports" / "scenario.json")
            verdict_path = write_verdict(scenario_report, root / "reports" / "verdict.json")
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
            memory_surface_html = memory_surface.read_text(encoding="utf-8")
            query_surface_html = query_surface.read_text(encoding="utf-8")
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
        self.assertIn("관련 Vault 노트", query_surface_html)
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
            journal_payload = json.loads((root / "reports" / "memory" / "analyst-journal.json").read_text(encoding="utf-8"))
            morning_payload = json.loads((root / "reports" / "runtime" / "morning-control.json").read_text(encoding="utf-8"))
            agenda_payload = json.loads((root / "reports" / "daily" / "brief-agenda.json").read_text(encoding="utf-8"))
            agenda_errors = validate_daily_brief_agenda_file(root / "reports" / "daily" / "brief-agenda.json")
            readiness_payload = json.loads((root / "reports" / "runtime" / "daily-readiness.json").read_text(encoding="utf-8"))
            readiness_errors = validate_daily_readiness_file(root / "reports" / "runtime" / "daily-readiness.json")
            source_refresh_brief_payload = json.loads((root / "reports" / "runtime" / "source-refresh-brief.json").read_text(encoding="utf-8"))
            source_refresh_brief_errors = validate_source_refresh_brief_file(root / "reports" / "runtime" / "source-refresh-brief.json")
            scheduler_operations_payload = json.loads((root / "reports" / "runtime" / "scheduler-operations.json").read_text(encoding="utf-8"))
            scheduler_operations_errors = validate_scheduler_operations_file(root / "reports" / "runtime" / "scheduler-operations.json")
            manifest_payload = json.loads((root / "reports" / "archive" / "2026-06-05" / "manifest.json").read_text(encoding="utf-8"))
            today_html = (root / "reports" / "product" / "today.html").read_text(encoding="utf-8")
            morning_html = (root / "reports" / "product" / "morning.html").read_text(encoding="utf-8")
            agenda_html = (root / "reports" / "product" / "daily-agenda.html").read_text(encoding="utf-8")
            readiness_html = (root / "reports" / "product" / "readiness.html").read_text(encoding="utf-8")
            source_refresh_html = (root / "reports" / "product" / "source-refresh.html").read_text(encoding="utf-8")
            scheduler_html = (root / "reports" / "product" / "scheduler.html").read_text(encoding="utf-8")
            vault_html = (root / "reports" / "product" / "vault.html").read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertEqual(vault_payload["schema_version"], "knowledge_vault_compile.v1")
        self.assertEqual(vault_payload["compiled_count"], 1)
        self.assertEqual(vault_payload["compiled_notes"][0]["title"], "Semiconductor cycle note")
        self.assertTrue(any(item.get("linked_vault_notes") for item in scout_payload["recommendations"]))
        self.assertEqual(memory_index["vault_notes"][0]["title"], "Semiconductor cycle note")
        self.assertIn("vault note 1개", journal_payload["role_notes"][4]["finding"])
        self.assertIn("vault", morning_payload["phone_links"])
        self.assertIn("agenda", morning_payload["phone_links"])
        self.assertIn("readiness", morning_payload["phone_links"])
        self.assertIn("scheduler", morning_payload["phone_links"])
        self.assertIn("source_refresh", morning_payload["phone_links"])
        self.assertEqual(agenda_payload["schema_version"], "daily_brief_agenda.v1")
        self.assertEqual(agenda_errors, [])
        self.assertEqual(validate_daily_brief_agenda_payload(agenda_payload), [])
        self.assertIn("phone_first_local_personal_analyst", agenda_payload["mode"])
        self.assertGreaterEqual(len(agenda_payload["study_sequence"]), 4)
        self.assertTrue(any(role["role"] == "skeptic" for role in agenda_payload["role_brief"]))
        self.assertEqual(readiness_payload["schema_version"], "daily_readiness.v1")
        self.assertEqual(readiness_errors, [])
        self.assertEqual(validate_daily_readiness_payload(readiness_payload), [])
        self.assertFalse(readiness_payload["external_effect_performed"])
        self.assertIn(readiness_payload["status"], {"ready", "review", "stale", "blocked"})
        self.assertTrue(any(item["name"] == "daily_agenda" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "source_refresh_brief" for item in readiness_payload["artifacts"]))
        self.assertTrue(any(item["name"] == "scheduler_operations" for item in readiness_payload["artifacts"]))
        self.assertIn("source_refresh", readiness_payload["phone_links"])
        self.assertIn("scheduler", readiness_payload["phone_links"])
        self.assertEqual(source_refresh_brief_payload["schema_version"], "source_refresh_brief.v1")
        self.assertEqual(source_refresh_brief_errors, [])
        self.assertFalse(source_refresh_brief_payload["external_effect_performed"])
        self.assertFalse(source_refresh_brief_payload["host_write_performed"])
        self.assertIn(source_refresh_brief_payload["status"], {"local_ready", "approval_required", "preflight_required", "ready_to_execute", "executed", "blocked", "no_refresh_needed"})
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
        self.assertIn("source_refresh_brief", manifest_payload["artifacts"])
        self.assertIn("source_refresh_brief_surface", manifest_payload["artifacts"])
        self.assertIn("scheduler_operations", manifest_payload["artifacts"])
        self.assertIn("scheduler_operations_surface", manifest_payload["artifacts"])
        self.assertIn("오늘 20분 agenda", today_html)
        self.assertIn("Semiconductor cycle note", today_html)
        self.assertIn("오늘 20분 시장 공부 순서", agenda_html)
        self.assertIn("아직 결론내리면 안 되는 이유", agenda_html)
        self.assertIn("오늘 브리프 준비 상태", readiness_html)
        self.assertIn("Artifact freshness", readiness_html)
        self.assertIn("오늘 근거 새로고침 판단", source_refresh_html)
        self.assertIn("Source actions", source_refresh_html)
        self.assertIn("자동 실행 준비 상태", scheduler_html)
        self.assertIn("운영 증거", scheduler_html)
        self.assertIn("vault", morning_html)
        self.assertIn("readiness", morning_html)
        self.assertIn("source_refresh", morning_html)
        self.assertIn("scheduler", morning_html)
        self.assertIn("컴파일된 리서치 노트", vault_html)

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


if __name__ == "__main__":
    unittest.main()
