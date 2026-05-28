from __future__ import annotations

import unittest

from mybroker.policy import classify_action


class PolicyTests(unittest.TestCase):
    def test_research_note_is_allowed(self) -> None:
        decision = classify_action("research_note")

        self.assertTrue(decision.allowed)
        self.assertFalse(decision.human_review_required)

    def test_order_execution_is_blocked(self) -> None:
        decision = classify_action("order_execution")

        self.assertFalse(decision.allowed)
        self.assertTrue(decision.human_review_required)

    def test_unknown_action_requires_review(self) -> None:
        decision = classify_action("new_action")

        self.assertFalse(decision.allowed)
        self.assertTrue(decision.human_review_required)


if __name__ == "__main__":
    unittest.main()
