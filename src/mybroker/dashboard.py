from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mybroker.reports import load_report, validate_report_payload
from mybroker.scenario import validate_scenario_payload


ROLLUP_SCHEMA_VERSION = "report_rollup.v1"


def discover_report_files(reports_dir: str | Path) -> list[Path]:
    root = Path(reports_dir)
    if not root.exists():
        return []
    reports = []
    for path in root.rglob("*.json"):
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if payload.get("schema_version") == "research_report.v1":
            reports.append(path)
    return sorted(reports)


def discover_scenario_files(reports_dir: str | Path) -> list[Path]:
    root = Path(reports_dir)
    search_roots = [root, root.parent / "scenarios"] if root.name == "runs" else [root]
    scenarios = []
    for search_root in search_roots:
        if not search_root.exists():
            continue
        for path in search_root.rglob("*.json"):
            if not path.is_file():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if payload.get("schema_version") == "scenario_report.v1":
                scenarios.append(path)
    return sorted(dict.fromkeys(scenarios))


def build_report_rollup(reports_dir: str | Path = "reports/runs") -> dict[str, Any]:
    report_rows = []
    totals = {
        "total_signals": 0,
        "positive_watch": 0,
        "negative_watch": 0,
        "neutral_watch": 0,
        "insufficient_data": 0,
    }
    for path in discover_report_files(reports_dir):
        payload = load_report(path)
        errors = validate_report_payload(payload)
        summary = payload.get("summary", {})
        for key in totals:
            totals[key] += int(summary.get(key, 0) or 0)
        report_rows.append({
            "path": path.as_posix(),
            "run_id": payload.get("run_id", ""),
            "task_id": payload.get("task_id", ""),
            "generated_at": payload.get("generated_at", ""),
            "source": payload.get("source", {}),
            "summary": summary,
            "warnings": payload.get("warnings", []),
            "data_quality": payload.get("data_quality", {}),
            "validation": {
                "valid": not errors,
                "errors": errors,
            },
        })
    scenario_rows = []
    for path in discover_scenario_files(reports_dir):
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = validate_scenario_payload(payload)
        scenario_rows.append({
            "path": path.as_posix(),
            "run_id": payload.get("run_id", ""),
            "generated_at": payload.get("generated_at", ""),
            "product_mode": payload.get("product_mode", ""),
            "seed_sources": payload.get("seed_sources", []),
            "evidence_catalog": payload.get("evidence_catalog", {}),
            "profile_context": payload.get("profile_context"),
            "output_boundary": payload.get("output_boundary", ""),
            "market_map": payload.get("market_map", {}),
            "persona_views": payload.get("persona_views", []),
            "scenarios": payload.get("scenarios", []),
            "beginner_explanations": payload.get("beginner_explanations", []),
            "action_candidates": payload.get("action_candidates", []),
            "warnings": payload.get("warnings", []),
            "validation": {
                "valid": not errors,
                "errors": errors,
            },
        })
    report_rows.sort(key=lambda row: row.get("generated_at", ""), reverse=True)
    scenario_rows.sort(key=lambda row: row.get("generated_at", ""), reverse=True)
    latest = report_rows[0] if report_rows else None
    previous = report_rows[1] if len(report_rows) > 1 else None
    latest_scenario = scenario_rows[0] if scenario_rows else None
    return {
        "schema_version": ROLLUP_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reports_dir": Path(reports_dir).as_posix(),
        "report_count": len(report_rows),
        "latest_report": latest,
        "previous_report": previous,
        "latest_vs_previous": compare_reports(latest, previous),
        "dataset_coverage": dataset_coverage(report_rows),
        "scenario_count": len(scenario_rows),
        "latest_scenario": latest_scenario,
        "scenarios": scenario_rows,
        "totals": totals,
        "reports": report_rows,
        "disclaimer": "교육/리서치/시뮬레이션 전용 로컬 화면입니다. 주문 실행, 계좌 접근, 일임 운용, 근거 없는 개인화 투자 조언을 하지 않습니다.",
    }


