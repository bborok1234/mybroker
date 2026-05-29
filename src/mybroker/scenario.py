from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from mybroker.models import (
    ActionCandidate,
    BeginnerProfile,
    BeginnerExplanation,
    EvidenceCatalog,
    EvidenceSeed,
    MarketEntity,
    MarketMap,
    MarketRelationship,
    PersonaView,
    PolicyDecision,
    ScenarioPath,
    ScenarioReport,
)
from mybroker.policy import classify_action
from mybroker.profile import load_beginner_profile


SCENARIO_SCHEMA_VERSION = "scenario_report.v1"
VERDICT_SCHEMA_VERSION = "market_verdict.v1"
DEFAULT_SEED_PATH = Path(__file__).resolve().parents[2] / "examples" / "seeds"

TOPIC_DEFINITIONS: dict[str, dict[str, Any]] = {
    "ai_infrastructure": {
        "entity": ("AI 인프라", "theme", "AI 서버/데이터센터 수요"),
        "why": "AI 서비스가 늘면 서버, 반도체, 전력, 냉각, 클라우드 기업의 실적 기대가 함께 움직인다.",
        "keywords": ["ai", "인공지능", "데이터센터", "서버", "gpu", "클라우드"],
        "terms": [("AI 인프라", "AI 서비스를 돌리는 데 필요한 반도체, 서버, 데이터센터, 전력 설비를 묶어 부르는 말입니다.")],
    },
    "semiconductors": {
        "entity": ("반도체", "sector", "반도체 업종"),
        "why": "AI와 전자제품 수요의 핵심 공급망이라 성장 기대와 경기 둔화 우려를 동시에 반영한다.",
        "keywords": ["반도체", "chip", "chips", "nvidia", "삼성전자", "sk하이닉스", "tsmc", "memory", "메모리"],
        "terms": [("공급망", "제품이 만들어져 소비자에게 오기까지 필요한 회사와 공정의 연결망입니다.")],
    },
    "rates": {
        "entity": ("금리", "macro", "금리와 유동성"),
        "why": "금리는 주식의 할인율과 투자자 위험선호를 바꾸므로 성장주와 배당주의 평가에 영향을 준다.",
        "keywords": ["금리", "rate", "rates", "fed", "연준", "국채", "yield", "수익률"],
        "terms": [("할인율", "미래 이익을 현재 가치로 바꿀 때 쓰는 비율입니다. 높아지면 성장주의 현재 가치가 낮아질 수 있습니다.")],
    },
    "inflation": {
        "entity": ("물가", "macro", "물가와 소비 부담"),
        "why": "물가가 높으면 중앙은행이 금리를 오래 높게 둘 수 있고 소비 여력이 약해질 수 있다.",
        "keywords": ["물가", "inflation", "cpi", "인플레이션", "가격 상승"],
        "terms": [("인플레이션", "전반적인 상품과 서비스 가격이 계속 오르는 현상입니다.")],
    },
    "consumer": {
        "entity": ("소비", "sector", "소비와 경기 민감 업종"),
        "why": "소비 지표는 기업 매출과 경기 체감의 빠른 신호로 쓰인다.",
        "keywords": ["소비", "retail", "consumer", "가계", "고용", "임금"],
        "terms": [("경기 민감주", "경기가 좋아질 때 실적 기대가 커지고, 나빠질 때 압박을 받기 쉬운 업종입니다.")],
    },
    "risk": {
        "entity": ("리스크", "risk", "시장 위험 요인"),
        "why": "과열, 실적 실망, 지정학, 환율 같은 위험은 좋은 이야기의 가격 반영 여부를 확인하게 만든다.",
        "keywords": ["위험", "risk", "volatility", "변동성", "지정학", "환율", "실적 실망", "과열"],
        "terms": [("변동성", "가격이 오르내리는 폭입니다. 변동성이 크면 수익 기회와 손실 위험이 함께 커집니다.")],
    },
}


