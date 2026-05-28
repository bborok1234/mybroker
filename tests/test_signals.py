from __future__ import annotations

import unittest
from datetime import date

from mybroker.models import PriceBar
from mybroker.signals import momentum_signals


class MomentumSignalTests(unittest.TestCase):
    def test_positive_watch_signal_has_evidence(self) -> None:
        bars = [
            PriceBar("ABC", date(2026, 1, 1), 100.0),
            PriceBar("ABC", date(2026, 1, 2), 101.0),
            PriceBar("ABC", date(2026, 1, 3), 103.0),
            PriceBar("ABC", date(2026, 1, 4), 106.0),
            PriceBar("ABC", date(2026, 1, 5), 110.0),
        ]

        [signal] = momentum_signals(bars)

        self.assertEqual(signal.symbol, "ABC")
        self.assertEqual(signal.direction, "positive_watch")
        self.assertGreater(signal.score, 0)
        self.assertIn("short_window=3", signal.evidence)

    def test_insufficient_data_is_not_actionable(self) -> None:
        bars = [PriceBar("XYZ", date(2026, 1, 1), 10.0)]

        [signal] = momentum_signals(bars)

        self.assertEqual(signal.direction, "insufficient_data")
        self.assertEqual(signal.confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
