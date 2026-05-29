from __future__ import annotations

from mybroker.models import PolicyDecision


ALLOW = {"research_note", "backtest", "data_quality_check", "signal_generation", "scenario_simulation"}
REVIEW = {"portfolio_change_proposal", "personalized_recommendation", "external_publication"}
DENY = {"order_execution", "account_access", "discretionary_trade", "credential_storage"}


def classify_action(kind: str) -> PolicyDecision:
    normalized = kind.strip().lower()
    if normalized in ALLOW:
        return PolicyDecision(
            kind=normalized,
            allowed=True,
            human_review_required=False,
            reasons=["Research-only action with no account access or personalized instruction."],
        )
    if normalized in REVIEW:
        return PolicyDecision(
            kind=normalized,
            allowed=False,
            human_review_required=True,
            reasons=["Requires human review because it may affect individualized decisions or external claims."],
        )
    if normalized in DENY:
        return PolicyDecision(
            kind=normalized,
            allowed=False,
            human_review_required=True,
            reasons=["Blocked in this project scope because live advice, account access, and order execution are out of bounds."],
        )
    return PolicyDecision(
        kind=normalized,
        allowed=False,
        human_review_required=True,
        reasons=["Unknown action kind. Add an explicit policy classification before use."],
    )
