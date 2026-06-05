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
)
from mybroker.scenario import TOPIC_DEFINITIONS, detect_topics


TOPIC_CONFIG_SCHEMA_VERSION = "topic_config.v1"
RESEARCH_PLAN_SCHEMA_VERSION = "daily_research_plan.v1"
TOPIC_MEMORY_SCHEMA_VERSION = "topic_memory.v1"
DAILY_SCOUT_SCHEMA_VERSION = "daily_scout.v1"
SOURCE_REFRESH_PLAN_SCHEMA_VERSION = "source_refresh_plan.v1"
SOURCE_REFRESH_APPLY_SCHEMA_VERSION = "source_refresh_apply.v1"

DEFAULT_TOPICS_PATH = Path("config/topics.json")
DEFAULT_RESEARCH_PLAN_OUTPUT = Path("reports/daily/research-plan.json")
DEFAULT_DAILY_SCOUT_OUTPUT = Path("reports/daily/scout.json")
DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT = Path("reports/daily/source-refresh-plan.json")
DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT = Path("reports/daily/source-refresh-apply.json")
DEFAULT_TOPIC_MEMORY_OUTPUT = Path("reports/memory/topic-memory.json")
DEFAULT_DAILY_EVIDENCE_OUTPUT = Path("reports/evidence/daily-evidence-catalog.json")

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
    output_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    run_id: str = "daily-research",
) -> dict[str, Any]:
    config = load_topic_config(topics_path)
    plan = load_json(plan_path)
    evidence = load_json(evidence_path)
    memory = load_json(memory_path)
    vault = load_json(vault_path) if vault_path and Path(vault_path).exists() else {}
    plan_by_id = {item.get("topic_id"): item for item in plan.get("plan_items", [])}
    memory_by_id = {item.get("topic_id"): item for item in memory.get("topics", [])}
    vault_by_topic = _vault_notes_by_topic(vault)
    recommendations = []
    for interest in config.get("interests", []):
        topic_id = interest.get("topic_id", "")
        memory_topic = memory_by_id.get(topic_id, {})
        plan_item = plan_by_id.get(topic_id, {})
        linked_notes = vault_by_topic.get(topic_id, [])
        score, factors = _scout_score(memory_topic=memory_topic, plan_item=plan_item, linked_notes=linked_notes)
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
            "linked_vault_notes": [
                {
                    "title": note.get("title", ""),
                    "source_path": note.get("source_path", ""),
                    "wiki_path": note.get("wiki_path", ""),
                }
                for note in linked_notes[:3]
            ],
            "missing_evidence": memory_topic.get("collection_gaps", []),
            "score_factors": factors,
        }
        recommendations.append(recommendation)
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
        },
        "recommendation_count": len(recommendations),
        "recommended_topic": top,
        "recommendations": recommendations,
        "source_context": {
            "source_count": len(evidence.get("source_status", [])),
            "collection_gaps": evidence.get("collection_gaps", []),
            "mode": evidence.get("mode", ""),
        },
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
        for field in ["topic_id", "name", "score", "priority_rank", "action", "confidence", "why", "next_question"]:
            if field not in item:
                errors.append(f"recommendations[{index}] missing {field}")
        if item.get("action") not in {"inspect_first", "monitor", "defer"}:
            errors.append(f"recommendations[{index}] invalid action")
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


def _scout_score(*, memory_topic: dict[str, Any], plan_item: dict[str, Any], linked_notes: list[dict[str, Any]]) -> tuple[float, list[dict[str, Any]]]:
    score = 1.0
    factors = [{"name": "base_interest", "delta": 1.0, "reason": "configured local interest"}]
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


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "topic"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
