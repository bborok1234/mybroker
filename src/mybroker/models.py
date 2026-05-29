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
    sources: list[str] = field(default_factory=list)
    source_type: str = "file"
    file_count: int = 1
    start_date: str = ""
    end_date: str = ""


@dataclass(frozen=True)
class DataQualityIssue:
    level: str
    code: str
    message: str
    source: str = ""
    symbol: str = ""


@dataclass(frozen=True)
class DataQualityResult:
    status: str
    checks: dict[str, bool]
    issue_count: int
    warning_count: int
    error_count: int
    issues: list[DataQualityIssue] = field(default_factory=list)


@dataclass(frozen=True)
class PriceDataset:
    bars: list[PriceBar]
    metadata: DataSourceMetadata
    quality: DataQualityResult


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
    data_quality: DataQualityResult | None = None
    warnings: list[str] = field(default_factory=list)
