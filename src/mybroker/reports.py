from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mybroker.models import DataSourceMetadata, PolicyDecision, ResearchReport, Signal


REPORT_SCHEMA_VERSION = "research_report.v1"
SIGNAL_DIRECTIONS = {"positive_watch", "negative_watch", "neutral_watch", "insufficient_data"}


def build_research_report(
    *,
    run_id: str,
    task_id: str,
    source: DataSourceMetadata,
    signals: list[Signal],
    policy: PolicyDecision,
    generated_at: datetime | None = None,
) -> ResearchReport:
    warnings = []
    if not policy.allowed:
        warnings.append("policy gate blocked autonomous use of this report")
    if any(signal.direction == "insufficient_data" for signal in signals):
        warnings.append("one or more symbols have insufficient data")
    return ResearchReport(
        schema_version=REPORT_SCHEMA_VERSION,
        run_id=run_id,
        generated_at=generated_at or datetime.now(timezone.utc),
        task_id=task_id,
        source=source,
        signals=signals,
        policy=policy,
        summary=_signal_summary(signals),
        warnings=warnings,
    )


def report_to_dict(report: ResearchReport) -> dict[str, Any]:
    payload = asdict(report)
    payload["generated_at"] = report.generated_at.isoformat()
    for signal in payload["signals"]:
        signal["as_of"] = signal["as_of"].isoformat()
    return payload


def write_report(report: ResearchReport, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report_to_dict(report), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def load_report(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_report_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "run_id", "generated_at", "task_id", "source", "signals", "policy", "summary", "warnings"}
    missing = sorted(required.difference(payload))
    if missing:
        errors.append(f"missing required report fields: {', '.join(missing)}")
    if payload.get("schema_version") != REPORT_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    source = payload.get("source", {})
    for field in ["adapter_id", "source", "row_count", "symbols"]:
        if field not in source:
            errors.append(f"source missing {field}")
    if source.get("row_count", 0) <= 0:
        errors.append("source.row_count must be positive")
    if not source.get("symbols"):
        errors.append("source.symbols must not be empty")
    policy = payload.get("policy", {})
    for field in ["kind", "allowed", "human_review_required", "reasons"]:
        if field not in policy:
            errors.append(f"policy missing {field}")
    signals = payload.get("signals", [])
    if not signals:
        errors.append("signals must not be empty")
    for index, signal in enumerate(signals):
        for field in ["symbol", "as_of", "name", "score", "direction", "confidence", "rationale", "evidence"]:
            if field not in signal:
                errors.append(f"signals[{index}] missing {field}")
        if signal.get("direction") not in SIGNAL_DIRECTIONS:
            errors.append(f"signals[{index}] has invalid direction {signal.get('direction')}")
        confidence = signal.get("confidence")
        if not isinstance(confidence, int | float) or confidence < 0 or confidence > 1:
            errors.append(f"signals[{index}] confidence must be between 0 and 1")
    summary = payload.get("summary", {})
    if summary.get("total_signals") != len(signals):
        errors.append("summary.total_signals must match signals length")
    return errors


def validate_report_file(path: str | Path) -> list[str]:
    return validate_report_payload(load_report(path))


def _signal_summary(signals: list[Signal]) -> dict[str, int]:
    summary = {
        "total_signals": len(signals),
        "positive_watch": 0,
        "negative_watch": 0,
        "neutral_watch": 0,
        "insufficient_data": 0,
    }
    for signal in signals:
        summary[signal.direction] = summary.get(signal.direction, 0) + 1
    return summary