def compare_reports(latest: dict[str, Any] | None, previous: dict[str, Any] | None) -> dict[str, Any]:
    if not latest or not previous:
        return {"available": False, "reason": "Need at least two research reports."}
    latest_summary = latest.get("summary", {})
    previous_summary = previous.get("summary", {})
    latest_symbols = set(latest.get("source", {}).get("symbols", []))
    previous_symbols = set(previous.get("source", {}).get("symbols", []))
    return {
        "available": True,
        "previous_run_id": previous.get("run_id", ""),
        "delta_total_signals": int(latest_summary.get("total_signals", 0) or 0) - int(previous_summary.get("total_signals", 0) or 0),
        "delta_positive_watch": int(latest_summary.get("positive_watch", 0) or 0) - int(previous_summary.get("positive_watch", 0) or 0),
        "added_symbols": sorted(latest_symbols - previous_symbols),
        "removed_symbols": sorted(previous_symbols - latest_symbols),
    }


def dataset_coverage(reports: list[dict[str, Any]]) -> dict[str, Any]:
    symbols: set[str] = set()
    sources: set[str] = set()
    latest_quality = (reports[0].get("data_quality", {}) if reports else {})
    for report in reports:
        source = report.get("source", {})
        symbols.update(source.get("symbols", []))
        sources.update(source.get("sources", []) or [source.get("source", "")])
    return {
        "symbols": sorted(symbol for symbol in symbols if symbol),
        "sources": sorted(source for source in sources if source),
        "symbol_count": len(symbols),
        "source_count": len(sources),
        "latest_quality_status": latest_quality.get("status", "unknown"),
        "latest_quality_issue_count": latest_quality.get("issue_count", 0),
    }


