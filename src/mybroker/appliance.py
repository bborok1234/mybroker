from __future__ import annotations

import html
import json
import os
import shutil
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TODAY_SURFACE_SCHEMA_VERSION = "today_surface.v1"
NOTIFICATION_SCHEMA_VERSION = "notification_delivery.v1"
ARCHIVE_SCHEMA_VERSION = "daily_archive.v1"
RUNTIME_PLAYBOOK_SCHEMA_VERSION = "personal_analyst_runtime_playbook.v1"
PHONE_ACCESS_SCHEMA_VERSION = "phone_access_plan.v1"

DEFAULT_TODAY_OUTPUT = Path("reports/product/today.html")
DEFAULT_NOTIFICATION_OUTPUT = Path("reports/notifications/latest.json")
DEFAULT_ARCHIVE_ROOT = Path("reports/archive")
DEFAULT_RUNTIME_PLAYBOOK_OUTPUT = Path("reports/runtime/local-analyst-playbook.json")
DEFAULT_PHONE_ACCESS_OUTPUT = Path("reports/runtime/phone-access.json")
DEFAULT_LOCAL_OPS_DIR = Path("ops/local")


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(payload: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def esc(value: Any) -> str:
    return html.escape(str(value))


def write_runtime_playbook(output_path: str | Path = DEFAULT_RUNTIME_PLAYBOOK_OUTPUT) -> Path:
    payload = {
        "schema_version": RUNTIME_PLAYBOOK_SCHEMA_VERSION,
        "generated_at": _now(),
        "goal": "Run MyBroker as a local personal analyst appliance, not as a generic web app.",
        "absorbed_patterns": [
            {
                "source": "Hermes Agent",
                "pattern": "persistent memory, skill-like workflows, messaging gateway, scheduled loops",
                "mybroker_translation": "topic memory, CLI workflows, notification dry-runs, launchd schedule assets",
            },
            {
                "source": "OpenClaw",
                "pattern": "local workspace assistant with skills and tool routing",
                "mybroker_translation": "narrow finance-research appliance with explicit safety boundaries instead of broad file/account authority",
            },
            {
                "source": "MiroFish",
                "pattern": "graph-based simulation, personas, scenario paths, narrative maps",
                "mybroker_translation": "market map, persona views, optimistic/base/downside scenarios, beginner explanations",
            },
            {
                "source": "TradingAgents and FinRobot",
                "pattern": "role-specialized analyst debate and risk review",
                "mybroker_translation": "source scout, evidence curator, market mapper, scenario analyst, skeptic, tutor, memory librarian, publisher",
            },
            {
                "source": "Obsidian research vault workflows",
                "pattern": "local markdown/file memory that compounds over time",
                "mybroker_translation": "archive manifests, topic memory, source-linked artifacts, daily brief history",
            },
        ],
        "recommended_runtime": {
            "scheduler": "macOS launchd",
            "phone_access": "Tailscale Serve or private LAN URL before public deployment",
            "notification": "Pushover or Telegram via explicit environment secrets; dry-run by default",
            "storage": "local reports/ artifacts plus topic memory and daily archive",
        },
        "agent_roles": [
            "source_scout",
            "evidence_curator",
            "market_mapper",
            "scenario_analyst",
            "skeptic",
            "beginner_tutor",
            "memory_librarian",
            "publisher",
        ],
        "safety_boundaries": [
            "research_only",
            "no_brokerage_credentials",
            "no_live_trading",
            "no_discretionary_management",
            "no_unsupported_personalized_recommendations",
            "paid_or_credentialed_sources_require_explicit_approval",
        ],
    }
    return write_json(payload, output_path)


def write_phone_access_plan(
    *,
    output_path: str | Path = DEFAULT_PHONE_ACCESS_OUTPUT,
    port: int = 8787,
    tailnet_host: str = "mybroker-mac",
) -> Path:
    payload = {
        "schema_version": PHONE_ACCESS_SCHEMA_VERSION,
        "generated_at": _now(),
        "recommended_path": "tailscale_serve_private",
        "local_url": f"http://localhost:{port}/reports/product/today.html",
        "private_phone_url": f"https://{tailnet_host}/reports/product/today.html",
        "commands": [
            {
                "purpose": "serve local MyBroker artifacts",
                "command": f"cd <mybroker-repo> && python3 -m http.server {port}",
            },
            {
                "purpose": "share the local server only inside the tailnet",
                "command": f"tailscale serve --bg {port}",
            },
            {
                "purpose": "stop private serving",
                "command": "tailscale serve reset",
            },
        ],
        "do_not_default_to": [
            "public_tunnel",
            "funnel",
            "unauthenticated_public_hosting",
        ],
        "operator_checklist": [
            "MacBook remains powered and awake enough for scheduled jobs.",
            "Phone is on the same tailnet or private LAN.",
            "No secret values are committed to the repository.",
            "Notification sender is tested with dry-run before --send.",
        ],
    }
    return write_json(payload, output_path)


def write_today_surface(
    *,
    scenario_path: str | Path,
    verdict_path: str | Path,
    memory_path: str | Path,
    evidence_path: str | Path,
    brief_path: str | Path,
    output_path: str | Path = DEFAULT_TODAY_OUTPUT,
    archive_manifest_path: str | Path | None = None,
) -> Path:
    scenario = load_json(scenario_path)
    verdict = load_json(verdict_path)
    memory = load_json(memory_path)
    evidence = load_json(evidence_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_today_surface(
            scenario=scenario,
            verdict=verdict,
            memory=memory,
            evidence=evidence,
            brief_path=Path(brief_path),
            archive_manifest_path=Path(archive_manifest_path) if archive_manifest_path else None,
        ),
        encoding="utf-8",
    )
    return target


def render_today_surface(
    *,
    scenario: dict[str, Any],
    verdict: dict[str, Any],
    memory: dict[str, Any],
    evidence: dict[str, Any],
    brief_path: Path,
    archive_manifest_path: Path | None = None,
) -> str:
    market_map = scenario.get("market_map", {})
    primary = verdict.get("primary_next_step") or {}
    scenarios = scenario.get("scenarios", [])
    memory_topics = memory.get("topics", [])
    source_rows = evidence.get("source_status", [])
    gaps = evidence.get("collection_gaps", [])
    generated_at = scenario.get("generated_at", _now())
    theme_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(topic.get('name', ''))}</span>"
        f"<strong>{esc('새 변화' if topic.get('changed_since_previous') else '누적 관찰')}</strong>"
        f"<p>{esc(topic.get('latest_summary', ''))}</p>"
        "</article>"
        for topic in memory_topics[:5]
    ) or "<p>아직 누적 주제 기억이 없습니다.</p>"
    path_cards = "".join(
        "<article class='path'>"
        f"<span>{esc(path.get('probability_label', ''))}</span>"
        f"<h3>{esc(path.get('name', ''))}</h3>"
        f"<p>{esc(path.get('beginner_explanation', path.get('summary', '')))}</p>"
        "</article>"
        for path in scenarios[:3]
    )
    source_chips = "".join(
        f"<span class='chip'>{esc(row.get('source_name', 'source'))} · {esc(row.get('freshness_status', 'unknown'))}</span>"
        for row in source_rows[:8]
    ) or "<span class='chip'>로컬 seed</span>"
    gap_items = "".join(f"<li>{esc(_gap_label(gap))}</li>" for gap in gaps[:6]) or "<li>오늘 기록된 차단 이슈는 없습니다.</li>"
    archive_link = (
        f"<a href='{esc(_relative_href(archive_manifest_path))}'>아카이브 manifest</a>"
        if archive_manifest_path
        else "<span>아카이브 manifest 없음</span>"
    )
    questions = _daily_questions(memory_topics, evidence)
    question_cards = "".join(f"<article class='question'><p>{esc(question)}</p></article>" for question in questions)

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Today</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
main {{ max-width:760px; margin:0 auto; padding:16px; }}
header {{ padding:26px 0 16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p {{ margin:0; color:var(--muted); }}
.hero {{ border:1px solid var(--line); border-radius:8px; background:linear-gradient(180deg,#fffefa,#f1f7f3); padding:18px; }}
.primary {{ display:block; margin-top:14px; font-size:24px; color:var(--ink); }}
.section {{ margin:14px 0; padding:16px; border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.stack {{ display:grid; gap:10px; }}
.card,.path,.question {{ border:1px solid var(--line); border-radius:8px; background:white; padding:14px; }}
.card span,.path span {{ display:block; margin-bottom:7px; color:var(--blue); font-size:12px; font-weight:900; }}
.card strong {{ display:block; margin-bottom:6px; }}
.chips {{ display:flex; flex-wrap:wrap; gap:7px; }}
.chip {{ display:inline-flex; min-height:28px; align-items:center; border-radius:999px; padding:3px 10px; background:#eef4fb; color:#1f4f78; font-size:12px; font-weight:800; }}
.links {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
.links a,.links span {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
ul {{ margin:0; padding-left:18px; color:var(--muted); }}
.boundary {{ border-left:4px solid var(--green); }}
@media (max-width:520px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Today · {esc(_short_date(generated_at))}</span>
<h1>오늘 시장을 이해하기 위한 5분 브리프</h1>
</header>
<section class="hero">
<span class="eyebrow">가장 먼저 볼 것</span>
<strong class="primary">{esc(primary.get('title', '근거 확인부터 시작'))}</strong>
<p>{esc(primary.get('rationale', market_map.get('beginner_summary', '오늘 브리프를 만들 근거를 점검합니다.')))}</p>
</section>
<section class="section">
<h2>오늘의 주제 기억</h2>
<div class="stack">{theme_cards}</div>
</section>
<section class="section">
<h2>가능한 세 가지 경로</h2>
<div class="stack">{path_cards}</div>
</section>
<section class="section">
<h2>자료 상태</h2>
<div class="chips">{source_chips}</div>
</section>
<section class="section">
<h2>아직 약한 부분</h2>
<ul>{gap_items}</ul>
</section>
<section class="section">
<h2>오늘 공부할 질문</h2>
<div class="stack">{question_cards}</div>
</section>
<section class="section">
<h2>연결된 산출물</h2>
<div class="links">
<a href="{esc(_relative_href(brief_path))}">상세 시장 브리프</a>
{archive_link}
</div>
</section>
<section class="section boundary">
<h2>안전 경계</h2>
<p>이 화면은 교육과 리서치, 시뮬레이션용입니다. 계좌 연결, 주문 실행, 일임 운용, 근거 없는 개인화 추천을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def archive_daily_run(
    *,
    run_id: str,
    scenario_path: str | Path,
    verdict_path: str | Path,
    evidence_path: str | Path,
    memory_path: str | Path,
    brief_path: str | Path,
    today_path: str | Path,
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
) -> Path:
    timestamp = datetime.now(timezone.utc)
    archive_dir = Path(archive_root) / timestamp.strftime("%Y-%m-%d")
    archive_dir.mkdir(parents=True, exist_ok=True)
    copied: dict[str, str] = {}
    for label, source in {
        "scenario": scenario_path,
        "verdict": verdict_path,
        "evidence": evidence_path,
        "memory": memory_path,
        "brief": brief_path,
        "today": today_path,
    }.items():
        source_path = Path(source)
        if source_path.exists():
            target = archive_dir / source_path.name
            shutil.copy2(source_path, target)
            copied[label] = target.as_posix()
    manifest = {
        "schema_version": ARCHIVE_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at": timestamp.isoformat(),
        "archive_dir": archive_dir.as_posix(),
        "artifacts": copied,
        "policy": "research_only",
    }
    return write_json(manifest, archive_dir / "manifest.json")


def write_notification_payload(
    *,
    provider: str,
    today_url: str,
    today_path: str | Path,
    scenario_path: str | Path,
    verdict_path: str | Path,
    output_path: str | Path = DEFAULT_NOTIFICATION_OUTPUT,
    dry_run: bool = True,
) -> Path:
    scenario = load_json(scenario_path)
    verdict = load_json(verdict_path)
    primary = verdict.get("primary_next_step") or {}
    payload = {
        "schema_version": NOTIFICATION_SCHEMA_VERSION,
        "generated_at": _now(),
        "provider": provider,
        "dry_run": dry_run,
        "title": "MyBroker 오늘의 시장 브리프",
        "message": primary.get("title", "오늘 브리프가 준비되었습니다."),
        "url": today_url,
        "local_path": Path(today_path).as_posix(),
        "required_env": _provider_env(provider),
        "run_id": scenario.get("run_id", ""),
        "policy": "research_only",
        "delivery_status": "dry_run_ready" if dry_run else "prepared_requires_sender",
    }
    return write_json(payload, output_path)


def send_notification_payload(path: str | Path) -> dict[str, Any]:
    payload = load_json(path)
    provider = payload.get("provider", "")
    if provider == "telegram":
        result = _send_telegram(payload)
    elif provider == "pushover":
        result = _send_pushover(payload)
    else:
        raise ValueError(f"unsupported notification provider: {provider}")
    payload["dry_run"] = False
    payload["delivery_status"] = "sent" if result.get("ok") else "send_failed"
    payload["sent_at"] = _now()
    payload["send_result"] = result
    write_json(payload, path)
    return payload


def write_launchd_assets(
    *,
    project_root: str | Path,
    output_dir: str | Path = DEFAULT_LOCAL_OPS_DIR,
    hour: int = 7,
    minute: int = 30,
    python_bin: str = "python3",
) -> dict[str, str]:
    root = Path(project_root).resolve()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    script_path = out / "run-daily-analyst.sh"
    plist_path = out / "com.mybroker.daily-analyst.plist"
    log_dir = root / "reports" / "runtime"
    script = f"""#!/bin/sh
set -eu
cd "{root.as_posix()}"
mkdir -p reports/runtime
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src {python_bin} -m mybroker appliance run \\
  --topics config/topics.json \\
  --profile examples/profiles/beginner-conservative.json \\
  ${{MYBROKER_EVIDENCE_SOURCES:-}} \\
  --today-url "${{MYBROKER_TODAY_URL:-http://localhost:8787/reports/product/today.html}}" \\
  --notification-provider "${{MYBROKER_NOTIFICATION_PROVIDER:-telegram}}" \\
  --dry-run
"""
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.mybroker.daily-analyst</string>
  <key>ProgramArguments</key>
  <array>
    <string>{script_path.resolve().as_posix()}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>{root.as_posix()}</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>{hour}</integer>
    <key>Minute</key>
    <integer>{minute}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>{(log_dir / "daily-analyst.out.log").as_posix()}</string>
  <key>StandardErrorPath</key>
  <string>{(log_dir / "daily-analyst.err.log").as_posix()}</string>
</dict>
</plist>
"""
    script_path.write_text(script, encoding="utf-8")
    script_path.chmod(0o755)
    plist_path.write_text(plist, encoding="utf-8")
    return {"script": script_path.as_posix(), "plist": plist_path.as_posix()}


def _provider_env(provider: str) -> list[str]:
    if provider == "pushover":
        return ["PUSHOVER_USER_KEY", "PUSHOVER_APP_TOKEN"]
    if provider == "telegram":
        return ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    return []


def _send_telegram(payload: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": f"{payload.get('title')}\n{payload.get('message')}\n{payload.get('url')}",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    return _post_form(url, data)


def _send_pushover(payload: dict[str, Any]) -> dict[str, Any]:
    user_key = os.environ.get("PUSHOVER_USER_KEY")
    app_token = os.environ.get("PUSHOVER_APP_TOKEN")
    if not user_key or not app_token:
        raise RuntimeError("PUSHOVER_USER_KEY and PUSHOVER_APP_TOKEN are required")
    data = urllib.parse.urlencode({
        "token": app_token,
        "user": user_key,
        "title": payload.get("title", "MyBroker"),
        "message": payload.get("message", ""),
        "url": payload.get("url", ""),
    }).encode("utf-8")
    return _post_form("https://api.pushover.net/1/messages.json", data)


def _post_form(url: str, data: bytes) -> dict[str, Any]:
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(request, timeout=15) as response:
        body = response.read().decode("utf-8")
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        parsed = {"body": body}
    parsed.setdefault("ok", 200 <= getattr(response, "status", 200) < 300)
    return parsed


def _daily_questions(memory_topics: list[dict[str, Any]], evidence: dict[str, Any]) -> list[str]:
    questions = []
    for topic in memory_topics[:3]:
        daily = topic.get("daily_questions", [])
        if daily:
            questions.append(daily[0])
    if evidence.get("collection_gaps"):
        questions.append("오늘 부족한 근거가 결론의 강도를 얼마나 낮추나요?")
    questions.append("이 브리프가 틀렸다고 판단할 가장 빠른 반대 신호는 무엇인가요?")
    return questions[:5]


def _gap_label(value: str) -> str:
    labels = {
        "live_refresh_not_enabled": "실시간 새로고침은 아직 연결되지 않았습니다.",
        "source_license_review_pending": "소스 이용조건 검토가 남아 있습니다.",
        "less_than_three_source_families": "자료군이 3종 미만이라 근거 다양성이 약합니다.",
        "topic_filter_too_thin_used_full_sample_cache": "주제별 필터 결과가 얇아 전체 샘플 캐시를 보강 사용했습니다.",
    }
    return labels.get(value, value)


def _relative_href(path: Path | None) -> str:
    if not path:
        return ""
    return path.as_posix()


def _short_date(value: str) -> str:
    return value[:10] if value else datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
