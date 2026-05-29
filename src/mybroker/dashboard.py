from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mybroker.reports import load_report, validate_report_payload


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
    report_rows.sort(key=lambda row: row.get("generated_at", ""), reverse=True)
    latest = report_rows[0] if report_rows else None
    previous = report_rows[1] if len(report_rows) > 1 else None
    return {
        "schema_version": ROLLUP_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reports_dir": Path(reports_dir).as_posix(),
        "report_count": len(report_rows),
        "latest_report": latest,
        "previous_report": previous,
        "latest_vs_previous": compare_reports(latest, previous),
        "dataset_coverage": dataset_coverage(report_rows),
        "totals": totals,
        "reports": report_rows,
        "disclaimer": "Research-only local artifact view. Not trading execution or personalized investment advice.",
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


def render_dashboard_html(rollup: dict[str, Any]) -> str:
    latest = rollup.get("latest_report") or {}
    totals = rollup.get("totals", {})
    source = latest.get("source", {}) if latest else {}
    validation = latest.get("validation", {}) if latest else {}
    warnings = latest.get("warnings", []) if latest else []
    data_quality = latest.get("data_quality", {}) if latest else {}
    coverage = rollup.get("dataset_coverage", {})
    comparison = rollup.get("latest_vs_previous", {})
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
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Report Dashboard</title>
<style>
:root {{ --bg:#f6f7f9; --panel:#fff; --ink:#1e2530; --muted:#667085; --line:#dde3ea; --ok:#0f7a4c; --bad:#a23a3a; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ max-width:1180px; margin:0 auto; padding:28px; }}
header {{ display:flex; justify-content:space-between; gap:24px; align-items:end; margin-bottom:18px; }}
h1 {{ margin:0 0 8px; font-size:30px; line-height:1.1; }}
p {{ margin:0; color:var(--muted); }}
.panel {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:18px; margin:14px 0; box-shadow:0 12px 32px rgba(20,32,50,.06); }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; padding:12px; background:#fbfcfd; }}
.metric span {{ display:block; color:var(--muted); font-size:12px; font-weight:700; }}
.metric strong {{ display:block; margin-top:6px; font-size:24px; }}
.metric small {{ display:block; color:var(--muted); margin-top:6px; overflow:hidden; text-overflow:ellipsis; }}
.split {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
table {{ width:100%; border-collapse:collapse; }}
td,th {{ padding:10px 8px; border-top:1px solid var(--line); text-align:left; vertical-align:top; }}
th {{ color:var(--muted); font-size:11px; text-transform:uppercase; }}
td span {{ display:block; color:var(--muted); font-size:12px; margin-top:3px; }}
ul {{ margin:8px 0 0 18px; padding:0; color:var(--muted); }}
.pill {{ display:inline-flex; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:700; background:#eef2f7; }}
.pill.valid {{ color:var(--ok); background:#e7f5ee; }}
.pill.invalid {{ color:var(--bad); background:#fae8e8; }}
@media (max-width:780px) {{ header,.split {{ display:block; }} .metrics {{ grid-template-columns:1fr; }} main {{ padding:16px; }} }}
</style>
</head>
<body>
<main>
<header>
<div>
<h1>MyBroker Report Dashboard</h1>
<p>{esc(rollup.get('disclaimer', ''))}</p>
</div>
<p>Generated {esc(rollup.get('generated_at', ''))}</p>
</header>
<section class="panel">
<div class="metrics">
{metric('Reports', rollup.get('report_count', 0), rollup.get('reports_dir', ''))}
{metric('Total signals', totals.get('total_signals', 0), 'across artifacts')}
{metric('Dataset symbols', coverage.get('symbol_count', 0), ', '.join(coverage.get('symbols', [])))}
{metric('Latest valid', 'yes' if validation.get('valid') else 'no', latest.get('run_id', 'no latest report'))}
</div>
</section>
<section class="split">
<article class="panel">
<h2>Latest Run</h2>
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
<h2>Validation and Warnings</h2>
<h3>Validation</h3>
<ul>{validation_items}</ul>
<h3>Data Quality</h3>
<ul>{quality_items}</ul>
<h3>Warnings</h3>
<ul>{warning_items}</ul>
</article>
</section>
<section class="panel">
<h2>Run Comparison</h2>
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
