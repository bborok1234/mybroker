from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mybroker.public_evidence import (
    PUBLIC_EVIDENCE_SCHEMA_VERSION,
    SOURCE_MATRIX,
    PublicEvidenceItem,
    build_public_evidence_catalog,
    build_public_evidence_graph,
    evaluate_feasibility,
    write_public_evidence_catalog,
)
from mybroker.scenario import TOPIC_DEFINITIONS, detect_topics


TOPIC_CONFIG_SCHEMA_VERSION = "topic_config.v1"
RESEARCH_PLAN_SCHEMA_VERSION = "daily_research_plan.v1"
TOPIC_MEMORY_SCHEMA_VERSION = "topic_memory.v1"
DAILY_SCOUT_SCHEMA_VERSION = "daily_scout.v1"
SOURCE_REFRESH_PLAN_SCHEMA_VERSION = "source_refresh_plan.v1"
SOURCE_REFRESH_APPLY_SCHEMA_VERSION = "source_refresh_apply.v1"
SOURCE_REFRESH_LIVE_GATE_SCHEMA_VERSION = "source_refresh_live_gate.v1"
SOURCE_REFRESH_LIVE_RUN_SCHEMA_VERSION = "source_refresh_live_run.v1"
SOURCE_REFRESH_LIVE_PREFLIGHT_SCHEMA_VERSION = "source_refresh_live_preflight.v1"

DEFAULT_TOPICS_PATH = Path("config/topics.json")
DEFAULT_RESEARCH_PLAN_OUTPUT = Path("reports/daily/research-plan.json")
DEFAULT_DAILY_SCOUT_OUTPUT = Path("reports/daily/scout.json")
DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT = Path("reports/daily/source-refresh-plan.json")
DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT = Path("reports/daily/source-refresh-apply.json")
DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT = Path("reports/daily/source-refresh-live-gate.json")
DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT = Path("reports/daily/source-refresh-live-run.json")
DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT = Path("reports/daily/source-refresh-live-preflight.json")
DEFAULT_TOPIC_MEMORY_OUTPUT = Path("reports/memory/topic-memory.json")
DEFAULT_DAILY_REVIEW_OUTPUT = Path("reports/memory/daily-review.json")
DEFAULT_DAILY_EVIDENCE_OUTPUT = Path("reports/evidence/daily-evidence-catalog.json")
DEFAULT_LIVE_EVIDENCE_OUTPUT = Path("reports/evidence/live-evidence-catalog.json")

DEFAULT_INTERESTS = [
    {
        "name": "AI infrastructure",
        "description": "AI data center, GPU, cloud, power, and semiconductor demand.",
        "beginner_focus": "AI 수요가 실제 실적과 공급망으로 이어지는지 이해한다.",
        "keywords": ["ai", "data center", "gpu", "cloud", "semiconductors"],
    },
    {
        "name": "Semiconductors",
        "description": "Chip supply chain, memory, foundry, and AI-linked demand.",
        "beginner_focus": "반도체가 AI 기대와 경기 둔화 리스크를 동시에 받는 이유를 본다.",
        "keywords": ["semiconductor", "chip", "memory", "supply chain"],
    },
    {
        "name": "US rates",
        "description": "Treasury yields, Fed expectations, liquidity, and growth-stock pressure.",
        "beginner_focus": "금리가 성장 테마의 가격 부담을 어떻게 바꾸는지 본다.",
        "keywords": ["rates", "yield", "fed", "treasury"],
    },
    {
        "name": "Consumer weakness",
        "description": "Consumer demand, retail pressure, employment, and inflation burden.",
        "beginner_focus": "소비 둔화가 기업 매출과 경기 기대에 주는 영향을 이해한다.",
        "keywords": ["consumer", "retail", "inflation", "demand", "risk"],
    },
]


