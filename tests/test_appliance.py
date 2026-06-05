from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mybroker.appliance import (
    archive_daily_run,
    send_notification_payload,
    write_launchd_assets,
    write_memory_query,
    write_memory_surface,
    write_notification_payload,
    write_phone_access_plan,
    write_runtime_doctor,
    write_runtime_playbook,
    write_today_surface,
)
from mybroker.public_evidence import build_public_evidence_catalog, write_public_evidence_catalog
from mybroker.scenario import run_market_simulation, write_scenario_report, write_verdict
from mybroker.topics import build_research_plan, collect_topic_evidence, init_topic_config


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

            today = write_today_surface(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                brief_path=brief_path,
                output_path=today_path,
            )
            manifest = archive_daily_run(
                run_id="daily-test",
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                evidence_path=evidence_path,
                memory_path=memory_path,
                brief_path=brief_path,
                today_path=today,
                archive_root=root / "archive",
            )
            today = write_today_surface(
                scenario_path=scenario_path,
                verdict_path=verdict_path,
                memory_path=memory_path,
                evidence_path=evidence_path,
                brief_path=brief_path,
                output_path=today_path,
                archive_manifest_path=manifest,
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

            html = today.read_text(encoding="utf-8")
            memory_html = memory_surface.read_text(encoding="utf-8")
            query_payload = json.loads((root / "memory-query.json").read_text(encoding="utf-8"))
            query_html = query_surface.read_text(encoding="utf-8")
            notification_payload = json.loads(notification.read_text(encoding="utf-8"))
            access_payload = json.loads(access_plan.read_text(encoding="utf-8"))
            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
            playbook_payload = json.loads(playbook.read_text(encoding="utf-8"))
            doctor_payload = json.loads(doctor.read_text(encoding="utf-8"))
            script_exists = Path(assets["script"]).exists()
            plist_exists = Path(assets["plist"]).exists()

        self.assertIn("MyBroker Today", html)
        self.assertIn("오늘 시장을 이해하기 위한 5분 브리프", html)
        self.assertIn("근거 품질", html)
        self.assertIn("아카이브 manifest", html)
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
        self.assertIn("Hermes Agent", {item["source"] for item in playbook_payload["absorbed_patterns"]})
        self.assertEqual(doctor_payload["schema_version"], "local_runtime_doctor.v1")
        self.assertEqual(doctor_payload["status"], "ready")
        self.assertEqual(doctor_payload["fail_count"], 0)
        self.assertIn("launchd_loaded", {item["name"] for item in doctor_payload["checks"]})
        self.assertTrue(doctor_payload["install_boundary"]["launchd_install_is_host_level"])
        self.assertTrue(script_exists)
        self.assertTrue(plist_exists)

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


if __name__ == "__main__":
    unittest.main()
