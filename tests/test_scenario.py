from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mybroker.scenario import (
    build_verdict,
    run_market_simulation,
    scenario_report_to_dict,
    validate_scenario_file,
    validate_scenario_payload,
    validate_verdict_payload,
    write_scenario_report,
    write_verdict,
)


class ScenarioTests(unittest.TestCase):
    def test_market_simulation_builds_beginner_report(self) -> None:
        report = run_market_simulation(seed_sources=["examples/seeds"], run_id="test-scenario")
        payload = scenario_report_to_dict(report)

        self.assertEqual(report.schema_version, "scenario_report.v1")
        self.assertEqual(report.run_id, "test-scenario")
        self.assertGreaterEqual(len(report.market_map.entities), 3)
        self.assertEqual(len(report.scenarios), 3)
        self.assertTrue(any(candidate.action_type == "learn" for candidate in report.action_candidates))
        self.assertEqual(report.policy.kind, "scenario_simulation")
        self.assertTrue(report.policy.allowed)
        self.assertIn("seed_sources", payload)

    def test_scenario_report_and_verdict_validate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = run_market_simulation(seed_sources=["examples/seeds"], run_id="validation-scenario")
            scenario_path = write_scenario_report(report, Path(directory) / "scenario.json")
            verdict_path = write_verdict(report, Path(directory) / "verdict.json")

            scenario_errors = validate_scenario_file(scenario_path)
            verdict_errors = validate_verdict_payload(json.loads(verdict_path.read_text(encoding="utf-8")))

        self.assertEqual(scenario_errors, [])
        self.assertEqual(verdict_errors, [])

    def test_validator_rejects_missing_market_map(self) -> None:
        errors = validate_scenario_payload({"schema_version": "scenario_report.v1"})

        self.assertTrue(any("missing required scenario fields" in error for error in errors))

    def test_verdict_keeps_action_candidate_boundary(self) -> None:
        report = run_market_simulation(seed_sources=["examples/seeds"])
        verdict = build_verdict(report)

        self.assertEqual(verdict["schema_version"], "market_verdict.v1")
        self.assertIn(verdict["primary_next_step"]["action_type"], {"learn", "observe", "watchlist", "defer"})
        self.assertIn("매수 지시", verdict["operator_note"])


if __name__ == "__main__":
    unittest.main()
