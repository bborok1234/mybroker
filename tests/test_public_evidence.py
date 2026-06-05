from __future__ import annotations

import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

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
        self.assertIn("relevance", catalog["items"][0])
        self.assertIn("relevance_label", catalog["source_status"][0])
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

    def test_live_gdelt_adapter_normalizes_api_articles(self) -> None:
        body = (
            b'{"articles":[{"title":"AI chip demand lifts semiconductor narrative",'
            b'"url":"https://example.com/article","seendate":"20260605T010000Z",'
            b'"domain":"example.com","sourceCountry":"US","language":"English"}]}'
        )

        with patch("urllib.request.urlopen", return_value=_Response(body)):
            catalog = build_public_evidence_catalog(["gdelt-live", "stooq-sample"])

        self.assertIn(catalog["mode"], {"live", "live_with_cache_fallback"})
        gdelt_items = [item for item in catalog["items"] if item["source_name"] == "GDELT"]
        self.assertEqual(gdelt_items[0]["freshness_status"], "live")
        self.assertIn("semiconductors", gdelt_items[0]["topics"])

    def test_live_adapters_fall_back_to_sample_cache_on_network_error(self) -> None:
        with patch("urllib.request.urlopen", side_effect=TimeoutError("offline")):
            catalog = build_public_evidence_catalog(["gdelt-live", "stooq-live"])

        self.assertEqual(catalog["mode"], "live_with_cache_fallback")
        self.assertGreaterEqual(len(catalog["items"]), 2)
        self.assertTrue(any(item["freshness_status"] == "live_error_fallback_sample" for item in catalog["items"]))


class _Response:
    status = 200

    def __init__(self, body: bytes) -> None:
        self.body = BytesIO(body)

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self.body.read()


if __name__ == "__main__":
    unittest.main()
