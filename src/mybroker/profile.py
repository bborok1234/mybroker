from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from mybroker.models import BeginnerProfile


DEFAULT_PROFILE_PATH = Path(__file__).resolve().parents[2] / "examples" / "profiles" / "beginner-conservative.json"
EXPERIENCE_LEVELS = {"new", "beginner", "intermediate"}
LEARNING_GOALS = {"market_overview", "risk_first", "theme_discovery", "vocabulary", "watchlist_building"}
RISK_COMFORT = {"low", "medium", "high"}
TIME_HORIZONS = {"weeks", "months", "years", "unspecified"}
DECISION_STYLES = {"learn_first", "guided", "fast_scan", "risk_first"}


def load_beginner_profile(path: str | Path | None) -> BeginnerProfile | None:
    if path is None:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_profile_payload(payload)
    if errors:
        raise ValueError("; ".join(errors))
    return BeginnerProfile(
        profile_id=payload["profile_id"],
        experience_level=payload["experience_level"],
        learning_goal=payload["learning_goal"],
        risk_comfort=payload["risk_comfort"],
        time_horizon=payload["time_horizon"],
        decision_style=payload["decision_style"],
        capital_context=payload.get("capital_context", "unspecified"),
    )


def profile_to_dict(profile: BeginnerProfile) -> dict[str, Any]:
    return asdict(profile)


def validate_profile_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"profile_id", "experience_level", "learning_goal", "risk_comfort", "time_horizon", "decision_style"}
    missing = sorted(required.difference(payload))
    if missing:
        errors.append(f"missing required profile fields: {', '.join(missing)}")
    if payload.get("experience_level") not in EXPERIENCE_LEVELS:
        errors.append(f"invalid experience_level: {payload.get('experience_level')}")
    if payload.get("learning_goal") not in LEARNING_GOALS:
        errors.append(f"invalid learning_goal: {payload.get('learning_goal')}")
    if payload.get("risk_comfort") not in RISK_COMFORT:
        errors.append(f"invalid risk_comfort: {payload.get('risk_comfort')}")
    if payload.get("time_horizon") not in TIME_HORIZONS:
        errors.append(f"invalid time_horizon: {payload.get('time_horizon')}")
    if payload.get("decision_style") not in DECISION_STYLES:
        errors.append(f"invalid decision_style: {payload.get('decision_style')}")
    if payload.get("capital_context") and str(payload["capital_context"]).lower() not in {"unspecified", "small", "medium", "large"}:
        errors.append(f"invalid capital_context: {payload.get('capital_context')}")
    return errors


def validate_profile_file(path: str | Path) -> list[str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_profile_payload(payload)
