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
        self.assertIn("MyBroker Report Dashboard", html)
        self.assertIn("Latest Run", html)

    def test_discovers_nested_report_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reports_dir = Path(directory) / "runs"
            report_path = reports_dir / "nested" / "report.json"
            run_research_task(output_path=report_path)

            reports = discover_report_files(reports_dir)

        self.assertEqual([path.name for path in reports], ["report.json"])


if __name__ == "__main__":
    unittest.main()
