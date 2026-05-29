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

DEFAULT_TOPICS_PATH = Path("config/topics.json")
DEFAULT_RESEARCH_PLAN_OUTPUT = Path("reports/daily/research-plan.json")
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
        rows.append({
            "source_id": _slugify(source_name),
            "source_name": source_name,
            "adapter_id": "sample_cache_topic_research",
            "item_count": str(len(source_items)),
            "freshness_status": "sample_cache",
        })
    return rows


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