def resolve_seed_files(sources: Iterable[str | Path] | None = None) -> list[Path]:
    raw_sources = list(sources or [DEFAULT_SEED_PATH])
    files: list[Path] = []
    for source in raw_sources:
        path = Path(source)
        if path.is_dir():
            files.extend(sorted(path.glob("*.md")))
            files.extend(sorted(path.glob("*.txt")))
        else:
            files.append(path)
    return sorted(dict.fromkeys(files))


def load_evidence_seeds(sources: Iterable[str | Path] | None = None) -> list[EvidenceSeed]:
    seeds: list[EvidenceSeed] = []
    for path in resolve_seed_files(sources):
        if not path.exists():
            raise FileNotFoundError(f"seed file does not exist: {path}")
        text = path.read_text(encoding="utf-8").strip()
        title = _extract_title(text, path)
        topics = detect_topics(text)
        seeds.append(EvidenceSeed(source=path.as_posix(), title=title, excerpt=_excerpt(text), topics=topics))
    if not seeds:
        raise ValueError("no seed files found")
    return seeds


def detect_topics(text: str) -> list[str]:
    lowered = text.lower()
    topics = []
    for topic, definition in TOPIC_DEFINITIONS.items():
        if any(keyword.lower() in lowered for keyword in definition["keywords"]):
            topics.append(topic)
    return topics or ["risk"]


def build_market_map(seeds: list[EvidenceSeed]) -> MarketMap:
    topic_counts: dict[str, int] = {}
    for seed in seeds:
        for topic in seed.topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
    entities = []
    for topic, count in sorted(topic_counts.items(), key=lambda item: (-item[1], item[0])):
        definition = TOPIC_DEFINITIONS.get(topic, TOPIC_DEFINITIONS["risk"])
        name, kind, label = definition["entity"]
        evidence = [seed.title for seed in seeds if topic in seed.topics][:3]
        entities.append(
            MarketEntity(
                name=name,
                kind=kind,
                beginner_label=label,
                why_it_matters=definition["why"],
                mentions=count,
                evidence=evidence,
            )
        )
    relationships = _relationships_for_topics(topic_counts)
    summary = _beginner_market_summary(entities)
    return MarketMap(entities=entities, relationships=relationships, beginner_summary=summary)


def build_evidence_catalog(seeds: list[EvidenceSeed], profile: BeginnerProfile | None = None, public_catalog: dict[str, Any] | None = None) -> EvidenceCatalog:
    topic_counts: dict[str, int] = {}
    for seed in seeds:
        for topic in seed.topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
    missing_context = []
    if not profile:
        missing_context.append("beginner_profile")
    if len(seeds) < 2:
        missing_context.append("multiple_evidence_sources")
    if "risk" not in topic_counts:
        missing_context.append("explicit_risk_evidence")
    source_coverage = []
    freshness_status = "sample_cache" if public_catalog else "local_seed"
    meaningfulness_status = "unknown"
    if public_catalog:
        source_coverage = public_catalog.get("source_status", [])
        meaningfulness_status = public_catalog.get("feasibility", {}).get("status", "unknown")
    coverage_status = "strong" if len(seeds) >= 2 and "risk" in topic_counts else "limited"
    return EvidenceCatalog(
        source_count=len(seeds),
        topic_counts=dict(sorted(topic_counts.items())),
        coverage_status=coverage_status,
        missing_context=missing_context,
        source_coverage=source_coverage,
        freshness_status=freshness_status,
        meaningfulness_status=meaningfulness_status,
        configured_interests=public_catalog.get("configured_interests", []) if public_catalog else [],
        research_plan=public_catalog.get("research_plan", {}) if public_catalog else {},
        topic_memory_snapshot=public_catalog.get("topic_memory_snapshot", {}) if public_catalog else {},
        collection_gaps=public_catalog.get("collection_gaps", []) if public_catalog else [],
    )


