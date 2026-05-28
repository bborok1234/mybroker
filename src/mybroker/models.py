from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass(frozen=True)
class PriceBar:
    symbol: str
    as_of: date
    close: float


@dataclass(frozen=True)
class Signal:
    symbol: str
    as_of: date
    name: str
    score: float
    direction: str
    confidence: float
    rationale: str
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PolicyDecision:
    kind: str
    allowed: bool
    human_review_required: bool
    reasons: list[str]


@dataclass(frozen=True)
class DataSourceMetadata:
    adapter_id: str
    source: str
    row_count: int
    symbols: list[str]


@dataclass(frozen=True)
class ResearchTask:
    task_id: str
    name: str
    description: str
    default_short_window: int = 3
    default_long_window: int = 5


@dataclass(frozen=True)
class ResearchReport:
    schema_version: str
    run_id: str
    generated_at: datetime
    task_id: str
    source: DataSourceMetadata
    signals: list[Signal]
    policy: PolicyDecision
    summary: dict[str, int]
    warnings: list[str] = field(default_factory=list)
