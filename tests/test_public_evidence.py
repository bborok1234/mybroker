from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mybroker.public_evidence import (
    SOURCE_MATRIX,
    build_public_evidence_catalog,
    validate_public_evidence_catalog_file,
    validate_public_evidence_catalog_payload,
    write_public_evidence_catalog,
)


class PublicEvidenceTests(unittest.TestCase):
    def test_source_matrix_classifies_required_sources(self) -> None:
        names = {source["source_name"] for source in SOURCE_MATRIX}

        self.assertIn("SEC EDGAR", names)
        self.assertIn("FRED", names)
        self.assertIn("GDELT", names)
        self.assertIn("Stooq", names)
        self.assertIn("Alpha Vantage free tier", names)
        self.assertIn("Nasdaq Data Link", names)

    def test_cached_public_evidence_builds_meaningful_catalog(self) -> None:
        catalog = build_public_evidence_catalog()

        self.assertEqual(catalog["schema_version"], "public_evidence_catalog.v1")
        self.assertEqual(catalog["mode"], "sample_cache")
        self.assertGreaterEqual(len(catalog["source_status"]), 3)
        self.assertGreaterEqual(len(catalog["items"]), 4)
        self.assertEqual(catalog["feasibility"]["status"], "meaningful")
        self.assertGreaterEqual(len(catalog["graph"]["nodes"]), 3)
        self.assertGreaterEqual(len(catalog["graph"]["edges"]), 3)

    def test_catalog_validation_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            catalog = build_public_evidence_catalog(["gdelt-sample", "stooq-sample"])
            path = write_public_evidence_catalog(catalog, Path(directory) / "catalog.json")

            errors = validate_public_evidence_catalog_file(path)

        self.assertEqual(errors, [])

    def test_catalog_validator_rejects_missing_graph(self) -> None:
        errors = validate_public_evidence_catalog_payload({"schema_version": "public_evidence_catalog.v1"})

        self.assertTrue(any("missing required public evidence catalog fields" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
