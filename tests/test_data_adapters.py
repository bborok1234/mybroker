from __future__ import annotations

import unittest

from mybroker.data import CsvPriceDataAdapter, SamplePriceDataAdapter


class DataAdapterTests(unittest.TestCase):
    def test_sample_adapter_loads_metadata(self) -> None:
        adapter = SamplePriceDataAdapter()

        bars = adapter.load()
        metadata = adapter.metadata(bars)

        self.assertEqual(metadata.adapter_id, "sample_price_v1")
        self.assertEqual(metadata.row_count, 10)
        self.assertEqual(metadata.symbols, ["ABC", "XYZ"])

    def test_csv_adapter_uses_explicit_source(self) -> None:
        adapter = CsvPriceDataAdapter("examples/prices.csv")

        bars = adapter.load()
        metadata = adapter.metadata(bars)

        self.assertEqual(metadata.adapter_id, "csv_price_v1")
        self.assertTrue(metadata.source.endswith("examples/prices.csv"))


if __name__ == "__main__":
    unittest.main()
