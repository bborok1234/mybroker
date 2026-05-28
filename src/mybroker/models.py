from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


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
