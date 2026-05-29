from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mybroker.profile import load_beginner_profile, validate_profile_file, validate_profile_payload


class ProfileTests(unittest.TestCase):
    def test_sample_profile_validates_and_loads(self) -> None:
        profile = load_beginner_profile("examples/profiles/beginner-conservative.json")

        self.assertEqual(profile.profile_id, "beginner-conservative")
        self.assertEqual(validate_profile_file("examples/profiles/beginner-conservative.json"), [])

    def test_profile_validator_rejects_invalid_risk(self) -> None:
        errors = validate_profile_payload({
            "profile_id": "bad",
            "experience_level": "new",
            "learning_goal": "market_overview",
            "risk_comfort": "reckless",
            "time_horizon": "months",
            "decision_style": "risk_first",
        })

        self.assertTrue(any("invalid risk_comfort" in error for error in errors))

    def test_load_profile_raises_on_invalid_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(json.dumps({"profile_id": "bad"}), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_beginner_profile(path)


if __name__ == "__main__":
    unittest.main()