def run_market_simulation(
    *,
    seed_sources: Iterable[str | Path] | None = None,
    profile_path: str | Path | None = None,
    evidence_catalog_path: str | Path | None = None,
    run_id: str = "beginner-market-sim",
    generated_at: datetime | None = None,
) -> ScenarioReport:
    seeds = load_evidence_seeds(seed_sources)
    public_catalog = _load_public_catalog(evidence_catalog_path)
    seeds.extend(_public_catalog_to_seeds(public_catalog))
    profile = load_beginner_profile(profile_path)
    evidence_catalog = build_evidence_catalog(seeds, profile, public_catalog)
    market_map = build_market_map(seeds)
    topics = {topic for seed in seeds for topic in seed.topics}
    personas = _persona_views(topics, seeds, profile)
    scenarios = _scenario_paths(topics, market_map, profile)
    explanations = _beginner_explanations(topics, profile)
    action_candidates = _action_candidates(topics, market_map, profile)
    policy = classify_action("scenario_simulation")
    warnings = [
        "교육/리서치/시뮬레이션 목적의 로컬 산출물입니다. 계좌 접근, 주문 실행, 일임 운용을 하지 않습니다.",
    ]
    if profile:
        warnings.append("사용자 입력은 학습/위험/기간 맥락만 반영합니다. 개인화된 매수/매도 지시나 포트폴리오 운용은 아닙니다.")
    else:
        warnings.append("사용자 재무상황과 위험성향이 없으므로 generic next-action 후보만 제공합니다.")
    return ScenarioReport(
        schema_version=SCENARIO_SCHEMA_VERSION,
        run_id=run_id,
        generated_at=generated_at or datetime.now(timezone.utc),
        product_mode="beginner_market_understanding_simulation",
        seed_sources=seeds,
        evidence_catalog=evidence_catalog,
        profile_context=profile,
        output_boundary=_output_boundary(profile),
        market_map=market_map,
        persona_views=personas,
        scenarios=scenarios,
        beginner_explanations=explanations,
        action_candidates=action_candidates,
        policy=policy,
        warnings=warnings,
    )


def scenario_report_to_dict(report: ScenarioReport) -> dict[str, Any]:
    payload = asdict(report)
    payload["generated_at"] = report.generated_at.isoformat()
    return payload


