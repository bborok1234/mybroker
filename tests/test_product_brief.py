from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mybroker.product_brief import write_product_brief
from mybroker.public_evidence import build_public_evidence_catalog, write_public_evidence_catalog
from mybroker.scenario import run_market_simulation, write_scenario_report, write_verdict


class ProductBriefTests(unittest.TestCase):
    def test_product_brief_is_user_facing_and_hides_internal_terms(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence_path = write_public_evidence_catalog(build_public_evidence_catalog(), root / "evidence.json")
            report = run_market_simulation(
                seed_sources=["examples/seeds"],
                profile_path="examples/profiles/beginner-conservative.json",
                evidence_catalog_path=evidence_path,
                run_id="brief-sim",
            )
            scenario_path = write_scenario_report(report, root / "scenario.json")
            verdict_path = write_verdict(report, root / "verdict.json")

            brief_path = write_product_brief(scenario_path, verdict_path, root / "market-brief.html")
            html = brief_path.read_text(encoding="utf-8")

        self.assertIn("MyBroker 시장 브리프", html)
        self.assertIn("오늘 바뀐 점", html)
        self.assertIn("시장 관계 지도", html)
        self.assertIn("세 가지 경로", html)
        self.assertIn("다음에 확인할 질문", html)
        self.assertIn("안전 경계", html)
        self.assertNotIn("adapter_id", html)
        self.assertNotIn("schema_version", html)
        self.assertNotIn("Flyhigh", html)
        self.assertNotIn("validation", html.lower())


if __name__ == "__main__":
    unittest.main()
