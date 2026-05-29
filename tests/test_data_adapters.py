from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mybroker.data import DirectoryPriceDataAdapter, MultiCsvPriceDataAdapter, SamplePriceDataAdapter, load_price_dataset


class DataAdapterTests(unittest.TestCase):
    def test_sample_adapter_loads_metadata(self) -> None:
        adapter = SamplePriceDataAdapter()

        bars = adapter.load()
        metadata = adapter.metadata(bars)

        self.assertEqual(metadata.adapter_id, "sample_price_v1")
        self.assertEqual(metadata.row_count, 10)
        self.assertEqual(metadata.symbols, ["ABC", "XYZ"])

    def test_directory_adapter_loads_dataset_metadata_and_quality(self) -> None:
        adapter = DirectoryPriceDataAdapter("examples/prices-multi")

        dataset = adapter.load_dataset()

        self.assertEqual(dataset.metadata.adapter_id, "directory_csv_price_v1")
        self.assertEqual(dataset.metadata.file_count, 2)
        self.assertEqual(dataset.metadata.row_count, 10)
        self.assertEqual(dataset.metadata.symbols, ["ABC", "XYZ"])
        self.assertEqual(dataset.quality.status, "pass")

    def test_multi_file_adapter_loads_explicit_sources(self) -> None:
        adapter = MultiCsvPriceDataAdapter(["examples/prices-multi/abc.csv", "examples/prices-multi/xyz.csv"])

        dataset = adapter.load_dataset()

        self.assertEqual(dataset.metadata.adapter_id, "multi_csv_price_v1")
        self.assertEqual(dataset.metadata.file_count, 2)
        self.assertEqual(dataset.quality.error_count, 0)

    def test_quality_detects_missing_values_duplicates_order_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text(
                "date,symbol,close\n"
                "2026-01-02,ABC,101\n"
                "2026-01-01,ABC,100\n"
                "2026-01-01,ABC,100\n"
                "2026-01-03,XYZ,\n",
                encoding="utf-8",
            )

            dataset = load_price_dataset(path, min_history=5)

        codes = {issue.code for issue in dataset.quality.issues}
        self.assertIn("missing_value", codes)
        self.assertIn("duplicate_row", codes)
        self.assertIn("date_order", codes)
        self.assertIn("insufficient_history", codes)
        self.assertEqual(dataset.quality.status, "error")


if __name__ == "__main__":
    unittest.main()