def init_topic_config(path: str | Path = DEFAULT_TOPICS_PATH, interests: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected = interests if interests is not None else DEFAULT_INTERESTS
    payload = {
        "schema_version": TOPIC_CONFIG_SCHEMA_VERSION,
        "generated_at": _now(),
        "policy": _research_only_policy(),
        "interests": [_normalize_interest(item) for item in selected],
    }
    return write_json(payload, path)


def add_interest(
    *,
    name: str,
    description: str = "",
    keywords: list[str] | None = None,
    beginner_focus: str = "",
    path: str | Path = DEFAULT_TOPICS_PATH,
) -> dict[str, Any]:
    config_path = Path(path)
    if config_path.exists():
        payload = load_json(config_path)
    else:
        payload = init_topic_config(config_path, interests=[])
    interests = payload.setdefault("interests", [])
    normalized = _normalize_interest({
        "name": name,
        "description": description,
        "keywords": keywords or [],
        "beginner_focus": beginner_focus,
    })
    existing = {item.get("topic_id") for item in interests}
    if normalized["topic_id"] in existing:
        interests[:] = [normalized if item.get("topic_id") == normalized["topic_id"] else item for item in interests]
    else:
        interests.append(normalized)
    payload["generated_at"] = _now()
    return write_json(payload, config_path)


def load_topic_config(path: str | Path = DEFAULT_TOPICS_PATH) -> dict[str, Any]:
    return load_json(path)


def validate_topic_config_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != TOPIC_CONFIG_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if not payload.get("interests"):
        errors.append("interests must not be empty")
    for index, interest in enumerate(payload.get("interests", [])):
        for field in ["topic_id", "name", "target_topics", "beginner_focus", "keywords"]:
            if field not in interest:
                errors.append(f"interests[{index}] missing {field}")
        if not interest.get("target_topics"):
            errors.append(f"interests[{index}] target_topics must not be empty")
    policy = payload.get("policy", {})
    if policy.get("output_boundary") != "research_only":
        errors.append("policy.output_boundary must be research_only")
    return errors


def validate_topic_config_file(path: str | Path) -> list[str]:
    return validate_topic_config_payload(load_json(path))


def build_research_plan(
    *,
    topics_path: str | Path = DEFAULT_TOPICS_PATH,
    output_path: str | Path = DEFAULT_RESEARCH_PLAN_OUTPUT,
    run_id: str = "daily-research",
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    config = load_topic_config(topics_path)
    config_errors = validate_topic_config_payload(config)
    if config_errors:
        raise ValueError("; ".join(config_errors))
    plan_items = []
    for index, interest in enumerate(config.get("interests", []), start=1):
        target_topics = interest.get("target_topics", [])
        plan_items.append({
            "topic_id": interest["topic_id"],
            "name": interest["name"],
            "priority": index,
            "target_topics": target_topics,
            "beginner_reason": interest.get("beginner_focus", ""),
            "daily_questions": _questions_for_topics(target_topics, interest["name"]),
            "source_needs": _source_needs_for_topics(target_topics),
            "missing_evidence": ["live_refresh", "deduplication", "source_terms_review"],
        })
    payload = {
        "schema_version": RESEARCH_PLAN_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "topics_path": Path(topics_path).as_posix(),
        "policy": _research_only_policy(),
        "plan_items": plan_items,
        "next_step": "collect_free_public_evidence",
    }
    return write_json(payload, output_path)


def validate_research_plan_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != RESEARCH_PLAN_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if not payload.get("plan_items"):
        errors.append("plan_items must not be empty")
    for index, item in enumerate(payload.get("plan_items", [])):
        for field in ["topic_id", "name", "priority", "target_topics", "daily_questions", "source_needs"]:
            if field not in item:
                errors.append(f"plan_items[{index}] missing {field}")
        if not item.get("daily_questions"):
            errors.append(f"plan_items[{index}] daily_questions must not be empty")
    return errors


def validate_research_plan_file(path: str | Path) -> list[str]:
    return validate_research_plan_payload(load_json(path))


def build_daily_scout(
    *,
    topics_path: str | Path = DEFAULT_TOPICS_PATH,
    plan_path: str | Path = DEFAULT_RESEARCH_PLAN_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    vault_path: str | Path | None = None,
    review_path: str | Path | None = DEFAULT_DAILY_REVIEW_OUTPUT,
    output_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    run_id: str = "daily-research",
) -> dict[str, Any]:
    config = load_topic_config(topics_path)
    plan = load_json(plan_path)
    evidence = load_json(evidence_path)
    memory = load_json(memory_path)
    vault = load_json(vault_path) if vault_path and Path(vault_path).exists() else {}
    review = load_json(review_path) if review_path and Path(review_path).exists() else {}
    plan_by_id = {item.get("topic_id"): item for item in plan.get("plan_items", [])}
    memory_by_id = {item.get("topic_id"): item for item in memory.get("topics", [])}
    vault_by_topic = _vault_notes_by_topic(vault)
    review_by_topic = _review_signals_by_topic(review)
    recommendations = []
    recommendation_contexts: dict[str, dict[str, Any]] = {}
    for interest in config.get("interests", []):
        topic_id = interest.get("topic_id", "")
        memory_topic = memory_by_id.get(topic_id, {})
        plan_item = plan_by_id.get(topic_id, {})
        linked_notes = vault_by_topic.get(topic_id, [])
        review_signal = review_by_topic.get(topic_id, {})
        score, factors = _scout_score(
            memory_topic=memory_topic,
            plan_item=plan_item,
            linked_notes=linked_notes,
            review_signal=review_signal,
        )
        source_names = memory_topic.get("source_names", [])
        recommendation = {
            "topic_id": topic_id,
            "name": interest.get("name", ""),
            "score": round(score, 2),
            "priority_rank": 0,
            "action": _scout_action(score, memory_topic),
            "confidence": _scout_confidence(memory_topic),
            "why": _scout_why(interest, memory_topic, linked_notes, factors),
            "beginner_focus": interest.get("beginner_focus", ""),
            "next_question": _scout_next_question(plan_item, memory_topic, linked_notes),
            "source_names": source_names,
            "latest_titles": memory_topic.get("latest_titles", [])[:5],
            "new_evidence_count": int(memory_topic.get("new_evidence_count", 0) or 0),
            "changed_since_previous": bool(memory_topic.get("changed_since_previous")),
            "linked_vault_notes": [
                {
                    "title": note.get("title", ""),
                    "source_path": note.get("source_path", ""),
                    "wiki_path": note.get("wiki_path", ""),
                }
                for note in linked_notes[:3]
            ],
            "review_signal": review_signal,
            "missing_evidence": memory_topic.get("collection_gaps", []),
            "score_factors": factors,
        }
        recommendation["operator_brief"] = _scout_operator_brief(
            recommendation=recommendation,
            interest=interest,
            memory_topic=memory_topic,
            plan_item=plan_item,
        )
        recommendation["beginner_reading_order"] = _scout_reading_order(
            recommendation=recommendation,
            plan_item=plan_item,
            memory_topic=memory_topic,
            linked_notes=linked_notes,
        )
        recommendation["copy_ready_responses"] = _scout_copy_ready_responses(recommendation)
        recommendations.append(recommendation)
        recommendation_contexts[topic_id] = {
            "interest": interest,
            "memory_topic": memory_topic,
            "plan_item": plan_item,
            "linked_notes": linked_notes,
        }
    rotation_guard = _apply_scout_rotation_guard(
        recommendations=recommendations,
        recommendation_contexts=recommendation_contexts,
        memory_run_count=int(memory.get("run_count", 0) or 0),
    )
    recommendations.sort(key=lambda row: (-float(row["score"]), row["name"]))
    for index, recommendation in enumerate(recommendations, start=1):
        recommendation["priority_rank"] = index
    top = recommendations[0] if recommendations else {}
    payload = {
        "schema_version": DAILY_SCOUT_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at": _now(),
        "inputs": {
            "topics_path": Path(topics_path).as_posix(),
            "plan_path": Path(plan_path).as_posix(),
            "evidence_path": Path(evidence_path).as_posix(),
            "memory_path": Path(memory_path).as_posix(),
            "vault_path": Path(vault_path).as_posix() if vault_path else "",
            "review_path": Path(review_path).as_posix() if review_path else "",
        },
        "recommendation_count": len(recommendations),
        "recommended_topic": top,
        "recommendations": recommendations,
        "rotation_guard": rotation_guard,
        "source_context": {
            "source_count": len(evidence.get("source_status", [])),
            "collection_gaps": evidence.get("collection_gaps", []),
            "mode": evidence.get("mode", ""),
        },
        "review_context": {
            "schema_version": review.get("schema_version", ""),
            "response_count": int(review.get("summary", {}).get("response_count", 0) or 0),
            "signal_count": len(review_by_topic),
        },
        "autonomous_start": {
            "mode": "system_recommends_first_topic",
            "operator_input_required": False,
            "why": "초보 사용자는 종목, 섹터, 이벤트 가설을 직접 넣기 어렵기 때문에 scout가 먼저 오늘 볼 주제를 추천합니다.",
            "operator_can_respond_with": ["more", "less", "confusing", "done", "carry"],
        },
        "pattern_watch": _scout_pattern_watch(),
        "policy": _research_only_policy(),
        "next_step": "inspect_recommended_topic_first",
    }
    return write_json(payload, output_path)


def validate_daily_scout_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DAILY_SCOUT_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if not payload.get("recommendations"):
        errors.append("recommendations must not be empty")
    if not payload.get("recommended_topic"):
        errors.append("recommended_topic must not be empty")
    for index, item in enumerate(payload.get("recommendations", [])):
        for field in [
            "topic_id",
            "name",
            "score",
            "priority_rank",
            "action",
            "confidence",
            "why",
            "next_question",
            "operator_brief",
            "beginner_reading_order",
            "copy_ready_responses",
        ]:
            if field not in item:
                errors.append(f"recommendations[{index}] missing {field}")
        if item.get("action") not in {"inspect_first", "monitor", "defer"}:
            errors.append(f"recommendations[{index}] invalid action")
        if not item.get("beginner_reading_order"):
            errors.append(f"recommendations[{index}] beginner_reading_order must not be empty")
        if not item.get("copy_ready_responses"):
            errors.append(f"recommendations[{index}] copy_ready_responses must not be empty")
        brief = item.get("operator_brief", {})
        for field in ["headline", "why_today", "confidence_note", "missing_evidence_note", "research_only_note"]:
            if field not in brief:
                errors.append(f"recommendations[{index}].operator_brief missing {field}")
    rotation = payload.get("rotation_guard", {})
    for field in ["status", "run_count", "pre_rotation_topic", "selected_topic", "rotated", "reason", "external_effect_performed"]:
        if field not in rotation:
            errors.append(f"rotation_guard missing {field}")
    if rotation.get("status") not in {"not_needed", "rotated", "insufficient_alternative", "operator_override", "missing"}:
        errors.append("rotation_guard.status must be not_needed, rotated, insufficient_alternative, operator_override, or missing")
    if rotation.get("external_effect_performed") is not False:
        errors.append("rotation_guard.external_effect_performed must be false")
    autonomous = payload.get("autonomous_start", {})
    if autonomous.get("mode") != "system_recommends_first_topic":
        errors.append("autonomous_start.mode must be system_recommends_first_topic")
    if autonomous.get("operator_input_required") is not False:
        errors.append("autonomous_start.operator_input_required must be false")
    if not payload.get("pattern_watch"):
        errors.append("pattern_watch must not be empty")
    policy = payload.get("policy", {})
    if policy.get("output_boundary") != "research_only":
        errors.append("policy.output_boundary must be research_only")
    return errors


def validate_daily_scout_file(path: str | Path) -> list[str]:
    return validate_daily_scout_payload(load_json(path))


def build_source_refresh_plan(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    vault_path: str | Path | None = None,
    output_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
) -> dict[str, Any]:
    scout = load_json(scout_path)
    evidence = load_json(evidence_path)
    vault = load_json(vault_path) if vault_path and Path(vault_path).exists() else {}
    top_recommendations = scout.get("recommendations", [])[:3]
    source_status = {row.get("source_name", ""): row for row in evidence.get("source_status", [])}
    actions = []
    selected_live_sources: list[str] = []
    if _needs_news_refresh(top_recommendations, source_status):
        actions.append(_refresh_action(
            source_name="GDELT",
            adapter_id="gdelt-live",
            cadence="daily",
            priority="high",
            reason="Scout 상위 주제는 최신 뉴스/이벤트 서사가 필요합니다.",
            command="PYTHONPATH=src python3 -m mybroker ingest-public-evidence --source gdelt-live --source stooq-live --source sec-sample --output reports/evidence/live-evidence-catalog.json",
        ))
        selected_live_sources.append("gdelt-live")
    if _needs_price_refresh(top_recommendations, source_status):
        actions.append(_refresh_action(
            source_name="Stooq",
            adapter_id="stooq-live",
            cadence="daily",
            priority="high",
            reason="Scout 상위 주제는 넓은 가격/위험 맥락 확인이 필요합니다.",
            command="PYTHONPATH=src python3 -m mybroker ingest-public-evidence --source gdelt-live --source stooq-live --source sec-sample --output reports/evidence/live-evidence-catalog.json",
        ))
        selected_live_sources.append("stooq-live")
    if _needs_filing_review(top_recommendations, source_status):
        actions.append(_refresh_action(
            source_name="SEC EDGAR",
            adapter_id="sec-sample",
            cadence="weekly_or_event",
            priority="medium",
            reason="기업 공시 맥락은 유용하지만 SEC live refresh는 아직 구현되지 않았습니다.",
            command="PYTHONPATH=src python3 -m mybroker ingest-public-evidence --source sec-sample --output reports/evidence/public-evidence-catalog.json",
        ))
    if vault.get("schema_version") == "knowledge_vault_compile.v1":
        actions.append(_refresh_action(
            source_name="Local vault",
            adapter_id="vault-compile",
            cadence="daily_if_raw_changed",
            priority="medium",
            reason="컴파일된 원천 노트가 오늘 Scout 추천과 계속 맞물려 있어야 합니다.",
            command="PYTHONPATH=src python3 -m mybroker appliance vault compile --raw-dir examples/vault/raw --wiki-dir reports/vault/wiki --output reports/vault/compile.json --surface-output reports/product/vault.html",
        ))
    if not actions:
        actions.append(_refresh_action(
            source_name="Local cache",
            adapter_id="sample-cache",
            cadence="no_refresh_needed",
            priority="low",
            reason="현재 근거는 로컬 교육용 dry-run에는 충분합니다.",
            command="PYTHONPATH=src python3 -m mybroker collect-evidence --topics config/topics.json --plan reports/daily/research-plan.json --output reports/evidence/daily-evidence-catalog.json --memory-output reports/memory/topic-memory.json",
        ))
    payload = {
        "schema_version": SOURCE_REFRESH_PLAN_SCHEMA_VERSION,
        "generated_at": _now(),
        "inputs": {
            "scout_path": Path(scout_path).as_posix(),
            "evidence_path": Path(evidence_path).as_posix(),
            "vault_path": Path(vault_path).as_posix() if vault_path else "",
        },
        "recommended_topic": scout.get("recommended_topic", {}),
        "actions": actions,
        "selected_live_sources": selected_live_sources,
        "external_effect_performed": False,
        "policy": _research_only_policy(),
        "next_step": "review_refresh_plan_before_running_live_sources",
    }
    return write_json(payload, output_path)


def validate_source_refresh_plan_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SOURCE_REFRESH_PLAN_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if not payload.get("actions"):
        errors.append("actions must not be empty")
    for index, action in enumerate(payload.get("actions", [])):
        for field in ["source_name", "adapter_id", "cadence", "priority", "reason", "command", "dry_run_only"]:
            if field not in action:
                errors.append(f"actions[{index}] missing {field}")
        if action.get("priority") not in {"high", "medium", "low"}:
            errors.append(f"actions[{index}] invalid priority")
        if action.get("dry_run_only") is not True:
            errors.append(f"actions[{index}] dry_run_only must be true")
        command = action.get("command", "")
        if any(blocked in command for blocked in ["--send", "--confirm-host-write", "launchctl", "tailscale serve --bg"]):
            errors.append(f"actions[{index}] command crosses external-effect boundary")
    policy = payload.get("policy", {})
    if policy.get("output_boundary") != "research_only":
        errors.append("policy.output_boundary must be research_only")
    return errors


def validate_source_refresh_plan_file(path: str | Path) -> list[str]:
    return validate_source_refresh_plan_payload(load_json(path))


def build_source_refresh_apply(
    *,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    output_path: str | Path = DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
) -> dict[str, Any]:
    plan = load_json(refresh_plan_path)
    plan_errors = validate_source_refresh_plan_payload(plan)
    if plan_errors:
        raise ValueError("; ".join(plan_errors))
    results = [_refresh_apply_result(index, action) for index, action in enumerate(plan.get("actions", []), start=1)]
    blocked_count = sum(1 for result in results if result["decision"] == "blocked")
    ready_count = sum(1 for result in results if result["decision"] == "ready")
    payload = {
        "schema_version": SOURCE_REFRESH_APPLY_SCHEMA_VERSION,
        "generated_at": _now(),
        "inputs": {
            "refresh_plan_path": Path(refresh_plan_path).as_posix(),
        },
        "execution_mode": "dry_run",
        "external_effect_performed": False,
        "summary": {
            "action_count": len(results),
            "ready_count": ready_count,
            "blocked_count": blocked_count,
            "skipped_count": sum(1 for result in results if result["decision"] == "skipped"),
        },
        "results": results,
        "policy": _research_only_policy(),
        "next_step": "operator_review_before_live_or_host_effect",
    }
    return write_json(payload, output_path)


def validate_source_refresh_apply_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SOURCE_REFRESH_APPLY_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("execution_mode") != "dry_run":
        errors.append("execution_mode must be dry_run")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if not payload.get("results"):
        errors.append("results must not be empty")
    for index, result in enumerate(payload.get("results", [])):
        for field in [
            "action_index",
            "source_name",
            "adapter_id",
            "decision",
            "status",
            "will_execute",
            "approval_required",
            "reason",
            "command",
            "expected_artifact",
        ]:
            if field not in result:
                errors.append(f"results[{index}] missing {field}")
        if result.get("decision") not in {"ready", "blocked", "skipped"}:
            errors.append(f"results[{index}] invalid decision")
        if result.get("will_execute") is not False:
            errors.append(f"results[{index}] will_execute must be false in dry-run mode")
        command = result.get("command", "")
        if any(blocked in command for blocked in ["--send", "--confirm-host-write", "launchctl", "tailscale serve --bg"]):
            errors.append(f"results[{index}] command crosses external-effect boundary")
    summary = payload.get("summary", {})
    if summary.get("action_count") != len(payload.get("results", [])):
        errors.append("summary.action_count must equal results length")
    policy = payload.get("policy", {})
    if policy.get("output_boundary") != "research_only":
        errors.append("policy.output_boundary must be research_only")
    return errors


def validate_source_refresh_apply_file(path: str | Path) -> list[str]:
    return validate_source_refresh_apply_payload(load_json(path))


def build_source_refresh_live_gate(
    *,
    refresh_apply_path: str | Path = DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    output_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
) -> dict[str, Any]:
    refresh_apply = load_json(refresh_apply_path)
    apply_errors = validate_source_refresh_apply_payload(refresh_apply)
    if apply_errors:
        raise ValueError("; ".join(apply_errors))
    blocked_live = [
        result for result in refresh_apply.get("results", [])
        if result.get("decision") == "blocked" and result.get("approval_required") == "live_network_refresh"
    ]
    commands = _unique_preserve_order(result.get("command", "") for result in blocked_live if result.get("command"))
    decisions = []
    if blocked_live:
        decisions.append({
            "id": "live_network_refresh",
            "status": "needs_operator_approval",
            "approval_scope": "live_network_refresh",
            "risk_level": "medium",
            "reversibility": "cache_artifact_can_be_deleted",
            "copy_ready_response": "approve live_network_refresh live_network_refresh",
            "agent_will_run": commands,
            "agent_will_not_run": [
                "paid API calls",
                "credentialed sources",
                "host-level scheduler or private serving commands",
                "notification send",
                "account access",
                "execution or personalized advice",
            ],
            "stale_context_guard": "Regenerate source_refresh_apply.v1 before approval if scout, evidence, or source plan changed.",
        })
    payload = {
        "schema_version": SOURCE_REFRESH_LIVE_GATE_SCHEMA_VERSION,
        "generated_at": _now(),
        "inputs": {
            "refresh_apply_path": Path(refresh_apply_path).as_posix(),
        },
        "status": "approval_required" if decisions else "no_live_refresh_requested",
        "blocked_action_count": len(blocked_live),
        "proposed_command_count": len(commands),
        "decisions": decisions,
        "blocked_actions": [
            {
                "source_name": result.get("source_name", ""),
                "adapter_id": result.get("adapter_id", ""),
                "reason": result.get("reason", ""),
                "command": result.get("command", ""),
                "expected_artifact": result.get("expected_artifact", ""),
            }
            for result in blocked_live
        ],
        "external_effect_performed": False,
        "policy": _research_only_policy(),
        "next_step": "operator_may_approve_live_network_refresh_scope",
    }
    return write_json(payload, output_path)


def validate_source_refresh_live_gate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SOURCE_REFRESH_LIVE_GATE_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("status") not in {"approval_required", "no_live_refresh_requested"}:
        errors.append("status must be approval_required or no_live_refresh_requested")
    if payload.get("status") == "approval_required" and not payload.get("decisions"):
        errors.append("approval_required gates must include decisions")
    for index, decision in enumerate(payload.get("decisions", [])):
        for field in ["id", "approval_scope", "copy_ready_response", "agent_will_run", "agent_will_not_run", "stale_context_guard"]:
            if field not in decision:
                errors.append(f"decisions[{index}] missing {field}")
        if decision.get("approval_scope") != "live_network_refresh":
            errors.append(f"decisions[{index}] approval_scope must be live_network_refresh")
        if not str(decision.get("copy_ready_response", "")).startswith("approve "):
            errors.append(f"decisions[{index}] copy_ready_response must start with approve")
        for command in decision.get("agent_will_run", []):
            if any(blocked in command for blocked in ["--send", "--confirm-host-write", "launchctl", "tailscale serve --bg"]):
                errors.append(f"decisions[{index}] command crosses non-network external-effect boundary")
    if int(payload.get("blocked_action_count", 0) or 0) != len(payload.get("blocked_actions", [])):
        errors.append("blocked_action_count must equal blocked_actions length")
    policy = payload.get("policy", {})
    if policy.get("output_boundary") != "research_only":
        errors.append("policy.output_boundary must be research_only")
    return errors


def validate_source_refresh_live_gate_file(path: str | Path) -> list[str]:
    return validate_source_refresh_live_gate_payload(load_json(path))


def build_source_refresh_live_run(
    *,
    live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    response: str = "",
    output_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    evidence_output_path: str | Path = DEFAULT_LIVE_EVIDENCE_OUTPUT,
    execute: bool = False,
    confirm_live_network: bool = False,
) -> dict[str, Any]:
    gate = load_json(live_gate_path)
    gate_errors = validate_source_refresh_live_gate_payload(gate)
    if gate_errors:
        raise ValueError("; ".join(gate_errors))
    normalized_response = " ".join(response.strip().split())
    decision = (gate.get("decisions") or [{}])[0] if gate.get("decisions") else {}
    expected_response = decision.get("copy_ready_response", "")
    approval_status = "not_required" if gate.get("status") == "no_live_refresh_requested" else "missing"
    if expected_response and normalized_response == expected_response:
        approval_status = "approved"
    elif normalized_response:
        approval_status = "invalid"
    proposed_commands = list(decision.get("agent_will_run", []))
    source_ids = _live_source_ids_from_gate(gate)
    blockers = []
    if gate.get("status") == "approval_required" and approval_status != "approved":
        blockers.append("live_network_refresh_not_approved")
    if execute and not confirm_live_network:
        blockers.append("missing_confirm_live_network")
    if execute and not source_ids:
        blockers.append("no_live_sources_to_run")
    execution_status = "not_requested"
    catalog_summary: dict[str, Any] = {}
    external_effect_performed = False
    if not execute:
        execution_status = "ready_to_execute" if approval_status == "approved" and not blockers else "not_requested"
    elif blockers:
        execution_status = "blocked"
    else:
        catalog = build_public_evidence_catalog(source_ids)
        write_public_evidence_catalog(catalog, evidence_output_path)
        external_effect_performed = True
        execution_status = "executed"
        catalog_summary = {
            "evidence_output_path": Path(evidence_output_path).as_posix(),
            "mode": catalog.get("mode", ""),
            "source_count": len(catalog.get("source_status", [])),
            "item_count": len(catalog.get("items", [])),
            "freshness": [
                {
                    "source_id": row.get("source_id", ""),
                    "freshness_status": row.get("freshness_status", ""),
                    "item_count": row.get("item_count", "0"),
                }
                for row in catalog.get("source_status", [])
            ],
        }
    payload = {
        "schema_version": SOURCE_REFRESH_LIVE_RUN_SCHEMA_VERSION,
        "generated_at": _now(),
        "inputs": {
            "live_gate_path": Path(live_gate_path).as_posix(),
            "evidence_output_path": Path(evidence_output_path).as_posix(),
        },
        "response": normalized_response,
        "expected_response": expected_response,
        "approval_status": approval_status,
        "execution": {
            "execute_requested": execute,
            "confirm_live_network": confirm_live_network,
            "status": execution_status,
            "source_ids": source_ids,
            "proposed_commands": proposed_commands,
            "blockers": blockers,
        },
        "catalog_summary": catalog_summary,
        "external_effect_performed": external_effect_performed,
        "policy": _research_only_policy(),
        "next_step": _live_run_next_step(execution_status, approval_status),
    }
    return write_json(payload, output_path)


def validate_source_refresh_live_run_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SOURCE_REFRESH_LIVE_RUN_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("approval_status") not in {"approved", "missing", "invalid", "not_required"}:
        errors.append("approval_status must be approved, missing, invalid, or not_required")
    execution = payload.get("execution", {})
    if execution.get("status") not in {"not_requested", "ready_to_execute", "blocked", "executed"}:
        errors.append("execution.status must be not_requested, ready_to_execute, blocked, or executed")
    if payload.get("external_effect_performed") is True:
        if execution.get("status") != "executed":
            errors.append("external_effect_performed true requires execution.status executed")
        if not execution.get("execute_requested") or not execution.get("confirm_live_network"):
            errors.append("executed live run requires execute_requested and confirm_live_network")
    else:
        if execution.get("status") == "executed":
            errors.append("execution.status executed requires external_effect_performed true")
    for command in execution.get("proposed_commands", []):
        if any(blocked in command for blocked in ["--send", "--confirm-host-write", "launchctl", "tailscale serve --bg"]):
            errors.append("proposed command crosses non-network external-effect boundary")
    policy = payload.get("policy", {})
    if policy.get("output_boundary") != "research_only":
        errors.append("policy.output_boundary must be research_only")
    return errors


def validate_source_refresh_live_run_file(path: str | Path) -> list[str]:
    return validate_source_refresh_live_run_payload(load_json(path))


def build_source_refresh_live_preflight(
    *,
    live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    output_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    intend_execute: bool = False,
    confirm_live_network: bool = False,
) -> dict[str, Any]:
    live_run = load_json(live_run_path)
    live_run_errors = validate_source_refresh_live_run_payload(live_run)
    if live_run_errors:
        raise ValueError("; ".join(live_run_errors))
    execution = live_run.get("execution", {})
    source_ids = list(execution.get("source_ids", []))
    proposed_commands = list(execution.get("proposed_commands", []))
    blockers: list[str] = []
    warnings: list[str] = []
    if live_run.get("approval_status") == "not_required":
        status = "not_required"
    else:
        status = "blocked"
        if live_run.get("approval_status") != "approved":
            blockers.append("approval_not_approved")
        if execution.get("status") != "ready_to_execute":
            blockers.append(f"live_run_status_{execution.get('status', 'unknown')}")
        if not intend_execute:
            blockers.append("execute_intent_missing")
        if not confirm_live_network:
            blockers.append("confirm_live_network_missing")
        if live_run.get("external_effect_performed") is True:
            blockers.append("live_run_already_executed")
        if not source_ids:
            blockers.append("no_live_sources")
        if any(_forbidden_live_preflight_command(command) for command in proposed_commands):
            blockers.append("forbidden_external_effect_command")
        evidence_output = str(live_run.get("inputs", {}).get("evidence_output_path", ""))
        if not evidence_output:
            blockers.append("missing_evidence_output_path")
        elif not evidence_output.startswith("reports/evidence/"):
            warnings.append("evidence_output_path_outside_default_reports_evidence")
        if not blockers:
            status = "passed"
    payload = {
        "schema_version": SOURCE_REFRESH_LIVE_PREFLIGHT_SCHEMA_VERSION,
        "generated_at": _now(),
        "inputs": {
            "live_run_path": Path(live_run_path).as_posix(),
            "live_gate_path": live_run.get("inputs", {}).get("live_gate_path", ""),
            "evidence_output_path": live_run.get("inputs", {}).get("evidence_output_path", ""),
        },
        "status": status,
        "approval_status": live_run.get("approval_status", ""),
        "live_run_status": execution.get("status", ""),
        "requested_execution": {
            "intend_execute": intend_execute,
            "confirm_live_network": confirm_live_network,
        },
        "source_ids": source_ids,
        "proposed_commands": proposed_commands,
        "blockers": blockers,
        "warnings": warnings,
        "external_effect_performed": False,
        "policy": _research_only_policy(),
        "next_step": _live_preflight_next_step(status, blockers),
    }
    return write_json(payload, output_path)


def validate_source_refresh_live_preflight_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SOURCE_REFRESH_LIVE_PREFLIGHT_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"passed", "blocked", "not_required"}:
        errors.append("status must be passed, blocked, or not_required")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if not isinstance(payload.get("blockers", []), list):
        errors.append("blockers must be a list")
    if not isinstance(payload.get("warnings", []), list):
        errors.append("warnings must be a list")
    requested = payload.get("requested_execution", {})
    if payload.get("status") == "passed":
        if payload.get("approval_status") != "approved":
            errors.append("passed preflight requires approval_status approved")
        if payload.get("live_run_status") != "ready_to_execute":
            errors.append("passed preflight requires live_run_status ready_to_execute")
        if requested.get("intend_execute") is not True or requested.get("confirm_live_network") is not True:
            errors.append("passed preflight requires intend_execute and confirm_live_network")
        if not payload.get("source_ids"):
            errors.append("passed preflight requires source_ids")
        if payload.get("blockers"):
            errors.append("passed preflight must not include blockers")
    for command in payload.get("proposed_commands", []):
        if _forbidden_live_preflight_command(command):
            errors.append("proposed command crosses non-network external-effect boundary")
    policy = payload.get("policy", {})
    if policy.get("output_boundary") != "research_only":
        errors.append("policy.output_boundary must be research_only")
    return errors


def validate_source_refresh_live_preflight_file(path: str | Path) -> list[str]:
    return validate_source_refresh_live_preflight_payload(load_json(path))


def collect_topic_evidence(
    *,
    topics_path: str | Path = DEFAULT_TOPICS_PATH,
    plan_path: str | Path = DEFAULT_RESEARCH_PLAN_OUTPUT,
    output_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    source_ids: list[str] | None = None,
) -> dict[str, Any]:
    config = load_topic_config(topics_path)
    plan = load_json(plan_path)
    raw_catalog = build_public_evidence_catalog(source_ids)
    target_topics = _target_topic_set(config)
    filtered_items = []
    gaps = []
    for item in raw_catalog.get("items", []):
        matched_interests = _matched_interest_ids(item, config)
        if set(item.get("topics", [])).intersection(target_topics) or matched_interests:
            updated = dict(item)
            updated["matched_interests"] = matched_interests
            filtered_items.append(updated)
    if len({item.get("source_name") for item in filtered_items}) < 2:
        filtered_items = [dict(item, matched_interests=_matched_interest_ids(item, config)) for item in raw_catalog.get("items", [])]
        gaps.append("topic_filter_too_thin_used_full_sample_cache")
    evidence_items = [_payload_to_item(item) for item in filtered_items]
    graph = build_public_evidence_graph(evidence_items)
    catalog = {
        "schema_version": PUBLIC_EVIDENCE_SCHEMA_VERSION,
        "generated_at": _now(),
        "mode": "sample_cache_topic_research",
        "source_status": _source_status(filtered_items),
        "source_matrix": SOURCE_MATRIX,
        "items": filtered_items,
        "graph": graph,
        "feasibility": evaluate_feasibility(evidence_items, graph),
        "configured_interests": config.get("interests", []),
        "research_plan": _plan_summary(plan),
        "collection_gaps": gaps + _collection_gaps(filtered_items, config),
    }
    memory = update_topic_memory(config=config, plan=plan, catalog=catalog, memory_path=memory_path)
    catalog["topic_memory_snapshot"] = {
        "memory_path": Path(memory_path).as_posix(),
        "run_count": memory.get("run_count", 0),
        "topics": [
            {
                "topic_id": item.get("topic_id"),
                "name": item.get("name"),
                "new_evidence_count": item.get("new_evidence_count", 0),
                "changed_since_previous": item.get("changed_since_previous", False),
                "summary": item.get("latest_summary", ""),
            }
            for item in memory.get("topics", [])
        ],
    }
    return write_json(catalog, output_path)


def update_topic_memory(
    *,
    config: dict[str, Any],
    plan: dict[str, Any],
    catalog: dict[str, Any],
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
) -> dict[str, Any]:
    target = Path(memory_path)
    previous = load_json(target) if target.exists() else {
        "schema_version": TOPIC_MEMORY_SCHEMA_VERSION,
        "generated_at": "",
        "run_count": 0,
        "topics": [],
        "runs": [],
    }
    previous_by_id = {item.get("topic_id"): item for item in previous.get("topics", [])}
    plan_by_id = {item.get("topic_id"): item for item in plan.get("plan_items", [])}
    topic_rows = []
    for interest in config.get("interests", []):
        topic_id = interest["topic_id"]
        items = [item for item in catalog.get("items", []) if topic_id in item.get("matched_interests", [])]
        item_ids = sorted(item.get("item_id", "") for item in items if item.get("item_id"))
        previous_ids = set(previous_by_id.get(topic_id, {}).get("last_seen_item_ids", []))
        new_ids = sorted(set(item_ids) - previous_ids)
        source_names = sorted({item.get("source_name", "") for item in items if item.get("source_name")})
        titles = [item.get("title", "") for item in items[:5]]
        plan_item = plan_by_id.get(topic_id, {})
        topic_rows.append({
            "topic_id": topic_id,
            "name": interest["name"],
            "target_topics": interest.get("target_topics", []),
            "last_seen_item_ids": item_ids,
            "latest_titles": titles,
            "source_names": source_names,
            "new_evidence_count": len(new_ids),
            "changed_since_previous": bool(new_ids),
            "latest_summary": _topic_memory_summary(interest, titles, source_names, new_ids),
            "daily_questions": plan_item.get("daily_questions", []),
            "collection_gaps": _topic_gaps(items, plan_item),
        })
    run_record = {
        "run_id": plan.get("run_id", "daily-research"),
        "generated_at": _now(),
        "evidence_catalog": catalog.get("generated_at", ""),
        "topic_count": len(topic_rows),
        "changed_topics": [row["topic_id"] for row in topic_rows if row["changed_since_previous"]],
    }
    memory = {
        "schema_version": TOPIC_MEMORY_SCHEMA_VERSION,
        "generated_at": _now(),
        "run_count": int(previous.get("run_count", 0) or 0) + 1,
        "topics": topic_rows,
        "runs": (previous.get("runs", []) + [run_record])[-20:],
        "policy": _research_only_policy(),
    }
    return write_json(memory, target)


def validate_topic_memory_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != TOPIC_MEMORY_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if not payload.get("topics"):
        errors.append("topics must not be empty")
    if int(payload.get("run_count", 0) or 0) < 1:
        errors.append("run_count must be at least 1")
    for index, topic in enumerate(payload.get("topics", [])):
        for field in ["topic_id", "name", "last_seen_item_ids", "latest_summary", "collection_gaps"]:
            if field not in topic:
                errors.append(f"topics[{index}] missing {field}")
    return errors


def validate_topic_memory_file(path: str | Path) -> list[str]:
    return validate_topic_memory_payload(load_json(path))


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(payload: dict[str, Any], path: str | Path) -> dict[str, Any]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def _normalize_interest(raw: dict[str, Any]) -> dict[str, Any]:
    name = str(raw.get("name", "")).strip()
    if not name:
        raise ValueError("interest name is required")
    description = str(raw.get("description", "")).strip()
    keywords = [str(item).strip() for item in raw.get("keywords", []) if str(item).strip()]
    beginner_focus = str(raw.get("beginner_focus", "")).strip() or f"{name} 흐름이 시장에 왜 중요한지 초보자 관점에서 이해한다."
    topic_text = " ".join([name, description, " ".join(keywords)])
    target_topics = sorted(set(detect_topics(topic_text)))
    return {
        "topic_id": raw.get("topic_id") or _slugify(name),
        "name": name,
        "description": description,
        "beginner_focus": beginner_focus,
        "keywords": keywords,
        "target_topics": target_topics,
        "status": raw.get("status", "active"),
    }


def _research_only_policy() -> dict[str, Any]:
    return {
        "output_boundary": "research_only",
        "disallowed": [
            "paid_api_operations",
            "account_credentials",
            "live_trading",
            "discretionary_management",
            "unsupported_personalized_recommendations",
        ],
    }


def _target_topic_set(config: dict[str, Any]) -> set[str]:
    return {topic for interest in config.get("interests", []) for topic in interest.get("target_topics", [])}


def _matched_interest_ids(item: dict[str, Any], config: dict[str, Any]) -> list[str]:
    text = " ".join([item.get("title", ""), item.get("text", ""), " ".join(item.get("topics", []))]).lower()
    matched = []
    for interest in config.get("interests", []):
        target_topics = set(interest.get("target_topics", []))
        keywords = [keyword.lower() for keyword in interest.get("keywords", [])]
        if target_topics.intersection(item.get("topics", [])) or any(keyword and keyword in text for keyword in keywords):
            matched.append(interest["topic_id"])
    return matched


def _payload_to_item(payload: dict[str, Any]) -> PublicEvidenceItem:
    return PublicEvidenceItem(
        item_id=payload.get("item_id", ""),
        source_name=payload.get("source_name", ""),
        evidence_type=payload.get("evidence_type", ""),
        title=payload.get("title", ""),
        published_at=payload.get("published_at", ""),
        url=payload.get("url", ""),
        text=payload.get("text", ""),
        topics=payload.get("topics", []),
        entities=payload.get("entities", []),
        freshness_status=payload.get("freshness_status", "unknown"),
    )


def _source_status(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for source_name in sorted({item.get("source_name", "") for item in items if item.get("source_name")}):
        source_items = [item for item in items if item.get("source_name") == source_name]
        freshness = sorted({item.get("freshness_status", "unknown") for item in source_items})
        relevance_scores = [
            float(item.get("relevance", {}).get("score", 0))
            for item in source_items
            if item.get("relevance")
        ]
        average_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        rows.append({
            "source_id": _slugify(source_name),
            "source_name": source_name,
            "adapter_id": "sample_cache_topic_research",
            "item_count": str(len(source_items)),
            "freshness_status": freshness[0] if freshness else "unknown",
            "relevance_score": f"{average_relevance:.2f}",
            "relevance_label": _relevance_label(average_relevance),
        })
    return rows


def _relevance_label(score: float) -> str:
    if score >= 0.75:
        return "strong"
    if score >= 0.50:
        return "usable"
    if score >= 0.30:
        return "thin"
    return "weak"


def _plan_summary(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": plan.get("run_id", ""),
        "generated_at": plan.get("generated_at", ""),
        "topic_count": len(plan.get("plan_items", [])),
        "next_step": plan.get("next_step", ""),
    }


def _collection_gaps(items: list[dict[str, Any]], config: dict[str, Any]) -> list[str]:
    gaps = []
    source_names = {item.get("source_name") for item in items}
    if len(source_names) < 3:
        gaps.append("less_than_three_source_families")
    matched_interest_ids = {topic_id for item in items for topic_id in item.get("matched_interests", [])}
    configured_ids = {item.get("topic_id") for item in config.get("interests", [])}
    missing = sorted(configured_ids - matched_interest_ids)
    if missing:
        gaps.append("no_matching_evidence_for:" + ",".join(missing))
    gaps.extend(["live_refresh_not_enabled", "source_license_review_pending"])
    return gaps


def _topic_gaps(items: list[dict[str, Any]], plan_item: dict[str, Any]) -> list[str]:
    gaps = []
    if not items:
        gaps.append("no_matching_evidence")
    if len({item.get("source_name") for item in items}) < 2:
        gaps.append("needs_second_source_family")
    gaps.extend(plan_item.get("missing_evidence", [])[:2])
    return sorted(set(gaps))


def _topic_memory_summary(interest: dict[str, Any], titles: list[str], source_names: list[str], new_ids: list[str]) -> str:
    if not titles:
        return f"{interest['name']} 주제는 아직 연결된 공개 근거가 부족합니다."
    change_text = f"새 근거 {len(new_ids)}개" if new_ids else "새 근거 없음"
    return f"{interest['name']} 주제는 {', '.join(source_names) or 'sample cache'}에서 {len(titles)}개 근거를 확인했습니다. {change_text}."


def _vault_notes_by_topic(vault: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    if vault.get("schema_version") != "knowledge_vault_compile.v1":
        return {}
    rows: dict[str, list[dict[str, Any]]] = {}
    for note in vault.get("compiled_notes", []):
        topic_id = note.get("topic_id", "")
        if topic_id:
            rows.setdefault(topic_id, []).append(note)
    return rows


def _review_signals_by_topic(review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if review.get("schema_version") != "daily_review.v1":
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for signal in review.get("topic_signals", []):
        topic_id = signal.get("topic_id", "")
        if topic_id:
            rows[topic_id] = signal
    return rows


def _apply_scout_rotation_guard(
    *,
    recommendations: list[dict[str, Any]],
    recommendation_contexts: dict[str, dict[str, Any]],
    memory_run_count: int,
) -> dict[str, Any]:
    if not recommendations:
        return {
            "status": "missing",
            "run_count": memory_run_count,
            "pre_rotation_topic": "",
            "selected_topic": "",
            "rotated": False,
            "reason": "추천 후보가 없습니다.",
            "external_effect_performed": False,
        }
    base_sorted = sorted(recommendations, key=lambda row: (-float(row["score"]), row["name"]))
    top = base_sorted[0]
    top_id = top.get("topic_id", "")
    top_review = top.get("review_signal", {})
    if memory_run_count < 3:
        return {
            "status": "not_needed",
            "run_count": memory_run_count,
            "pre_rotation_topic": top_id,
            "selected_topic": top_id,
            "rotated": False,
            "reason": "아직 반복 실행이 충분히 쌓이지 않아 점수순 추천을 유지합니다.",
            "external_effect_performed": False,
        }
    if _positive_scout_review(top_review):
        return {
            "status": "operator_override",
            "run_count": memory_run_count,
            "pre_rotation_topic": top_id,
            "selected_topic": top_id,
            "rotated": False,
            "reason": "사용자가 이 주제를 더 보겠다는 피드백을 남겨 순환보다 operator review를 우선합니다.",
            "external_effect_performed": False,
        }
    if top.get("changed_since_previous") or int(top.get("new_evidence_count", 0) or 0) > 0:
        return {
            "status": "not_needed",
            "run_count": memory_run_count,
            "pre_rotation_topic": top_id,
            "selected_topic": top_id,
            "rotated": False,
            "reason": "최고점 주제에 새 근거 또는 변화가 있어 반복이어도 먼저 봅니다.",
            "external_effect_performed": False,
        }
    eligible = [
        row for row in recommendations
        if row.get("topic_id") != top_id
        and row.get("latest_titles")
        and row.get("source_names")
        and not _positive_scout_review(row.get("review_signal", {}))
    ]
    if not eligible:
        return {
            "status": "insufficient_alternative",
            "run_count": memory_run_count,
            "pre_rotation_topic": top_id,
            "selected_topic": top_id,
            "rotated": False,
            "reason": "반복은 감지됐지만 오늘 순환할 만한 대체 주제의 근거가 부족합니다.",
            "external_effect_performed": False,
        }
    topic_order = [row.get("topic_id", "") for row in recommendations]
    start = memory_run_count % len(recommendations)
    selected = next(
        (
            recommendations[(start + offset) % len(recommendations)]
            for offset in range(len(recommendations))
            if recommendations[(start + offset) % len(recommendations)] in eligible
        ),
        eligible[0],
    )
    selected_id = selected.get("topic_id", "")
    bonus = max(0.1, round(float(top.get("score", 0) or 0) - float(selected.get("score", 0) or 0) + 0.1, 2))
    selected["score"] = round(float(selected.get("score", 0) or 0) + bonus, 2)
    selected.setdefault("score_factors", []).append({
        "name": "coverage_rotation_guard",
        "delta": bonus,
        "reason": "새 근거 없는 반복 추천을 줄이고 오늘 학습 커버리지를 넓힘",
    })
    context = recommendation_contexts.get(selected_id, {})
    memory_topic = context.get("memory_topic", selected)
    selected["action"] = _scout_action(float(selected.get("score", 0) or 0), memory_topic)
    selected["rotation_guard_note"] = "이 주제는 반복 고착을 줄이기 위한 오늘의 커버리지 순환 후보입니다."
    if context:
        selected["operator_brief"] = _scout_operator_brief(
            recommendation=selected,
            interest=context.get("interest", {}),
            memory_topic=memory_topic,
            plan_item=context.get("plan_item", {}),
        )
        selected["operator_brief"]["headline"] = f"오늘은 {selected.get('name', '이 주제')}로 커버리지를 넓힙니다."
        selected["operator_brief"]["why_today"] = (
            selected["operator_brief"].get("why_today", "")
            + " 기존 최고점 주제가 새 근거 없이 반복되어, 오늘은 다른 흐름을 먼저 보도록 순환 가드가 개입했습니다."
        ).strip()
        selected["beginner_reading_order"] = _scout_reading_order(
            recommendation=selected,
            plan_item=context.get("plan_item", {}),
            memory_topic=memory_topic,
            linked_notes=context.get("linked_notes", []),
        )
    return {
        "status": "rotated",
        "run_count": memory_run_count,
        "pre_rotation_topic": top_id,
        "selected_topic": selected_id,
        "rotated": True,
        "reason": (
            f"{top.get('name', top_id)}가 새 근거 없이 반복되어 "
            f"{selected.get('name', selected_id)}로 오늘 커버리지를 넓혔습니다."
        ),
        "coverage_slot": topic_order[start] if topic_order else "",
        "external_effect_performed": False,
    }


def _positive_scout_review(review_signal: dict[str, Any] | None) -> bool:
    signal = review_signal or {}
    if str(signal.get("latest_status", "")) != "want_more" and float(signal.get("score_delta", 0) or 0) <= 0:
        return False
    return _scout_review_is_fresh(signal)


def _scout_review_is_fresh(review_signal: dict[str, Any] | None) -> bool:
    signal = review_signal or {}
    responses = signal.get("responses", [])
    recorded_at = responses[-1].get("recorded_at", "") if responses else ""
    if not recorded_at:
        return True
    try:
        parsed = datetime.fromisoformat(str(recorded_at).replace("Z", "+00:00"))
    except ValueError:
        return False
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds() / 3600
    return age_hours <= 36


def _scout_score(
    *,
    memory_topic: dict[str, Any],
    plan_item: dict[str, Any],
    linked_notes: list[dict[str, Any]],
    review_signal: dict[str, Any] | None = None,
) -> tuple[float, list[dict[str, Any]]]:
    score = 1.0
    factors = [{"name": "base_interest", "delta": 1.0, "reason": "configured local interest"}]
    review_signal = review_signal or {}
    review_delta = float(review_signal.get("score_delta", 0) or 0)
    if review_delta and _scout_review_is_fresh(review_signal):
        score += review_delta
        factors.append({
            "name": "operator_review",
            "delta": round(review_delta, 2),
            "reason": review_signal.get("reason", "operator daily review signal"),
        })
    elif review_delta:
        factors.append({
            "name": "operator_review_expired",
            "delta": 0,
            "reason": "오래된 operator review라 오늘 scout 점수에는 반영하지 않음",
        })
    new_count = int(memory_topic.get("new_evidence_count", 0) or 0)
    if new_count:
        delta = min(3.0, new_count * 0.8)
        score += delta
        factors.append({"name": "new_evidence", "delta": round(delta, 2), "reason": f"새 근거 {new_count}개"})
    if memory_topic.get("changed_since_previous"):
        score += 1.5
        factors.append({"name": "changed_since_previous", "delta": 1.5, "reason": "이전 실행 대비 변화 있음"})
    source_count = len(memory_topic.get("source_names", []))
    if source_count >= 3:
        score += 1.2
        factors.append({"name": "source_breadth", "delta": 1.2, "reason": "세 개 이상 source family"})
    elif source_count >= 2:
        score += 0.7
        factors.append({"name": "source_breadth", "delta": 0.7, "reason": "두 개 source family"})
    if linked_notes:
        delta = min(1.2, len(linked_notes) * 0.6)
        score += delta
        factors.append({"name": "vault_link", "delta": round(delta, 2), "reason": "컴파일된 원천 노트 연결"})
    gaps = memory_topic.get("collection_gaps", [])
    if gaps:
        score += 0.4
        factors.append({"name": "needs_inspection", "delta": 0.4, "reason": "부족한 근거를 점검해야 함"})
    if not memory_topic.get("latest_titles"):
        score -= 1.0
        factors.append({"name": "thin_evidence", "delta": -1.0, "reason": "연결된 공개 근거 부족"})
    if not plan_item.get("daily_questions"):
        score -= 0.5
        factors.append({"name": "weak_plan", "delta": -0.5, "reason": "daily question 없음"})
    return max(0.0, score), factors


def _scout_action(score: float, memory_topic: dict[str, Any]) -> str:
    if score >= 3.0 or memory_topic.get("changed_since_previous"):
        return "inspect_first"
    if score >= 1.5:
        return "monitor"
    return "defer"


def _scout_confidence(memory_topic: dict[str, Any]) -> str:
    source_count = len(memory_topic.get("source_names", []))
    if source_count >= 3:
        return "medium"
    if source_count >= 2:
        return "low-medium"
    return "low"


def _scout_why(interest: dict[str, Any], memory_topic: dict[str, Any], linked_notes: list[dict[str, Any]], factors: list[dict[str, Any]]) -> str:
    del factors
    parts = []
    if memory_topic.get("latest_titles"):
        parts.append(f"근거 {len(memory_topic.get('latest_titles', []))}개")
    else:
        parts.append("근거 얇음")
    if memory_topic.get("source_names"):
        parts.append(f"출처군 {len(memory_topic.get('source_names', []))}개")
    if linked_notes:
        parts.append(f"vault {len(linked_notes)}개")
    if memory_topic.get("collection_gaps"):
        parts.append("부족한 근거 점검 필요")
    return " · ".join(part for part in parts if part) + ". 결론보다 먼저 확인할 주제입니다."


def _scout_next_question(plan_item: dict[str, Any], memory_topic: dict[str, Any], linked_notes: list[dict[str, Any]]) -> str:
    if linked_notes:
        return f"Vault 노트 '{linked_notes[0].get('title', '')}'가 오늘 근거와 같은 방향을 가리키나요?"
    questions = plan_item.get("daily_questions", [])
    if questions:
        return questions[0]
    name = memory_topic.get("name", "이 주제")
    return f"오늘 {name}를 먼저 볼 만큼 근거가 충분한가요?"


def _scout_operator_brief(
    *,
    recommendation: dict[str, Any],
    interest: dict[str, Any],
    memory_topic: dict[str, Any],
    plan_item: dict[str, Any],
) -> dict[str, str]:
    source_count = len(memory_topic.get("source_names", []))
    latest_titles = memory_topic.get("latest_titles", [])
    gaps = memory_topic.get("collection_gaps", [])
    name = recommendation.get("name", interest.get("name", "오늘 주제"))
    if recommendation.get("action") == "inspect_first":
        headline = f"오늘은 {name}부터 봅니다."
    elif recommendation.get("action") == "monitor":
        headline = f"{name}는 짧게 점검합니다."
    else:
        headline = f"{name}는 아직 보류해도 됩니다."
    if latest_titles:
        why_today = f"최근 연결된 공개 근거 {len(latest_titles)}개와 출처군 {source_count}개가 있어 시장 흐름을 배우기 좋은 주제입니다."
    else:
        why_today = "연결된 공개 근거가 얇아서 결론보다 자료 부족 자체를 먼저 배우는 주제입니다."
    if memory_topic.get("changed_since_previous"):
        why_today += " 이전 실행 대비 새 근거가 있어 변화 여부를 확인해야 합니다."
    beginner_focus = interest.get("beginner_focus") or plan_item.get("beginner_reason", "")
    confidence_note = f"신뢰도는 {recommendation.get('confidence', 'low')}입니다. 초보자용 학습/리서치 판단으로만 사용합니다."
    missing_note = " · ".join(_gap_label(gap) for gap in gaps[:3]) if gaps else "오늘 scout 기준의 핵심 missing evidence는 크지 않습니다."
    return {
        "headline": headline,
        "why_today": why_today,
        "beginner_focus": beginner_focus,
        "confidence_note": confidence_note,
        "missing_evidence_note": missing_note,
        "research_only_note": "계좌 접근, 주문, 일임, 개인화 매수/매도 지시는 하지 않습니다.",
    }


def _scout_reading_order(
    *,
    recommendation: dict[str, Any],
    plan_item: dict[str, Any],
    memory_topic: dict[str, Any],
    linked_notes: list[dict[str, Any]],
) -> list[dict[str, str]]:
    name = recommendation.get("name", "오늘 주제")
    titles = memory_topic.get("latest_titles", [])
    first_title = titles[0] if titles else ""
    steps = [
        {
            "step": "1",
            "title": f"{name}를 왜 보는지 먼저 읽기",
            "why": recommendation.get("operator_brief", {}).get("why_today", recommendation.get("why", "")),
            "done_when": "오늘 이 주제가 중요한 이유를 한 문장으로 말할 수 있습니다.",
        },
        {
            "step": "2",
            "title": "가장 가까운 공개 근거 확인",
            "why": first_title or "연결 근거가 얇으면 source refresh 필요 여부를 먼저 확인합니다.",
            "done_when": "근거가 충분한지, 오래됐는지, 한쪽으로 치우쳤는지 표시할 수 있습니다.",
        },
        {
            "step": "3",
            "title": "반대 근거와 missing evidence 표시",
            "why": recommendation.get("next_question", ""),
            "done_when": "오늘 결론을 약하게 만드는 이유를 최소 하나 적을 수 있습니다.",
        },
    ]
    if linked_notes:
        steps.insert(2, {
            "step": "2b",
            "title": "내 vault 노트와 연결하기",
            "why": linked_notes[0].get("title", ""),
            "done_when": "예전 노트가 오늘 근거와 같은 방향인지, 반대 방향인지 구분합니다.",
        })
    questions = plan_item.get("daily_questions", [])
    if questions:
        steps.append({
            "step": str(len(steps) + 1),
            "title": "내일 이어갈 질문 고르기",
            "why": questions[-1],
            "done_when": "내일 scout에 반영할 질문 하나를 고릅니다.",
        })
    return steps[:5]


def _scout_copy_ready_responses(recommendation: dict[str, Any]) -> list[dict[str, str]]:
    name = recommendation.get("name", "오늘 주제")
    quoted = name.replace('"', "'")
    return [
        {
            "intent": "more",
            "command": f'more "{quoted}" "내일도 이 주제를 더 보고 싶다"',
            "effect": "다음 scout에서 이 주제의 operator_review 점수를 올립니다.",
        },
        {
            "intent": "confusing",
            "command": f'confusing "{quoted}" "초보자 설명과 반대 근거를 더 쉽게 풀어줘"',
            "effect": "다음 brief에서 tutor/skeptic 설명을 강화합니다.",
        },
        {
            "intent": "done",
            "command": f'done "{quoted}" "오늘은 충분히 읽었다"',
            "effect": "handoff에서 오늘 주제 확인 상태로 남길 수 있습니다.",
        },
    ]


def _scout_pattern_watch() -> list[dict[str, str]]:
    return [
        {
            "pattern": "local_worker_memory_scheduler",
            "status": "adopted",
            "why": "daily run, archive, review memory, run ledger가 로컬 애널리스트 루프의 기본 골격입니다.",
        },
        {
            "pattern": "multi_role_research_council",
            "status": "adopted",
            "why": "역할별 검토는 결론 과신을 낮추고 초보자 설명을 분리합니다.",
        },
        {
            "pattern": "live_browser_scrape_tools",
            "status": "gated_candidate",
            "why": "최신 근거 수집에는 유용하지만 live network와 브라우저 권한은 별도 preflight 뒤에만 허용합니다.",
        },
    ]


def _refresh_action(*, source_name: str, adapter_id: str, cadence: str, priority: str, reason: str, command: str) -> dict[str, Any]:
    return {
        "source_name": source_name,
        "adapter_id": adapter_id,
        "cadence": cadence,
        "priority": priority,
        "reason": reason,
        "command": command,
        "dry_run_only": True,
        "expected_artifact": _expected_refresh_artifact(adapter_id),
    }


def _refresh_apply_result(index: int, action: dict[str, Any]) -> dict[str, Any]:
    adapter_id = action.get("adapter_id", "")
    source_name = action.get("source_name", "")
    command = action.get("command", "")
    expected_artifact = action.get("expected_artifact", _expected_refresh_artifact(adapter_id))
    if adapter_id in {"gdelt-live", "stooq-live"}:
        decision = "blocked"
        status = "needs_live_network_gate"
        approval_required = "live_network_refresh"
        reason = f"{source_name} 새로고침은 무료/no-key 후보지만 라이브 네트워크 호출이므로 별도 승인 전에는 실행하지 않습니다."
    elif adapter_id in {"vault-compile", "sample-cache", "sec-sample"}:
        decision = "ready"
        status = "dry_run_ready"
        approval_required = "none"
        reason = f"{source_name} 작업은 로컬/샘플 캐시 경계 안에서 다음 dry-run 검증 대상으로 사용할 수 있습니다."
    else:
        decision = "skipped"
        status = "unknown_adapter"
        approval_required = "operator_review"
        reason = f"{source_name} adapter 경계가 아직 정의되지 않아 실행하지 않습니다."
    return {
        "action_index": index,
        "source_name": source_name,
        "adapter_id": adapter_id,
        "decision": decision,
        "status": status,
        "will_execute": False,
        "approval_required": approval_required,
        "reason": reason,
        "command": command,
        "expected_artifact": expected_artifact,
    }


def _unique_preserve_order(values: Any) -> list[str]:
    seen = set()
    rows = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            rows.append(value)
    return rows


def _live_source_ids_from_gate(gate: dict[str, Any]) -> list[str]:
    source_ids = []
    for action in gate.get("blocked_actions", []):
        adapter_id = action.get("adapter_id", "")
        if adapter_id in {"gdelt-live", "stooq-live"}:
            source_ids.append(adapter_id)
    if source_ids:
        source_ids.append("sec-sample")
    return _unique_preserve_order(source_ids)


def _live_run_next_step(execution_status: str, approval_status: str) -> str:
    if execution_status == "executed":
        return "validate_live_evidence_catalog_then_refresh_daily_loop"
    if execution_status == "ready_to_execute":
        return "operator_may_run_with_execute_and_confirm_live_network"
    if approval_status in {"missing", "invalid"}:
        return "provide_copy_ready_live_network_refresh_approval"
    return "review_live_refresh_gate"


def _live_preflight_next_step(status: str, blockers: list[str]) -> str:
    if status == "passed":
        return "operator_may_execute_live_refresh_with_current_proof"
    if status == "not_required":
        return "no_live_refresh_execution_needed"
    if "approval_not_approved" in blockers:
        return "provide_copy_ready_live_network_refresh_approval"
    if "execute_intent_missing" in blockers or "confirm_live_network_missing" in blockers:
        return "rerun_preflight_with_explicit_execute_intent_and_live_network_confirmation"
    return "fix_live_refresh_preflight_blockers"


def _forbidden_live_preflight_command(command: str) -> bool:
    return any(
        blocked in command
        for blocked in ["--send", "--confirm-host-write", "launchctl", "tailscale serve --bg"]
    )


def _needs_news_refresh(recommendations: list[dict[str, Any]], source_status: dict[str, dict[str, Any]]) -> bool:
    if any("live_refresh" in item.get("missing_evidence", []) for item in recommendations):
        return True
    gdelt = source_status.get("GDELT", {})
    return gdelt.get("freshness_status") in {"sample_cache", "live_error_fallback_sample", "empty", None}


def _needs_price_refresh(recommendations: list[dict[str, Any]], source_status: dict[str, dict[str, Any]]) -> bool:
    topics = {topic for item in recommendations for topic in [item.get("topic_id", ""), *item.get("source_names", [])]}
    if {"us-rates", "consumer-weakness"}.intersection(topics):
        return True
    stooq = source_status.get("Stooq", {})
    return stooq.get("freshness_status") in {"sample_cache", "live_error_fallback_sample", "empty", None}


def _needs_filing_review(recommendations: list[dict[str, Any]], source_status: dict[str, dict[str, Any]]) -> bool:
    if any(item.get("linked_vault_notes") for item in recommendations):
        return True
    sec = source_status.get("SEC EDGAR", {})
    return sec.get("freshness_status") in {"sample_cache", "empty", None}


def _expected_refresh_artifact(adapter_id: str) -> str:
    if adapter_id == "vault-compile":
        return "reports/vault/compile.json"
    if adapter_id == "sample-cache":
        return "reports/evidence/daily-evidence-catalog.json"
    return "reports/evidence/live-evidence-catalog.json"


def _questions_for_topics(topics: list[str], name: str) -> list[str]:
    questions = [f"오늘 {name}에서 초보자가 먼저 이해해야 할 변화는 무엇인가요?"]
    if "ai_infrastructure" in topics or "semiconductors" in topics:
        questions.append("AI/반도체 기대가 실제 수요, 공급망, 실적 근거로 이어지고 있나요?")
    if "rates" in topics:
        questions.append("금리와 국채 수익률 변화가 이 테마의 가격 부담을 키우고 있나요?")
    if "consumer" in topics or "inflation" in topics:
        questions.append("소비와 물가 흐름이 기업 매출 기대를 약하게 만들 신호가 있나요?")
    if "risk" in topics:
        questions.append("이 주제가 틀릴 수 있는 가장 중요한 반대 근거는 무엇인가요?")
    questions.append("다음 브리프에서 확인해야 할 missing evidence는 무엇인가요?")
    return questions[:5]


def _source_needs_for_topics(topics: list[str]) -> list[str]:
    needs = {"GDELT news/event narratives", "Stooq broad market price context"}
    if {"ai_infrastructure", "semiconductors", "consumer", "risk"}.intersection(topics):
        needs.add("SEC EDGAR company filings")
    if {"rates", "inflation", "consumer"}.intersection(topics):
        needs.add("FRED macro series once free-key support is configured")
    return sorted(needs)


def _gap_label(value: str) -> str:
    labels = {
        "live_refresh": "live refresh 미실행",
        "deduplication": "중복 근거 점검 필요",
        "source_terms_review": "source 사용 조건 검토 필요",
        "no_matching_evidence": "직접 연결 근거 없음",
        "needs_second_source_family": "두 번째 출처군 필요",
        "live_refresh_not_enabled": "live refresh 비활성",
        "source_license_review_pending": "source 라이선스 검토 필요",
    }
    if value.startswith("no_matching_evidence_for:"):
        return "일부 관심 주제에 연결 근거 없음"
    return labels.get(value, value.replace("_", " "))


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "topic"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
