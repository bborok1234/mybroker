from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mybroker.reports import load_report, validate_report_file, validate_report_payload
from mybroker.runner import run_research_task


class ReportTests(unittest.TestCase):
    def test_research_runner_writes_valid_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"

            report = run_research_task(output_path=output, run_id="test-run")
            payload = load_report(output)

        self.assertEqual(report.run_id, "test-run")
        self.assertEqual(payload["schema_version"], "research_report.v1")
        self.assertEqual(payload["summary"]["total_signals"], 2)
        self.assertEqual(payload["policy"]["kind"], "signal_generation")
        self.assertEqual(payload["data_quality"]["status"], "pass")
        self.assertEqual(validate_report_payload(payload), [])

    def test_report_validator_rejects_missing_fields(self) -> None:
        errors = validate_report_payload({"schema_version": "research_report.v1"})

        self.assertTrue(any("missing required report fields" in error for error in errors))

    def test_report_file_validator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            run_research_task(output_path=output)

            errors = validate_report_file(output)

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