def write_scenario_report(report: ScenarioReport, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(scenario_report_to_dict(report), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def build_verdict(report: ScenarioReport) -> dict[str, Any]:
    candidates = sorted(report.action_candidates, key=lambda item: item.confidence, reverse=True)
    primary = candidates[0] if candidates else None
    return {
        "schema_version": VERDICT_SCHEMA_VERSION,
        "run_id": report.run_id,
        "generated_at": report.generated_at.isoformat(),
        "primary_next_step": asdict(primary) if primary else None,
        "action_candidates": [asdict(candidate) for candidate in candidates],
        "profile_context": asdict(report.profile_context) if report.profile_context else None,
        "output_boundary": report.output_boundary,
        "evidence_catalog": asdict(report.evidence_catalog),
        "scenario_count": len(report.scenarios),
        "policy": asdict(report.policy),
        "operator_note": "초보자는 후보를 매수 지시로 받아들이지 말고 근거, 반대 시나리오, 본인 투자기간을 먼저 확인해야 합니다.",
    }


def write_verdict(report: ScenarioReport, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_verdict(report), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def validate_scenario_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "run_id",
        "generated_at",
        "product_mode",
        "seed_sources",
        "market_map",
        "persona_views",
        "scenarios",
        "beginner_explanations",
        "action_candidates",
        "evidence_catalog",
        "output_boundary",
        "policy",
        "warnings",
    }
    missing = sorted(required.difference(payload))
    if missing:
        errors.append(f"missing required scenario fields: {', '.join(missing)}")
    if payload.get("schema_version") != SCENARIO_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if not payload.get("seed_sources"):
        errors.append("seed_sources must not be empty")
    evidence_catalog = payload.get("evidence_catalog", {})
    for field in ["source_count", "topic_counts", "coverage_status", "missing_context"]:
        if field not in evidence_catalog:
            errors.append(f"evidence_catalog missing {field}")
    if payload.get("profile_context") is not None:
        profile = payload.get("profile_context", {})
        for field in ["profile_id", "experience_level", "learning_goal", "risk_comfort", "time_horizon", "decision_style"]:
            if field not in profile:
                errors.append(f"profile_context missing {field}")
    if payload.get("output_boundary") not in {"generic_research_only", "context_aware_research_only"}:
        errors.append(f"invalid output_boundary: {payload.get('output_boundary')}")
    market_map = payload.get("market_map", {})
    if not market_map.get("entities"):
        errors.append("market_map.entities must not be empty")
    if not market_map.get("beginner_summary"):
        errors.append("market_map.beginner_summary is required")
    for index, persona in enumerate(payload.get("persona_views", [])):
        confidence = persona.get("confidence")
        if not isinstance(confidence, int | float) or not 0 <= confidence <= 1:
            errors.append(f"persona_views[{index}].confidence must be between 0 and 1")
    if len(payload.get("scenarios", [])) < 3:
        errors.append("at least three scenario paths are required")
    for index, candidate in enumerate(payload.get("action_candidates", [])):
        if candidate.get("action_type") not in {"learn", "observe", "watchlist", "small_experiment_candidate", "defer", "avoid"}:
            errors.append(f"action_candidates[{index}] has invalid action_type {candidate.get('action_type')}")
        confidence = candidate.get("confidence")
        if not isinstance(confidence, int | float) or not 0 <= confidence <= 1:
            errors.append(f"action_candidates[{index}].confidence must be between 0 and 1")
    policy = payload.get("policy", {})
    if policy.get("kind") != "scenario_simulation":
        errors.append("policy.kind must be scenario_simulation")
    if not policy.get("allowed"):
        errors.append("scenario_simulation must be allowed by policy")
    return errors


def validate_scenario_file(path: str | Path) -> list[str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_scenario_payload(payload)


def validate_verdict_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != VERDICT_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if not payload.get("run_id"):
        errors.append("run_id is required")
    if not payload.get("primary_next_step"):
        errors.append("primary_next_step is required")
    if not payload.get("action_candidates"):
        errors.append("action_candidates must not be empty")
    policy = payload.get("policy", {})
    if policy.get("kind") != "scenario_simulation":
        errors.append("policy.kind must be scenario_simulation")
    if payload.get("output_boundary") not in {"generic_research_only", "context_aware_research_only"}:
        errors.append("output_boundary is required")
    return errors


def validate_verdict_file(path: str | Path) -> list[str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_verdict_payload(payload)


def _extract_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
        if stripped:
            return stripped[:80]
    return path.stem


def _excerpt(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact[:360]


def _load_public_catalog(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _public_catalog_to_seeds(catalog: dict[str, Any] | None) -> list[EvidenceSeed]:
    if not catalog:
        return []
    seeds = []
    for item in catalog.get("items", []):
        seeds.append(
            EvidenceSeed(
                source=f"public:{item.get('source_name', '')}:{item.get('item_id', '')}",
                title=item.get("title", ""),
                excerpt=_excerpt(item.get("text", "")),
                topics=item.get("topics", []) or ["risk"],
            )
        )
    return seeds


def _relationships_for_topics(topic_counts: dict[str, int]) -> list[MarketRelationship]:
    topics = set(topic_counts)
    relationships: list[MarketRelationship] = []
    if {"ai_infrastructure", "semiconductors"}.issubset(topics):
        relationships.append(
            MarketRelationship(
                source="AI 인프라",
                target="반도체",
                relation="수요 연결",
                beginner_explanation="AI 서비스가 늘수록 GPU와 메모리 같은 반도체 수요 기대가 커집니다.",
                evidence=["seed topics: ai_infrastructure + semiconductors"],
            )
        )
    if {"rates", "ai_infrastructure"}.issubset(topics) or {"rates", "semiconductors"}.issubset(topics):
        relationships.append(
            MarketRelationship(
                source="금리",
                target="성장 기대 업종",
                relation="평가 압력",
                beginner_explanation="금리가 높으면 미래 성장 기대가 큰 업종의 현재 가치가 눌릴 수 있습니다.",
                evidence=["seed topics: rates + growth themes"],
            )
        )
    if {"inflation", "rates"}.issubset(topics):
        relationships.append(
            MarketRelationship(
                source="물가",
                target="금리",
                relation="정책 연결",
                beginner_explanation="물가가 높으면 중앙은행이 금리 인하를 늦출 수 있어 시장 기대가 바뀝니다.",
                evidence=["seed topics: inflation + rates"],
            )
        )
    if "risk" in topics:
        relationships.append(
            MarketRelationship(
                source="리스크",
                target="관찰 후보",
                relation="진입 조건",
                beginner_explanation="좋은 이야기라도 가격이 이미 많이 올랐거나 근거가 약하면 관찰부터 해야 합니다.",
                evidence=["seed topics: risk"],
            )
        )
    return relationships


def _beginner_market_summary(entities: list[MarketEntity]) -> str:
    names = [entity.name for entity in entities[:3]]
    if not names:
        return "아직 시장 흐름을 만들 충분한 seed가 없습니다."
    return f"이번 seed에서 먼저 볼 흐름은 {', '.join(names)}입니다. 초보자는 가격보다 '왜 이 흐름이 생겼는지'와 '무엇이 바뀌면 틀리는지'를 먼저 확인해야 합니다."


def _persona_views(topics: set[str], seeds: list[EvidenceSeed], profile: BeginnerProfile | None = None) -> list[PersonaView]:
    evidence = [seed.title for seed in seeds][:3]
    tutor_summary = "종목부터 고르기보다 시장이 움직인 이유, 연결된 업종, 틀릴 조건을 먼저 이해해야 한다고 봅니다."
    if profile and profile.learning_goal == "vocabulary":
        tutor_summary = "용어 이해가 우선 목표이므로 각 후보를 행동보다 개념 학습 단위로 쪼개야 한다고 봅니다."
    if profile and profile.decision_style == "risk_first":
        tutor_summary = "리스크 먼저 보는 성향이므로 상방보다 보류 조건과 반대 시나리오를 먼저 읽어야 한다고 봅니다."
    views = [
        PersonaView(
            persona_id="beginner_tutor",
            name="초보자 튜터",
            role="용어와 인과관계 해설",
            stance="explain_first",
            summary=tutor_summary,
            confidence=0.82,
            evidence=evidence,
        ),
        PersonaView(
            persona_id="macro_strategist",
            name="매크로 전략가",
            role="금리/물가/유동성 관점",
            stance="rates_first" if "rates" in topics else "context_needed",
            summary="금리와 물가가 있으면 성장 테마의 평가가 흔들릴 수 있으므로 거시 변수 확인을 우선합니다.",
            confidence=0.74 if "rates" in topics else 0.58,
            evidence=evidence,
        ),
        PersonaView(
            persona_id="growth_investor",
            name="성장주 관찰자",
            role="AI/반도체/수요 확장 관점",
            stance="watch_growth" if topics.intersection({"ai_infrastructure", "semiconductors"}) else "wait_for_theme",
            summary="AI와 반도체가 함께 보이면 실적 기대가 이어지는지 관찰 후보로 둘 만하다고 봅니다.",
            confidence=0.78 if topics.intersection({"ai_infrastructure", "semiconductors"}) else 0.55,
            evidence=evidence,
        ),
        PersonaView(
            persona_id="risk_manager",
            name="리스크 관리자",
            role="과열/근거 부족/손실 가능성 점검",
            stance="guardrails",
            summary="초보자는 이야기의 매력보다 손실 조건, 과열 여부, 분산 여부를 먼저 확인해야 한다고 경고합니다.",
            confidence=0.86,
            evidence=evidence,
        ),
    ]
    return views


def _scenario_paths(topics: set[str], market_map: MarketMap, profile: BeginnerProfile | None = None) -> list[ScenarioPath]:
    primary_watch = [entity.name for entity in market_map.entities[:3]]
    risk_note = "좋은 뉴스가 이미 가격에 반영됐을 수 있습니다."
    if profile and profile.risk_comfort == "low":
        risk_note = "낮은 위험 선호에서는 관찰 기준과 보류 조건을 먼저 정해야 합니다."
    return [
        ScenarioPath(
            scenario_id="base",
            name="기준 경로",
            probability_label="중간",
            summary="시장은 주요 테마를 인정하지만 금리, 실적, 가격 부담을 함께 확인하며 천천히 재평가합니다.",
            triggers=["실적 발표가 기대에 부합", "금리 기대가 급격히 악화되지 않음", "거래량이 과열 없이 유지"],
            watch_items=primary_watch,
            beginner_explanation="가장 먼저 볼 경로입니다. 지금 당장 결론을 내리기보다 어떤 조건이 유지되는지 체크합니다.",
            risk_notes=[risk_note],
        ),
        ScenarioPath(
            scenario_id="bull",
            name="상방 경로",
            probability_label="가능하지만 확인 필요",
            summary="AI/반도체 같은 성장 테마의 실적 근거가 강화되고 금리 부담이 줄어 관심 후보가 넓어집니다.",
            triggers=["수요 증가 근거가 반복 확인", "금리 하락 또는 완화 기대", "섹터 내 후발 종목으로 관심 확산"],
            watch_items=primary_watch + ["동종업계 확산"],
            beginner_explanation="상방 경로는 '좋아 보인다'가 아니라 근거가 여러 번 확인될 때 힘을 얻습니다.",
            risk_notes=["추격 매수는 손실 폭을 키울 수 있어 분할/관찰 기준이 필요합니다."],
        ),
        ScenarioPath(
            scenario_id="bear",
            name="하방 경로",
            probability_label="항상 대비",
            summary="금리, 실적 실망, 과열 해소가 겹치면 좋은 테마도 조정받고 관찰 후보가 보류 후보로 바뀝니다.",
            triggers=["실적 가이던스 하향", "금리 상승", "뉴스는 좋은데 가격 반응이 약함"],
            watch_items=["손절/보류 조건", "현금 비중", "반대 근거"],
            beginner_explanation="하방 경로는 겁주기용이 아니라 틀렸을 때 무엇을 할지 미리 정하는 장치입니다.",
            risk_notes=["개인 상황 없이 평균적 시나리오만 제공합니다."],
        ),
    ]


def _beginner_explanations(topics: set[str], profile: BeginnerProfile | None = None) -> list[BeginnerExplanation]:
    explanations: list[BeginnerExplanation] = [
        BeginnerExplanation("관찰 후보", "지금 바로 사라는 뜻이 아니라 뉴스, 가격, 실적, 리스크를 계속 볼 가치가 있다는 뜻입니다."),
        BeginnerExplanation("반대 시나리오", "내 생각이 틀리는 경우를 미리 적어두는 것입니다. 초보자일수록 이 단계가 중요합니다."),
        BeginnerExplanation("컨텍스트 반영", "학습 목표, 위험 선호, 투자 기간 같은 입력은 설명의 우선순위를 조정할 뿐 매수/매도 지시가 되지 않습니다."),
    ]
    if profile and profile.risk_comfort == "low":
        explanations.append(BeginnerExplanation("보류 조건", "낮은 위험 선호에서는 언제 하지 않을지를 먼저 정해 손실 가능성을 줄이는 기준입니다."))
    seen = {item.term for item in explanations}
    for topic in sorted(topics):
        for term, explanation in TOPIC_DEFINITIONS.get(topic, {}).get("terms", []):
            if term not in seen:
                explanations.append(BeginnerExplanation(term, explanation))
                seen.add(term)
    return explanations


def _action_candidates(topics: set[str], market_map: MarketMap, profile: BeginnerProfile | None = None) -> list[ActionCandidate]:
    entities = [entity.name for entity in market_map.entities[:3]]
    learn_confidence = 0.94 if profile and profile.experience_level in {"new", "beginner"} else 0.9
    observe_confidence = 0.78 if profile and profile.risk_comfort == "low" else 0.84
    candidates = [
        ActionCandidate(
            action_type="learn",
            title="먼저 시장 흐름을 학습",
            rationale=f"{', '.join(entities) or '핵심 흐름'}가 왜 연결되는지 이해하는 것이 첫 단계입니다.",
            suitability=_profile_suitability(profile, "종목 선택 기준이 아직 없는 초보자에게 적합합니다."),
            confidence=learn_confidence,
            evidence=[market_map.beginner_summary],
            risk_notes=["학습 없이 후보를 매수 결론으로 해석하지 마세요."],
        ),
        ActionCandidate(
            action_type="observe",
            title="관찰 리스트 만들기",
            rationale="주요 흐름과 반대 시나리오를 같이 적어두면 다음 뉴스의 의미를 빠르게 판단할 수 있습니다.",
            suitability=_profile_suitability(profile, "시장을 따라가고 싶지만 바로 투자하기 부담스러운 사용자에게 적합합니다."),
            confidence=observe_confidence,
            evidence=entities,
            risk_notes=["관찰은 투자 실행이 아니며 수익을 보장하지 않습니다."],
        ),
    ]
    if topics.intersection({"ai_infrastructure", "semiconductors"}):
        candidates.append(
            ActionCandidate(
                action_type="watchlist",
                title="AI/반도체 흐름을 관심 테마로 등록",
                rationale="seed에서 AI 인프라와 반도체가 함께 나타나 수요 연결을 추적할 가치가 있습니다.",
                suitability=_profile_suitability(profile, "테마가 왜 움직이는지 배우며 후보군을 좁히고 싶은 사용자에게 적합합니다."),
                confidence=0.68 if profile and profile.risk_comfort == "low" else 0.78,
                evidence=["AI 인프라와 반도체 관계가 market_map에 포착됨"],
                risk_notes=["테마주는 과열될 수 있어 가격이 아니라 근거 변화를 먼저 봐야 합니다."],
            )
        )
    if "rates" in topics:
        candidates.append(
            ActionCandidate(
                action_type="defer",
                title="금리 민감 구간에서는 진입 판단 보류",
                rationale="금리 변화는 성장 테마의 평가를 흔들 수 있으므로 확인 전까지 보류가 합리적일 수 있습니다.",
                suitability="손실 회피 성향이 높거나 투자기간이 짧은 사용자에게 특히 중요합니다.",
                confidence=0.72,
                evidence=["금리 topic detected"],
                risk_notes=["보류도 기회비용이 있으므로 조건을 명확히 정해야 합니다."],
            )
        )
    return candidates


def _output_boundary(profile: BeginnerProfile | None) -> str:
    return "context_aware_research_only" if profile else "generic_research_only"


def _profile_suitability(profile: BeginnerProfile | None, fallback: str) -> str:
    if not profile:
        return fallback
    parts = [
        f"경험 수준={profile.experience_level}",
        f"목표={profile.learning_goal}",
        f"위험 선호={profile.risk_comfort}",
        f"기간={profile.time_horizon}",
    ]
    return " / ".join(parts) + " 맥락에서 교육/리서치 후보로만 적합합니다."
