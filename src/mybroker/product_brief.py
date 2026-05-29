from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


DEFAULT_PRODUCT_BRIEF_OUTPUT = Path("reports/product/market-brief.html")


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value))


def chip(value: Any, tone: str = "neutral") -> str:
    return f"<span class='chip {tone}'>{esc(value)}</span>"


def render_product_brief(scenario: dict[str, Any], verdict: dict[str, Any]) -> str:
    market_map = scenario.get("market_map", {})
    catalog = scenario.get("evidence_catalog", {})
    profile = scenario.get("profile_context") or {}
    entities = market_map.get("entities", [])
    scenarios = scenario.get("scenarios", [])
    personas = scenario.get("persona_views", [])
    explanations = scenario.get("beginner_explanations", [])
    candidates = verdict.get("action_candidates") or scenario.get("action_candidates", [])
    primary = verdict.get("primary_next_step") or (candidates[0] if candidates else {})
    topic_counts = catalog.get("topic_counts", {})
    source_names = sorted({
        source.get("source_name", "")
        for source in catalog.get("source_coverage", [])
        if source.get("source_name")
    })
    product_confidence = _product_confidence(catalog)

    entity_cards = "".join(
        "<article class='node-card'>"
        f"<small>{esc(entity.get('beginner_label', entity.get('kind', '')))}</small>"
        f"<h3>{esc(entity.get('name', ''))}</h3>"
        f"<p>{esc(entity.get('why_it_matters', ''))}</p>"
        f"<div class='chiprow'>{''.join(chip(item) for item in entity.get('evidence', [])[:3])}</div>"
        "</article>"
        for entity in entities[:6]
    )
    scenario_cards = "".join(
        "<article class='path-card'>"
        f"<span>{esc(path.get('probability_label', ''))}</span>"
        f"<h3>{esc(path.get('name', ''))}</h3>"
        f"<p>{esc(path.get('beginner_explanation', path.get('summary', '')))}</p>"
        f"<div class='chiprow'>{''.join(chip(item, 'watch') for item in path.get('watch_items', [])[:4])}</div>"
        "</article>"
        for path in scenarios[:3]
    )
    persona_cards = "".join(
        "<article class='persona-card'>"
        f"<h3>{esc(view.get('name', ''))}</h3>"
        f"<small>{esc(view.get('role', ''))}</small>"
        f"<p>{esc(view.get('summary', ''))}</p>"
        "</article>"
        for view in personas[:4]
    )
    candidate_cards = "".join(
        "<article class='action-card'>"
        f"<span>{esc(_action_label(candidate.get('action_type', '')))}</span>"
        f"<h3>{esc(candidate.get('title', ''))}</h3>"
        f"<p>{esc(candidate.get('rationale', ''))}</p>"
        f"<small>{esc(candidate.get('suitability', ''))}</small>"
        "</article>"
        for candidate in candidates[:4]
    )
    explanation_rows = "".join(
        f"<li><strong>{esc(item.get('term', ''))}</strong><span>{esc(item.get('explanation', ''))}</span></li>"
        for item in explanations[:7]
    )
    source_text = ", ".join(source_names) if source_names else "로컬 seed"
    topic_chips = "".join(chip(f"{_topic_label(topic)} {count}", "topic") for topic, count in sorted(topic_counts.items(), key=lambda item: (-item[1], item[0]))[:6])
    questions = _inspection_questions(topic_counts, product_confidence)

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker 시장 브리프</title>
<style>
:root {{ --bg:#f6f7f2; --ink:#17202a; --muted:#647080; --line:#d9ded6; --panel:#fffdf7; --blue:#1f5f8b; --green:#1d6b52; --gold:#b7791f; --red:#9b3d3d; --soft:#edf5f1; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:linear-gradient(180deg,#edf5f1 0,#f6f7f2 260px); font:16px/1.58 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; letter-spacing:0; }}
main {{ max-width:1180px; margin:0 auto; padding:28px; }}
header {{ min-height:260px; display:grid; grid-template-columns:minmax(0,1fr) 330px; gap:28px; align-items:end; padding:30px 0 24px; }}
h1 {{ margin:0 0 12px; font-size:42px; line-height:1.08; letter-spacing:0; }}
h2 {{ margin:0 0 14px; font-size:22px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p {{ margin:0; color:var(--muted); }}
.eyebrow {{ display:block; margin-bottom:10px; color:var(--blue); font-size:12px; font-weight:800; }}
.hero-summary {{ max-width:760px; font-size:18px; color:#344052; }}
.brief-card,.panel,.node-card,.path-card,.persona-card,.action-card {{ border:1px solid var(--line); background:rgba(255,253,247,.94); border-radius:8px; box-shadow:0 10px 26px rgba(23,32,42,.06); }}
.brief-card {{ padding:18px; }}
.brief-card strong {{ display:block; font-size:26px; margin-top:6px; }}
.grid-4 {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin:16px 0; }}
.metric {{ padding:14px; border:1px solid var(--line); border-radius:8px; background:#fffaf0; min-height:104px; }}
.metric span {{ display:block; color:var(--muted); font-size:12px; font-weight:800; }}
.metric strong {{ display:block; margin-top:5px; font-size:24px; overflow-wrap:anywhere; }}
.panel {{ padding:20px; margin:14px 0; }}
.map-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }}
.node-card,.path-card,.persona-card,.action-card {{ padding:16px; box-shadow:none; }}
.node-card small,.path-card span,.action-card span {{ display:inline-flex; margin-bottom:10px; color:var(--blue); font-size:12px; font-weight:800; }}
.scenario-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }}
.path-card:nth-child(2) {{ border-color:#bad8c7; background:#f7fcf8; }}
.path-card:nth-child(3) {{ border-color:#e8c4c4; background:#fff8f8; }}
.split {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.persona-card,.action-card {{ margin-bottom:10px; }}
.chiprow {{ display:flex; flex-wrap:wrap; gap:7px; margin-top:12px; }}
.chip {{ display:inline-flex; align-items:center; min-height:28px; border-radius:999px; padding:3px 10px; background:#edf2ef; color:#244238; font-size:12px; font-weight:700; }}
.chip.topic {{ background:#eef4fb; color:#1f4f78; }}
.chip.watch {{ background:#f8eddc; color:#745018; }}
.questions {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; counter-reset:item; }}
.question {{ padding:14px; border:1px solid var(--line); border-radius:8px; background:#fff; }}
.question:before {{ counter-increment:item; content:counter(item); display:inline-grid; place-items:center; width:26px; height:26px; border-radius:999px; background:var(--blue); color:white; font-weight:800; margin-bottom:10px; }}
.terms li {{ display:grid; grid-template-columns:150px minmax(0,1fr); gap:12px; padding:10px 0; border-top:1px solid var(--line); }}
.terms strong {{ color:var(--ink); }}
.terms span {{ color:var(--muted); }}
.boundary {{ border-left:4px solid var(--green); background:#f6fbf8; }}
@media (max-width:900px) {{ main {{ padding:16px; }} header,.split {{ display:block; min-height:auto; }} h1 {{ font-size:32px; }} .grid-4,.map-grid,.scenario-grid,.questions {{ grid-template-columns:1fr; }} .terms li {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<section>
<span class="eyebrow">MyBroker market brief</span>
<h1>오늘의 시장 흐름을 먼저 이해하기</h1>
<p class="hero-summary">{esc(market_map.get('beginner_summary', '시장 흐름을 만들 근거가 아직 부족합니다.'))}</p>
<div class="chiprow">{topic_chips}</div>
</section>
<aside class="brief-card">
<span class="eyebrow">가장 먼저 할 일</span>
<strong>{esc(primary.get('title', '근거 확인부터 시작'))}</strong>
<p>{esc(primary.get('rationale', '시장 흐름과 반대 시나리오를 먼저 확인합니다.'))}</p>
</aside>
</header>
<section class="grid-4">
<article class="metric"><span>자료 기반</span><strong>{esc(product_confidence)}</strong><p>{esc(source_text)}</p></article>
<article class="metric"><span>초보자 맥락</span><strong>{esc(profile.get('experience_level', '일반'))}</strong><p>{esc(profile.get('learning_goal', '시장 이해'))}</p></article>
<article class="metric"><span>관찰 대상</span><strong>{esc(len(entities))}</strong><p>테마와 리스크 연결</p></article>
<article class="metric"><span>출력 경계</span><strong>리서치 전용</strong><p>주문 실행이나 일임 운용이 아닙니다.</p></article>
</section>
<section class="panel">
<h2>시장 관계 지도</h2>
<div class="map-grid">{entity_cards}</div>
</section>
<section class="panel">
<h2>세 가지 경로</h2>
<div class="scenario-grid">{scenario_cards}</div>
</section>
<section class="split">
<section class="panel">
<h2>관점별 해석</h2>
{persona_cards}
</section>
<section class="panel">
<h2>다음 행동 후보</h2>
{candidate_cards}
</section>
</section>
<section class="panel">
<h2>다음에 확인할 질문</h2>
<div class="questions">{''.join(f"<article class='question'><p>{esc(question)}</p></article>" for question in questions)}</div>
</section>
<section class="panel">
<h2>초보자 용어 해설</h2>
<ul class="terms">{explanation_rows}</ul>
</section>
<section class="panel boundary">
<h2>안전 경계</h2>
<p>이 화면은 교육, 리서치, 시뮬레이션용입니다. 계좌 연결, 주문 실행, 일임 운용, 근거 없는 개인화 추천을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def write_product_brief(scenario_path: str | Path, verdict_path: str | Path, output_path: str | Path = DEFAULT_PRODUCT_BRIEF_OUTPUT) -> Path:
    scenario = load_json(scenario_path)
    verdict = load_json(verdict_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_product_brief(scenario, verdict), encoding="utf-8")
    return target


def _product_confidence(catalog: dict[str, Any]) -> str:
    status = catalog.get("meaningfulness_status", "unknown")
    if status == "meaningful":
        return "초기 검증 가능"
    if status == "weak":
        return "근거 보강 필요"
    if status == "blocked":
        return "판단 보류"
    return "미확인"


def _topic_label(topic: str) -> str:
    return {
        "ai_infrastructure": "AI 인프라",
        "semiconductors": "반도체",
        "rates": "금리",
        "inflation": "물가",
        "consumer": "소비",
        "risk": "리스크",
    }.get(topic, topic)


def _action_label(action_type: str) -> str:
    return {
        "learn": "학습",
        "observe": "관찰",
        "watchlist": "관심 흐름",
        "defer": "보류",
        "avoid": "회피",
    }.get(action_type, action_type)


def _inspection_questions(topic_counts: dict[str, int], confidence: str) -> list[str]:
    questions = ["이 흐름을 뒷받침하는 근거가 뉴스, 가격, 공시 중 어디에서 반복되나요?"]
    if "rates" in topic_counts:
        questions.append("금리나 국채 수익률이 바뀌면 이 흐름은 어떻게 약해질까요?")
    if "ai_infrastructure" in topic_counts or "semiconductors" in topic_counts:
        questions.append("AI/반도체 기대가 실제 실적이나 수요 지표로 이어지고 있나요?")
    if "consumer" in topic_counts:
        questions.append("소비 둔화가 기업 매출 기대를 낮출 신호가 있나요?")
    questions.append("내 생각이 틀렸다고 판단할 반대 근거는 무엇인가요?")
    if confidence != "초기 검증 가능":
        questions.append("자료가 부족하다면 어떤 source를 먼저 보강해야 하나요?")
    return questions[:6]
