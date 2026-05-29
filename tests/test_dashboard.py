from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mybroker.dashboard import build_report_rollup, discover_report_files, write_dashboard, write_rollup
from mybroker.runner import run_research_task


class DashboardTests(unittest.TestCase):
    def test_rollup_summarizes_valid_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reports_dir = Path(directory) / "runs"
            report_path = reports_dir / "report.json"
            run_research_task(output_path=report_path, run_id="dashboard-run")

            rollup = build_report_rollup(reports_dir)

        self.assertEqual(rollup["schema_version"], "report_rollup.v1")
        self.assertEqual(rollup["report_count"], 1)
        self.assertEqual(rollup["latest_report"]["run_id"], "dashboard-run")
        self.assertTrue(rollup["latest_report"]["validation"]["valid"])
        self.assertEqual(rollup["latest_report"]["data_quality"]["status"], "pass")
        self.assertEqual(rollup["totals"]["total_signals"], 2)

    def test_empty_rollup_is_valid_operator_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            rollup = build_report_rollup(Path(directory) / "missing")

        self.assertEqual(rollup["report_count"], 0)
        self.assertIsNone(rollup["latest_report"])
        self.assertEqual(rollup["totals"]["total_signals"], 0)

    def test_writes_dashboard_and_rollup_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reports_dir = Path(directory) / "runs"
            run_research_task(output_path=reports_dir / "report.json")
            rollup = build_report_rollup(reports_dir)
            dashboard_path = write_dashboard(rollup, Path(directory) / "dashboard.html")
            rollup_path = write_rollup(rollup, Path(directory) / "rollup.json")

            html = dashboard_path.read_text(encoding="utf-8")
            rollup_exists = rollup_path.exists()

        self.assertTrue(rollup_exists)
        self.assertIn("MyBroker 산출물 운영 대시보드", html)
        self.assertIn("가격 데이터 리서치 최신 실행", html)
        self.assertIn("Data Quality", html)

    def test_dashboard_includes_scenario_artifacts(self) -> None:
        from mybroker.public_evidence import build_public_evidence_catalog, write_public_evidence_catalog
        from mybroker.scenario import run_market_simulation, write_scenario_report

        with tempfile.TemporaryDirectory() as directory:
            reports_dir = Path(directory) / "runs"
            scenarios_dir = Path(directory) / "scenarios"
            evidence_path = write_public_evidence_catalog(
                build_public_evidence_catalog(),
                Path(directory) / "evidence" / "public-evidence.json",
            )
            run_research_task(output_path=reports_dir / "report.json")
            scenario = run_market_simulation(
                seed_sources=["examples/seeds"],
                profile_path="examples/profiles/beginner-conservative.json",
                evidence_catalog_path=evidence_path,
                run_id="dashboard-sim",
            )
            write_scenario_report(scenario, scenarios_dir / "scenario.json")

            rollup = build_report_rollup(reports_dir)
            dashboard_path = write_dashboard(rollup, Path(directory) / "dashboard.html")
            html = dashboard_path.read_text(encoding="utf-8")

        self.assertEqual(rollup["scenario_count"], 1)
        self.assertEqual(rollup["latest_scenario"]["run_id"], "dashboard-sim")
        self.assertEqual(rollup["latest_scenario"]["profile_context"]["profile_id"], "beginner-conservative")
        self.assertIn("Scenario artifact", html)
        self.assertIn("Output boundary", html)
        self.assertIn("Public evidence artifact coverage", html)
        self.assertIn("의미 있음", html)
        self.assertNotIn("다음 행동 후보", html)
        self.assertNotIn("MiroFish 참고 초보자 보기", html)

    def test_dashboard_includes_daily_research_ops_without_product_ui(self) -> None:
        from mybroker.topics import build_research_plan, collect_topic_evidence, init_topic_config

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reports_dir = root / "reports" / "runs"
            topics_path = root / "topics.json"
            plan_path = root / "reports" / "daily" / "research-plan.json"
            catalog_path = root / "reports" / "evidence" / "daily-evidence-catalog.json"
            memory_path = root / "reports" / "memory" / "topic-memory.json"
            init_topic_config(topics_path)
            build_research_plan(topics_path=topics_path, output_path=plan_path)
            collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=catalog_path,
                memory_path=memory_path,
            )

            rollup = build_report_rollup(reports_dir)
            dashboard_path = write_dashboard(rollup, root / "reports" / "dashboard.html")
            html = dashboard_path.read_text(encoding="utf-8")

        self.assertTrue(rollup["daily_research"]["ready"])
        self.assertIn("Daily research loop 상태", html)
        self.assertIn("Topic memory", html)
        self.assertIn("Collection gaps", html)
        self.assertNotIn("다음 행동 후보", html)

    def test_rollup_compares_latest_against_previous(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reports_dir = Path(directory) / "runs"
            run_research_task(output_path=reports_dir / "a.json", run_id="run-a")
            run_research_task(output_path=reports_dir / "b.json", run_id="run-b")

            rollup = build_report_rollup(reports_dir)

        self.assertTrue(rollup["latest_vs_previous"]["available"])
        self.assertEqual(rollup["latest_vs_previous"]["delta_total_signals"], 0)

    def test_discovers_nested_report_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reports_dir = Path(directory) / "runs"
            report_path = reports_dir / "nested" / "report.json"
            run_research_task(output_path=report_path)

            reports = discover_report_files(reports_dir)

        self.assertEqual([path.name for path in reports], ["report.json"])


if __name__ == "__main__":
    unittest.main()
