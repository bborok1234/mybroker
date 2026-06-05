from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mybroker.appliance import (
    archive_daily_run,
    write_launchd_assets,
    write_notification_payload,
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
            plan_path = root / "research-plan.json"
            evidence_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            scenario_path = root / "scenario.json"
            verdict_path = root / "verdict.json"
            brief_path = root / "market-brief.html"
            today_path = root / "today.html"
            init_topic_config(topics_path)
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
            playbook = write_runtime_playbook(root / "playbook.json")
            assets = write_launchd_assets(project_root=root, output_dir=root / "ops", hour=7, minute=15)

            html = today.read_text(encoding="utf-8")
            notification_payload = json.loads(notification.read_text(encoding="utf-8"))
            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
            playbook_payload = json.loads(playbook.read_text(encoding="utf-8"))
            script_exists = Path(assets["script"]).exists()
            plist_exists = Path(assets["plist"]).exists()

        self.assertIn("MyBroker Today", html)
        self.assertIn("오늘 시장을 이해하기 위한 5분 브리프", html)
        self.assertIn("아카이브 manifest", html)
        self.assertNotIn("schema_version", html)
        self.assertNotIn("Flyhigh", html)
        self.assertEqual(notification_payload["schema_version"], "notification_delivery.v1")
        self.assertEqual(notification_payload["delivery_status"], "dry_run_ready")
        self.assertIn("TELEGRAM_BOT_TOKEN", notification_payload["required_env"])
        self.assertEqual(manifest_payload["schema_version"], "daily_archive.v1")
        self.assertIn("Hermes Agent", {item["source"] for item in playbook_payload["absorbed_patterns"]})
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


if __name__ == "__main__":
    unittest.main()
