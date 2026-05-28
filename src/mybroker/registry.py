from __future__ import annotations

from dataclasses import replace

from mybroker.models import ResearchTask


DEFAULT_TASK = ResearchTask(
    task_id="momentum_research_v1",
    name="Momentum research",
    description="Generate explainable momentum watch signals from local price bars.",
)


class ResearchTaskRegistry:
    def __init__(self, tasks: list[ResearchTask] | None = None) -> None:
        self._tasks = {task.task_id: task for task in tasks or [DEFAULT_TASK]}

    def list_tasks(self) -> list[ResearchTask]:
        return sorted(self._tasks.values(), key=lambda task: task.task_id)

    def get(self, task_id: str) -> ResearchTask:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            known = ", ".join(sorted(self._tasks))
            raise ValueError(f"unknown research task {task_id!r}; known tasks: {known}") from exc


def default_registry() -> ResearchTaskRegistry:
    return ResearchTaskRegistry()


def task_with_windows(task: ResearchTask, short_window: int | None, long_window: int | None) -> ResearchTask:
    return replace(
        task,
        default_short_window=short_window if short_window is not None else task.default_short_window,
        default_long_window=long_window if long_window is not None else task.default_long_window,
    )
