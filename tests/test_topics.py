from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mybroker.public_evidence import validate_public_evidence_catalog_payload
from mybroker.topics import (
    add_interest,
    build_daily_scout,
    build_research_plan,
    build_source_refresh_apply,
    build_source_refresh_live_gate,
    build_source_refresh_plan,
    collect_topic_evidence,
    init_topic_config,
    validate_daily_scout_file,
    validate_research_plan_file,
    validate_source_refresh_apply_file,
    validate_source_refresh_live_gate_file,
    validate_source_refresh_plan_file,
    validate_topic_config_file,
    validate_topic_memory_file,
)


class TopicResearchLoopTests(unittest.TestCase):
    def test_topic_config_init_add_list_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            topics_path = Path(directory) / "topics.json"

            config = init_topic_config(topics_path)
            updated = add_interest(
                name="Korea semiconductors",
                description="Korea chip exporters, memory cycle, and AI demand.",
                keywords=["korea", "memory", "chip"],
                beginner_focus="한국 반도체가 AI와 수출 사이에서 왜 움직이는지 본다.",
                path=topics_path,
            )
            errors = validate_topic_config_file(topics_path)

        self.assertEqual(config["schema_version"], "topic_config.v1")
        self.assertEqual(errors, [])
        self.assertGreaterEqual(len(updated["interests"]), 5)
        self.assertTrue(any(item["topic_id"] == "korea-semiconductors" for item in updated["interests"]))

    def test_research_plan_and_collection_update_topic_memory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics_path = root / "topics.json"
            plan_path = root / "research-plan.json"
            catalog_path = root / "daily-evidence.json"
            memory_path = root / "topic-memory.json"
            init_topic_config(topics_path)

            plan = build_research_plan(topics_path=topics_path, output_path=plan_path, run_id="daily-test")
            catalog = collect_topic_evidence(
                topics_path=topics_path,
                plan_path=plan_path,
                output_path=catalog_path,
                memory_path=memory_path,
            )
            scout_path = root / "daily-scout.json"
            scout = build_daily_scout(
                topics_path=topics_path,
                plan_path=plan_path,
                evidence_path=catalog_path,
                memory_path=memory_path,
                output_path=scout_path,
                run_id="daily-test",
            )
            refresh_plan_path = root / "source-refresh-plan.json"
            refresh_plan = build_source_refresh_plan(
                scout_path=scout_path,
                evidence_path=catalog_path,
                output_path=refresh_plan_path,
            )
            refresh_apply_path = root / "source-refresh-apply.json"
            refresh_apply = build_source_refresh_apply(
                refresh_plan_path=refresh_plan_path,
                output_path=refresh_apply_path,
            )
            refresh_live_gate_path = root / "source-refresh-live-gate.json"
            refresh_live_gate = build_source_refresh_live_gate(
                refresh_apply_path=refresh_apply_path,
                output_path=refresh_live_gate_path,
            )

            plan_errors = validate_research_plan_file(plan_path)
            scout_errors = validate_daily_scout_file(scout_path)
            refresh_plan_errors = validate_source_refresh_plan_file(refresh_plan_path)
            refresh_apply_errors = validate_source_refresh_apply_file(refresh_apply_path)
            refresh_live_gate_errors = validate_source_refresh_live_gate_file(refresh_live_gate_path)
            catalog_errors = validate_public_evidence_catalog_payload(catalog)
            memory_errors = validate_topic_memory_file(memory_path)

        self.assertEqual(plan["schema_version"], "daily_research_plan.v1")
        self.assertEqual(plan_errors, [])
        self.assertEqual(scout_errors, [])
        self.assertEqual(refresh_plan_errors, [])
        self.assertEqual(refresh_apply_errors, [])
        self.assertEqual(refresh_live_gate_errors, [])
        self.assertEqual(catalog_errors, [])
        self.assertEqual(memory_errors, [])
        self.assertEqual(catalog["mode"], "sample_cache_topic_research")
        self.assertIn("topic_memory_snapshot", catalog)
        self.assertEqual(scout["schema_version"], "daily_scout.v1")
        self.assertGreaterEqual(scout["recommendation_count"], 1)
        self.assertIn(scout["recommended_topic"]["action"], {"inspect_first", "monitor", "defer"})
        self.assertEqual(refresh_plan["schema_version"], "source_refresh_plan.v1")
        self.assertFalse(refresh_plan["external_effect_performed"])
        self.assertGreaterEqual(len(refresh_plan["actions"]), 1)
        self.assertEqual(refresh_apply["schema_version"], "source_refresh_apply.v1")
        self.assertFalse(refresh_apply["external_effect_performed"])
        self.assertEqual(refresh_apply["summary"]["action_count"], len(refresh_plan["actions"]))
        self.assertTrue(all(result["will_execute"] is False for result in refresh_apply["results"]))
        self.assertTrue(any(result["decision"] in {"ready", "blocked"} for result in refresh_apply["results"]))
        self.assertEqual(refresh_live_gate["schema_version"], "source_refresh_live_gate.v1")
        self.assertFalse(refresh_live_gate["external_effect_performed"])
        if refresh_live_gate["decisions"]:
            self.assertEqual(refresh_live_gate["decisions"][0]["copy_ready_response"], "approve live_network_refresh live_network_refresh")
        self.assertGreaterEqual(len(catalog["items"]), 2)


if __name__ == "__main__":
    unittest.main()
