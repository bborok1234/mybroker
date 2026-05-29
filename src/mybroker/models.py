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


@dataclass(frozen=True)
class EvidenceSeed:
    source: str
    title: str
    excerpt: str
    topics: list[str]


@dataclass(frozen=True)
class EvidenceCatalog:
    source_count: int
    topic_counts: dict[str, int]
    coverage_status: str
    missing_context: list[str] = field(default_factory=list)
    source_coverage: list[dict[str, str]] = field(default_factory=list)
    freshness_status: str = "unknown"
    meaningfulness_status: str = "unknown"
    configured_interests: list[dict[str, str]] = field(default_factory=list)
    research_plan: dict[str, str | int] = field(default_factory=dict)
    topic_memory_snapshot: dict[str, object] = field(default_factory=dict)
    collection_gaps: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BeginnerProfile:
    profile_id: str
    experience_level: str
    learning_goal: str
    risk_comfort: str
    time_horizon: str
    decision_style: str
    capital_context: str = "unspecified"


@dataclass(frozen=True)
class MarketEntity:
    name: str
    kind: str
    beginner_label: str
    why_it_matters: str
    mentions: int
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MarketRelationship:
    source: str
    target: str
    relation: str
    beginner_explanation: str
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MarketMap:
    entities: list[MarketEntity]
    relationships: list[MarketRelationship]
    beginner_summary: str


@dataclass(frozen=True)
class PersonaView:
    persona_id: str
    name: str
    role: str
    stance: str
    summary: str
    confidence: float
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScenarioPath:
    scenario_id: str
    name: str
    probability_label: str
    summary: str
    triggers: list[str]
    watch_items: list[str]
    beginner_explanation: str
    risk_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BeginnerExplanation:
    term: str
    explanation: str


@dataclass(frozen=True)
class ActionCandidate:
    action_type: str
    title: str
    rationale: str
    suitability: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    risk_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScenarioReport:
    schema_version: str
    run_id: str
    generated_at: datetime
    product_mode: str
    seed_sources: list[EvidenceSeed]
    evidence_catalog: EvidenceCatalog
    profile_context: BeginnerProfile | None
    output_boundary: str
    market_map: MarketMap
    persona_views: list[PersonaView]
    scenarios: list[ScenarioPath]
    beginner_explanations: list[BeginnerExplanation]
    action_candidates: list[ActionCandidate]
    policy: PolicyDecision
    warnings: list[str] = field(default_factory=list)