def write_rollup(rollup: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(rollup, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def write_dashboard(rollup: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_dashboard_html(rollup), encoding="utf-8")
    return target


def esc(value: Any) -> str:
    return html.escape(str(value))


def metric(label: str, value: Any, detail: str = "") -> str:
    return f"<article class='metric'><span>{esc(label)}</span><strong>{esc(value)}</strong><small>{esc(detail)}</small></article>"


def chip(value: Any) -> str:
    return f"<span class='chip'>{esc(value)}</span>"


def render_dashboard_html(rollup: dict[str, Any]) -> str:
    latest = rollup.get("latest_report") or {}
    totals = rollup.get("totals", {})
    source = latest.get("source", {}) if latest else {}
    validation = latest.get("validation", {}) if latest else {}
    warnings = latest.get("warnings", []) if latest else []
    data_quality = latest.get("data_quality", {}) if latest else {}
    coverage = rollup.get("dataset_coverage", {})
    comparison = rollup.get("latest_vs_previous", {})
    latest_scenario = rollup.get("latest_scenario") or {}
    report_rows = []
    for report in rollup.get("reports", []):
        status = "valid" if report.get("validation", {}).get("valid") else "invalid"
        report_rows.append(
            "<tr>"
            f"<td><strong>{esc(report.get('run_id', ''))}</strong><span>{esc(report.get('path', ''))}</span></td>"
            f"<td>{esc(report.get('generated_at', ''))}</td>"
            f"<td>{esc(report.get('summary', {}).get('total_signals', 0))}</td>"
            f"<td>{esc(report.get('data_quality', {}).get('status', 'unknown'))}</td>"
            f"<td><span class='pill {status}'>{esc(status)}</span></td>"
            "</tr>"
        )
    if not report_rows:
        report_rows.append("<tr><td colspan='4'>No report artifacts found.</td></tr>")
    warning_items = "".join(f"<li>{esc(item)}</li>" for item in warnings) or "<li>No warnings.</li>"
    validation_errors = validation.get("errors", [])
    validation_items = "".join(f"<li>{esc(item)}</li>" for item in validation_errors) or "<li>Latest report validates cleanly.</li>"
    quality_items = "".join(
        f"<li>{esc(issue.get('level', ''))}: {esc(issue.get('code', ''))} - {esc(issue.get('message', ''))}</li>"
        for issue in data_quality.get("issues", [])
    ) or "<li>Latest dataset quality checks passed.</li>"
    comparison_text = (
        f"Compared with {esc(comparison.get('previous_run_id', ''))}: "
        f"total {esc(comparison.get('delta_total_signals', 0))}, "
        f"positive {esc(comparison.get('delta_positive_watch', 0))}, "
        f"added {esc(', '.join(comparison.get('added_symbols', [])) or 'none')}, "
        f"removed {esc(', '.join(comparison.get('removed_symbols', [])) or 'none')}"
        if comparison.get("available")
        else esc(comparison.get("reason", "No comparison available."))
    )
    scenario_section = render_scenario_section(latest_scenario)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker 시장 시뮬레이션 대시보드</title>
<style>
:root {{ --bg:#f4f1ea; --panel:#fffdf8; --ink:#19212b; --muted:#69717d; --line:#ded6c7; --ok:#0f7a4c; --bad:#a23a3a; --accent:#22577a; --warm:#d48c45; --soft:#e8f1ef; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:radial-gradient(circle at 20% 0%, #eef6f4 0, transparent 32%), var(--bg); color:var(--ink); font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ max-width:1220px; margin:0 auto; padding:28px; }}
header {{ display:grid; grid-template-columns:minmax(0,1fr) auto; gap:24px; align-items:end; margin-bottom:18px; }}
h1 {{ margin:0 0 8px; font-size:32px; line-height:1.12; letter-spacing:0; }}
h2 {{ margin:0 0 12px; font-size:18px; }}
h3 {{ margin:14px 0 7px; font-size:14px; }}
p {{ margin:0; color:var(--muted); }}
.eyebrow {{ color:var(--accent); font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0; }}
.panel {{ background:rgba(255,253,248,.94); border:1px solid var(--line); border-radius:8px; padding:18px; margin:14px 0; box-shadow:0 12px 28px rgba(31,39,47,.07); }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; padding:12px; background:#fffaf1; min-height:106px; }}
.metric span {{ display:block; color:var(--muted); font-size:12px; font-weight:700; }}
.metric strong {{ display:block; margin-top:6px; font-size:24px; line-height:1.15; overflow-wrap:anywhere; }}
.metric small {{ display:block; color:var(--muted); margin-top:6px; overflow:hidden; text-overflow:ellipsis; }}
.split {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.sim-grid {{ display:grid; grid-template-columns:1.05fr .95fr; gap:14px; }}
.map {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-top:12px; }}
.node {{ border:1px solid var(--line); border-radius:8px; padding:12px; background:#f7fbfa; min-height:142px; }}
.node strong {{ display:block; font-size:16px; margin-bottom:5px; }}
.node small {{ display:block; color:var(--accent); font-weight:800; margin-bottom:8px; }}
.scenario-lanes {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
.lane {{ border-left:4px solid var(--accent); background:#fffaf1; border-radius:8px; padding:12px; }}
.lane:nth-child(2) {{ border-left-color:var(--ok); }}
.lane:nth-child(3) {{ border-left-color:var(--bad); }}
.persona {{ border:1px solid var(--line); border-radius:8px; padding:10px; margin-top:8px; background:#ffffff; }}
.candidate {{ border:1px solid var(--line); border-radius:8px; padding:12px; background:#ffffff; margin-top:8px; }}
.source-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-top:12px; }}
.source-card {{ border:1px solid var(--line); border-radius:8px; padding:12px; background:#f8fbff; min-height:104px; }}
.source-card strong {{ display:block; font-size:15px; margin-bottom:5px; }}
.source-card small {{ display:block; color:var(--muted); overflow-wrap:anywhere; }}
.chiprow {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }}
.chip {{ display:inline-flex; align-items:center; min-height:26px; padding:3px 9px; border-radius:999px; background:#edf2f0; color:#26433d; font-size:12px; font-weight:700; }}
table {{ width:100%; border-collapse:collapse; }}
td,th {{ padding:10px 8px; border-top:1px solid var(--line); text-align:left; vertical-align:top; }}
th {{ color:var(--muted); font-size:11px; text-transform:uppercase; }}
td span {{ display:block; color:var(--muted); font-size:12px; margin-top:3px; }}
ul {{ margin:8px 0 0 18px; padding:0; color:var(--muted); }}
.pill {{ display:inline-flex; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:700; background:#eef2f7; }}
.pill.valid {{ color:var(--ok); background:#e7f5ee; }}
.pill.invalid {{ color:var(--bad); background:#fae8e8; }}
@media (max-width:900px) {{ header,.split,.sim-grid {{ display:block; }} .metrics,.map,.scenario-lanes,.source-grid {{ grid-template-columns:1fr; }} main {{ padding:16px; }} }}
</style>
</head>
<body>
<main>
<header>
<div>
<p class="eyebrow">초보자용 시장 이해 시뮬레이션 OS</p>
<h1>MyBroker 시장 이해 대시보드</h1>
<p>{esc(rollup.get('disclaimer', ''))}</p>
</div>
<p>Generated {esc(rollup.get('generated_at', ''))}</p>
</header>
<section class="panel">
<div class="metrics">
{metric('시나리오', rollup.get('scenario_count', 0), latest_scenario.get('run_id', 'no scenario'))}
{metric('리서치 리포트', rollup.get('report_count', 0), rollup.get('reports_dir', ''))}
{metric('신호 수', totals.get('total_signals', 0), 'research_report artifacts')}
{metric('검증 상태', '통과' if validation.get('valid') else '확인 필요', latest.get('run_id', 'no latest report'))}
</div>
</section>
{scenario_section}
<section class="split">
<article class="panel">
<h2>가격 데이터 리서치 최신 실행</h2>
<table><tbody>
<tr><th>Run</th><td>{esc(latest.get('run_id', 'No report'))}</td></tr>
<tr><th>Task</th><td>{esc(latest.get('task_id', ''))}</td></tr>
<tr><th>Generated</th><td>{esc(latest.get('generated_at', ''))}</td></tr>
<tr><th>Source</th><td>{esc(source.get('source', ''))}</td></tr>
<tr><th>Files</th><td>{esc(source.get('file_count', ''))}</td></tr>
<tr><th>Rows</th><td>{esc(source.get('row_count', ''))}</td></tr>
<tr><th>Range</th><td>{esc(source.get('start_date', ''))} to {esc(source.get('end_date', ''))}</td></tr>
<tr><th>Symbols</th><td>{esc(', '.join(source.get('symbols', [])))}</td></tr>
</tbody></table>
</article>
<article class="panel">
<h2>검증과 경고</h2>
<h3>Validation</h3>
<ul>{validation_items}</ul>
<h3>Data Quality</h3>
<ul>{quality_items}</ul>
<h3>Warnings</h3>
<ul>{warning_items}</ul>
</article>
</section>
<section class="panel">
<h2>리서치 실행 비교</h2>
<p>{comparison_text}</p>
</section>
<section class="panel">
<h2>Artifacts</h2>
<table><thead><tr><th>Run</th><th>Generated</th><th>Signals</th><th>Quality</th><th>Validation</th></tr></thead><tbody>{''.join(report_rows)}</tbody></table>
</section>
</main>
</body>
</html>
"""


def render_scenario_section(scenario: dict[str, Any]) -> str:
    if not scenario:
        return """
<section class="panel">
<h2>시장 시뮬레이션</h2>
<p>아직 scenario_report.v1 artifact가 없습니다. <code>mybroker scenario</code>를 실행하면 시장 지도와 시나리오가 여기에 표시됩니다.</p>
</section>
"""
    market_map = scenario.get("market_map", {})
    catalog = scenario.get("evidence_catalog", {})
    profile = scenario.get("profile_context") or {}
    boundary = scenario.get("output_boundary", "generic_research_only")
    boundary_label = {
        "generic_research_only": "일반 리서치 전용",
        "context_aware_research_only": "맥락 반영 리서치 전용",
    }.get(boundary, boundary)
    meaningfulness = catalog.get("meaningfulness_status", "unknown")
    meaningfulness_label = {
        "meaningful": "의미 있음",
        "weak": "약함",
        "blocked": "차단",
        "unknown": "미확인",
    }.get(meaningfulness, meaningfulness)
    freshness = catalog.get("freshness_status", "unknown")
    freshness_label = {
        "sample_cache": "샘플 캐시",
        "local_seed": "로컬 seed",
        "unknown": "미확인",
    }.get(freshness, freshness)
    entities = market_map.get("entities", [])
    entity_cards = "".join(
        "<article class='node'>"
        f"<small>{esc(entity.get('kind', ''))}</small>"
        f"<strong>{esc(entity.get('name', ''))}</strong>"
        f"<p>{esc(entity.get('why_it_matters', ''))}</p>"
        f"<div class='chiprow'>{''.join(chip(item) for item in entity.get('evidence', []))}</div>"
        "</article>"
        for entity in entities[:6]
    )
    scenario_lanes = "".join(
        "<article class='lane'>"
        f"<small>{esc(path.get('probability_label', ''))}</small>"
        f"<h3>{esc(path.get('name', ''))}</h3>"
        f"<p>{esc(path.get('beginner_explanation', path.get('summary', '')))}</p>"
        f"<div class='chiprow'>{''.join(chip(item) for item in path.get('watch_items', []))}</div>"
        "</article>"
        for path in scenario.get("scenarios", [])[:3]
    )
    personas = "".join(
        "<article class='persona'>"
        f"<strong>{esc(view.get('name', ''))}</strong>"
        f"<p>{esc(view.get('summary', ''))}</p>"
        f"<small>confidence {esc(view.get('confidence', ''))}</small>"
        "</article>"
        for view in scenario.get("persona_views", [])[:4]
    )
    candidates = "".join(
        "<article class='candidate'>"
        f"<span class='pill valid'>{esc(candidate.get('action_type', ''))}</span>"
        f"<h3>{esc(candidate.get('title', ''))}</h3>"
        f"<p>{esc(candidate.get('rationale', ''))}</p>"
        f"<small>{esc(candidate.get('suitability', ''))}</small>"
        "</article>"
        for candidate in scenario.get("action_candidates", [])[:4]
    )
    explanations = "".join(
        f"<li><strong>{esc(item.get('term', ''))}</strong>: {esc(item.get('explanation', ''))}</li>"
        for item in scenario.get("beginner_explanations", [])[:6]
    )
    topics = catalog.get("topic_counts", {})
    topic_chips = "".join(chip(f"{topic}: {count}") for topic, count in sorted(topics.items()))
    source_coverage = catalog.get("source_coverage", [])
    source_cards = "".join(
        "<article class='source-card'>"
        f"<strong>{esc(source.get('source_name', 'unknown source'))}</strong>"
        f"<small>adapter: {esc(source.get('adapter_id', ''))}</small>"
        f"<small>items: {esc(source.get('item_count', '0'))}</small>"
        f"<small>freshness: {esc(source.get('freshness_status', 'unknown'))}</small>"
        "</article>"
        for source in source_coverage[:6]
    )
    if not source_cards:
        source_cards = "<p>공개 자료 catalog가 연결되지 않았습니다.</p>"
    profile_summary = (
        f"{esc(profile.get('experience_level', ''))} / {esc(profile.get('learning_goal', ''))} / "
        f"{esc(profile.get('risk_comfort', ''))} / {esc(profile.get('time_horizon', ''))}"
        if profile
        else "프로필 없음: generic research-only 후보만 표시"
    )
    status = "valid" if scenario.get("validation", {}).get("valid") else "invalid"
    return f"""
<section class="panel">
<div class="metrics">
{metric('근거 수', catalog.get('source_count', 0), catalog.get('coverage_status', 'unknown'))}
{metric('시뮬레이션 판정', meaningfulness_label, '무료/공개 자료 기반 가능성')}
{metric('자료 신선도', freshness_label, '샘플 캐시는 재현 가능하지만 실시간은 아님')}
{metric('출력 경계', boundary_label, '맥락을 반영해도 리서치 전용')}
{metric('초보자 프로필', profile.get('profile_id', 'none'), profile_summary)}
</div>
<div class="chiprow">{topic_chips}</div>
</section>
<section class="panel">
<h2>공개 자료 커버리지</h2>
<p>각 시나리오에 영향을 준 무료/공개 source입니다. sample_cache는 재현 가능한 로컬 검증 단계이며, live refresh와 라이선스 검토는 별도 게이트입니다.</p>
<div class="source-grid">{source_cards}</div>
<h3>부족한 맥락</h3>
<div class="chiprow">{''.join(chip(item) for item in catalog.get('missing_context', [])) or chip('none')}</div>
</section>
<section class="panel">
<div class="sim-grid">
<div>
<p class="eyebrow">MiroFish 참고 초보자 보기</p>
<h2>시장 지도</h2>
<p>{esc(market_map.get('beginner_summary', ''))}</p>
<div class="map">{entity_cards}</div>
</div>
<aside>
<h2>다음 행동 후보</h2>
{candidates}
</aside>
</div>
</section>
<section class="panel">
<div class="split">
<article>
<h2>시나리오 분기</h2>
<div class="scenario-lanes">{scenario_lanes}</div>
</article>
<article>
<h2>에이전트 관점</h2>
{personas}
</article>
</div>
</section>
<section class="panel">
<h2>초보자 해설과 검증</h2>
<ul>{explanations}</ul>
<p><span class="pill {status}">{esc(status)}</span> {esc(scenario.get('path', ''))}</p>
</section>
"""
