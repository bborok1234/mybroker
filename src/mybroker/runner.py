from __future__ import annotations

from pathlib import Path

from mybroker.data import CsvPriceDataAdapter, DirectoryPriceDataAdapter, MultiCsvPriceDataAdapter, PriceDataAdapter, SamplePriceDataAdapter
from mybroker.models import ResearchReport
from mybroker.policy import classify_action
from mybroker.registry import default_registry, task_with_windows
from mybroker.reports import build_research_report, write_report
from mybroker.signals import momentum_signals


def make_price_adapter(source: str | list[str] | None) -> PriceDataAdapter:
    if isinstance(source, list) and len(source) > 1:
        return MultiCsvPriceDataAdapter(source)
    if isinstance(source, list) and len(source) == 1:
        source = source[0]
    if source:
        path = Path(source)
        if path.is_dir():
            return DirectoryPriceDataAdapter(path)
        return CsvPriceDataAdapter(source)
    return SamplePriceDataAdapter()


def run_research_task(
    *,
    source: str | list[str] | None = None,
    task_id: str = "momentum_research_v1",
    short_window: int | None = None,
    long_window: int | None = None,
    run_id: str = "local-momentum-research",
    output_path: str | Path | None = None,
) -> ResearchReport:
    registry = default_registry()
    task = task_with_windows(registry.get(task_id), short_window, long_window)
    adapter = make_price_adapter(source)
    dataset = adapter.load_dataset(min_history=task.default_long_window)
    if dataset.quality.error_count:
        errors = "; ".join(issue.message for issue in dataset.quality.issues if issue.level == "error")
        raise ValueError(f"cannot run research with blocking data quality errors: {errors}")
    signals = momentum_signals(
        dataset.bars,
        short_window=task.default_short_window,
        long_window=task.default_long_window,
    )
    report = build_research_report(
        run_id=run_id,
        task_id=task.task_id,
        source=dataset.metadata,
        data_quality=dataset.quality,
        signals=signals,
        policy=classify_action("signal_generation"),
    )
    if output_path:
        write_report(report, output_path)
    return report
