from __future__ import annotations

import unittest

from mybroker.registry import default_registry, task_with_windows


class RegistryTests(unittest.TestCase):
    def test_default_registry_exposes_momentum_task(self) -> None:
        registry = default_registry()

        task = registry.get("momentum_research_v1")

        self.assertEqual(task.default_short_window, 3)
        self.assertEqual(task.default_long_window, 5)
        self.assertEqual([item.task_id for item in registry.list_tasks()], ["momentum_research_v1"])

    def test_task_window_override_is_explicit(self) -> None:
        task = default_registry().get("momentum_research_v1")

        updated = task_with_windows(task, short_window=2, long_window=4)

        self.assertEqual(updated.default_short_window, 2)
        self.assertEqual(updated.default_long_window, 4)
        self.assertEqual(task.default_short_window, 3)

    def test_unknown_task_names_known_tasks(self) -> None:
        with self.assertRaisesRegex(ValueError, "known tasks"):
            default_registry().get("missing")


if __name__ == "__main__":
    unittest.main()
