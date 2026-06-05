from __future__ import annotations

import html
import json
import os
import shutil
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mybroker.topics import (
    DEFAULT_DAILY_EVIDENCE_OUTPUT,
    DEFAULT_DAILY_SCOUT_OUTPUT,
    DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    DEFAULT_TOPIC_MEMORY_OUTPUT,
)
from mybroker.vault import DEFAULT_VAULT_COMPILE_OUTPUT, DEFAULT_VAULT_SURFACE_OUTPUT


TODAY_SURFACE_SCHEMA_VERSION = "today_surface.v1"
DAILY_BRIEF_AGENDA_SCHEMA_VERSION = "daily_brief_agenda.v1"
DAILY_READINESS_SCHEMA_VERSION = "daily_readiness.v1"
SOURCE_REFRESH_BRIEF_SCHEMA_VERSION = "source_refresh_brief.v1"
NOTIFICATION_SCHEMA_VERSION = "notification_delivery.v1"
ARCHIVE_SCHEMA_VERSION = "daily_archive.v1"
RUNTIME_PLAYBOOK_SCHEMA_VERSION = "personal_analyst_runtime_playbook.v1"
PHONE_ACCESS_SCHEMA_VERSION = "phone_access_plan.v1"
OPERATOR_DECISION_PACKET_SCHEMA_VERSION = "operator_decision_packet.v1"
OPERATOR_DECISION_APPLY_SCHEMA_VERSION = "operator_decision_apply.v1"
MEMORY_INDEX_SCHEMA_VERSION = "personal_memory_index.v1"
MEMORY_QUERY_SCHEMA_VERSION = "personal_memory_query.v1"
ANALYST_JOURNAL_SCHEMA_VERSION = "personal_analyst_journal.v1"
ANALYST_TASK_QUEUE_SCHEMA_VERSION = "personal_analyst_task_queue.v1"
ANALYST_TASK_LEDGER_SCHEMA_VERSION = "personal_analyst_task_ledger.v1"
ANALYST_TASK_STATUS_APPLY_SCHEMA_VERSION = "personal_analyst_task_status_apply.v1"
MORNING_CONTROL_SCHEMA_VERSION = "morning_control_packet.v1"
RUNTIME_DOCTOR_SCHEMA_VERSION = "local_runtime_doctor.v1"
SCHEDULER_STATUS_SCHEMA_VERSION = "local_scheduler_status.v1"
SCHEDULER_APPLY_SCHEMA_VERSION = "local_scheduler_apply.v1"
SCHEDULER_RUN_ONCE_SCHEMA_VERSION = "local_scheduler_run_once.v1"
SCHEDULER_ACTIVATION_PREFLIGHT_SCHEMA_VERSION = "local_scheduler_activation_preflight.v1"
SCHEDULER_ACTIVATION_VERIFY_SCHEMA_VERSION = "local_scheduler_activation_verify.v1"
SCHEDULER_OPERATIONS_SCHEMA_VERSION = "local_scheduler_operations.v1"
LAUNCHD_LABEL = "com.mybroker.daily-analyst"

DEFAULT_TODAY_OUTPUT = Path("reports/product/today.html")
DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT = Path("reports/daily/brief-agenda.json")
DEFAULT_DAILY_BRIEF_AGENDA_SURFACE = Path("reports/product/daily-agenda.html")
DEFAULT_DAILY_READINESS_OUTPUT = Path("reports/runtime/daily-readiness.json")
DEFAULT_DAILY_READINESS_SURFACE = Path("reports/product/readiness.html")
DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT = Path("reports/runtime/source-refresh-brief.json")
DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE = Path("reports/product/source-refresh.html")
DEFAULT_NOTIFICATION_OUTPUT = Path("reports/notifications/latest.json")
DEFAULT_ARCHIVE_ROOT = Path("reports/archive")
DEFAULT_RUNTIME_PLAYBOOK_OUTPUT = Path("reports/runtime/local-analyst-playbook.json")
DEFAULT_PHONE_ACCESS_OUTPUT = Path("reports/runtime/phone-access.json")
DEFAULT_OPERATOR_DECISION_PACKET_OUTPUT = Path("reports/runtime/operator-decision-packet.json")
DEFAULT_OPERATOR_DECISION_APPLY_OUTPUT = Path("reports/runtime/operator-decision-apply.json")
DEFAULT_MEMORY_INDEX_OUTPUT = Path("reports/memory/index.json")
DEFAULT_MEMORY_OUTPUT = Path("reports/product/memory.html")
DEFAULT_MEMORY_QUERY_OUTPUT = Path("reports/memory/latest-query.json")
DEFAULT_MEMORY_QUERY_SURFACE = Path("reports/product/memory-query.html")
DEFAULT_ANALYST_JOURNAL_OUTPUT = Path("reports/product/journal.html")
DEFAULT_ANALYST_JOURNAL_ARTIFACT = Path("reports/memory/analyst-journal.json")
DEFAULT_ANALYST_TASK_QUEUE_OUTPUT = Path("reports/product/tasks.html")
DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT = Path("reports/memory/analyst-task-queue.json")
DEFAULT_ANALYST_TASK_LEDGER_OUTPUT = Path("reports/product/task-ledger.html")
DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT = Path("reports/memory/analyst-task-ledger.json")
DEFAULT_ANALYST_TASK_RESPONSES = Path("reports/memory/analyst-task-responses.jsonl")
DEFAULT_ANALYST_TASK_STATUS_APPLY = Path("reports/memory/analyst-task-status-apply.json")
DEFAULT_MORNING_CONTROL_OUTPUT = Path("reports/runtime/morning-control.json")
DEFAULT_MORNING_CONTROL_SURFACE = Path("reports/product/morning.html")
DEFAULT_RUNTIME_DOCTOR_OUTPUT = Path("reports/runtime/local-runtime-doctor.json")
DEFAULT_RUNTIME_DOCTOR_ACTIVATION_OUTPUT = Path("reports/runtime/local-runtime-doctor-activation.json")
DEFAULT_SCHEDULER_STATUS_OUTPUT = Path("reports/runtime/scheduler-status.json")
DEFAULT_SCHEDULER_APPLY_OUTPUT = Path("reports/runtime/scheduler-apply.json")
DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT = Path("reports/runtime/scheduler-run-once.json")
DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT = Path("reports/runtime/scheduler-activation-preflight.json")
DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT = Path("reports/runtime/scheduler-activation-verify.json")
DEFAULT_SCHEDULER_OPERATIONS_OUTPUT = Path("reports/runtime/scheduler-operations.json")
DEFAULT_SCHEDULER_OPERATIONS_SURFACE = Path("reports/product/scheduler.html")
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


def write_runtime_doctor(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_RUNTIME_DOCTOR_OUTPUT,
    freshness_hours: int = 36,
    require_launchd_loaded: bool = False,
) -> Path:
    root = Path(project_root).resolve()
    ops_dir = root / DEFAULT_LOCAL_OPS_DIR
    script_path = ops_dir / "run-daily-analyst.sh"
    plist_path = ops_dir / "com.mybroker.daily-analyst.plist"
    checks = [
        _doctor_check_path("project_root", root, "fail", "MyBroker project root exists."),
        _doctor_check_path("topics_config", root / "config" / "topics.json", "fail", "Daily interests are configured."),
        _doctor_check_path("runner_script", script_path, "fail", "Daily runner script exists.", executable=True),
        _doctor_check_path("launchd_plist", plist_path, "fail", "LaunchAgent plist exists."),
        _doctor_check_path("phone_access_plan", root / DEFAULT_PHONE_ACCESS_OUTPUT, "warn", "Private phone access guidance exists."),
        _doctor_check_path("today_surface", root / DEFAULT_TODAY_OUTPUT, "warn", "Phone-readable today surface exists.", freshness_hours=freshness_hours),
        _doctor_check_path("memory_surface", root / DEFAULT_MEMORY_OUTPUT, "warn", "Accumulated memory surface exists.", freshness_hours=freshness_hours),
        _doctor_check_path("memory_query_surface", root / DEFAULT_MEMORY_QUERY_SURFACE, "warn", "Memory recall surface exists.", freshness_hours=freshness_hours),
        _doctor_check_path("archive_manifest", _latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT), "warn", "Latest daily archive manifest exists.", freshness_hours=freshness_hours),
        _doctor_check_notification(root / DEFAULT_NOTIFICATION_OUTPUT),
        _doctor_check_launchd(plist_path, require_launchd_loaded=require_launchd_loaded),
    ]
    fail_count = sum(1 for check in checks if check["status"] == "fail")
    warn_count = sum(1 for check in checks if check["status"] == "warn")
    payload = {
        "schema_version": RUNTIME_DOCTOR_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "status": "ready" if fail_count == 0 else "blocked",
        "fail_count": fail_count,
        "warn_count": warn_count,
        "checks": checks,
        "next_actions": _doctor_next_actions(checks),
        "install_boundary": {
            "launchd_install_is_host_level": True,
            "default_behavior": "diagnose_only",
            "manual_install_commands": [
                f"mkdir -p ~/Library/LaunchAgents",
                f"cp {plist_path.as_posix()} ~/Library/LaunchAgents/com.mybroker.daily-analyst.plist",
                "launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.mybroker.daily-analyst.plist",
                "launchctl kickstart -k gui/$(id -u)/com.mybroker.daily-analyst",
            ],
            "manual_uninstall_commands": [
                "launchctl bootout gui/$(id -u)/com.mybroker.daily-analyst",
                "rm ~/Library/LaunchAgents/com.mybroker.daily-analyst.plist",
            ],
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_status(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_STATUS_OUTPUT,
) -> Path:
    root = Path(project_root).resolve()
    source_plist = root / DEFAULT_LOCAL_OPS_DIR / f"{LAUNCHD_LABEL}.plist"
    source_script = root / DEFAULT_LOCAL_OPS_DIR / "run-daily-analyst.sh"
    installed_plist = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"
    launchd = _launchd_state()
    log_paths = {
        "stdout": (root / "reports" / "runtime" / "daily-analyst.out.log").as_posix(),
        "stderr": (root / "reports" / "runtime" / "daily-analyst.err.log").as_posix(),
    }
    payload = {
        "schema_version": SCHEDULER_STATUS_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "host_write_performed": False,
        "status": _scheduler_status(source_plist=source_plist, source_script=source_script, installed_plist=installed_plist, loaded=launchd["loaded"]),
        "source_assets": {
            "script": source_script.as_posix(),
            "script_exists": source_script.exists(),
            "script_executable": source_script.exists() and os.access(source_script, os.X_OK),
            "plist": source_plist.as_posix(),
            "plist_exists": source_plist.exists(),
        },
        "installed_plist": {
            "path": installed_plist.as_posix(),
            "exists": installed_plist.exists(),
        },
        "launchd": launchd,
        "logs": {
            "paths": log_paths,
            "stdout_exists": Path(log_paths["stdout"]).exists(),
            "stderr_exists": Path(log_paths["stderr"]).exists(),
        },
        "commands": _scheduler_commands(source_plist=source_plist, installed_plist=installed_plist),
        "next_actions": _scheduler_next_actions(
            source_plist=source_plist,
            source_script=source_script,
            installed_plist=installed_plist,
            loaded=launchd["loaded"],
        ),
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_apply(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_APPLY_OUTPUT,
    install: bool = False,
    load: bool = False,
    start_now: bool = False,
    unload: bool = False,
    uninstall: bool = False,
    confirm_host_write: bool = False,
) -> Path:
    root = Path(project_root).resolve()
    source_plist = root / DEFAULT_LOCAL_OPS_DIR / f"{LAUNCHD_LABEL}.plist"
    installed_plist = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"
    actions = _scheduler_apply_actions(
        source_plist=source_plist,
        installed_plist=installed_plist,
        install=install,
        load=load,
        start_now=start_now,
        unload=unload,
        uninstall=uninstall,
    )
    dry_run = not confirm_host_write
    results = []
    for action in actions:
        if dry_run:
            result = dict(action)
            result["status"] = "planned"
            result["executed"] = False
        else:
            result = _execute_scheduler_action(action)
        results.append(result)
    post_status_path = write_scheduler_status(project_root=root, output_path=root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    payload = {
        "schema_version": SCHEDULER_APPLY_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "dry_run": dry_run,
        "host_write_performed": bool(confirm_host_write and actions),
        "requested": {
            "install": install,
            "load": load,
            "start_now": start_now,
            "unload": unload,
            "uninstall": uninstall,
        },
        "actions": results,
        "post_status_path": post_status_path.as_posix(),
        "post_status": load_json(post_status_path),
        "safety": {
            "requires_confirm_host_write": True,
            "default_behavior": "dry_run",
            "notes": [
                "Dry-run records planned host-level commands without changing launchd state.",
                "Actual install/load/start/unload/uninstall requires --confirm-host-write.",
            ],
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_run_once(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT,
    timeout_seconds: int = 240,
) -> Path:
    root = Path(project_root).resolve()
    script_path = root / DEFAULT_LOCAL_OPS_DIR / "run-daily-analyst.sh"
    command = [script_path.as_posix()]
    started_at = datetime.now(timezone.utc)
    status = "failed"
    returncode: int | None = None
    stdout_excerpt = ""
    stderr_excerpt = ""
    error = ""

    if not script_path.exists():
        error = f"Runner script is missing: {script_path.as_posix()}"
    elif not os.access(script_path, os.X_OK):
        error = f"Runner script is not executable: {script_path.as_posix()}"
    else:
        try:
            completed = subprocess.run(
                command,
                cwd=root,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            returncode = completed.returncode
            stdout_excerpt = completed.stdout[-2000:]
            stderr_excerpt = completed.stderr[-2000:]
            status = "passed" if completed.returncode == 0 else "failed"
        except subprocess.TimeoutExpired as exc:
            status = "timeout"
            returncode = None
            stdout_excerpt = _timeout_output_excerpt(exc.stdout)
            stderr_excerpt = _timeout_output_excerpt(exc.stderr)
            error = f"Runner script exceeded timeout_seconds={timeout_seconds}"
        except OSError as exc:
            error = str(exc)

    finished_at = datetime.now(timezone.utc)
    post_status_path = write_scheduler_status(project_root=root, output_path=root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    doctor_path = write_runtime_doctor(project_root=root, output_path=root / DEFAULT_RUNTIME_DOCTOR_OUTPUT)
    payload = {
        "schema_version": SCHEDULER_RUN_ONCE_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "script_path": script_path.as_posix(),
        "command": command,
        "timeout_seconds": timeout_seconds,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": round((finished_at - started_at).total_seconds(), 3),
        "status": status,
        "returncode": returncode,
        "stdout_excerpt": stdout_excerpt,
        "stderr_excerpt": stderr_excerpt,
        "error": error,
        "host_write_performed": False,
        "post_status_path": post_status_path.as_posix(),
        "doctor_path": doctor_path.as_posix(),
        "expected_outputs": [
            DEFAULT_TODAY_OUTPUT.as_posix(),
            DEFAULT_MEMORY_OUTPUT.as_posix(),
            DEFAULT_NOTIFICATION_OUTPUT.as_posix(),
            DEFAULT_ARCHIVE_ROOT.as_posix(),
        ],
        "safety": {
            "launchd_install_performed": False,
            "launchd_load_performed": False,
            "notification_send_performed": False,
            "notes": [
                "This proof executes the same local runner script launchd would call.",
                "It does not install, load, start, unload, or uninstall a LaunchAgent.",
                "The runner uses notification dry-run unless the script is edited by the operator.",
            ],
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_activation_preflight(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT,
    max_proof_age_hours: int = 24,
) -> Path:
    root = Path(project_root).resolve()
    status_path = write_scheduler_status(project_root=root, output_path=root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    doctor_path = write_runtime_doctor(project_root=root, output_path=root / DEFAULT_RUNTIME_DOCTOR_OUTPUT)
    artifacts = {
        "scheduler_status": status_path,
        "runtime_doctor": doctor_path,
        "scheduler_apply": root / DEFAULT_SCHEDULER_APPLY_OUTPUT,
        "scheduler_run_once": root / DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT,
        "notification": root / DEFAULT_NOTIFICATION_OUTPUT,
    }
    loaded_status = load_json(status_path).get("status", "unknown")
    checks = [
        _preflight_artifact_check(
            "runtime_doctor_ready",
            artifacts["runtime_doctor"],
            expected_schema=RUNTIME_DOCTOR_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=lambda payload: payload.get("status") == "ready" and int(payload.get("fail_count", 1)) == 0,
            message="Runtime doctor is ready with zero failures.",
        ),
        _preflight_artifact_check(
            "scheduler_assets_ready",
            artifacts["scheduler_status"],
            expected_schema=SCHEDULER_STATUS_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=lambda payload: payload.get("status") in {"assets_ready", "installed_not_loaded", "loaded"}
            and bool(payload.get("source_assets", {}).get("script_executable"))
            and bool(payload.get("source_assets", {}).get("plist_exists")),
            message="Scheduler source assets are present and executable.",
        ),
        _preflight_artifact_check(
            "dry_run_apply_planned",
            artifacts["scheduler_apply"],
            expected_schema=SCHEDULER_APPLY_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=_dry_run_apply_is_activation_plan,
            message="Dry-run activation plan exists for install/load/start-now without host writes.",
        ),
        _preflight_artifact_check(
            "runner_run_once_passed",
            artifacts["scheduler_run_once"],
            expected_schema=SCHEDULER_RUN_ONCE_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=lambda payload: payload.get("status") == "passed"
            and payload.get("returncode") == 0
            and payload.get("host_write_performed") is False,
            message="The scheduler runner executed once locally without host writes.",
        ),
        _preflight_artifact_check(
            "notification_remains_dry_run",
            artifacts["notification"],
            expected_schema=NOTIFICATION_SCHEMA_VERSION,
            max_age_hours=max_proof_age_hours,
            predicate=lambda payload: payload.get("dry_run") is True
            and payload.get("delivery_status") == "dry_run_ready",
            message="Notification payload remains dry-run until explicit send approval.",
        ),
    ]
    blockers = [check["message"] for check in checks if check["status"] == "fail"]
    warnings = [check["message"] for check in checks if check["status"] == "warn"]
    if loaded_status == "loaded":
        status = "already_active" if not blockers else "blocked"
        next_action = "Scheduler already appears loaded. Run scheduler status and inspect logs before changing it."
    elif blockers:
        status = "blocked"
        next_action = "Refresh the failed proof artifacts before requesting confirmed host-level activation."
    else:
        status = "ready"
        next_action = "Operator may decide whether to run scheduler apply --install --load --start-now --confirm-host-write."
    payload = {
        "schema_version": SCHEDULER_ACTIVATION_PREFLIGHT_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "status": status,
        "max_proof_age_hours": max_proof_age_hours,
        "host_write_performed": False,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "artifacts": {name: path.as_posix() for name, path in artifacts.items()},
        "activation_command": "PYTHONPATH=src python3 -m mybroker appliance scheduler apply --install --load --start-now --confirm-host-write",
        "next_action": next_action,
        "safety": {
            "requires_explicit_operator_approval": True,
            "preflight_does_not_install_or_load": True,
            "confirmed_activation_is_host_level": True,
            "notification_send_remains_separate": True,
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_scheduler_activation_verify(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT,
    freshness_hours: int = 36,
) -> Path:
    root = Path(project_root).resolve()
    source_plist = root / DEFAULT_LOCAL_OPS_DIR / f"{LAUNCHD_LABEL}.plist"
    installed_plist = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"
    status_path = write_scheduler_status(project_root=root, output_path=root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    doctor_path = write_runtime_doctor(
        project_root=root,
        output_path=root / DEFAULT_RUNTIME_DOCTOR_ACTIVATION_OUTPUT,
        freshness_hours=freshness_hours,
        require_launchd_loaded=True,
    )
    scheduler_status = load_json(status_path)
    doctor = load_json(doctor_path)
    checks = [
        _activation_verify_check(
            "launchd_loaded",
            bool(scheduler_status.get("launchd", {}).get("loaded")),
            "LaunchAgent is loaded for the current user.",
            evidence=scheduler_status.get("launchd", {}),
        ),
        _activation_verify_check(
            "installed_plist_exists",
            bool(scheduler_status.get("installed_plist", {}).get("exists")),
            "LaunchAgent plist is installed under ~/Library/LaunchAgents.",
            evidence=scheduler_status.get("installed_plist", {}),
        ),
        _activation_verify_check(
            "installed_plist_matches_source",
            _same_file_contents(source_plist, installed_plist),
            "Installed plist matches the source scheduler asset.",
            evidence={
                "source": source_plist.as_posix(),
                "installed": installed_plist.as_posix(),
            },
        ),
        _activation_verify_check(
            "runtime_doctor_strict",
            doctor.get("status") == "ready" and int(doctor.get("fail_count", 1)) == 0,
            "Runtime doctor passes with launchd loaded required.",
            evidence={
                "doctor_path": doctor_path.as_posix(),
                "fail_count": doctor.get("fail_count"),
                "warn_count": doctor.get("warn_count"),
            },
        ),
        _activation_verify_check(
            "today_surface_fresh",
            _path_fresh(root / DEFAULT_TODAY_OUTPUT, freshness_hours),
            f"Phone-readable today surface is fresher than {freshness_hours} hours.",
            evidence={"path": (root / DEFAULT_TODAY_OUTPUT).as_posix()},
        ),
        _activation_verify_check(
            "archive_manifest_fresh",
            _path_fresh(_latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT), freshness_hours),
            f"Latest daily archive manifest is fresher than {freshness_hours} hours.",
            evidence={"path": (_latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT).as_posix() if _latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT) else "")},
        ),
    ]
    stdout_log = root / "reports" / "runtime" / "daily-analyst.out.log"
    stderr_log = root / "reports" / "runtime" / "daily-analyst.err.log"
    warnings = []
    if not stdout_log.exists() and not stderr_log.exists():
        warnings.append("Scheduler log files do not exist yet. This is expected before the first launchd-triggered run.")
    blockers = [check["message"] for check in checks if check["status"] == "fail"]
    status = "active_verified" if not blockers else "blocked"
    payload = {
        "schema_version": SCHEDULER_ACTIVATION_VERIFY_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "label": LAUNCHD_LABEL,
        "status": status,
        "freshness_hours": freshness_hours,
        "host_write_performed": False,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "artifacts": {
            "scheduler_status": status_path.as_posix(),
            "runtime_doctor": doctor_path.as_posix(),
            "today": (root / DEFAULT_TODAY_OUTPUT).as_posix(),
            "latest_archive_manifest": (_latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT).as_posix() if _latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT) else ""),
            "stdout_log": stdout_log.as_posix(),
            "stderr_log": stderr_log.as_posix(),
        },
        "next_action": (
            "Activation is verified. Keep the Mac powered, inspect logs after the next scheduled run, and keep notification send as a separate gate."
            if not blockers
            else "Run activation-preflight, then perform the separate confirmed host-level activation before running verify again."
        ),
        "safety": {
            "verify_does_not_install_or_load": True,
            "confirmed_activation_is_separate": True,
            "notification_send_remains_separate": True,
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def build_scheduler_operations(
    *,
    project_root: str | Path = ".",
    freshness_hours: int = 24,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    generated = generated_at or datetime.now(timezone.utc)
    status_path = root / DEFAULT_SCHEDULER_STATUS_OUTPUT
    run_once_path = root / DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT
    preflight_path = root / DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT
    verify_path = root / DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT
    doctor_path = root / DEFAULT_RUNTIME_DOCTOR_OUTPUT
    status = _load_optional_json(status_path)
    run_once = _load_optional_json(run_once_path)
    preflight = _load_optional_json(preflight_path)
    verify = _load_optional_json(verify_path)
    doctor = _load_optional_json(doctor_path)
    proof_artifacts = [
        _scheduler_proof_artifact(
            name="scheduler_status",
            path=status_path,
            expected_schema=SCHEDULER_STATUS_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
        _scheduler_proof_artifact(
            name="run_once",
            path=run_once_path,
            expected_schema=SCHEDULER_RUN_ONCE_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
        _scheduler_proof_artifact(
            name="activation_preflight",
            path=preflight_path,
            expected_schema=SCHEDULER_ACTIVATION_PREFLIGHT_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
        _scheduler_proof_artifact(
            name="activation_verify",
            path=verify_path,
            expected_schema=SCHEDULER_ACTIVATION_VERIFY_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
        _scheduler_proof_artifact(
            name="runtime_doctor",
            path=doctor_path,
            expected_schema=RUNTIME_DOCTOR_SCHEMA_VERSION,
            freshness_hours=freshness_hours,
            now=generated,
        ),
    ]
    install_state = {
        "source_assets_status": status.get("status", "missing"),
        "script_ready": bool(status.get("source_assets", {}).get("script_executable")),
        "plist_ready": bool(status.get("source_assets", {}).get("plist_exists")),
        "installed": bool(status.get("installed_plist", {}).get("exists")),
        "loaded": bool(status.get("launchd", {}).get("loaded")),
        "installed_path": status.get("installed_plist", {}).get("path", ""),
    }
    local_run = {
        "status": run_once.get("status", "missing"),
        "returncode": run_once.get("returncode"),
        "duration_seconds": run_once.get("duration_seconds"),
        "host_write_performed": run_once.get("host_write_performed", False),
        "path": run_once_path.as_posix(),
    }
    activation_preflight = {
        "status": preflight.get("status", "missing"),
        "blockers": preflight.get("blockers", []),
        "warnings": preflight.get("warnings", []),
        "next_action": preflight.get("next_action", "Run activation-preflight after dry-run apply and run-once proof."),
        "host_write_performed": preflight.get("host_write_performed", False),
        "path": preflight_path.as_posix(),
    }
    activation_verify = {
        "status": verify.get("status", "missing"),
        "blockers": verify.get("blockers", []),
        "warnings": verify.get("warnings", []),
        "next_action": verify.get("next_action", "Verify only after confirmed activation."),
        "host_write_performed": verify.get("host_write_performed", False),
        "path": verify_path.as_posix(),
    }
    runtime = {
        "doctor_status": doctor.get("status", "missing"),
        "fail_count": doctor.get("fail_count", 0),
        "warn_count": doctor.get("warn_count", 0),
        "path": doctor_path.as_posix(),
    }
    overall_status = _scheduler_operations_status(
        install_state=install_state,
        local_run=local_run,
        activation_preflight=activation_preflight,
        activation_verify=activation_verify,
        runtime=runtime,
        proof_artifacts=proof_artifacts,
    )
    operator_next_action = _scheduler_operations_next_action(
        status=overall_status,
        install_state=install_state,
        local_run=local_run,
        activation_preflight=activation_preflight,
        runtime=runtime,
    )
    payload = {
        "schema_version": SCHEDULER_OPERATIONS_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "project_root": root.as_posix(),
        "status": overall_status,
        "freshness_hours": freshness_hours,
        "install_state": install_state,
        "local_run": local_run,
        "activation_preflight": activation_preflight,
        "activation_verify": activation_verify,
        "runtime": runtime,
        "proof_artifacts": proof_artifacts,
        "operator_next_action": operator_next_action,
        "copy_ready_commands": _scheduler_operations_commands(overall_status=overall_status),
        "phone_links": {
            "scheduler": DEFAULT_SCHEDULER_OPERATIONS_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_install_or_load_scheduler",
            "does_not_start_scheduler",
            "does_not_send_notifications",
            "does_not_fetch_live_network",
            "no_account_access",
            "no_order_execution",
            "host_writes_require_separate_confirmation",
        ],
    }
    return payload


def write_scheduler_operations(
    *,
    project_root: str | Path = ".",
    freshness_hours: int = 24,
    artifact_output_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_OUTPUT,
    surface_output_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_SURFACE,
) -> Path:
    payload = build_scheduler_operations(project_root=project_root, freshness_hours=freshness_hours)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_scheduler_operations(payload), encoding="utf-8")
    return target


def validate_scheduler_operations_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SCHEDULER_OPERATIONS_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"not_ready", "manual_ready", "activation_ready", "active_verified", "blocked"}:
        errors.append("status must be not_ready, manual_ready, activation_ready, active_verified, or blocked")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("operator_next_action"):
        errors.append("operator_next_action must not be empty")
    if not payload.get("proof_artifacts"):
        errors.append("proof_artifacts must not be empty")
    if not payload.get("phone_links", {}).get("scheduler"):
        errors.append("phone_links.scheduler must not be empty")
    if "does_not_install_or_load_scheduler" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_install_or_load_scheduler")
    for index, item in enumerate(payload.get("proof_artifacts", [])):
        for field in ["name", "path", "exists", "freshness_status"]:
            if field not in item:
                errors.append(f"proof_artifacts[{index}] missing {field}")
        if item.get("freshness_status") not in {"fresh", "stale", "missing", "invalid_schema"}:
            errors.append(f"proof_artifacts[{index}] invalid freshness_status")
    for index, command in enumerate(payload.get("copy_ready_commands", [])):
        command_text = command.get("command", "")
        if "--confirm-host-write" in command_text and command.get("requires_separate_approval") is not True:
            errors.append(f"copy_ready_commands[{index}] host write command must require separate approval")
        if command.get("external_effect_performed") is not False:
            errors.append(f"copy_ready_commands[{index}] external_effect_performed must be false")
    return errors


def validate_scheduler_operations_file(path: str | Path) -> list[str]:
    return validate_scheduler_operations_payload(load_json(path))


def render_scheduler_operations(payload: dict[str, Any]) -> str:
    status_label = {
        "active_verified": "자동 실행 확인됨",
        "activation_ready": "활성화 준비됨",
        "manual_ready": "수동 실행은 준비됨",
        "not_ready": "준비 전",
        "blocked": "차단됨",
    }.get(payload.get("status", ""), payload.get("status", "unknown"))
    install = payload.get("install_state", {})
    local_run = payload.get("local_run", {})
    preflight = payload.get("activation_preflight", {})
    verify = payload.get("activation_verify", {})
    runtime = payload.get("runtime", {})
    proof_rows = "".join(
        "<tr>"
        f"<td><strong>{esc(item.get('name', ''))}</strong><span>{esc(item.get('path', ''))}</span></td>"
        f"<td><span class='pill {esc(_readiness_css(item.get('freshness_status', 'missing')))}'>{esc(item.get('freshness_status', ''))}</span></td>"
        f"<td>{esc(item.get('summary_status', ''))}</td>"
        f"<td>{esc(item.get('age_hours', ''))}</td>"
        "</tr>"
        for item in payload.get("proof_artifacts", [])
    )
    commands = "".join(
        "<article class='command'>"
        f"<span>{esc(command.get('label', 'command'))}</span>"
        f"<code>{esc(command.get('command', ''))}</code>"
        f"<small>{esc(command.get('why', ''))}</small>"
        "</article>"
        for command in payload.get("copy_ready_commands", [])
    ) or "<p>지금 복사할 안전한 로컬 명령이 없습니다.</p>"
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "scheduler"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Scheduler Operations</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; --bad:#9f2d2d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow,.command span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small,td span {{ color:var(--muted); }}
.hero,.section,.command {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.panel {{ border:1px solid var(--line); border-radius:8px; background:white; padding:13px; min-width:0; }}
.panel strong {{ display:block; margin-bottom:4px; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
td strong,td span {{ display:block; overflow-wrap:anywhere; }}
.pill {{ display:inline-block; border-radius:999px; padding:2px 8px; font-size:12px; font-weight:900; }}
.fresh {{ background:#e7f5ee; color:var(--green); }}
.stale {{ background:#fff3d8; color:var(--warn); }}
.missing {{ background:#ffe2e2; color:var(--bad); }}
.command {{ background:white; padding:14px; margin:10px 0; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.grid,.links {{ grid-template-columns:1fr; }} table {{ font-size:13px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Scheduler · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>자동 실행 준비 상태</h1>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('operator_next_action', ''))}</p>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Script</span><strong>{esc('OK' if install.get('script_ready') else 'NO')}</strong></article>
<article class="metric"><span>Plist</span><strong>{esc('OK' if install.get('plist_ready') else 'NO')}</strong></article>
<article class="metric"><span>Installed</span><strong>{esc('YES' if install.get('installed') else 'NO')}</strong></article>
<article class="metric"><span>Loaded</span><strong>{esc('YES' if install.get('loaded') else 'NO')}</strong></article>
</div>
</section>
<section class="section">
<h2>운영 증거</h2>
<div class="grid">
<article class="panel"><strong>수동 run-once</strong><p>{esc(local_run.get('status', 'missing'))} · returncode {esc(local_run.get('returncode', ''))}</p></article>
<article class="panel"><strong>Activation preflight</strong><p>{esc(preflight.get('status', 'missing'))} · blockers {esc(len(preflight.get('blockers', [])))}</p></article>
<article class="panel"><strong>Activation verify</strong><p>{esc(verify.get('status', 'missing'))} · blockers {esc(len(verify.get('blockers', [])))}</p></article>
<article class="panel"><strong>Runtime doctor</strong><p>{esc(runtime.get('doctor_status', 'missing'))} · fails {esc(runtime.get('fail_count', 0))} · warns {esc(runtime.get('warn_count', 0))}</p></article>
</div>
</section>
<section class="section">
<h2>다음에 복사할 명령</h2>
{commands}
</section>
<section class="section">
<h2>Proof freshness</h2>
<table><thead><tr><th>Proof</th><th>Freshness</th><th>Status</th><th>Age</th></tr></thead><tbody>{proof_rows}</tbody></table>
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 로컬 파일만 읽습니다. 설치, load, start, 알림 전송, live source refresh는 별도 승인과 확인 없이는 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def write_operator_decision_packet(
    *,
    project_root: str | Path = ".",
    output_path: str | Path = DEFAULT_OPERATOR_DECISION_PACKET_OUTPUT,
) -> Path:
    root = Path(project_root).resolve()
    preflight_path = write_scheduler_activation_preflight(
        project_root=root,
        output_path=root / DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT,
    )
    verify_path = write_scheduler_activation_verify(
        project_root=root,
        output_path=root / DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT,
    )
    preflight = load_json(preflight_path)
    verify = load_json(verify_path)
    notification_path = root / DEFAULT_NOTIFICATION_OUTPUT
    notification = load_json(notification_path) if notification_path.exists() else {}
    phone_access_path = root / DEFAULT_PHONE_ACCESS_OUTPUT
    phone_access = load_json(phone_access_path) if phone_access_path.exists() else {}
    decisions = [
        _scheduler_activation_decision(preflight=preflight, verify=verify),
        _notification_send_decision(notification=notification),
        _private_phone_access_decision(phone_access=phone_access),
    ]
    payload = {
        "schema_version": OPERATOR_DECISION_PACKET_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "status": "pending_operator_decision",
        "host_write_performed": False,
        "decisions": decisions,
        "summary": {
            "decision_count": len(decisions),
            "ready_count": sum(1 for decision in decisions if decision.get("readiness") == "ready"),
            "blocked_count": sum(1 for decision in decisions if decision.get("readiness") == "blocked"),
            "pending_count": sum(1 for decision in decisions if decision.get("readiness") == "pending"),
        },
        "artifacts": {
            "scheduler_activation_preflight": preflight_path.as_posix(),
            "scheduler_activation_verify": verify_path.as_posix(),
            "notification": notification_path.as_posix(),
            "phone_access": phone_access_path.as_posix(),
        },
        "safety": {
            "packet_does_not_execute_external_effects": True,
            "scheduler_activation_requires_confirm_host_write": True,
            "notification_send_requires_provider_secrets": True,
            "private_serving_changes_network_exposure": True,
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def write_operator_decision_apply(
    *,
    response: str,
    project_root: str | Path = ".",
    packet_path: str | Path = DEFAULT_OPERATOR_DECISION_PACKET_OUTPUT,
    output_path: str | Path = DEFAULT_OPERATOR_DECISION_APPLY_OUTPUT,
) -> Path:
    root = Path(project_root).resolve()
    packet_file = Path(packet_path)
    if not packet_file.is_absolute():
        packet_file = root / packet_file
    packet = load_json(packet_file)
    parsed = _parse_operator_approval_response(response)
    decision = _find_packet_decision(packet=packet, decision_id=parsed.get("decision_id", ""))
    blockers = _operator_decision_apply_blockers(parsed=parsed, decision=decision)
    commands = list(decision.get("agent_will_run", [])) if decision and not blockers else []
    rollback_command = decision.get("rollback_command", "") if decision else ""
    payload = {
        "schema_version": OPERATOR_DECISION_APPLY_SCHEMA_VERSION,
        "generated_at": _now(),
        "project_root": root.as_posix(),
        "packet_path": packet_file.as_posix(),
        "operator_response": response,
        "parsed_response": parsed,
        "decision_id": parsed.get("decision_id", ""),
        "approval_scope": parsed.get("approval_scope", ""),
        "status": "ready_to_apply" if not blockers else "blocked",
        "blockers": blockers,
        "commands": commands,
        "rollback_command": rollback_command,
        "external_effect_performed": False,
        "host_write_performed": False,
        "execution_mode": "dry_run_plan_only",
        "next_action": _operator_decision_apply_next_action(blockers=blockers, decision=decision),
        "safety": {
            "does_not_execute_commands": True,
            "requires_exact_decision_id": True,
            "requires_exact_approval_scope": True,
            "blocked_decisions_do_not_emit_commands": True,
        },
        "policy": "research_only",
    }
    return write_json(payload, output_path)


def build_daily_brief_agenda(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scout = _load_optional_json(scout_path)
    evidence = _load_optional_json(evidence_path)
    memory = _load_optional_json(memory_path)
    vault = _load_optional_json(vault_path)
    refresh_plan = _load_optional_json(refresh_plan_path)
    recommendations = scout.get("recommendations", []) if scout.get("schema_version") == "daily_scout.v1" else []
    source_rows = evidence.get("source_status", []) if evidence.get("schema_version") == "public_evidence_catalog.v1" else []
    evidence_items = evidence.get("items", []) if evidence.get("schema_version") == "public_evidence_catalog.v1" else []
    memory_by_id = {row.get("topic_id"): row for row in memory.get("topics", [])}
    vault_notes = vault.get("compiled_notes", []) if vault.get("schema_version") == "knowledge_vault_compile.v1" else []
    top_cards = [
        _agenda_topic_card(
            recommendation=recommendation,
            evidence_items=evidence_items,
            source_rows=source_rows,
            memory_topic=memory_by_id.get(recommendation.get("topic_id"), {}),
            vault_notes=vault_notes,
        )
        for recommendation in recommendations[:3]
    ]
    primary = top_cards[0] if top_cards else {}
    weak_points = _agenda_weak_points(top_cards=top_cards, source_rows=source_rows, evidence=evidence)
    role_brief = _agenda_role_brief(primary=primary, weak_points=weak_points, refresh_plan=refresh_plan)
    payload = {
        "schema_version": DAILY_BRIEF_AGENDA_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "run_id": scout.get("run_id", ""),
        "mode": "phone_first_local_personal_analyst",
        "operator_time_budget_minutes": 20,
        "primary_topic": primary,
        "study_sequence": _agenda_study_sequence(primary=primary, weak_points=weak_points),
        "topic_cards": top_cards,
        "source_fanout": _agenda_source_fanout(source_rows=source_rows, top_cards=top_cards),
        "role_brief": role_brief,
        "copy_ready_questions": _agenda_questions(primary=primary, weak_points=weak_points),
        "weak_points": weak_points,
        "external_effect_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "local_artifact_generation_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "no_account_access",
            "no_live_trading",
            "no_discretionary_management",
            "no_unsupported_personalized_recommendations",
        ],
        "inputs": {
            "scout": Path(scout_path).as_posix(),
            "evidence": Path(evidence_path).as_posix(),
            "memory": Path(memory_path).as_posix(),
            "vault": Path(vault_path).as_posix(),
            "refresh_plan": Path(refresh_plan_path).as_posix(),
        },
    }
    return payload


def write_daily_brief_agenda(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    surface_output_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_SURFACE,
) -> Path:
    payload = build_daily_brief_agenda(
        scout_path=scout_path,
        evidence_path=evidence_path,
        memory_path=memory_path,
        vault_path=vault_path,
        refresh_plan_path=refresh_plan_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_daily_brief_agenda(payload), encoding="utf-8")
    return target


def validate_daily_brief_agenda_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DAILY_BRIEF_AGENDA_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if not payload.get("primary_topic"):
        errors.append("primary_topic must not be empty")
    if not payload.get("study_sequence"):
        errors.append("study_sequence must not be empty")
    if not payload.get("topic_cards"):
        errors.append("topic_cards must not be empty")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    for index, step in enumerate(payload.get("study_sequence", [])):
        for field in ["step", "minutes", "title", "operator_action", "stop_condition"]:
            if field not in step:
                errors.append(f"study_sequence[{index}] missing {field}")
    return errors


def validate_daily_brief_agenda_file(path: str | Path) -> list[str]:
    return validate_daily_brief_agenda_payload(load_json(path))


def build_daily_readiness(
    *,
    project_root: str | Path = ".",
    freshness_hours: int = 24,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    generated = generated_at or datetime.now(timezone.utc)
    artifact_specs = [
        ("today_surface", DEFAULT_TODAY_OUTPUT, "phone_surface", True),
        ("daily_agenda_surface", DEFAULT_DAILY_BRIEF_AGENDA_SURFACE, "phone_surface", True),
        ("daily_agenda", DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT, "machine_artifact", True),
        ("source_refresh_brief", DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT, "control_artifact", False),
        ("source_refresh_surface", DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE, "phone_surface", False),
        ("morning_control", DEFAULT_MORNING_CONTROL_OUTPUT, "control_artifact", True),
        ("morning_surface", DEFAULT_MORNING_CONTROL_SURFACE, "phone_surface", True),
        ("daily_scout", DEFAULT_DAILY_SCOUT_OUTPUT, "machine_artifact", True),
        ("daily_evidence", DEFAULT_DAILY_EVIDENCE_OUTPUT, "machine_artifact", True),
        ("topic_memory", DEFAULT_TOPIC_MEMORY_OUTPUT, "memory_artifact", True),
        ("scenario_report", Path("reports/scenarios/daily-research-sim.json"), "machine_artifact", True),
        ("market_verdict", Path("reports/scenarios/daily-research-verdict.json"), "machine_artifact", True),
        ("archive_manifest", _latest_archive_manifest(root / DEFAULT_ARCHIVE_ROOT) or DEFAULT_ARCHIVE_ROOT / "missing" / "manifest.json", "archive", True),
        ("runtime_doctor", DEFAULT_RUNTIME_DOCTOR_OUTPUT, "runtime_artifact", False),
        ("scheduler_status", DEFAULT_SCHEDULER_STATUS_OUTPUT, "runtime_artifact", False),
        ("scheduler_operations", DEFAULT_SCHEDULER_OPERATIONS_OUTPUT, "runtime_artifact", False),
        ("scheduler_surface", DEFAULT_SCHEDULER_OPERATIONS_SURFACE, "phone_surface", False),
        ("vault_surface", DEFAULT_VAULT_SURFACE_OUTPUT, "phone_surface", False),
        ("memory_surface", DEFAULT_MEMORY_OUTPUT, "phone_surface", False),
    ]
    artifacts = [
        _readiness_artifact_check(
            root=root,
            name=name,
            path=path,
            kind=kind,
            required=required,
            freshness_hours=freshness_hours,
            now=generated,
        )
        for name, path, kind, required in artifact_specs
    ]
    required = [item for item in artifacts if item["required"]]
    missing_required = [item for item in required if item["freshness_status"] == "missing"]
    stale_required = [item for item in required if item["freshness_status"] == "stale"]
    warn_artifacts = [item for item in artifacts if item["freshness_status"] in {"missing", "stale"} and not item["required"]]
    scheduler = _readiness_scheduler_state(root / DEFAULT_SCHEDULER_STATUS_OUTPUT)
    status = _readiness_status(missing_required=missing_required, stale_required=stale_required)
    next_actions = _readiness_next_actions(
        status=status,
        missing_required=missing_required,
        stale_required=stale_required,
        scheduler=scheduler,
    )
    payload = {
        "schema_version": DAILY_READINESS_SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "status": status,
        "freshness_hours": freshness_hours,
        "summary": {
            "required_count": len(required),
            "fresh_required_count": sum(1 for item in required if item["freshness_status"] == "fresh"),
            "missing_required_count": len(missing_required),
            "stale_required_count": len(stale_required),
            "warning_count": len(warn_artifacts),
        },
        "artifacts": artifacts,
        "scheduler": scheduler,
        "phone_links": {
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "scheduler": DEFAULT_SCHEDULER_OPERATIONS_SURFACE.as_posix(),
            "source_refresh": DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix(),
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "agenda": DEFAULT_DAILY_BRIEF_AGENDA_SURFACE.as_posix(),
            "memory": DEFAULT_MEMORY_OUTPUT.as_posix(),
            "vault": DEFAULT_VAULT_SURFACE_OUTPUT.as_posix(),
        },
        "next_actions": next_actions,
        "recommended_local_run": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --profile examples/profiles/beginner-conservative.json --dry-run",
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "no_account_access",
            "no_order_execution",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_daily_readiness(
    *,
    project_root: str | Path = ".",
    freshness_hours: int = 24,
    artifact_output_path: str | Path = DEFAULT_DAILY_READINESS_OUTPUT,
    surface_output_path: str | Path = DEFAULT_DAILY_READINESS_SURFACE,
) -> Path:
    payload = build_daily_readiness(project_root=project_root, freshness_hours=freshness_hours)
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_daily_readiness(payload), encoding="utf-8")
    return target


def validate_daily_readiness_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DAILY_READINESS_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"ready", "review", "stale", "blocked"}:
        errors.append("status must be ready, review, stale, or blocked")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("artifacts"):
        errors.append("artifacts must not be empty")
    if not payload.get("next_actions"):
        errors.append("next_actions must not be empty")
    required_names = {item.get("name") for item in payload.get("artifacts", []) if item.get("required")}
    for name in ["today_surface", "daily_agenda", "daily_scout", "daily_evidence", "archive_manifest"]:
        if name not in required_names:
            errors.append(f"required artifact missing from readiness checks: {name}")
    for index, item in enumerate(payload.get("artifacts", [])):
        for field in ["name", "path", "kind", "required", "exists", "freshness_status"]:
            if field not in item:
                errors.append(f"artifacts[{index}] missing {field}")
        if item.get("freshness_status") not in {"fresh", "stale", "missing"}:
            errors.append(f"artifacts[{index}] invalid freshness_status")
    return errors


def validate_daily_readiness_file(path: str | Path) -> list[str]:
    return validate_daily_readiness_payload(load_json(path))


def build_source_refresh_brief(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    refresh_apply_path: str | Path = DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scout = _load_optional_json(scout_path)
    evidence = _load_optional_json(evidence_path)
    refresh_plan = _load_optional_json(refresh_plan_path)
    refresh_apply = _load_optional_json(refresh_apply_path)
    live_gate = _load_optional_json(refresh_live_gate_path)
    live_run = _load_optional_json(refresh_live_run_path)
    preflight = _load_optional_json(refresh_live_preflight_path)
    actions = _source_refresh_brief_actions(refresh_plan=refresh_plan, refresh_apply=refresh_apply, live_gate=live_gate)
    blocked_live = [action for action in actions if action.get("approval_required") == "live_network_refresh"]
    ready_local = [action for action in actions if action.get("decision") == "ready"]
    weak_evidence = _source_refresh_weak_evidence(evidence=evidence, scout=scout)
    status = _source_refresh_brief_status(
        actions=actions,
        live_gate=live_gate,
        live_run=live_run,
        preflight=preflight,
    )
    payload = {
        "schema_version": SOURCE_REFRESH_BRIEF_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "status": status,
        "recommended_topic": scout.get("recommended_topic", {}),
        "summary": {
            "action_count": len(actions),
            "ready_local_count": len(ready_local),
            "blocked_live_count": len(blocked_live),
            "weak_evidence_count": len(weak_evidence),
            "gate_status": live_gate.get("status", "missing"),
            "approval_status": live_run.get("approval_status", "missing"),
            "live_run_status": live_run.get("execution", {}).get("status", "missing"),
            "preflight_status": preflight.get("status", "missing"),
        },
        "weak_evidence": weak_evidence,
        "actions": actions,
        "operator_decision": _source_refresh_operator_decision(live_gate=live_gate, live_run=live_run, preflight=preflight),
        "next_action": _source_refresh_next_action(status=status, live_gate=live_gate, live_run=live_run, preflight=preflight),
        "phone_links": {
            "source_refresh": DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE.as_posix(),
            "today": DEFAULT_TODAY_OUTPUT.as_posix(),
            "agenda": DEFAULT_DAILY_BRIEF_AGENDA_SURFACE.as_posix(),
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "readiness": DEFAULT_DAILY_READINESS_SURFACE.as_posix(),
        },
        "inputs": {
            "scout": Path(scout_path).as_posix(),
            "evidence": Path(evidence_path).as_posix(),
            "refresh_plan": Path(refresh_plan_path).as_posix(),
            "refresh_apply": Path(refresh_apply_path).as_posix(),
            "refresh_live_gate": Path(refresh_live_gate_path).as_posix(),
            "refresh_live_run": Path(refresh_live_run_path).as_posix(),
            "refresh_live_preflight": Path(refresh_live_preflight_path).as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "reads_local_artifacts_only",
            "does_not_fetch_live_network",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "no_paid_api",
            "no_credentials",
            "no_account_access",
            "no_order_execution",
            "live_refresh_requires_separate_approval_and_confirmation",
        ],
    }
    return payload


def write_source_refresh_brief(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    refresh_apply_path: str | Path = DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_OUTPUT,
    surface_output_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE,
) -> Path:
    payload = build_source_refresh_brief(
        scout_path=scout_path,
        evidence_path=evidence_path,
        refresh_plan_path=refresh_plan_path,
        refresh_apply_path=refresh_apply_path,
        refresh_live_gate_path=refresh_live_gate_path,
        refresh_live_run_path=refresh_live_run_path,
        refresh_live_preflight_path=refresh_live_preflight_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_source_refresh_brief(payload), encoding="utf-8")
    return target


def validate_source_refresh_brief_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SOURCE_REFRESH_BRIEF_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("status") not in {"no_refresh_needed", "local_ready", "approval_required", "preflight_required", "ready_to_execute", "executed", "blocked"}:
        errors.append("status must be a recognized source refresh brief status")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("next_action"):
        errors.append("next_action must not be empty")
    if not payload.get("phone_links", {}).get("source_refresh"):
        errors.append("phone_links.source_refresh must not be empty")
    if "does_not_fetch_live_network" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_fetch_live_network")
    for index, action in enumerate(payload.get("actions", [])):
        for field in ["source_name", "adapter_id", "decision", "status", "approval_required", "reason"]:
            if field not in action:
                errors.append(f"actions[{index}] missing {field}")
        command = action.get("command", "")
        if any(fragment in command for fragment in ["--send", "--confirm-host-write", "launchctl", "tailscale serve --bg"]):
            errors.append(f"actions[{index}] command crosses non-refresh external-effect boundary")
    decision = payload.get("operator_decision", {})
    if decision.get("approval_required") and not decision.get("copy_ready_response"):
        errors.append("operator_decision with approval_required must include copy_ready_response")
    return errors


def validate_source_refresh_brief_file(path: str | Path) -> list[str]:
    return validate_source_refresh_brief_payload(load_json(path))


def render_source_refresh_brief(payload: dict[str, Any]) -> str:
    status_label = {
        "no_refresh_needed": "새로고침 필요 낮음",
        "local_ready": "로컬 작업 먼저 가능",
        "approval_required": "승인 필요",
        "preflight_required": "사전점검 필요",
        "ready_to_execute": "실행 전 최종 확인",
        "executed": "실행 증거 있음",
        "blocked": "차단됨",
    }.get(payload.get("status", ""), payload.get("status", "unknown"))
    summary = payload.get("summary", {})
    topic = payload.get("recommended_topic", {})
    weak_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(item.get('kind', 'weak'))}</span>"
        f"<strong>{esc(item.get('title', ''))}</strong>"
        f"<p>{esc(item.get('why_it_matters', ''))}</p>"
        "</article>"
        for item in payload.get("weak_evidence", [])
    ) or "<p>오늘 기록된 약한 근거가 없습니다.</p>"
    action_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(action.get('decision', ''))} · {esc(action.get('approval_required', 'none'))}</span>"
        f"<strong>{esc(action.get('source_name', ''))}</strong>"
        f"<p>{esc(action.get('reason', ''))}</p>"
        f"<small>{esc(action.get('expected_artifact', ''))}</small>"
        "</article>"
        for action in payload.get("actions", [])
    ) or "<p>오늘 계획된 source refresh action이 없습니다.</p>"
    decision = payload.get("operator_decision", {})
    decision_card = (
        "<article class='decision'>"
        f"<span>{esc(decision.get('risk_level', 'medium'))}</span>"
        f"<strong>{esc(decision.get('title', 'live refresh decision'))}</strong>"
        f"<p>{esc(decision.get('why', ''))}</p>"
        f"<code>{esc(decision.get('copy_ready_response', ''))}</code>"
        f"<small>{esc(decision.get('stale_context_guard', ''))}</small>"
        "</article>"
        if decision.get("approval_required")
        else "<p>지금 승인해야 할 live source refresh 결정은 없습니다.</p>"
    )
    links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in payload.get("phone_links", {}).items()
        if label != "source_refresh"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Source Refresh</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
a {{ color:var(--blue); font-weight:900; text-decoration:none; }}
.eyebrow,.card span,.decision span {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.card,.decision {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
.stack {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.card,.decision {{ background:white; padding:14px; min-width:0; }}
.card strong,.decision strong {{ display:block; margin:5px 0; }}
.card p,.card small,.decision p,.decision small {{ overflow-wrap:anywhere; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.stack,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Source Refresh · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘 근거 새로고침 판단</h1>
</header>
<section class="hero">
<span class="eyebrow">판정</span>
<strong class="status">{esc(status_label)}</strong>
<p>{esc(payload.get('next_action', ''))}</p>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>Actions</span><strong>{esc(summary.get('action_count', 0))}</strong></article>
<article class="metric"><span>Local</span><strong>{esc(summary.get('ready_local_count', 0))}</strong></article>
<article class="metric"><span>Live</span><strong>{esc(summary.get('blocked_live_count', 0))}</strong></article>
<article class="metric"><span>Weak</span><strong>{esc(summary.get('weak_evidence_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>오늘 주제</h2>
<article class="card">
<span>{esc(topic.get('confidence', 'unknown'))}</span>
<strong>{esc(topic.get('name', '오늘 추천 주제 없음'))}</strong>
<p>{esc(topic.get('why', topic.get('why_today', '')))}</p>
</article>
</section>
<section class="section">
<h2>약한 근거</h2>
<div class="stack">{weak_cards}</div>
</section>
<section class="section">
<h2>Source actions</h2>
<div class="stack">{action_cards}</div>
</section>
<section class="section">
<h2>사람이 결정할 것</h2>
{decision_card}
</section>
<section class="section">
<h2>연결 화면</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 로컬 artifact만 읽습니다. live network refresh, paid API, credential use, notification send, host scheduler write, 계좌 접근, 주문 실행은 별도 승인 없이 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_daily_readiness(payload: dict[str, Any]) -> str:
    status = payload.get("status", "review")
    summary = payload.get("summary", {})
    status_label = {
        "ready": "오늘 읽어도 됨",
        "review": "확인 필요",
        "stale": "다시 실행 권장",
        "blocked": "먼저 생성 필요",
    }.get(status, status)
    artifact_rows = "".join(
        "<tr>"
        f"<td><strong>{esc(item.get('name', ''))}</strong><span>{esc(item.get('kind', ''))}</span></td>"
        f"<td><span class='pill {esc(_readiness_css(item.get('freshness_status', 'missing')))}'>{esc(item.get('freshness_status', ''))}</span></td>"
        f"<td>{esc(item.get('age_hours', ''))}</td>"
        f"<td>{esc(item.get('path', ''))}</td>"
        "</tr>"
        for item in payload.get("artifacts", [])
    )
    actions = "".join(f"<li>{esc(action)}</li>" for action in payload.get("next_actions", []))
    links = "".join(
        f"<a href='{esc(path)}'>{esc(name)}</a>"
        for name, path in payload.get("phone_links", {}).items()
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Daily Readiness</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; --bad:#9f2d2d; }}
* {{ box-sizing:border-box; }}
html,body {{ max-width:100%; overflow-x:hidden; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p,li,td span {{ color:var(--muted); }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:14px 0; }}
.status {{ display:block; margin:8px 0; font-size:28px; line-height:1.1; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
td strong,td span {{ display:block; }}
.pill {{ display:inline-block; border-radius:999px; padding:2px 8px; font-size:12px; font-weight:900; }}
.fresh {{ background:#e7f5ee; color:var(--green); }}
.stale {{ background:#fff3d8; color:var(--warn); }}
.missing {{ background:#ffe2e2; color:var(--bad); }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; color:var(--blue); font-weight:900; text-decoration:none; overflow-wrap:anywhere; }}
code {{ display:block; padding:12px; border-radius:8px; background:#f1f5f9; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics,.links {{ grid-template-columns:1fr; }} table {{ font-size:13px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Daily Readiness · {esc(_local_date_label(payload.get('generated_at', '')))}</span>
<h1>오늘 브리프 준비 상태</h1>
</header>
<section class="hero">
<span class="eyebrow">상태</span>
<strong class="status">{esc(status_label)}</strong>
<p>전체 daily run을 다시 돌리기 전에도, 지금 폰에서 볼 산출물이 충분히 최신인지 확인합니다.</p>
</section>
<section class="section">
<div class="metrics">
<article class="metric"><span>필수</span><strong>{esc(summary.get('required_count', 0))}</strong></article>
<article class="metric"><span>Fresh</span><strong>{esc(summary.get('fresh_required_count', 0))}</strong></article>
<article class="metric"><span>Stale</span><strong>{esc(summary.get('stale_required_count', 0))}</strong></article>
<article class="metric"><span>Missing</span><strong>{esc(summary.get('missing_required_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>다음 행동</h2>
<ul>{actions}</ul>
<code>{esc(payload.get('recommended_local_run', ''))}</code>
</section>
<section class="section">
<h2>폰 링크</h2>
<div class="links">{links}</div>
</section>
<section class="section">
<h2>Artifact freshness</h2>
<table><thead><tr><th>Artifact</th><th>Freshness</th><th>Age hours</th><th>Path</th></tr></thead><tbody>{artifact_rows}</tbody></table>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 로컬 파일만 읽습니다. live source refresh, 알림 전송, host scheduler 쓰기, 계좌 접근, 주문 실행은 별도 승인 없이 수행하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def render_daily_brief_agenda(payload: dict[str, Any]) -> str:
    primary = payload.get("primary_topic", {})
    sequence_cards = "".join(
        "<article class='step'>"
        f"<span>{esc(step.get('minutes', ''))}분 · step {esc(step.get('step', ''))}</span>"
        f"<strong>{esc(step.get('title', ''))}</strong>"
        f"<p>{esc(step.get('operator_action', ''))}</p>"
        f"<small>멈춤 기준: {esc(step.get('stop_condition', ''))}</small>"
        "</article>"
        for step in payload.get("study_sequence", [])
    )
    topic_cards = "".join(
        "<article class='card'>"
        f"<span>#{esc(card.get('priority_rank', ''))} · {esc(card.get('action', 'monitor'))} · {esc(card.get('confidence', ''))}</span>"
        f"<strong>{esc(card.get('name', ''))}</strong>"
        f"<p>{esc(card.get('why_today', ''))}</p>"
        f"<small>근거 {esc(card.get('evidence_count', 0))}개 · source {esc(card.get('source_family_count', 0))}개 · vault {esc(card.get('vault_note_count', 0))}개</small>"
        "</article>"
        for card in payload.get("topic_cards", [])
    )
    source_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(row.get('freshness_status', 'unknown'))} · {esc(row.get('relevance_label', 'unscored'))}</span>"
        f"<strong>{esc(row.get('source_name', 'source'))}</strong>"
        f"<p>{esc(row.get('role', '오늘 주제 근거 확인'))}</p>"
        "</article>"
        for row in payload.get("source_fanout", [])
    )
    role_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(role.get('role', 'analyst'))}</span>"
        f"<strong>{esc(role.get('task', '오늘 근거 점검'))}</strong>"
        f"<p>{esc(role.get('success_condition', ''))}</p>"
        "</article>"
        for role in payload.get("role_brief", [])
    )
    weak_items = "".join(f"<li>{esc(item)}</li>" for item in payload.get("weak_points", [])) or "<li>오늘 기록된 약한 근거가 없습니다.</li>"
    questions = "".join(f"<article class='question'><p>{esc(question)}</p></article>" for question in payload.get("copy_ready_questions", []))
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Daily Agenda</title>
<style>
:root {{ --bg:#f6f7f2; --ink:#18212b; --muted:#63707c; --line:#d9dfd5; --panel:#fffefa; --accent:#1f5f8b; --green:#1e6b52; --warn:#93651a; }}
* {{ box-sizing:border-box; }}
html,body {{ max-width:100%; overflow-x:hidden; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:430px; min-width:0; padding:14px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 12px; font-size:32px; line-height:1.1; }}
h2 {{ margin:0 0 10px; font-size:20px; }}
p {{ margin:0; color:var(--muted); }}
.hero,.section {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:12px 0; }}
.hero strong {{ display:block; margin:8px 0; font-size:25px; line-height:1.15; }}
.stack {{ display:grid; grid-template-columns:minmax(0,1fr); gap:10px; }}
.step,.card,.question {{ min-width:0; border:1px solid var(--line); border-radius:8px; background:white; padding:13px; }}
.step span,.card span {{ display:block; margin-bottom:7px; color:var(--accent); font-size:12px; font-weight:900; }}
.step strong,.card strong {{ display:block; margin-bottom:6px; }}
.step p,.step small,.card p,.card small,.question p {{ overflow-wrap:anywhere; word-break:break-word; }}
.step small,.card small {{ display:block; color:var(--ink); }}
ul {{ margin:0; padding-left:18px; color:var(--muted); }}
.boundary {{ border-left:4px solid var(--green); }}
@media (max-width:520px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Daily Agenda · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>오늘 20분 시장 공부 순서</h1>
</header>
<section class="hero">
<span class="eyebrow">오늘의 첫 주제</span>
<strong>{esc(primary.get('name', '오늘 추천 주제 없음'))}</strong>
<p>{esc(primary.get('why_today', 'Scout와 근거를 먼저 생성하세요.'))}</p>
</section>
<section class="section">
<h2>읽는 순서</h2>
<div class="stack">{sequence_cards}</div>
</section>
<section class="section">
<h2>오늘 볼 주제 후보</h2>
<div class="stack">{topic_cards}</div>
</section>
<section class="section">
<h2>근거 fan-out</h2>
<div class="stack">{source_cards}</div>
</section>
<section class="section">
<h2>에이전트 역할별 다음 일</h2>
<div class="stack">{role_cards}</div>
</section>
<section class="section">
<h2>아직 결론내리면 안 되는 이유</h2>
<ul>{weak_items}</ul>
</section>
<section class="section">
<h2>오늘 물어볼 질문</h2>
<div class="stack">{questions}</div>
</section>
<section class="section boundary">
<h2>안전 경계</h2>
<p>이 agenda는 교육/리서치/시뮬레이션용입니다. 계좌 접근, 주문, 투자 일임, 개인화 매수/매도 지시는 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def write_today_surface(
    *,
    scenario_path: str | Path,
    verdict_path: str | Path,
    memory_path: str | Path,
    evidence_path: str | Path,
    brief_path: str | Path,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    refresh_plan_path: str | Path = DEFAULT_SOURCE_REFRESH_PLAN_OUTPUT,
    refresh_apply_path: str | Path = DEFAULT_SOURCE_REFRESH_APPLY_OUTPUT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    agenda_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    agenda_surface_path: str | Path | None = DEFAULT_DAILY_BRIEF_AGENDA_SURFACE,
    source_refresh_surface_path: str | Path | None = DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE,
    output_path: str | Path = DEFAULT_TODAY_OUTPUT,
    archive_manifest_path: str | Path | None = None,
    memory_surface_path: str | Path | None = None,
    journal_surface_path: str | Path | None = None,
    task_queue_surface_path: str | Path | None = None,
    task_ledger_surface_path: str | Path | None = None,
) -> Path:
    scenario = load_json(scenario_path)
    verdict = load_json(verdict_path)
    memory = load_json(memory_path)
    evidence = load_json(evidence_path)
    vault = load_json(vault_path) if Path(vault_path).exists() else {}
    scout = load_json(scout_path) if Path(scout_path).exists() else {}
    refresh_plan = load_json(refresh_plan_path) if Path(refresh_plan_path).exists() else {}
    refresh_apply = load_json(refresh_apply_path) if Path(refresh_apply_path).exists() else {}
    refresh_live_gate = load_json(refresh_live_gate_path) if Path(refresh_live_gate_path).exists() else {}
    refresh_live_run = load_json(refresh_live_run_path) if Path(refresh_live_run_path).exists() else {}
    refresh_live_preflight = load_json(refresh_live_preflight_path) if Path(refresh_live_preflight_path).exists() else {}
    agenda = load_json(agenda_path) if Path(agenda_path).exists() else {}
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_today_surface(
            scenario=scenario,
            verdict=verdict,
            memory=memory,
            evidence=evidence,
            vault_notes=_vault_notes_for_memory(vault),
            scout=scout,
            refresh_plan=refresh_plan,
            refresh_apply=refresh_apply,
            refresh_live_gate=refresh_live_gate,
            refresh_live_run=refresh_live_run,
            refresh_live_preflight=refresh_live_preflight,
            agenda=agenda,
            brief_path=Path(brief_path),
            agenda_surface_path=Path(agenda_surface_path) if agenda_surface_path else None,
            source_refresh_surface_path=Path(source_refresh_surface_path) if source_refresh_surface_path else None,
            archive_manifest_path=Path(archive_manifest_path) if archive_manifest_path else None,
            memory_surface_path=Path(memory_surface_path) if memory_surface_path else None,
            journal_surface_path=Path(journal_surface_path) if journal_surface_path else None,
            task_queue_surface_path=Path(task_queue_surface_path) if task_queue_surface_path else None,
            task_ledger_surface_path=Path(task_ledger_surface_path) if task_ledger_surface_path else None,
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
    vault_notes: list[dict[str, Any]],
    scout: dict[str, Any],
    refresh_plan: dict[str, Any],
    refresh_apply: dict[str, Any],
    refresh_live_gate: dict[str, Any],
    refresh_live_run: dict[str, Any],
    refresh_live_preflight: dict[str, Any],
    agenda: dict[str, Any],
    brief_path: Path,
    agenda_surface_path: Path | None = None,
    source_refresh_surface_path: Path | None = None,
    archive_manifest_path: Path | None = None,
    memory_surface_path: Path | None = None,
    journal_surface_path: Path | None = None,
    task_queue_surface_path: Path | None = None,
    task_ledger_surface_path: Path | None = None,
) -> str:
    market_map = scenario.get("market_map", {})
    primary = verdict.get("primary_next_step") or {}
    scenarios = scenario.get("scenarios", [])
    memory_topics = memory.get("topics", [])
    source_rows = evidence.get("source_status", [])
    gaps = evidence.get("collection_gaps", [])
    generated_at = scenario.get("generated_at", _now())
    scout_recommendations = scout.get("recommendations", []) if scout.get("schema_version") == "daily_scout.v1" else []
    refresh_actions = refresh_plan.get("actions", []) if refresh_plan.get("schema_version") == "source_refresh_plan.v1" else []
    refresh_results = refresh_apply.get("results", []) if refresh_apply.get("schema_version") == "source_refresh_apply.v1" else []
    live_gate_decisions = refresh_live_gate.get("decisions", []) if refresh_live_gate.get("schema_version") == "source_refresh_live_gate.v1" else []
    live_run_execution = refresh_live_run.get("execution", {}) if refresh_live_run.get("schema_version") == "source_refresh_live_run.v1" else {}
    live_preflight_requested = refresh_live_preflight.get("requested_execution", {}) if refresh_live_preflight.get("schema_version") == "source_refresh_live_preflight.v1" else {}
    agenda_primary = agenda.get("primary_topic", {}) if agenda.get("schema_version") == DAILY_BRIEF_AGENDA_SCHEMA_VERSION else {}
    agenda_steps = agenda.get("study_sequence", []) if agenda.get("schema_version") == DAILY_BRIEF_AGENDA_SCHEMA_VERSION else []
    agenda_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(step.get('minutes', ''))}분 · step {esc(step.get('step', ''))}</span>"
        f"<strong>{esc(step.get('title', ''))}</strong>"
        f"<p>{esc(step.get('operator_action', ''))}</p>"
        "</article>"
        for step in agenda_steps[:4]
    ) or "<p>오늘 agenda가 아직 없습니다.</p>"
    scout_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(item.get('action', 'monitor'))} · #{esc(item.get('priority_rank', ''))}</span>"
        f"<strong>{esc(item.get('name', ''))}</strong>"
        f"<p>{esc(item.get('why', ''))}</p>"
        f"<small>질문: {esc(item.get('next_question', ''))}</small>"
        "</article>"
        for item in scout_recommendations[:3]
    ) or "<p>오늘 scout 추천이 아직 없습니다.</p>"
    refresh_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(action.get('priority', 'low'))} · {esc(action.get('cadence', 'review'))}</span>"
        f"<strong>{esc(action.get('source_name', 'source'))}</strong>"
        f"<p>{esc(action.get('reason', ''))}</p>"
        f"<small>{esc(action.get('adapter_id', ''))} · dry-run 계획</small>"
        "</article>"
        for action in refresh_actions[:4]
    ) or "<p>오늘 source refresh plan이 아직 없습니다.</p>"
    refresh_apply_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(result.get('decision', 'review'))} · {esc(result.get('status', 'unknown'))}</span>"
        f"<strong>{esc(result.get('source_name', 'source'))}</strong>"
        f"<p>{esc(result.get('reason', ''))}</p>"
        f"<small>{esc(result.get('adapter_id', ''))} · 실행 여부: {esc('예' if result.get('will_execute') else '아니오')}</small>"
        "</article>"
        for result in refresh_results[:4]
    ) or "<p>오늘 source refresh apply 판정이 아직 없습니다.</p>"
    live_gate_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(decision.get('status', 'review'))} · {esc(decision.get('approval_scope', ''))}</span>"
        f"<strong>{esc(decision.get('id', 'live gate'))}</strong>"
        f"<p>{esc(decision.get('stale_context_guard', ''))}</p>"
        f"<small>{esc(decision.get('copy_ready_response', ''))}</small>"
        "</article>"
        for decision in live_gate_decisions[:3]
    ) or "<p>오늘 승인 대기 중인 live refresh gate가 없습니다.</p>"
    live_run_cards = (
        "<article class='card'>"
        f"<span>{esc(refresh_live_run.get('approval_status', 'unknown'))} · {esc(live_run_execution.get('status', 'unknown'))}</span>"
        "<strong>라이브 실행 증거</strong>"
        f"<p>{esc(refresh_live_run.get('next_step', '아직 live refresh run proof가 없습니다.'))}</p>"
        f"<small>external effect: {esc('yes' if refresh_live_run.get('external_effect_performed') else 'no')} · blockers: {esc(', '.join(live_run_execution.get('blockers', [])) or 'none')}</small>"
        "</article>"
        if refresh_live_run.get("schema_version") == "source_refresh_live_run.v1"
        else "<p>오늘 live refresh run proof가 아직 없습니다.</p>"
    )
    live_preflight_cards = (
        "<article class='card'>"
        f"<span>{esc(refresh_live_preflight.get('status', 'unknown'))} · execute intent: {esc('yes' if live_preflight_requested.get('intend_execute') else 'no')}</span>"
        "<strong>라이브 실행 사전점검</strong>"
        f"<p>{esc(refresh_live_preflight.get('next_step', '아직 live refresh preflight proof가 없습니다.'))}</p>"
        f"<small>external effect: {esc('yes' if refresh_live_preflight.get('external_effect_performed') else 'no')} · blockers: {esc(', '.join(refresh_live_preflight.get('blockers', [])) or 'none')}</small>"
        "</article>"
        if refresh_live_preflight.get("schema_version") == "source_refresh_live_preflight.v1"
        else "<p>오늘 live refresh preflight proof가 아직 없습니다.</p>"
    )
    theme_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(topic.get('name', ''))}</span>"
        f"<strong>{esc('새 변화' if topic.get('changed_since_previous') else '누적 관찰')}</strong>"
        f"<p>{esc(topic.get('latest_summary', ''))}</p>"
        "</article>"
        for topic in memory_topics[:5]
    ) or "<p>아직 누적 주제 기억이 없습니다.</p>"
    vault_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(note.get('topic_name', 'Vault'))}</span>"
        f"<strong>{esc(note.get('title', ''))}</strong>"
        f"<p>{esc(' · '.join(note.get('key_takeaways', [])[:2]))}</p>"
        f"<small>{esc(note.get('source_path', ''))}</small>"
        "</article>"
        for note in _today_vault_notes(vault_notes=vault_notes, memory_topics=memory_topics)[:4]
    ) or "<p>오늘 연결된 vault 원천 노트가 없습니다.</p>"
    path_cards = "".join(
        "<article class='path'>"
        f"<span>{esc(path.get('probability_label', ''))}</span>"
        f"<h3>{esc(path.get('name', ''))}</h3>"
        f"<p>{esc(path.get('beginner_explanation', path.get('summary', '')))}</p>"
        "</article>"
        for path in scenarios[:3]
    )
    source_chips = "".join(
        f"<span class='chip'>{esc(row.get('source_name', 'source'))} · {esc(row.get('freshness_status', 'unknown'))} · {esc(row.get('relevance_label', 'unscored'))}</span>"
        for row in source_rows[:8]
    ) or "<span class='chip'>로컬 seed</span>"
    relevance_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(row.get('source_name', 'source'))}</span>"
        f"<strong>{esc(row.get('relevance_label', 'unscored'))}</strong>"
        f"<p>관련도 {esc(row.get('relevance_score', '0.00'))} · 신선도 {esc(row.get('freshness_status', 'unknown'))}</p>"
        "</article>"
        for row in source_rows[:4]
    )
    gap_items = "".join(f"<li>{esc(_gap_label(gap))}</li>" for gap in gaps[:6]) or "<li>오늘 기록된 차단 이슈는 없습니다.</li>"
    archive_link = (
        f"<a href='{esc(_relative_href(archive_manifest_path))}'>아카이브 manifest</a>"
        if archive_manifest_path
        else "<span>아카이브 manifest 없음</span>"
    )
    memory_link = (
        f"<a href='{esc(_relative_href(memory_surface_path))}'>누적 기억 보기</a>"
        if memory_surface_path
        else "<span>누적 기억 없음</span>"
    )
    journal_link = (
        f"<a href='{esc(_relative_href(journal_surface_path))}'>오늘의 analyst journal</a>"
        if journal_surface_path
        else "<span>Analyst journal 없음</span>"
    )
    task_queue_link = (
        f"<a href='{esc(_relative_href(task_queue_surface_path))}'>다음 analyst tasks</a>"
        if task_queue_surface_path
        else "<span>Analyst tasks 없음</span>"
    )
    task_ledger_link = (
        f"<a href='{esc(_relative_href(task_ledger_surface_path))}'>task ledger</a>"
        if task_ledger_surface_path
        else "<span>Task ledger 없음</span>"
    )
    agenda_link = (
        f"<a href='{esc(_relative_href(agenda_surface_path))}'>오늘 20분 agenda</a>"
        if agenda_surface_path
        else "<span>오늘 agenda 없음</span>"
    )
    source_refresh_link = (
        f"<a href='{esc(_relative_href(source_refresh_surface_path))}'>근거 새로고침 판단</a>"
        if source_refresh_surface_path
        else "<span>근거 새로고침 판단 없음</span>"
    )
    questions = _daily_questions(memory_topics, evidence, vault_notes, scout_recommendations)
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
html,body {{ max-width:100%; overflow-x:hidden; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
main {{ width:100%; max-width:430px; min-width:0; margin:0; padding:16px; }}
header {{ padding:26px 0 16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; overflow-wrap:anywhere; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p {{ margin:0; color:var(--muted); }}
.hero {{ border:1px solid var(--line); border-radius:8px; background:linear-gradient(180deg,#fffefa,#f1f7f3); padding:18px; }}
.primary {{ display:block; margin-top:14px; font-size:24px; color:var(--ink); }}
.section {{ width:100%; min-width:0; overflow:hidden; margin:14px 0; padding:16px; border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.stack {{ display:grid; grid-template-columns:minmax(0,1fr); min-width:0; gap:10px; }}
.card,.path,.question {{ min-width:0; border:1px solid var(--line); border-radius:8px; background:white; padding:14px; }}
.card span,.path span {{ display:block; margin-bottom:7px; color:var(--blue); font-size:12px; font-weight:900; }}
.card strong {{ display:block; margin-bottom:6px; }}
.card p,.card small,.path p,.question p {{ overflow-wrap:anywhere; word-break:break-word; }}
.card small {{ display:block; color:var(--ink); line-height:1.5; }}
.chips {{ display:flex; flex-wrap:wrap; gap:7px; }}
.chip {{ display:inline-flex; min-height:28px; align-items:center; border-radius:999px; padding:3px 10px; background:#eef4fb; color:#1f4f78; font-size:12px; font-weight:800; }}
.links {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:8px; }}
.links a,.links span {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
ul {{ margin:0; padding-left:18px; color:var(--muted); }}
.boundary {{ border-left:4px solid var(--green); }}
@media (max-width:520px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; line-height:1.14; }} .links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Today · {esc(_short_date(generated_at))}</span>
<h1>오늘 시장 5분 브리프</h1>
</header>
<section class="hero">
<span class="eyebrow">가장 먼저 볼 것</span>
<strong class="primary">{esc(primary.get('title', '근거 확인부터 시작'))}</strong>
<p>{esc(primary.get('rationale', market_map.get('beginner_summary', '오늘 브리프를 만들 근거를 점검합니다.')))}</p>
</section>
<section class="section">
<h2>오늘 Scout 추천</h2>
<div class="stack">{scout_cards}</div>
</section>
<section class="section">
<h2>오늘 20분 agenda</h2>
<div class="stack">
<article class="card">
<span>{esc(agenda_primary.get('readiness', 'agenda'))}</span>
<strong>{esc(agenda_primary.get('name', '오늘 agenda 없음'))}</strong>
<p>{esc(agenda_primary.get('why_today', 'Scout 추천을 먼저 생성하세요.'))}</p>
</article>
{agenda_cards}
</div>
</section>
<section class="section">
<h2>오늘 새로고침 계획</h2>
<div class="stack">{refresh_cards}</div>
</section>
<section class="section">
<h2>오늘 실행 판정</h2>
<div class="stack">{refresh_apply_cards}</div>
</section>
<section class="section">
<h2>라이브 새로고침 게이트</h2>
<div class="stack">{live_gate_cards}</div>
</section>
<section class="section">
<h2>라이브 실행 증거</h2>
<div class="stack">{live_run_cards}</div>
</section>
<section class="section">
<h2>라이브 실행 사전점검</h2>
<div class="stack">{live_preflight_cards}</div>
</section>
<section class="section">
<h2>오늘의 주제 기억</h2>
<div class="stack">{theme_cards}</div>
</section>
<section class="section">
<h2>Vault에서 다시 볼 원천 노트</h2>
<div class="stack">{vault_cards}</div>
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
<h2>근거 품질</h2>
<div class="stack">{relevance_cards}</div>
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
{agenda_link}
{source_refresh_link}
{journal_link}
{task_queue_link}
{task_ledger_link}
{memory_link}
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
    refresh_plan_path: str | Path | None = None,
    refresh_apply_path: str | Path | None = None,
    refresh_live_gate_path: str | Path | None = None,
    refresh_live_run_path: str | Path | None = None,
    refresh_live_preflight_path: str | Path | None = None,
    journal_path: str | Path | None = None,
    task_queue_path: str | Path | None = None,
    task_ledger_path: str | Path | None = None,
    vault_compile_path: str | Path | None = None,
    vault_surface_path: str | Path | None = None,
    agenda_path: str | Path | None = None,
    agenda_surface_path: str | Path | None = None,
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
        "source_refresh_plan": refresh_plan_path,
        "source_refresh_apply": refresh_apply_path,
        "source_refresh_live_gate": refresh_live_gate_path,
        "source_refresh_live_run": refresh_live_run_path,
        "source_refresh_live_preflight": refresh_live_preflight_path,
        "journal": journal_path,
        "tasks": task_queue_path,
        "task_ledger": task_ledger_path,
        "vault_compile": vault_compile_path,
        "vault": vault_surface_path,
        "daily_agenda": agenda_path,
        "daily_agenda_surface": agenda_surface_path,
        "brief": brief_path,
        "today": today_path,
    }.items():
        if source is None:
            continue
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


def add_archive_artifacts(
    *,
    manifest_path: str | Path,
    artifacts: dict[str, str | Path],
) -> Path:
    manifest = load_json(manifest_path)
    archive_dir = Path(manifest.get("archive_dir", Path(manifest_path).parent))
    copied = dict(manifest.get("artifacts", {}))
    for label, source in artifacts.items():
        source_path = Path(source)
        if source_path.exists():
            target = archive_dir / source_path.name
            shutil.copy2(source_path, target)
            copied[label] = target.as_posix()
    manifest["artifacts"] = copied
    manifest["updated_at"] = _now()
    return write_json(manifest, manifest_path)


def build_analyst_journal(
    *,
    scenario_path: str | Path,
    verdict_path: str | Path,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    archive_manifest_path: str | Path | None = None,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scenario = load_json(scenario_path)
    verdict = load_json(verdict_path)
    memory = load_json(memory_path)
    evidence = load_json(evidence_path) if Path(evidence_path).exists() else {}
    scout = load_json(scout_path) if Path(scout_path).exists() else {}
    vault = load_json(vault_path) if Path(vault_path).exists() else {}
    archive_manifest = load_json(archive_manifest_path) if archive_manifest_path and Path(archive_manifest_path).exists() else {}
    source_rows = evidence.get("source_status", [])
    memory_topics = memory.get("topics", [])
    changed_topics = [topic for topic in memory_topics if topic.get("changed_since_previous")]
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    primary = verdict.get("primary_next_step") or {}
    weak_sources = [
        row for row in source_rows
        if row.get("freshness_status") in {"stale", "unknown"} or row.get("relevance_label") in {"weak", "unscored"}
    ]
    coverage_sources = sorted({source for topic in memory_topics for source in topic.get("source_names", [])})
    follow_up_questions = _journal_follow_up_questions(
        recommended=recommended,
        memory_topics=memory_topics,
        scenario=scenario,
    )
    role_notes = [
        {
            "role": "source_scout",
            "finding": f"{len(source_rows)}개 source 상태를 확인했고 {len(weak_sources)}개는 약하거나 오래된 근거입니다.",
            "next_check": "live refresh 승인 전에는 cached/sample 근거와 freshness를 분리해서 읽습니다.",
        },
        {
            "role": "market_mapper",
            "finding": scenario.get("market_map", {}).get("beginner_summary", "시장 지도 요약이 아직 약합니다."),
            "next_check": "주제, 기업, 이벤트가 같은 방향인지와 충돌하는지 분리합니다.",
        },
        {
            "role": "skeptic",
            "finding": _journal_skeptic_note(evidence=evidence, memory_topics=memory_topics),
            "next_check": "자료 부족을 매수/매도 결론으로 바꾸지 않습니다.",
        },
        {
            "role": "beginner_tutor",
            "finding": primary.get("rationale", "오늘은 결론보다 시장 흐름 이해를 우선합니다."),
            "next_check": "초보자가 먼저 이해할 단어와 원인-결과 연결을 매일 하나씩 남깁니다.",
        },
        {
            "role": "memory_librarian",
            "finding": f"누적 실행 {memory.get('run_count', 0)}회, vault note {len(_vault_notes_for_memory(vault))}개를 연결했습니다.",
            "next_check": "오늘 질문이 내일 다시 검색 가능한 표현인지 확인합니다.",
        },
    ]
    payload = {
        "schema_version": ANALYST_JOURNAL_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "run_id": scenario.get("run_id", ""),
        "status": _journal_status(source_rows=source_rows, memory_topics=memory_topics),
        "today_focus": {
            "title": primary.get("title", recommended.get("name", "오늘 먼저 볼 주제")),
            "rationale": primary.get("rationale", recommended.get("why", "")),
            "recommended_topic": recommended.get("name", ""),
            "recommended_action": recommended.get("action", ""),
            "confidence": recommended.get("confidence", ""),
        },
        "what_changed": [
            {
                "topic_id": topic.get("topic_id", ""),
                "name": topic.get("name", ""),
                "summary": topic.get("latest_summary", ""),
                "latest_titles": topic.get("latest_titles", [])[:5],
            }
            for topic in changed_topics
        ],
        "stable_observations": [
            {
                "topic_id": topic.get("topic_id", ""),
                "name": topic.get("name", ""),
                "summary": topic.get("latest_summary", ""),
            }
            for topic in memory_topics
            if not topic.get("changed_since_previous")
        ][:5],
        "role_notes": role_notes,
        "source_posture": {
            "source_count": len(source_rows),
            "coverage_sources": coverage_sources,
            "weak_or_stale_count": len(weak_sources),
            "collection_gaps": evidence.get("collection_gaps", []),
        },
        "follow_up_questions": follow_up_questions,
        "linked_artifacts": {
            "scenario": Path(scenario_path).as_posix(),
            "verdict": Path(verdict_path).as_posix(),
            "memory": Path(memory_path).as_posix(),
            "evidence": Path(evidence_path).as_posix(),
            "scout": Path(scout_path).as_posix(),
            "archive_manifest": Path(archive_manifest_path).as_posix() if archive_manifest_path else "",
            "archive_dir": archive_manifest.get("archive_dir", ""),
        },
        "operator_reading_order": [
            "today_focus",
            "what_changed",
            "role_notes",
            "follow_up_questions",
            "linked_artifacts",
        ],
        "policy": "research_only",
        "safety_boundary": [
            "education_and_research_only",
            "no_account_access",
            "no_live_trading",
            "no_discretionary_management",
            "no_unsupported_personalized_recommendation",
        ],
    }
    return payload


def write_analyst_journal(
    *,
    scenario_path: str | Path,
    verdict_path: str | Path,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    archive_manifest_path: str | Path | None = None,
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    surface_output_path: str | Path = DEFAULT_ANALYST_JOURNAL_OUTPUT,
) -> Path:
    payload = build_analyst_journal(
        scenario_path=scenario_path,
        verdict_path=verdict_path,
        memory_path=memory_path,
        evidence_path=evidence_path,
        scout_path=scout_path,
        archive_manifest_path=archive_manifest_path,
        vault_path=vault_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_analyst_journal(payload), encoding="utf-8")
    return target


def validate_analyst_journal_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != ANALYST_JOURNAL_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if not payload.get("today_focus"):
        errors.append("today_focus must not be empty")
    if not payload.get("role_notes"):
        errors.append("role_notes must not be empty")
    if not payload.get("follow_up_questions"):
        errors.append("follow_up_questions must not be empty")
    linked = payload.get("linked_artifacts", {})
    for field in ["scenario", "verdict", "memory", "evidence", "scout"]:
        if not linked.get(field):
            errors.append(f"linked_artifacts.{field} must not be empty")
    if "no_live_trading" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include no_live_trading")
    return errors


def validate_analyst_journal_file(path: str | Path) -> list[str]:
    return validate_analyst_journal_payload(load_json(path))


def render_analyst_journal(payload: dict[str, Any]) -> str:
    focus = payload.get("today_focus", {})
    changed_cards = "".join(
        "<article class='card'>"
        f"<span>변화 감지</span>"
        f"<h3>{esc(item.get('name', ''))}</h3>"
        f"<p>{esc(item.get('summary', ''))}</p>"
        f"<small>{esc(' · '.join(item.get('latest_titles', [])[:3]))}</small>"
        "</article>"
        for item in payload.get("what_changed", [])
    ) or "<p>오늘 새 변화로 판정된 주제는 없습니다. 그래서 결론보다 source freshness와 반복 관찰을 우선합니다.</p>"
    stable_cards = "".join(
        "<article class='card'>"
        f"<span>반복 관찰</span>"
        f"<h3>{esc(item.get('name', ''))}</h3>"
        f"<p>{esc(item.get('summary', ''))}</p>"
        "</article>"
        for item in payload.get("stable_observations", [])[:4]
    ) or "<p>아직 반복 관찰이 충분하지 않습니다.</p>"
    role_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(note.get('role', 'analyst'))}</span>"
        f"<h3>{esc(note.get('finding', ''))}</h3>"
        f"<p>{esc(note.get('next_check', ''))}</p>"
        "</article>"
        for note in payload.get("role_notes", [])
    )
    questions = "".join(f"<li>{esc(question)}</li>" for question in payload.get("follow_up_questions", []))
    artifacts = payload.get("linked_artifacts", {})
    artifact_links = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in artifacts.items()
        if path and label != "archive_dir"
    )
    source = payload.get("source_posture", {})
    gaps = "".join(f"<li>{esc(_gap_label(gap))}</li>" for gap in source.get("collection_gaps", [])) or "<li>기록된 자료 수집 gap 없음</li>"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Analyst Journal</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:28px 0 16px; }}
.eyebrow,.card span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p,small,li {{ color:var(--muted); }}
.hero,.section,.card {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero {{ padding:18px; }}
.section {{ margin:14px 0; padding:16px; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.card {{ background:white; padding:14px; min-width:0; }}
.card h3,.card p,.card small {{ overflow-wrap:anywhere; }}
.metrics {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; margin-top:12px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .grid,.metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Analyst Journal · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>오늘의 개인 애널리스트 작업일지</h1>
<p>브리프의 결론보다, 무엇을 봤고 무엇이 아직 약한지 매일 누적하는 로컬 기록입니다.</p>
</header>
<section class="hero">
<span class="eyebrow">오늘의 초점</span>
<h2>{esc(focus.get('title', '오늘 먼저 볼 주제'))}</h2>
<p>{esc(focus.get('rationale', ''))}</p>
<div class="metrics">
<article class="metric"><span>Status</span><strong>{esc(payload.get('status', 'review'))}</strong></article>
<article class="metric"><span>Sources</span><strong>{esc(source.get('source_count', 0))}</strong></article>
<article class="metric"><span>Weak</span><strong>{esc(source.get('weak_or_stale_count', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>오늘 바뀐 것</h2>
<div class="grid">{changed_cards}</div>
</section>
<section class="section">
<h2>계속 관찰 중인 것</h2>
<div class="grid">{stable_cards}</div>
</section>
<section class="section">
<h2>역할별 메모</h2>
<div class="grid">{role_cards}</div>
</section>
<section class="section">
<h2>내일 이어서 물어볼 질문</h2>
<ul>{questions}</ul>
</section>
<section class="section">
<h2>자료 gap</h2>
<ul>{gaps}</ul>
</section>
<section class="section">
<h2>연결된 산출물</h2>
<div class="links">{artifact_links}</div>
</section>
<section class="section">
<h2>다음 작업 큐</h2>
<div class="links"><a href="tasks.html">내일 이어갈 analyst tasks</a></div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>교육과 리서치, 시뮬레이션용 기록입니다. 계좌 접근, 주문 실행, 일임 운용, 근거 없는 개인화 추천을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def build_analyst_task_queue(
    *,
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    journal = load_json(journal_path)
    memory = load_json(memory_path) if Path(memory_path).exists() else {}
    evidence = load_json(evidence_path) if Path(evidence_path).exists() else {}
    scout = load_json(scout_path) if Path(scout_path).exists() else {}
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    source_posture = journal.get("source_posture", {})
    questions = journal.get("follow_up_questions", [])
    collection_gaps = source_posture.get("collection_gaps", evidence.get("collection_gaps", []))
    weak_count = int(source_posture.get("weak_or_stale_count", 0) or 0)
    task_specs = [
        {
            "role": "source_scout",
            "title": "자료 신선도와 부족한 근거를 먼저 확인",
            "why": _task_source_scout_why(collection_gaps=collection_gaps, weak_count=weak_count),
            "priority": "high" if collection_gaps or weak_count else "medium",
            "inputs": ["reports/evidence/daily-evidence-catalog.json", "reports/daily/source-refresh-plan.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker source-refresh-plan",
            "approval_scope": "local_dry_run_only",
        },
        {
            "role": "market_mapper",
            "title": "오늘 초점 주제를 시장 지도에 다시 연결",
            "why": recommended.get("why", journal.get("today_focus", {}).get("rationale", "오늘 초점과 시장 지도 연결을 점검합니다.")),
            "priority": "high",
            "inputs": ["reports/scenarios/daily-research-sim.json", "reports/scenarios/daily-research-verdict.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance today",
            "approval_scope": "local_render_only",
        },
        {
            "role": "skeptic",
            "title": "가장 약한 결론을 반대 근거로 공격",
            "why": _task_skeptic_why(journal=journal),
            "priority": "high",
            "inputs": ["reports/memory/analyst-journal.json", "reports/evidence/daily-evidence-catalog.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance journal",
            "approval_scope": "local_render_only",
        },
        {
            "role": "beginner_tutor",
            "title": "초보자가 이해할 질문 하나를 쉬운 언어로 풀기",
            "why": questions[0] if questions else "오늘 브리프를 처음 보는 사용자가 이해할 출발 질문을 만듭니다.",
            "priority": "medium",
            "inputs": ["reports/product/today.html", "reports/product/journal.html"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance query \"오늘 먼저 볼 주제\"",
            "approval_scope": "local_query_only",
        },
        {
            "role": "memory_librarian",
            "title": "내일 다시 찾을 수 있게 질문과 원천을 정리",
            "why": f"누적 실행 {memory.get('run_count', 0)}회를 다음 질문과 연결합니다.",
            "priority": "medium",
            "inputs": ["reports/memory/topic-memory.json", "reports/vault/compile.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance memory",
            "approval_scope": "local_render_only",
        },
        {
            "role": "publisher",
            "title": "폰에서 볼 표면과 dry-run 알림 상태 점검",
            "why": "오늘 산출물이 폰에서 읽히고 notification은 dry-run 상태인지 확인합니다.",
            "priority": "medium",
            "inputs": ["reports/product/today.html", "reports/product/tasks.html", "reports/notifications/latest.json"],
            "suggested_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance notify --dry-run",
            "approval_scope": "local_dry_run_only",
        },
    ]
    tasks = []
    for index, spec in enumerate(task_specs, start=1):
        tasks.append({
            "task_id": f"AT-{index:03d}",
            "role": spec["role"],
            "title": spec["title"],
            "why": spec["why"],
            "priority": spec["priority"],
            "status": "queued",
            "autonomy_level": "autonomous_local",
            "approval_scope": spec["approval_scope"],
            "external_effect_allowed": False,
            "requires_operator_approval": False,
            "inputs": spec["inputs"],
            "suggested_command": spec["suggested_command"],
            "stop_condition": "write_or_refresh_local_artifact_without_external_effect",
        })
    live_task = _maybe_live_refresh_task(journal=journal)
    if live_task:
        tasks.append(live_task)
    payload = {
        "schema_version": ANALYST_TASK_QUEUE_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "run_id": journal.get("run_id", ""),
        "status": "queued",
        "source_journal": Path(journal_path).as_posix(),
        "task_count": len(tasks),
        "tasks": tasks,
        "reading_order": ["high priority", "source_scout", "skeptic", "market_mapper", "beginner_tutor", "memory_librarian", "publisher"],
        "policy": "research_only",
        "safety_boundary": [
            "queued_tasks_do_not_execute",
            "no_account_access",
            "no_live_trading",
            "no_discretionary_management",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_analyst_task_queue(
    *,
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    memory_path: str | Path = DEFAULT_TOPIC_MEMORY_OUTPUT,
    evidence_path: str | Path = DEFAULT_DAILY_EVIDENCE_OUTPUT,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    artifact_output_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    surface_output_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_OUTPUT,
) -> Path:
    payload = build_analyst_task_queue(
        journal_path=journal_path,
        memory_path=memory_path,
        evidence_path=evidence_path,
        scout_path=scout_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_analyst_task_queue(payload), encoding="utf-8")
    return target


def validate_analyst_task_queue_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != ANALYST_TASK_QUEUE_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    tasks = payload.get("tasks", [])
    if not tasks:
        errors.append("tasks must not be empty")
    for index, task in enumerate(tasks):
        for field in ["task_id", "role", "title", "why", "priority", "status", "approval_scope", "external_effect_allowed", "inputs", "suggested_command"]:
            if field not in task:
                errors.append(f"tasks[{index}] missing {field}")
        if task.get("status") != "queued":
            errors.append(f"tasks[{index}] status must be queued")
        if task.get("external_effect_allowed") is True and task.get("requires_operator_approval") is not True:
            errors.append(f"tasks[{index}] external effects require operator approval")
    if "queued_tasks_do_not_execute" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include queued_tasks_do_not_execute")
    return errors


def validate_analyst_task_queue_file(path: str | Path) -> list[str]:
    return validate_analyst_task_queue_payload(load_json(path))


def render_analyst_task_queue(payload: dict[str, Any]) -> str:
    high_count = sum(1 for task in payload.get("tasks", []) if task.get("priority") == "high")
    task_cards = "".join(
        "<article class='task'>"
        f"<span>{esc(task.get('task_id', ''))} · {esc(task.get('role', ''))} · {esc(task.get('priority', ''))}</span>"
        f"<h2>{esc(task.get('title', ''))}</h2>"
        f"<p>{esc(task.get('why', ''))}</p>"
        f"<small>scope: {esc(task.get('approval_scope', ''))} · external effect: {esc('yes' if task.get('external_effect_allowed') else 'no')}</small>"
        f"<code>{esc(task.get('suggested_command', ''))}</code>"
        "</article>"
        for task in payload.get("tasks", [])
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Analyst Tasks</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
.eyebrow,.task span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.task {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.metric,.task {{ background:white; padding:14px; }}
.metric strong {{ display:block; font-size:24px; }}
.stack {{ display:grid; grid-template-columns:1fr; gap:10px; }}
code {{ display:block; margin-top:10px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Analyst Tasks · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>내일 이어갈 analyst 작업 큐</h1>
<p>실행 명령이 아니라, 로컬 개인 애널리스트가 다음에 처리할 역할별 작업 목록입니다.</p>
</header>
<section class="hero">
<div class="metrics">
<article class="metric"><span>Total</span><strong>{esc(payload.get('task_count', 0))}</strong></article>
<article class="metric"><span>High</span><strong>{esc(high_count)}</strong></article>
<article class="metric"><span>Effects</span><strong>0</strong></article>
</div>
</section>
<section class="section">
<h2>역할별 큐</h2>
<div class="stack">{task_cards}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 큐는 작업을 실행하지 않습니다. live network, host write, notification send, 계좌/주문/일임 행위는 별도 승인 게이트 없이는 허용하지 않습니다.</p>
</section>
<section class="section">
<h2>작업 이력</h2>
<p><a href="task-ledger.html">task ledger에서 완료, 이월, 보류 상태 보기</a></p>
</section>
</main>
</body>
</html>
"""


def build_analyst_task_ledger(
    *,
    task_queue_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    previous_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    status_apply_path: str | Path | None = DEFAULT_ANALYST_TASK_STATUS_APPLY,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    queue = load_json(task_queue_path)
    previous = load_json(previous_ledger_path) if Path(previous_ledger_path).exists() else {}
    status_apply = load_json(status_apply_path) if status_apply_path and Path(status_apply_path).exists() else {}
    overrides = _task_status_overrides(status_apply)
    generated = (generated_at or datetime.now(timezone.utc)).isoformat()
    previous_entries = previous.get("entries", []) if previous.get("schema_version") == ANALYST_TASK_LEDGER_SCHEMA_VERSION else []
    previous_by_fingerprint = {
        entry.get("fingerprint", ""): entry
        for entry in previous_entries
        if entry.get("fingerprint")
    }
    current_entries = []
    for task in queue.get("tasks", []):
        fingerprint = _task_fingerprint(task)
        prior = previous_by_fingerprint.get(fingerprint, {})
        override = overrides.get(task.get("task_id", ""))
        status = override.get("status") if override else _ledger_status_for_task(task=task, prior=prior)
        current_entries.append({
            "ledger_id": f"{queue.get('run_id', 'daily')}-{task.get('task_id', '')}",
            "task_id": task.get("task_id", ""),
            "fingerprint": fingerprint,
            "role": task.get("role", ""),
            "title": task.get("title", ""),
            "priority": task.get("priority", ""),
            "status": status,
            "previous_status": prior.get("status", ""),
            "first_seen_at": prior.get("first_seen_at", generated),
            "last_seen_at": generated,
            "run_id": queue.get("run_id", ""),
            "approval_scope": task.get("approval_scope", ""),
            "external_effect_allowed": bool(task.get("external_effect_allowed")),
            "requires_operator_approval": bool(task.get("requires_operator_approval")),
            "suggested_command": task.get("suggested_command", ""),
            "stop_condition": task.get("stop_condition", ""),
            "operator_note": override.get("note") if override and override.get("note") else _ledger_note_for_task(task=task, status=status),
            "operator_override": override or {},
        })
    current_fingerprints = {entry["fingerprint"] for entry in current_entries}
    retired_entries = []
    for entry in previous_entries:
        if entry.get("fingerprint") not in current_fingerprints:
            retired = dict(entry)
            retired["status"] = "retired_not_in_current_queue"
            retired["previous_status"] = entry.get("status", "")
            retired["last_seen_at"] = generated
            retired["operator_note"] = "이전 queue에는 있었지만 현재 queue에는 없습니다. 완료됐는지, 필요 없어졌는지 archive에서 확인하세요."
            retired_entries.append(retired)
    entries = current_entries + retired_entries[:12]
    summary = _ledger_summary(entries)
    return {
        "schema_version": ANALYST_TASK_LEDGER_SCHEMA_VERSION,
        "generated_at": generated,
        "run_id": queue.get("run_id", ""),
        "source_task_queue": Path(task_queue_path).as_posix(),
        "previous_ledger": Path(previous_ledger_path).as_posix() if Path(previous_ledger_path).exists() else "",
        "entry_count": len(entries),
        "summary": summary,
        "entries": entries,
        "policy": "research_only",
        "safety_boundary": [
            "ledger_records_status_only",
            "does_not_execute_tasks",
            "no_account_access",
            "no_live_trading",
            "external_effects_require_separate_gate",
        ],
    }


def write_analyst_task_ledger(
    *,
    task_queue_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    previous_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    status_apply_path: str | Path | None = DEFAULT_ANALYST_TASK_STATUS_APPLY,
    artifact_output_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    surface_output_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_OUTPUT,
) -> Path:
    payload = build_analyst_task_ledger(
        task_queue_path=task_queue_path,
        previous_ledger_path=previous_ledger_path,
        status_apply_path=status_apply_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_analyst_task_ledger(payload), encoding="utf-8")
    return target


def parse_task_status_response(response: str) -> dict[str, Any]:
    parts = response.strip().split(maxsplit=2)
    if len(parts) < 2:
        raise ValueError("response must look like: AT-001 complete [note]")
    task_id = parts[0].strip()
    action = parts[1].strip().lower()
    note = parts[2].strip().strip('"') if len(parts) > 2 else ""
    status_map = {
        "complete": "completed",
        "completed": "completed",
        "carry": "carried",
        "carried": "carried",
        "defer": "deferred",
        "deferred": "deferred",
        "block": "blocked_by_operator",
        "blocked": "blocked_by_operator",
    }
    if not task_id.startswith("AT-"):
        raise ValueError("task id must start with AT-")
    if action not in status_map:
        raise ValueError("action must be complete, carry, defer, or block")
    return {
        "schema_version": "personal_analyst_task_response.v1",
        "recorded_at": _now(),
        "task_id": task_id,
        "action": action,
        "status": status_map[action],
        "note": note,
        "external_effect_performed": False,
    }


def record_task_status_response(
    *,
    response: str,
    responses_path: str | Path = DEFAULT_ANALYST_TASK_RESPONSES,
) -> Path:
    payload = parse_task_status_response(response)
    target = Path(responses_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return target


def build_task_status_apply(
    *,
    ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    responses_path: str | Path = DEFAULT_ANALYST_TASK_RESPONSES,
    output_path: str | Path = DEFAULT_ANALYST_TASK_STATUS_APPLY,
) -> dict[str, Any]:
    ledger = load_json(ledger_path)
    responses = _load_task_responses(responses_path)
    valid_task_ids = {entry.get("task_id") for entry in ledger.get("entries", [])}
    applied = []
    ignored = []
    for response in responses:
        task_id = response.get("task_id", "")
        if task_id in valid_task_ids:
            applied.append(response)
        else:
            ignored.append({**response, "reason": "task_id_not_in_current_ledger"})
    latest_by_task: dict[str, dict[str, Any]] = {}
    for response in applied:
        latest_by_task[response["task_id"]] = response
    payload = {
        "schema_version": ANALYST_TASK_STATUS_APPLY_SCHEMA_VERSION,
        "generated_at": _now(),
        "ledger_path": Path(ledger_path).as_posix(),
        "responses_path": Path(responses_path).as_posix(),
        "applied_count": len(latest_by_task),
        "ignored_count": len(ignored),
        "applied": list(latest_by_task.values()),
        "ignored": ignored,
        "external_effect_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "local_status_update_only",
            "does_not_execute_tasks",
            "no_live_trading",
            "no_account_access",
        ],
    }
    write_json(payload, output_path)
    return payload


def build_morning_control_packet(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    task_queue_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    notification_path: str | Path = DEFAULT_NOTIFICATION_OUTPUT,
    runtime_doctor_path: str | Path = DEFAULT_RUNTIME_DOCTOR_OUTPUT,
    today_path: str | Path = DEFAULT_TODAY_OUTPUT,
    readiness_surface_path: str | Path = DEFAULT_DAILY_READINESS_SURFACE,
    scheduler_surface_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_SURFACE,
    source_refresh_surface_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE,
    vault_surface_path: str | Path = DEFAULT_VAULT_SURFACE_OUTPUT,
    agenda_surface_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_SURFACE,
    agenda_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    memory_surface_path: str | Path = DEFAULT_MEMORY_OUTPUT,
    journal_surface_path: str | Path = DEFAULT_ANALYST_JOURNAL_OUTPUT,
    task_queue_surface_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_OUTPUT,
    task_ledger_surface_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_OUTPUT,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    scout = _load_optional_json(scout_path)
    journal = _load_optional_json(journal_path)
    queue = _load_optional_json(task_queue_path)
    ledger = _load_optional_json(task_ledger_path)
    live_gate = _load_optional_json(refresh_live_gate_path)
    live_run = _load_optional_json(refresh_live_run_path)
    preflight = _load_optional_json(refresh_live_preflight_path)
    notification = _load_optional_json(notification_path)
    doctor = _load_optional_json(runtime_doctor_path)
    agenda = _load_optional_json(agenda_path)
    recommended = scout.get("recommended_topic", {}) if scout.get("schema_version") == "daily_scout.v1" else {}
    agenda_primary = agenda.get("primary_topic", {}) if agenda.get("schema_version") == DAILY_BRIEF_AGENDA_SCHEMA_VERSION else {}
    focus = journal.get("today_focus", {})
    ledger_summary = ledger.get("summary", {})
    pending_decisions = _morning_pending_decisions(live_gate=live_gate, live_run=live_run, preflight=preflight)
    command_bar = _morning_command_bar(ledger=ledger, pending_decisions=pending_decisions)
    status = _morning_status(
        pending_decisions=pending_decisions,
        ledger_summary=ledger_summary,
        doctor=doctor,
    )
    payload = {
        "schema_version": MORNING_CONTROL_SCHEMA_VERSION,
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "status": status,
        "run_id": journal.get("run_id", scout.get("run_id", "")),
        "read_first": {
            "title": agenda_primary.get("name", focus.get("title", recommended.get("name", "오늘 브리프 먼저 확인"))),
            "reason": agenda_primary.get("why_today", focus.get("rationale", recommended.get("why", ""))),
            "recommended_topic": agenda_primary.get("name", recommended.get("name", focus.get("recommended_topic", ""))),
            "confidence": agenda_primary.get("confidence", recommended.get("confidence", focus.get("confidence", ""))),
            "next_question": agenda_primary.get("next_question", recommended.get("next_question", "")),
        },
        "task_state": {
            "total": ledger.get("entry_count", queue.get("task_count", 0)),
            "ready": ledger_summary.get("ready_for_local_work", 0),
            "carried": ledger_summary.get("carried", 0),
            "completed": ledger_summary.get("completed", 0),
            "deferred": ledger_summary.get("deferred", 0),
            "blocked": ledger_summary.get("blocked_requires_approval", 0) + ledger_summary.get("blocked_by_operator", 0),
            "top_tasks": _morning_top_tasks(ledger=ledger, queue=queue),
        },
        "pending_decisions": pending_decisions,
        "command_bar": command_bar,
        "phone_links": {
            "morning": DEFAULT_MORNING_CONTROL_SURFACE.as_posix(),
            "readiness": Path(readiness_surface_path).as_posix(),
            "scheduler": Path(scheduler_surface_path).as_posix(),
            "source_refresh": Path(source_refresh_surface_path).as_posix(),
            "today": Path(today_path).as_posix(),
            "agenda": Path(agenda_surface_path).as_posix(),
            "vault": Path(vault_surface_path).as_posix(),
            "journal": Path(journal_surface_path).as_posix(),
            "tasks": Path(task_queue_surface_path).as_posix(),
            "task_ledger": Path(task_ledger_surface_path).as_posix(),
            "memory": Path(memory_surface_path).as_posix(),
        },
        "runtime": {
            "notification_status": notification.get("delivery_status", "missing"),
            "notification_dry_run": notification.get("dry_run", True),
            "runtime_doctor_status": doctor.get("status", "missing"),
            "runtime_warn_count": doctor.get("warn_count", 0),
            "runtime_fail_count": doctor.get("fail_count", 0),
        },
        "artifact_inputs": {
            "scout": Path(scout_path).as_posix(),
            "journal": Path(journal_path).as_posix(),
            "task_queue": Path(task_queue_path).as_posix(),
            "task_ledger": Path(task_ledger_path).as_posix(),
            "source_refresh_live_gate": Path(refresh_live_gate_path).as_posix(),
            "source_refresh_live_run": Path(refresh_live_run_path).as_posix(),
            "source_refresh_live_preflight": Path(refresh_live_preflight_path).as_posix(),
            "notification": Path(notification_path).as_posix(),
            "runtime_doctor": Path(runtime_doctor_path).as_posix(),
            "agenda": Path(agenda_path).as_posix(),
        },
        "external_effect_performed": False,
        "host_write_performed": False,
        "policy": "research_only",
        "safety_boundary": [
            "control_packet_reads_existing_artifacts_only",
            "does_not_execute_tasks",
            "does_not_send_notifications",
            "does_not_write_host_scheduler",
            "no_account_access",
            "no_live_trading",
            "external_effects_require_separate_gate",
        ],
    }
    return payload


def write_morning_control_packet(
    *,
    scout_path: str | Path = DEFAULT_DAILY_SCOUT_OUTPUT,
    journal_path: str | Path = DEFAULT_ANALYST_JOURNAL_ARTIFACT,
    task_queue_path: str | Path = DEFAULT_ANALYST_TASK_QUEUE_ARTIFACT,
    task_ledger_path: str | Path = DEFAULT_ANALYST_TASK_LEDGER_ARTIFACT,
    refresh_live_gate_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_GATE_OUTPUT,
    refresh_live_run_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_RUN_OUTPUT,
    refresh_live_preflight_path: str | Path = DEFAULT_SOURCE_REFRESH_LIVE_PREFLIGHT_OUTPUT,
    notification_path: str | Path = DEFAULT_NOTIFICATION_OUTPUT,
    runtime_doctor_path: str | Path = DEFAULT_RUNTIME_DOCTOR_OUTPUT,
    readiness_surface_path: str | Path = DEFAULT_DAILY_READINESS_SURFACE,
    scheduler_surface_path: str | Path = DEFAULT_SCHEDULER_OPERATIONS_SURFACE,
    source_refresh_surface_path: str | Path = DEFAULT_SOURCE_REFRESH_BRIEF_SURFACE,
    agenda_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_OUTPUT,
    agenda_surface_path: str | Path = DEFAULT_DAILY_BRIEF_AGENDA_SURFACE,
    artifact_output_path: str | Path = DEFAULT_MORNING_CONTROL_OUTPUT,
    surface_output_path: str | Path = DEFAULT_MORNING_CONTROL_SURFACE,
) -> Path:
    payload = build_morning_control_packet(
        scout_path=scout_path,
        journal_path=journal_path,
        task_queue_path=task_queue_path,
        task_ledger_path=task_ledger_path,
        refresh_live_gate_path=refresh_live_gate_path,
        refresh_live_run_path=refresh_live_run_path,
        refresh_live_preflight_path=refresh_live_preflight_path,
        notification_path=notification_path,
        runtime_doctor_path=runtime_doctor_path,
        readiness_surface_path=readiness_surface_path,
        scheduler_surface_path=scheduler_surface_path,
        source_refresh_surface_path=source_refresh_surface_path,
        agenda_path=agenda_path,
        agenda_surface_path=agenda_surface_path,
    )
    write_json(payload, artifact_output_path)
    target = Path(surface_output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_morning_control_packet(payload), encoding="utf-8")
    return target


def validate_morning_control_packet_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != MORNING_CONTROL_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    if payload.get("host_write_performed") is not False:
        errors.append("host_write_performed must be false")
    if payload.get("status") not in {"ready", "operator_review", "blocked"}:
        errors.append(f"invalid status {payload.get('status')}")
    if not payload.get("read_first", {}).get("title"):
        errors.append("read_first.title must not be empty")
    if not payload.get("phone_links", {}).get("today"):
        errors.append("phone_links.today must not be empty")
    if "does_not_execute_tasks" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_execute_tasks")
    forbidden_fragments = [" --send", "--confirm-host-write", "--execute", "launchctl bootstrap"]
    for index, item in enumerate(payload.get("command_bar", [])):
        command = item.get("command", "")
        if any(fragment in command for fragment in forbidden_fragments):
            errors.append(f"command_bar[{index}] includes gated execution fragment")
        if item.get("external_effect_performed") is not False:
            errors.append(f"command_bar[{index}] external_effect_performed must be false")
    for index, decision in enumerate(payload.get("pending_decisions", [])):
        if not decision.get("copy_ready_response"):
            errors.append(f"pending_decisions[{index}] missing copy_ready_response")
        if decision.get("agent_will_run") and decision.get("approval_required") is not True:
            errors.append(f"pending_decisions[{index}] runnable action requires approval flag")
    return errors


def validate_morning_control_packet_file(path: str | Path) -> list[str]:
    return validate_morning_control_packet_payload(load_json(path))


def render_morning_control_packet(payload: dict[str, Any]) -> str:
    read_first = payload.get("read_first", {})
    task_state = payload.get("task_state", {})
    runtime = payload.get("runtime", {})
    decision_cards = "".join(
        "<article class='card warn'>"
        f"<span>{esc(decision.get('id', 'decision'))} · {esc(decision.get('risk_level', 'risk'))}</span>"
        f"<h2>{esc(decision.get('title', '승인 필요'))}</h2>"
        f"<p>{esc(decision.get('why', ''))}</p>"
        f"<code>{esc(decision.get('copy_ready_response', ''))}</code>"
        f"<small>{esc(decision.get('stale_context_guard', ''))}</small>"
        "</article>"
        for decision in payload.get("pending_decisions", [])
    ) or "<p>지금 사람이 승인해야 할 외부효과 결정은 없습니다.</p>"
    task_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(task.get('task_id', ''))} · {esc(task.get('status', ''))} · {esc(task.get('priority', ''))}</span>"
        f"<h2>{esc(task.get('title', ''))}</h2>"
        f"<p>{esc(task.get('operator_note', task.get('why', '')))}</p>"
        "</article>"
        for task in task_state.get("top_tasks", [])
    ) or "<p>오늘 표시할 analyst task가 없습니다.</p>"
    command_cards = "".join(
        "<article class='command'>"
        f"<span>{esc(item.get('label', 'command'))}</span>"
        f"<code>{esc(item.get('command', ''))}</code>"
        f"<small>{esc(item.get('effect', 'local only'))}</small>"
        "</article>"
        for item in payload.get("command_bar", [])
    ) or "<p>오늘 복사할 로컬 응답 명령이 없습니다.</p>"
    links = payload.get("phone_links", {})
    link_cards = "".join(
        f"<a href='{esc(_relative_href(Path(path)))}'>{esc(label)}</a>"
        for label, path in links.items()
        if path and label != "morning"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Morning Control</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; --warn:#9a6a1d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:28px 0 16px; }}
.eyebrow,.card span,.command span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.card,.command {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.stack {{ display:grid; grid-template-columns:1fr; gap:10px; }}
.card,.command {{ background:white; padding:14px; min-width:0; }}
.warn {{ border-color:#d7b36a; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin-top:12px; }}
.metric {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; }}
.metric strong {{ display:block; font-size:24px; }}
code {{ display:block; margin-top:8px; padding:10px; border-radius:8px; background:#f1f5f9; color:#24415f; white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
.links {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.links a {{ border:1px solid var(--line); border-radius:8px; background:white; padding:12px; overflow-wrap:anywhere; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .grid,.metrics,.links {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Morning · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>아침 analyst 관제판</h1>
<p>오늘 무엇을 먼저 읽고, 무엇을 승인하지 말아야 하며, 어떤 짧은 응답으로 작업 상태를 닫을지 보는 운영면입니다.</p>
</header>
<section class="hero">
<span class="eyebrow">먼저 볼 것</span>
<h2>{esc(read_first.get('title', '오늘 브리프'))}</h2>
<p>{esc(read_first.get('reason', ''))}</p>
<div class="metrics">
<article class="metric"><span>Status</span><strong>{esc(payload.get('status', 'ready'))}</strong></article>
<article class="metric"><span>Carried</span><strong>{esc(task_state.get('carried', 0))}</strong></article>
<article class="metric"><span>Blocked</span><strong>{esc(task_state.get('blocked', 0))}</strong></article>
<article class="metric"><span>Runtime</span><strong>{esc(runtime.get('runtime_doctor_status', 'missing'))}</strong></article>
</div>
</section>
<section class="section">
<h2>결정 필요</h2>
<div class="stack">{decision_cards}</div>
</section>
<section class="section">
<h2>오늘 닫을 analyst 작업</h2>
<div class="grid">{task_cards}</div>
</section>
<section class="section">
<h2>복사 가능한 응답</h2>
<div class="stack">{command_cards}</div>
</section>
<section class="section">
<h2>폰에서 열기</h2>
<div class="links">{link_cards}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 관제판은 기존 산출물을 읽고 표시할 뿐입니다. queued task 실행, live network, host write, notification send, 계좌/주문/일임 행위는 별도 승인 게이트 없이는 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def validate_task_status_apply_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != ANALYST_TASK_STATUS_APPLY_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    if payload.get("external_effect_performed") is not False:
        errors.append("external_effect_performed must be false")
    allowed = {"completed", "carried", "deferred", "blocked_by_operator"}
    for index, response in enumerate(payload.get("applied", [])):
        if response.get("status") not in allowed:
            errors.append(f"applied[{index}] invalid status {response.get('status')}")
        if not response.get("task_id", "").startswith("AT-"):
            errors.append(f"applied[{index}] invalid task_id")
    if "does_not_execute_tasks" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_execute_tasks")
    return errors


def validate_task_status_apply_file(path: str | Path) -> list[str]:
    return validate_task_status_apply_payload(load_json(path))


def validate_analyst_task_ledger_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != ANALYST_TASK_LEDGER_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    entries = payload.get("entries", [])
    if payload.get("entry_count", 0) != len(entries):
        errors.append("entry_count must match entries length")
    if not entries:
        errors.append("entries must not be empty")
    allowed_statuses = {"ready_for_local_work", "carried", "blocked_requires_approval", "retired_not_in_current_queue", "completed", "deferred", "blocked_by_operator"}
    for index, entry in enumerate(entries):
        for field in ["ledger_id", "task_id", "fingerprint", "role", "title", "priority", "status", "first_seen_at", "last_seen_at", "operator_note"]:
            if field not in entry:
                errors.append(f"entries[{index}] missing {field}")
        if entry.get("status") not in allowed_statuses:
            errors.append(f"entries[{index}] invalid status {entry.get('status')}")
        if entry.get("external_effect_allowed") is True and entry.get("requires_operator_approval") is not True:
            errors.append(f"entries[{index}] external effects require operator approval")
    if "does_not_execute_tasks" not in payload.get("safety_boundary", []):
        errors.append("safety_boundary must include does_not_execute_tasks")
    return errors


def validate_analyst_task_ledger_file(path: str | Path) -> list[str]:
    return validate_analyst_task_ledger_payload(load_json(path))


def render_analyst_task_ledger(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    cards = "".join(
        "<article class='entry'>"
        f"<span>{esc(entry.get('status', ''))} · {esc(entry.get('role', ''))} · {esc(entry.get('priority', ''))}</span>"
        f"<h2>{esc(entry.get('title', ''))}</h2>"
        f"<p>{esc(entry.get('operator_note', ''))}</p>"
        f"<small>first: {esc(_short_date(entry.get('first_seen_at', '')))} · last: {esc(_short_date(entry.get('last_seen_at', '')))} · scope: {esc(entry.get('approval_scope', ''))}</small>"
        "</article>"
        for entry in payload.get("entries", [])
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Task Ledger</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ width:100%; max-width:760px; margin:0 auto; padding:18px; }}
.eyebrow,.entry span {{ color:var(--green); font-size:12px; font-weight:900; text-transform:uppercase; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 8px; font-size:18px; }}
p,small {{ color:var(--muted); }}
.hero,.section,.entry {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.hero,.section {{ padding:16px; margin:14px 0; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
.metric,.entry {{ background:white; padding:14px; }}
.metric strong {{ display:block; font-size:24px; }}
.stack {{ display:grid; grid-template-columns:1fr; gap:10px; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .metrics {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Task Ledger · {esc(_short_date(payload.get('generated_at', '')))}</span>
<h1>analyst 작업 이력</h1>
<p>오늘 queue가 어제와 어떻게 이어지는지, 무엇이 이월되고 무엇이 승인 대기인지 보는 기록입니다.</p>
</header>
<section class="hero">
<div class="metrics">
<article class="metric"><span>Total</span><strong>{esc(payload.get('entry_count', 0))}</strong></article>
<article class="metric"><span>Ready</span><strong>{esc(summary.get('ready_for_local_work', 0))}</strong></article>
<article class="metric"><span>Carried</span><strong>{esc(summary.get('carried', 0))}</strong></article>
<article class="metric"><span>Done</span><strong>{esc(summary.get('completed', 0))}</strong></article>
<article class="metric"><span>Blocked</span><strong>{esc(summary.get('blocked_requires_approval', 0) + summary.get('blocked_by_operator', 0))}</strong></article>
</div>
</section>
<section class="section">
<h2>상태별 작업</h2>
<div class="stack">{cards}</div>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 ledger는 상태만 기록합니다. queued task 실행, live network, host write, notification send, 계좌/주문/일임 행위는 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


def build_memory_index(
    *,
    memory_path: str | Path = "reports/memory/topic-memory.json",
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = "reports/evidence/daily-evidence-catalog.json",
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
) -> dict[str, Any]:
    memory = load_json(memory_path)
    evidence = load_json(evidence_path) if Path(evidence_path).exists() else {}
    vault = load_json(vault_path) if Path(vault_path).exists() else {}
    archive_manifests = []
    for manifest_path in sorted(Path(archive_root).glob("*/manifest.json"), reverse=True):
        try:
            archive_manifests.append(load_json(manifest_path))
        except json.JSONDecodeError:
            continue
    topic_rows = []
    for topic in memory.get("topics", []):
        topic_rows.append({
            "topic_id": topic.get("topic_id", ""),
            "name": topic.get("name", ""),
            "latest_summary": topic.get("latest_summary", ""),
            "daily_questions": topic.get("daily_questions", []),
            "latest_titles": topic.get("latest_titles", []),
            "source_names": topic.get("source_names", []),
            "collection_gaps": topic.get("collection_gaps", []),
            "changed_since_previous": topic.get("changed_since_previous", False),
        })
    return {
        "schema_version": MEMORY_INDEX_SCHEMA_VERSION,
        "generated_at": _now(),
        "memory_path": Path(memory_path).as_posix(),
        "archive_root": Path(archive_root).as_posix(),
        "run_count": memory.get("run_count", 0),
        "topic_count": len(topic_rows),
        "topics": topic_rows,
        "recent_runs": list(reversed(memory.get("runs", [])[-10:])),
        "archives": archive_manifests[:12],
        "source_relevance": [
            {
                "source_name": row.get("source_name", ""),
                "freshness_status": row.get("freshness_status", ""),
                "relevance_score": row.get("relevance_score", "0.00"),
                "relevance_label": row.get("relevance_label", "unscored"),
                "item_count": row.get("item_count", "0"),
            }
            for row in evidence.get("source_status", [])
        ],
        "vault_path": Path(vault_path).as_posix(),
        "vault_notes": _vault_notes_for_memory(vault),
        "policy": "research_only",
    }


def write_memory_surface(
    *,
    memory_path: str | Path = "reports/memory/topic-memory.json",
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = "reports/evidence/daily-evidence-catalog.json",
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    index_output_path: str | Path = DEFAULT_MEMORY_INDEX_OUTPUT,
    output_path: str | Path = DEFAULT_MEMORY_OUTPUT,
) -> Path:
    index = build_memory_index(memory_path=memory_path, archive_root=archive_root, evidence_path=evidence_path, vault_path=vault_path)
    write_json(index, index_output_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_memory_surface(index), encoding="utf-8")
    return target


def build_memory_query(
    *,
    query: str,
    memory_path: str | Path = "reports/memory/topic-memory.json",
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = "reports/evidence/daily-evidence-catalog.json",
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    limit: int = 5,
) -> dict[str, Any]:
    index = build_memory_index(memory_path=memory_path, archive_root=archive_root, evidence_path=evidence_path, vault_path=vault_path)
    tokens = _query_tokens(query)
    matched_topics = []
    for topic in index.get("topics", []):
        haystacks = [
            topic.get("name", ""),
            topic.get("latest_summary", ""),
            " ".join(topic.get("daily_questions", [])),
            " ".join(topic.get("latest_titles", [])),
            " ".join(topic.get("source_names", [])),
            " ".join(topic.get("collection_gaps", [])),
        ]
        score = _match_score(tokens, haystacks)
        if score > 0:
            matched_topics.append({
                "topic_id": topic.get("topic_id", ""),
                "name": topic.get("name", ""),
                "score": round(score, 3),
                "summary": topic.get("latest_summary", ""),
                "source_names": topic.get("source_names", []),
                "latest_titles": topic.get("latest_titles", [])[:5],
                "questions": topic.get("daily_questions", [])[:4],
                "why_matched": _match_reasons(tokens, haystacks),
            })
    matched_topics.sort(key=lambda row: (-row["score"], row["name"]))

    matched_archives = []
    for manifest in index.get("archives", []):
        haystacks = [
            manifest.get("run_id", ""),
            manifest.get("generated_at", ""),
            " ".join(str(value) for value in manifest.get("artifacts", {}).values()),
        ]
        score = _match_score(tokens, haystacks)
        if score > 0 or matched_topics:
            matched_archives.append({
                "run_id": manifest.get("run_id", ""),
                "generated_at": manifest.get("generated_at", ""),
                "score": round(score, 3),
                "archive_dir": manifest.get("archive_dir", ""),
                "artifacts": manifest.get("artifacts", {}),
            })
    matched_archives.sort(key=lambda row: (row["score"], row.get("generated_at", "")), reverse=True)

    matched_vault_notes = []
    for note in index.get("vault_notes", []):
        haystacks = [
            note.get("title", ""),
            note.get("topic_name", ""),
            note.get("source_path", ""),
            note.get("wiki_path", ""),
            " ".join(note.get("key_takeaways", [])),
        ]
        score = _match_score(tokens, haystacks)
        if score > 0:
            matched_vault_notes.append({
                "title": note.get("title", ""),
                "topic_name": note.get("topic_name", ""),
                "score": round(score, 3),
                "source_path": note.get("source_path", ""),
                "wiki_path": note.get("wiki_path", ""),
                "key_takeaways": note.get("key_takeaways", [])[:5],
                "why_matched": _match_reasons(tokens, haystacks),
            })
    matched_vault_notes.sort(key=lambda row: (-row["score"], row["title"]))

    selected_topics = matched_topics[:limit]
    selected_archives = matched_archives[:limit]
    selected_vault_notes = matched_vault_notes[:limit]
    status = "matched" if selected_topics or selected_archives or selected_vault_notes else "no_direct_match"
    next_questions = _query_next_questions(query=query, topics=selected_topics, status=status)
    return {
        "schema_version": MEMORY_QUERY_SCHEMA_VERSION,
        "generated_at": _now(),
        "query": query,
        "status": status,
        "matched_topic_count": len(selected_topics),
        "matched_archive_count": len(selected_archives),
        "matched_vault_note_count": len(selected_vault_notes),
        "matched_topics": selected_topics,
        "matched_archives": selected_archives,
        "matched_vault_notes": selected_vault_notes,
        "source_relevance": index.get("source_relevance", []),
        "next_questions": next_questions,
        "policy": "research_only",
        "limitations": [
            "This is deterministic local retrieval, not a model-generated answer.",
            "Use the linked artifacts to inspect original context before relying on a conclusion.",
        ],
    }


def write_memory_query(
    *,
    query: str,
    memory_path: str | Path = "reports/memory/topic-memory.json",
    archive_root: str | Path = DEFAULT_ARCHIVE_ROOT,
    evidence_path: str | Path = "reports/evidence/daily-evidence-catalog.json",
    vault_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    output_path: str | Path = DEFAULT_MEMORY_QUERY_OUTPUT,
    surface_path: str | Path = DEFAULT_MEMORY_QUERY_SURFACE,
    limit: int = 5,
) -> Path:
    payload = build_memory_query(
        query=query,
        memory_path=memory_path,
        archive_root=archive_root,
        evidence_path=evidence_path,
        vault_path=vault_path,
        limit=limit,
    )
    write_json(payload, output_path)
    target = Path(surface_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_memory_query_surface(payload), encoding="utf-8")
    return target


def render_memory_surface(index: dict[str, Any]) -> str:
    topic_cards = "".join(
        "<article class='card'>"
        f"<span>{esc('새 변화' if topic.get('changed_since_previous') else '누적')}</span>"
        f"<h3>{esc(topic.get('name', ''))}</h3>"
        f"<p>{esc(topic.get('latest_summary', ''))}</p>"
        f"<small>{esc(', '.join(topic.get('source_names', [])) or 'source 없음')}</small>"
        "</article>"
        for topic in index.get("topics", [])
    ) or "<p>아직 topic memory가 없습니다.</p>"
    source_rows = "".join(
        "<tr>"
        f"<td>{esc(row.get('source_name', ''))}</td>"
        f"<td>{esc(row.get('relevance_label', 'unscored'))}</td>"
        f"<td>{esc(row.get('relevance_score', '0.00'))}</td>"
        f"<td>{esc(row.get('freshness_status', 'unknown'))}</td>"
        "</tr>"
        for row in index.get("source_relevance", [])
    ) or "<tr><td colspan='4'>아직 source relevance가 없습니다.</td></tr>"
    archive_cards = "".join(
        "<article class='archive'>"
        f"<strong>{esc(manifest.get('generated_at', '')[:10])}</strong>"
        f"<span>{esc(manifest.get('run_id', ''))}</span>"
        f"<a href='{esc(manifest.get('archive_dir', ''))}/today.html'>today</a>"
        f"<a href='{esc(manifest.get('archive_dir', ''))}/market-brief.html'>brief</a>"
        "</article>"
        for manifest in index.get("archives", [])
    ) or "<p>아직 archive manifest가 없습니다.</p>"
    vault_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(note.get('topic_name', ''))}</span>"
        f"<h3>{esc(note.get('title', ''))}</h3>"
        f"<p>{esc(note.get('source_path', ''))}</p>"
        f"<small>{esc(' · '.join(note.get('key_takeaways', [])[:2]))}</small>"
        f"<p><a href='{esc(note.get('wiki_path', ''))}'>wiki note</a></p>"
        "</article>"
        for note in index.get("vault_notes", [])[:8]
    ) or "<p>아직 컴파일된 vault note가 없습니다.</p>"
    run_items = "".join(
        f"<li><strong>{esc(run.get('run_id', ''))}</strong><span>{esc(run.get('generated_at', ''))} · changed {esc(', '.join(run.get('changed_topics', [])) or 'none')}</span></li>"
        for run in index.get("recent_runs", [])
    ) or "<li>아직 run history가 없습니다.</li>"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Memory</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ max-width:860px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:26px 0 16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:34px; line-height:1.08; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p,small,li span {{ color:var(--muted); }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.section,.card,.archive {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.section {{ margin:14px 0; padding:16px; }}
.card,.archive {{ padding:14px; background:white; }}
.card span,.archive span {{ display:block; color:var(--blue); font-size:12px; font-weight:900; }}
.metrics {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
.metric {{ padding:14px; border:1px solid var(--line); border-radius:8px; background:white; }}
.metric strong {{ display:block; font-size:24px; }}
table {{ width:100%; border-collapse:collapse; overflow:hidden; border-radius:8px; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; }}
ul {{ padding-left:18px; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:29px; }} .grid,.metrics {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Memory · {esc(index.get('generated_at', '')[:10])}</span>
<h1>내가 매일 쌓아온 시장 이해</h1>
<p>오늘 브리프가 끝이 아니라, 주제별 기억과 과거 브리프가 계속 누적되는 개인 리서치 노트입니다.</p>
</header>
<section class="metrics">
<article class="metric"><span>Memory runs</span><strong>{esc(index.get('run_count', 0))}</strong></article>
<article class="metric"><span>Topics</span><strong>{esc(index.get('topic_count', 0))}</strong></article>
<article class="metric"><span>Vault notes</span><strong>{esc(len(index.get('vault_notes', [])))}</strong></article>
</section>
<section class="section">
<h2>주제별 누적 기억</h2>
<div class="grid">{topic_cards}</div>
</section>
<section class="section">
<h2>근거 품질 추적</h2>
<table><thead><tr><th>Source</th><th>Label</th><th>Score</th><th>Freshness</th></tr></thead><tbody>{source_rows}</tbody></table>
</section>
<section class="section">
<h2>Vault 원천 노트</h2>
<div class="grid">{vault_cards}</div>
</section>
<section class="section">
<h2>최근 실행</h2>
<ul>{run_items}</ul>
</section>
<section class="section">
<h2>아카이브</h2>
<div class="grid">{archive_cards}</div>
</section>
</main>
</body>
</html>
"""


def render_memory_query_surface(payload: dict[str, Any]) -> str:
    topic_cards = "".join(
        "<article class='card'>"
        f"<span>관련도 {esc(topic.get('score', 0))}</span>"
        f"<h3>{esc(topic.get('name', ''))}</h3>"
        f"<p>{esc(topic.get('summary', ''))}</p>"
        f"<small>{esc(', '.join(topic.get('why_matched', [])) or 'matched context')}</small>"
        "</article>"
        for topic in payload.get("matched_topics", [])
    ) or "<p>직접 매칭된 주제 기억이 없습니다. 질문을 더 넓게 바꾸거나 오늘 브리프를 먼저 실행하세요.</p>"
    archive_cards = "".join(
        "<article class='archive'>"
        f"<strong>{esc(archive.get('generated_at', '')[:10])}</strong>"
        f"<span>{esc(archive.get('run_id', ''))}</span>"
        f"<a href='{esc(archive.get('artifacts', {}).get('today', ''))}'>today</a>"
        f"<a href='{esc(archive.get('artifacts', {}).get('brief', ''))}'>brief</a>"
        "</article>"
        for archive in payload.get("matched_archives", [])
    ) or "<p>연결할 아카이브가 아직 없습니다.</p>"
    vault_cards = "".join(
        "<article class='card'>"
        f"<span>{esc(note.get('topic_name', ''))} · 관련도 {esc(note.get('score', 0))}</span>"
        f"<h3>{esc(note.get('title', ''))}</h3>"
        f"<p>{esc(note.get('source_path', ''))}</p>"
        f"<small>{esc(' · '.join(note.get('why_matched', [])) or 'matched note')}</small>"
        f"<p><a href='{esc(note.get('wiki_path', ''))}'>wiki note</a></p>"
        "</article>"
        for note in payload.get("matched_vault_notes", [])
    ) or "<p>연결된 vault note가 없습니다.</p>"
    questions = "".join(f"<li>{esc(question)}</li>" for question in payload.get("next_questions", []))
    source_rows = "".join(
        "<tr>"
        f"<td>{esc(row.get('source_name', ''))}</td>"
        f"<td>{esc(row.get('relevance_label', 'unscored'))}</td>"
        f"<td>{esc(row.get('freshness_status', 'unknown'))}</td>"
        "</tr>"
        for row in payload.get("source_relevance", [])[:6]
    ) or "<tr><td colspan='3'>source context 없음</td></tr>"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Memory Query</title>
<style>
:root {{ --bg:#f7f8f4; --ink:#18212b; --muted:#66717e; --line:#dbe1d8; --panel:#fffefa; --blue:#1f5f8b; --green:#1d6b52; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ max-width:860px; margin:0 auto; padding:18px; }}
a {{ color:var(--blue); font-weight:800; text-decoration:none; }}
header {{ padding:26px 0 16px; }}
.eyebrow {{ color:var(--green); font-size:12px; font-weight:900; }}
h1 {{ margin:8px 0 10px; font-size:32px; line-height:1.1; }}
h2 {{ margin:0 0 12px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:17px; }}
p,small,li {{ color:var(--muted); }}
.section,.card,.archive {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
.section {{ margin:14px 0; padding:16px; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.card,.archive {{ padding:14px; background:white; }}
.card span,.archive span {{ display:block; color:var(--blue); font-size:12px; font-weight:900; }}
table {{ width:100%; border-collapse:collapse; }}
td,th {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; }}
@media (max-width:640px) {{ main {{ padding:12px; }} h1 {{ font-size:28px; }} .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">MyBroker Memory Query · {esc(payload.get('generated_at', '')[:10])}</span>
<h1>{esc(payload.get('query', ''))}</h1>
<p>누적 메모리와 아카이브에서 다시 꺼내본 맥락입니다. 결론이 아니라 다음 탐색의 출발점입니다.</p>
</header>
<section class="section">
<h2>연결된 주제 기억</h2>
<div class="grid">{topic_cards}</div>
</section>
<section class="section">
<h2>다음에 확인할 질문</h2>
<ul>{questions}</ul>
</section>
<section class="section">
<h2>관련 아카이브</h2>
<div class="grid">{archive_cards}</div>
</section>
<section class="section">
<h2>관련 Vault 노트</h2>
<div class="grid">{vault_cards}</div>
</section>
<section class="section">
<h2>자료 상태</h2>
<table><thead><tr><th>Source</th><th>Relevance</th><th>Freshness</th></tr></thead><tbody>{source_rows}</tbody></table>
</section>
<section class="section">
<h2>안전 경계</h2>
<p>이 화면은 교육과 리서치, 시뮬레이션용입니다. 계좌 연결, 주문 실행, 일임 운용, 근거 없는 개인화 추천을 하지 않습니다.</p>
</section>
</main>
</body>
</html>
"""


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


def _daily_questions(
    memory_topics: list[dict[str, Any]],
    evidence: dict[str, Any],
    vault_notes: list[dict[str, Any]] | None = None,
    scout_recommendations: list[dict[str, Any]] | None = None,
) -> list[str]:
    questions = []
    for recommendation in (scout_recommendations or [])[:2]:
        question = recommendation.get("next_question", "")
        if question:
            questions.append(question)
    for topic in memory_topics[:3]:
        daily = topic.get("daily_questions", [])
        if daily:
            questions.append(daily[0])
    for note in (vault_notes or [])[:2]:
        title = note.get("title", "")
        if title:
            questions.append(f"Vault 노트 '{title}'의 원천 근거가 오늘 자료와 같은 방향을 가리키나요?")
    if evidence.get("collection_gaps"):
        questions.append("오늘 부족한 근거가 결론의 강도를 얼마나 낮추나요?")
    questions.append("이 브리프가 틀렸다고 판단할 가장 빠른 반대 신호는 무엇인가요?")
    deduped = []
    for question in questions:
        if question not in deduped:
            deduped.append(question)
    return deduped[:5]


def _journal_status(*, source_rows: list[dict[str, Any]], memory_topics: list[dict[str, Any]]) -> str:
    if not source_rows:
        return "blocked_no_sources"
    weak_count = sum(
        1 for row in source_rows
        if row.get("freshness_status") in {"stale", "unknown"} or row.get("relevance_label") in {"weak", "unscored"}
    )
    changed_count = sum(1 for topic in memory_topics if topic.get("changed_since_previous"))
    if weak_count >= len(source_rows):
        return "weak_needs_refresh"
    if changed_count:
        return "changed_review_first"
    return "stable_monitor"


def _journal_skeptic_note(*, evidence: dict[str, Any], memory_topics: list[dict[str, Any]]) -> str:
    gaps = evidence.get("collection_gaps", [])
    if gaps:
        return f"아직 {', '.join(_gap_label(gap) for gap in gaps[:3])} 문제가 있어 확신을 낮춰야 합니다."
    stale_topics = [topic.get("name", "") for topic in memory_topics if topic.get("collection_gaps")]
    if stale_topics:
        return f"{', '.join(stale_topics[:3])} 주제는 추가 근거 없이는 방향 판단이 약합니다."
    return "현재 근거는 학습용 시뮬레이션에는 충분하지만 투자 행동 결론에는 부족합니다."


def _journal_follow_up_questions(
    *,
    recommended: dict[str, Any],
    memory_topics: list[dict[str, Any]],
    scenario: dict[str, Any],
) -> list[str]:
    questions = []
    next_question = recommended.get("next_question", "")
    if next_question:
        questions.append(next_question)
    for topic in memory_topics:
        for question in topic.get("daily_questions", []):
            if question not in questions:
                questions.append(question)
            if len(questions) >= 5:
                break
        if len(questions) >= 5:
            break
    for candidate in scenario.get("action_candidates", [])[:2]:
        title = candidate.get("title", "")
        if title:
            questions.append(f"{title} 후보가 성립하려면 어떤 반대 근거를 먼저 확인해야 하나요?")
    if not questions:
        questions.append("오늘 시장을 이해하기 전에 먼저 확인해야 할 원천 자료는 무엇인가요?")
    return questions[:6]


def _task_source_scout_why(*, collection_gaps: list[str], weak_count: int) -> str:
    parts = []
    if collection_gaps:
        parts.append(f"자료 gap: {', '.join(_gap_label(gap) for gap in collection_gaps[:3])}")
    if weak_count:
        parts.append(f"약하거나 오래된 source {weak_count}개")
    if not parts:
        parts.append("오늘 source 상태가 안정적이지만 다음 run 전에 refresh 계획을 확인합니다.")
    return " · ".join(parts)


def _task_skeptic_why(*, journal: dict[str, Any]) -> str:
    changed = journal.get("what_changed", [])
    if changed:
        return f"{changed[0].get('name', '오늘 변화')} 변화가 실제 근거 변화인지 반복 관찰인지 구분합니다."
    stable = journal.get("stable_observations", [])
    if stable:
        return f"{stable[0].get('name', '반복 관찰')}은 새 변화가 없으므로 결론 강도를 낮춰 읽습니다."
    return "오늘 journal의 가장 강한 문장을 반대 근거로 검토합니다."


def _maybe_live_refresh_task(*, journal: dict[str, Any]) -> dict[str, Any] | None:
    gaps = set(journal.get("source_posture", {}).get("collection_gaps", []))
    if "live_refresh" not in gaps:
        return None
    return {
        "task_id": "AT-999",
        "role": "operator_gate",
        "title": "live source execution 승인 여부 결정",
        "why": "live_refresh gap이 남아 있지만 실제 live network 실행은 별도 승인과 preflight 통과 없이는 수행하지 않습니다.",
        "priority": "high",
        "status": "queued",
        "autonomy_level": "requires_human_approval",
        "approval_scope": "live_network_refresh",
        "external_effect_allowed": False,
        "requires_operator_approval": True,
        "inputs": [
            "reports/daily/source-refresh-live-gate.json",
            "reports/daily/source-refresh-live-run.json",
            "reports/daily/source-refresh-live-preflight.json",
        ],
        "suggested_command": "Review /today live refresh gate; do not execute without explicit approval.",
        "stop_condition": "operator_decision_recorded_or_deferred",
    }


def _task_fingerprint(task: dict[str, Any]) -> str:
    return "|".join([
        str(task.get("role", "")),
        str(task.get("title", "")),
        str(task.get("approval_scope", "")),
    ])


def _ledger_status_for_task(*, task: dict[str, Any], prior: dict[str, Any]) -> str:
    if task.get("requires_operator_approval"):
        return "blocked_requires_approval"
    if prior:
        return "carried"
    return "ready_for_local_work"


def _ledger_note_for_task(*, task: dict[str, Any], status: str) -> str:
    if status == "blocked_requires_approval":
        return "명시 승인 없이는 진행하지 않습니다. gate와 preflight를 먼저 확인하세요."
    if status == "carried":
        return "이전 run에서도 남아 있던 작업입니다. 오늘 완료할지, 계속 이월할지 판단하세요."
    return "로컬에서 외부 효과 없이 수행 가능한 작업입니다."


def _ledger_summary(entries: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "ready_for_local_work": 0,
        "carried": 0,
        "blocked_requires_approval": 0,
        "retired_not_in_current_queue": 0,
        "completed": 0,
        "deferred": 0,
        "blocked_by_operator": 0,
    }
    for entry in entries:
        status = entry.get("status", "")
        if status in summary:
            summary[status] += 1
    return summary


def _load_task_responses(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    responses = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        responses.append(json.loads(line))
    return responses


def _task_status_overrides(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if payload.get("schema_version") != ANALYST_TASK_STATUS_APPLY_SCHEMA_VERSION:
        return {}
    return {item.get("task_id", ""): item for item in payload.get("applied", []) if item.get("task_id")}


def _load_optional_json(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {}
    try:
        return load_json(target)
    except json.JSONDecodeError:
        return {}


def _morning_pending_decisions(
    *,
    live_gate: dict[str, Any],
    live_run: dict[str, Any],
    preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    decisions = []
    if live_gate.get("status") == "approval_required":
        for decision in live_gate.get("decisions", []):
            decisions.append({
                "id": decision.get("id", "live_network_refresh"),
                "title": "live source refresh 승인 여부",
                "why": "무료 공개 자료 live refresh 후보가 있지만 실제 네트워크 호출은 별도 승인 전까지 실행하지 않습니다.",
                "approval_scope": decision.get("approval_scope", ""),
                "risk_level": decision.get("risk_level", "medium"),
                "reversibility": decision.get("reversibility", ""),
                "copy_ready_response": decision.get("copy_ready_response", ""),
                "agent_will_run": decision.get("agent_will_run", []),
                "agent_will_not_run": decision.get("agent_will_not_run", []),
                "stale_context_guard": decision.get("stale_context_guard", ""),
                "approval_required": True,
            })
    execution = live_run.get("execution", {})
    if execution.get("status") in {"blocked", "not_requested"} and live_run.get("approval_status") == "missing":
        for blocker in execution.get("blockers", []):
            if blocker == "live_network_refresh_not_approved" and not decisions:
                decisions.append({
                    "id": "live_network_refresh",
                    "title": "live source refresh 승인 누락",
                    "why": live_run.get("next_step", "approval response is missing"),
                    "approval_scope": "live_network_refresh",
                    "risk_level": "medium",
                    "reversibility": "cache_artifact_can_be_deleted",
                    "copy_ready_response": "approve live_network_refresh live_network_refresh",
                    "agent_will_run": execution.get("proposed_commands", []),
                    "agent_will_not_run": ["paid API calls", "credentialed sources", "notification send", "host-level writes"],
                    "stale_context_guard": "Regenerate live-run proof before approval if source plan changed.",
                    "approval_required": True,
                })
    if preflight.get("status") == "blocked" and preflight.get("blockers"):
        decisions.append({
            "id": "live_refresh_preflight",
            "title": "live execution preflight 차단",
            "why": "; ".join(preflight.get("blockers", [])[:3]),
            "approval_scope": "live_network_refresh",
            "risk_level": "medium",
            "reversibility": "no external effect performed",
            "copy_ready_response": "rerun preflight after exact approval and confirmation",
            "agent_will_run": [],
            "agent_will_not_run": ["network execution until preflight passes"],
            "stale_context_guard": "Preflight must be regenerated after any approval or source change.",
            "approval_required": True,
        })
    return decisions


def _morning_top_tasks(*, ledger: dict[str, Any], queue: dict[str, Any]) -> list[dict[str, Any]]:
    entries = ledger.get("entries", [])
    if not entries:
        return queue.get("tasks", [])[:4]
    rank = {
        "blocked_requires_approval": 0,
        "blocked_by_operator": 1,
        "ready_for_local_work": 2,
        "carried": 3,
        "deferred": 4,
        "completed": 5,
        "retired_not_in_current_queue": 6,
    }
    return sorted(entries, key=lambda item: (rank.get(item.get("status", ""), 9), item.get("priority", ""), item.get("task_id", "")))[:4]


def _morning_command_bar(*, ledger: dict[str, Any], pending_decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    commands = []
    actionable = [
        entry for entry in ledger.get("entries", [])
        if entry.get("status") in {"ready_for_local_work", "carried", "deferred"}
        and entry.get("requires_operator_approval") is not True
    ]
    for entry in actionable[:3]:
        task_id = entry.get("task_id", "")
        commands.append({
            "label": f"{task_id} 완료 표시",
            "command": f"{task_id} complete \"오늘 확인 완료\"",
            "effect": "local task status response only",
            "external_effect_performed": False,
        })
        commands.append({
            "label": f"{task_id} 이월 표시",
            "command": f"{task_id} carry \"내일 계속 확인\"",
            "effect": "local task status response only",
            "external_effect_performed": False,
        })
        if len(commands) >= 4:
            break
    for decision in pending_decisions[:2]:
        commands.append({
            "label": f"{decision.get('id', 'decision')} 승인 응답",
            "command": decision.get("copy_ready_response", ""),
            "effect": "approval response only; separate apply/preflight still required",
            "external_effect_performed": False,
        })
    return commands[:6]


def _morning_status(
    *,
    pending_decisions: list[dict[str, Any]],
    ledger_summary: dict[str, Any],
    doctor: dict[str, Any],
) -> str:
    if doctor.get("fail_count", 0):
        return "blocked"
    if pending_decisions or ledger_summary.get("blocked_requires_approval", 0) or ledger_summary.get("blocked_by_operator", 0):
        return "operator_review"
    return "ready"


def _today_vault_notes(*, vault_notes: list[dict[str, Any]], memory_topics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    topic_ids = {topic.get("topic_id", "") for topic in memory_topics[:5]}
    topic_names = {topic.get("name", "").lower() for topic in memory_topics[:5]}
    matched = []
    fallback = []
    for note in vault_notes:
        fallback.append(note)
        if note.get("topic_id") in topic_ids or note.get("topic_name", "").lower() in topic_names:
            matched.append(note)
    return matched or fallback


def _vault_notes_for_memory(vault: dict[str, Any]) -> list[dict[str, Any]]:
    if vault.get("schema_version") != "knowledge_vault_compile.v1":
        return []
    notes = []
    for note in vault.get("compiled_notes", []):
        notes.append({
            "title": note.get("title", ""),
            "topic_id": note.get("topic_id", ""),
            "topic_name": note.get("topic_name", ""),
            "source_path": note.get("source_path", ""),
            "wiki_path": note.get("wiki_path", ""),
            "source_hash": note.get("source_hash", ""),
            "key_takeaways": note.get("key_takeaways", []),
        })
    return notes


def _query_tokens(query: str) -> list[str]:
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in query)
    tokens = [token for token in normalized.split() if len(token) >= 2]
    compact = normalized.replace(" ", "")
    if compact and compact not in tokens:
        tokens.append(compact)
    return tokens or [query.strip().lower()]


def _match_score(tokens: list[str], haystacks: list[str]) -> float:
    text = " ".join(haystacks).lower()
    if not text:
        return 0.0
    hits = 0
    weighted = 0.0
    for token in tokens:
        if token and token in text:
            hits += 1
            weighted += min(1.0, max(0.2, len(token) / 12))
    if not tokens:
        return 0.0
    coverage = hits / len(tokens)
    return min(1.0, (coverage * 0.65) + (weighted / max(1, len(tokens)) * 0.35))


def _match_reasons(tokens: list[str], haystacks: list[str]) -> list[str]:
    text = " ".join(haystacks).lower()
    reasons = [f"'{token}' 포함" for token in tokens if token and token in text]
    return reasons[:5]


def _query_next_questions(*, query: str, topics: list[dict[str, Any]], status: str) -> list[str]:
    if status == "no_direct_match":
        return [
            f"'{query}'를 더 넓은 주제명이나 쉬운 키워드로 다시 물어볼까요?",
            "오늘 브리프를 먼저 실행해 최신 메모리를 만든 뒤 다시 검색할까요?",
            "이 질문에 필요한 무료 공개 자료원이 무엇인지 먼저 확인할까요?",
        ]
    questions = []
    for topic in topics:
        questions.extend(topic.get("questions", [])[:2])
    questions.append(f"'{query}'에 대해 최근 아카이브의 설명이 오늘도 유효한지 확인할까요?")
    questions.append("반대 근거가 쌓인 source가 있는지 먼저 볼까요?")
    return questions[:5]


def _doctor_check_path(
    name: str,
    path: Path | None,
    missing_level: str,
    message: str,
    *,
    executable: bool = False,
    freshness_hours: int | None = None,
) -> dict[str, Any]:
    if not path or not path.exists():
        return {
            "name": name,
            "status": missing_level,
            "message": f"{message} Missing: {path.as_posix() if path else 'not_found'}",
            "path": path.as_posix() if path else "",
        }
    details: dict[str, Any] = {
        "name": name,
        "status": "pass",
        "message": message,
        "path": path.as_posix(),
    }
    if executable and not os.access(path, os.X_OK):
        details["status"] = "fail"
        details["message"] = f"{message} File is not executable."
    if freshness_hours is not None:
        age = _file_age_hours(path)
        details["age_hours"] = round(age, 2)
        if age > freshness_hours:
            details["status"] = "warn"
            details["message"] = f"{message} Artifact is older than {freshness_hours} hours."
    return details


def _doctor_check_notification(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "name": "notification_payload",
            "status": "warn",
            "message": "Notification payload has not been generated yet.",
            "path": path.as_posix(),
        }
    payload = load_json(path)
    required_env = payload.get("required_env", [])
    missing_env = [key for key in required_env if not os.environ.get(key)]
    status = "pass" if payload.get("dry_run") or not missing_env else "warn"
    message = "Notification payload exists."
    if payload.get("dry_run"):
        message = "Notification payload is dry-run ready; real send remains explicitly gated."
    elif missing_env:
        message = "Notification send is configured but provider environment variables are missing."
    return {
        "name": "notification_payload",
        "status": status,
        "message": message,
        "path": path.as_posix(),
        "provider": payload.get("provider", ""),
        "delivery_status": payload.get("delivery_status", ""),
        "missing_env": missing_env,
    }


def _doctor_check_launchd(plist_path: Path, *, require_launchd_loaded: bool) -> dict[str, Any]:
    launchd = _launchd_state()
    if launchd.get("inspect_error"):
        return {
            "name": "launchd_loaded",
            "status": "fail" if require_launchd_loaded else "warn",
            "message": f"Could not inspect launchd state: {launchd['inspect_error']}",
            "plist": plist_path.as_posix(),
            "loaded": False,
        }
    loaded = bool(launchd["loaded"])
    if loaded:
        status = "pass"
        message = "LaunchAgent is loaded for the current user."
    else:
        status = "fail" if require_launchd_loaded else "warn"
        message = "LaunchAgent is not loaded yet; install remains a host-level explicit step."
    return {
        "name": "launchd_loaded",
        "status": status,
        "message": message,
        "plist": plist_path.as_posix(),
        "loaded": loaded,
        "command": launchd["command"],
    }


def _launchd_state() -> dict[str, Any]:
    command = ["launchctl", "print", f"gui/{os.getuid()}/{LAUNCHD_LABEL}"]
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=8, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "loaded": False,
            "command": " ".join(command),
            "returncode": None,
            "inspect_error": str(exc),
        }
    return {
        "loaded": result.returncode == 0,
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout_excerpt": result.stdout[:500],
        "stderr_excerpt": result.stderr[:500],
    }


def _scheduler_status(*, source_plist: Path, source_script: Path, installed_plist: Path, loaded: bool) -> str:
    if loaded:
        return "loaded"
    if installed_plist.exists():
        return "installed_not_loaded"
    if source_plist.exists() and source_script.exists() and os.access(source_script, os.X_OK):
        return "assets_ready"
    return "not_ready"


def _scheduler_commands(*, source_plist: Path, installed_plist: Path) -> dict[str, str]:
    return {
        "prepare_assets": "PYTHONPATH=src python3 -m mybroker appliance init --project-root .",
        "install": f"mkdir -p ~/Library/LaunchAgents && cp {source_plist.as_posix()} {installed_plist.as_posix()}",
        "load": f"launchctl bootstrap gui/$(id -u) {installed_plist.as_posix()}",
        "start_now": f"launchctl kickstart -k gui/$(id -u)/{LAUNCHD_LABEL}",
        "status": f"launchctl print gui/$(id -u)/{LAUNCHD_LABEL}",
        "unload": f"launchctl bootout gui/$(id -u)/{LAUNCHD_LABEL}",
        "uninstall": f"rm {installed_plist.as_posix()}",
    }


def _scheduler_next_actions(*, source_plist: Path, source_script: Path, installed_plist: Path, loaded: bool) -> list[str]:
    if not source_plist.exists() or not source_script.exists() or not os.access(source_script, os.X_OK):
        return ["Run `PYTHONPATH=src python3 -m mybroker appliance init --project-root .` to prepare scheduler assets."]
    if not installed_plist.exists():
        return ["Review reports/runtime/scheduler-status.json, then run the install and load commands if you want the daily schedule active."]
    if not loaded:
        return ["The LaunchAgent plist is installed but not loaded. Run the load command, then `appliance scheduler status` again."]
    return ["Scheduler is loaded. Use the start_now command for an immediate proof run, then inspect reports/runtime logs and tomorrow's archive."]


def _scheduler_apply_actions(
    *,
    source_plist: Path,
    installed_plist: Path,
    install: bool,
    load: bool,
    start_now: bool,
    unload: bool,
    uninstall: bool,
) -> list[dict[str, Any]]:
    actions = []
    if install:
        actions.append({
            "name": "install",
            "kind": "copy_plist",
            "source": source_plist.as_posix(),
            "target": installed_plist.as_posix(),
            "command": f"mkdir -p {installed_plist.parent.as_posix()} && cp {source_plist.as_posix()} {installed_plist.as_posix()}",
        })
    if load:
        actions.append({
            "name": "load",
            "kind": "launchctl",
            "command": f"launchctl bootstrap gui/{os.getuid()} {installed_plist.as_posix()}",
        })
    if start_now:
        actions.append({
            "name": "start_now",
            "kind": "launchctl",
            "command": f"launchctl kickstart -k gui/{os.getuid()}/{LAUNCHD_LABEL}",
        })
    if unload:
        actions.append({
            "name": "unload",
            "kind": "launchctl",
            "command": f"launchctl bootout gui/{os.getuid()}/{LAUNCHD_LABEL}",
        })
    if uninstall:
        actions.append({
            "name": "uninstall",
            "kind": "remove_file",
            "target": installed_plist.as_posix(),
            "command": f"rm {installed_plist.as_posix()}",
        })
    return actions


def _execute_scheduler_action(action: dict[str, Any]) -> dict[str, Any]:
    result = dict(action)
    result["executed"] = True
    try:
        if action["kind"] == "copy_plist":
            source = Path(action["source"])
            target = Path(action["target"])
            if not source.exists():
                raise FileNotFoundError(source.as_posix())
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            result["status"] = "ok"
            return result
        if action["kind"] == "remove_file":
            target = Path(action["target"])
            if target.exists():
                target.unlink()
            result["status"] = "ok"
            return result
        completed = subprocess.run(action["command"].split(), text=True, capture_output=True, timeout=30, check=False)
        result["returncode"] = completed.returncode
        result["stdout_excerpt"] = completed.stdout[:500]
        result["stderr_excerpt"] = completed.stderr[:500]
        result["status"] = "ok" if completed.returncode == 0 else "failed"
    except Exception as exc:  # pragma: no cover - defensive host-level guard
        result["status"] = "failed"
        result["error"] = str(exc)
    return result


def _preflight_artifact_check(
    name: str,
    path: Path,
    *,
    expected_schema: str,
    max_age_hours: int,
    predicate: Any,
    message: str,
) -> dict[str, Any]:
    if not path.exists():
        return {
            "name": name,
            "status": "fail",
            "message": f"Missing artifact: {path.as_posix()}",
            "path": path.as_posix(),
        }
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return {
            "name": name,
            "status": "fail",
            "message": f"Invalid JSON: {exc}",
            "path": path.as_posix(),
        }
    if payload.get("schema_version") != expected_schema:
        return {
            "name": name,
            "status": "fail",
            "message": f"Unexpected schema_version: {payload.get('schema_version')}",
            "path": path.as_posix(),
        }
    age_hours = _artifact_age_hours(path, payload)
    status = "pass"
    reason = message
    if age_hours > max_age_hours:
        status = "warn"
        reason = f"{message} Artifact is older than {max_age_hours} hours."
    if not predicate(payload):
        status = "fail"
        reason = f"{message} Required condition was not met."
    return {
        "name": name,
        "status": status,
        "message": reason,
        "path": path.as_posix(),
        "age_hours": round(age_hours, 2),
    }


def _activation_verify_check(name: str, condition: bool, message: str, *, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pass" if condition else "fail",
        "message": message if condition else f"Required condition not met: {message}",
        "evidence": evidence,
    }


def _scheduler_activation_decision(*, preflight: dict[str, Any], verify: dict[str, Any]) -> dict[str, Any]:
    preflight_ready = preflight.get("status") in {"ready", "already_active"}
    active_verified = verify.get("status") == "active_verified"
    readiness = "ready" if preflight_ready and not active_verified else "pending"
    if not preflight_ready:
        readiness = "blocked"
    if active_verified:
        readiness = "complete"
    return {
        "id": "scheduler_activation",
        "title": "Activate daily scheduler",
        "approval_scope": "confirmed_host_write",
        "readiness": readiness,
        "current_state": {
            "preflight_status": preflight.get("status", "missing"),
            "verify_status": verify.get("status", "missing"),
            "preflight_blockers": preflight.get("blockers", []),
            "verify_blockers": verify.get("blockers", []),
        },
        "operator_can_say": "approve scheduler_activation confirmed_host_write",
        "agent_will_run": [
            "PYTHONPATH=src python3 -m mybroker appliance scheduler apply --install --load --start-now --confirm-host-write",
            "PYTHONPATH=src python3 -m mybroker appliance scheduler activation-verify",
        ],
        "risk": "Installs and loads a LaunchAgent for the current macOS user and starts the local runner.",
        "reversibility": "partially_reversible",
        "rollback_command": "PYTHONPATH=src python3 -m mybroker appliance scheduler apply --unload --uninstall --confirm-host-write",
    }


def _notification_send_decision(*, notification: dict[str, Any]) -> dict[str, Any]:
    required_env = notification.get("required_env", [])
    missing_env = [key for key in required_env if not os.environ.get(key)]
    dry_run_ready = notification.get("dry_run") is True and notification.get("delivery_status") == "dry_run_ready"
    readiness = "ready" if dry_run_ready and not missing_env else "blocked"
    return {
        "id": "notification_send",
        "title": "Send phone notification",
        "approval_scope": "send_notification",
        "readiness": readiness,
        "current_state": {
            "provider": notification.get("provider", "missing"),
            "delivery_status": notification.get("delivery_status", "missing"),
            "dry_run": notification.get("dry_run"),
            "missing_env": missing_env,
        },
        "operator_can_say": "approve notification_send send_notification",
        "agent_will_run": [
            "PYTHONPATH=src python3 -m mybroker appliance notify --provider <provider> --send",
        ],
        "risk": "Sends one message through the configured provider using local environment secrets.",
        "reversibility": "not_reversible",
        "rollback_command": "",
    }


def _private_phone_access_decision(*, phone_access: dict[str, Any]) -> dict[str, Any]:
    enable_commands = _phone_access_enable_commands(phone_access=phone_access)
    rollback_command = _phone_access_rollback_command(phone_access=phone_access)
    readiness = "ready" if phone_access.get("schema_version") == PHONE_ACCESS_SCHEMA_VERSION and enable_commands else "blocked"
    return {
        "id": "private_phone_access",
        "title": "Enable private phone access",
        "approval_scope": "private_network_exposure",
        "readiness": readiness,
        "current_state": {
            "recommended_path": phone_access.get("recommended_path", "missing"),
            "local_url": phone_access.get("local_url", ""),
            "private_phone_url": phone_access.get("private_phone_url", ""),
        },
        "operator_can_say": "approve private_phone_access private_network_exposure",
        "agent_will_run": enable_commands,
        "risk": "Starts local/private serving so the phone can read the daily brief. Public exposure remains out of scope.",
        "reversibility": "reversible",
        "rollback_command": rollback_command,
    }


def _phone_access_enable_commands(*, phone_access: dict[str, Any]) -> list[str]:
    enable_commands = []
    for item in phone_access.get("commands", []):
        command = item.get("command", "")
        purpose = item.get("purpose", "")
        if not command or _phone_access_command_is_rollback(command=command, purpose=purpose):
            continue
        enable_commands.append(command)
    return enable_commands


def _phone_access_rollback_command(*, phone_access: dict[str, Any]) -> str:
    for item in phone_access.get("commands", []):
        command = item.get("command", "")
        purpose = item.get("purpose", "")
        if command and _phone_access_command_is_rollback(command=command, purpose=purpose):
            return command
    return "tailscale serve reset"


def _phone_access_command_is_rollback(*, command: str, purpose: str) -> bool:
    normalized = f"{purpose} {command}".lower()
    return "stop" in normalized or "reset" in normalized or "unserve" in normalized


def _parse_operator_approval_response(response: str) -> dict[str, str]:
    parts = response.strip().split()
    if len(parts) != 3:
        return {
            "action": "",
            "decision_id": "",
            "approval_scope": "",
            "parse_status": "invalid",
            "parse_error": "Expected response shape: approve <decision_id> <approval_scope>",
        }
    action, decision_id, approval_scope = parts
    return {
        "action": action,
        "decision_id": decision_id,
        "approval_scope": approval_scope,
        "parse_status": "parsed",
        "parse_error": "",
    }


def _find_packet_decision(*, packet: dict[str, Any], decision_id: str) -> dict[str, Any] | None:
    for decision in packet.get("decisions", []):
        if decision.get("id") == decision_id:
            return decision
    return None


def _operator_decision_apply_blockers(*, parsed: dict[str, str], decision: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if parsed.get("parse_status") != "parsed":
        blockers.append(parsed.get("parse_error", "operator response could not be parsed"))
        return blockers
    if parsed.get("action") != "approve":
        blockers.append("Only approve responses can create an apply plan.")
    if decision is None:
        blockers.append(f"Decision not found in packet: {parsed.get('decision_id', '')}")
        return blockers
    if parsed.get("approval_scope") != decision.get("approval_scope"):
        blockers.append(
            f"Approval scope mismatch: expected {decision.get('approval_scope')}, got {parsed.get('approval_scope')}"
        )
    if decision.get("readiness") != "ready":
        blockers.append(f"Decision readiness is {decision.get('readiness')}, not ready.")
    if not decision.get("agent_will_run"):
        blockers.append("Decision has no runnable command plan.")
    return blockers


def _operator_decision_apply_next_action(*, blockers: list[str], decision: dict[str, Any] | None) -> str:
    if blockers:
        return "Fix the blocker or regenerate the operator decision packet before asking the agent to execute anything."
    return (
        "Review the commands and rollback_command. The artifact did not execute anything; external execution still requires "
        f"explicit scoped approval for {decision.get('approval_scope') if decision else 'unknown'}."
    )


def _same_file_contents(left: Path, right: Path) -> bool:
    if not left.exists() or not right.exists():
        return False
    return left.read_bytes() == right.read_bytes()


def _path_fresh(path: Path | None, freshness_hours: int) -> bool:
    if not path or not path.exists():
        return False
    return _file_age_hours(path) <= freshness_hours


def _dry_run_apply_is_activation_plan(payload: dict[str, Any]) -> bool:
    requested = payload.get("requested", {})
    actions = payload.get("actions", [])
    action_names = {action.get("name") for action in actions}
    action_statuses = {action.get("status") for action in actions}
    return (
        payload.get("dry_run") is True
        and payload.get("host_write_performed") is False
        and requested.get("install") is True
        and requested.get("load") is True
        and requested.get("start_now") is True
        and {"install", "load", "start_now"}.issubset(action_names)
        and action_statuses == {"planned"}
    )


def _artifact_age_hours(path: Path, payload: dict[str, Any]) -> float:
    generated_at = payload.get("generated_at")
    if isinstance(generated_at, str) and generated_at:
        try:
            generated = datetime.fromisoformat(generated_at)
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - generated.astimezone(timezone.utc)).total_seconds() / 3600
        except ValueError:
            pass
    return _file_age_hours(path)


def _timeout_output_excerpt(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")[-2000:]
    return value[-2000:]


def _doctor_next_actions(checks: list[dict[str, Any]]) -> list[str]:
    actions = []
    names = {check["name"]: check for check in checks}
    if names.get("runner_script", {}).get("status") == "fail" or names.get("launchd_plist", {}).get("status") == "fail":
        actions.append("Run `PYTHONPATH=src python3 -m mybroker appliance init --project-root .` to regenerate local runner assets.")
    if names.get("today_surface", {}).get("status") != "pass":
        actions.append("Run `PYTHONPATH=src python3 -m mybroker appliance run --topics config/topics.json --profile examples/profiles/beginner-conservative.json --dry-run` to refresh daily artifacts.")
    if names.get("phone_access_plan", {}).get("status") != "pass":
        actions.append("Run `PYTHONPATH=src python3 -m mybroker appliance access` to write private phone access guidance.")
    if names.get("launchd_loaded", {}).get("status") != "pass":
        actions.append("Install the LaunchAgent manually only after reviewing reports/runtime/local-runtime-doctor.json.")
    if not actions:
        actions.append("Local runtime evidence is ready; keep the Mac powered and review tomorrow's archive after the scheduled run.")
    return actions


def _latest_archive_manifest(archive_root: Path) -> Path | None:
    manifests = sorted(archive_root.glob("*/manifest.json"), reverse=True)
    return manifests[0] if manifests else None


def _file_age_hours(path: Path) -> float:
    modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return (datetime.now(timezone.utc) - modified).total_seconds() / 3600


def _agenda_topic_card(
    *,
    recommendation: dict[str, Any],
    evidence_items: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    memory_topic: dict[str, Any],
    vault_notes: list[dict[str, Any]],
) -> dict[str, Any]:
    latest_titles = set(recommendation.get("latest_titles", []))
    source_names = set(recommendation.get("source_names", []))
    supporting = [
        item
        for item in evidence_items
        if item.get("title") in latest_titles or item.get("source_name") in source_names
    ][:5]
    linked_vault = recommendation.get("linked_vault_notes", [])
    if not linked_vault:
        linked_vault = [
            {
                "title": note.get("title", ""),
                "source_path": note.get("source_path", ""),
                "wiki_path": note.get("wiki_path", ""),
            }
            for note in vault_notes
            if note.get("topic_id") == recommendation.get("topic_id")
        ][:3]
    source_family_count = len(source_names)
    weak_points = list(dict.fromkeys(recommendation.get("missing_evidence", []) + memory_topic.get("collection_gaps", [])))
    return {
        "topic_id": recommendation.get("topic_id", ""),
        "name": recommendation.get("name", ""),
        "priority_rank": recommendation.get("priority_rank", 0),
        "action": recommendation.get("action", "monitor"),
        "confidence": recommendation.get("confidence", ""),
        "why_today": recommendation.get("why", ""),
        "beginner_focus": recommendation.get("beginner_focus", ""),
        "next_question": recommendation.get("next_question", ""),
        "evidence_count": len(supporting),
        "source_family_count": source_family_count,
        "vault_note_count": len(linked_vault),
        "supporting_evidence": [
            {
                "source_name": item.get("source_name", ""),
                "title": item.get("title", ""),
                "freshness_status": item.get("freshness_status", ""),
                "entities": item.get("entities", [])[:5],
            }
            for item in supporting
        ],
        "source_status": [
            row
            for row in source_rows
            if row.get("source_name") in source_names
        ],
        "linked_vault_notes": linked_vault,
        "weak_points": weak_points,
        "readiness": _agenda_readiness(
            source_family_count=source_family_count,
            evidence_count=len(supporting),
            weak_points=weak_points,
        ),
    }


def _agenda_readiness(*, source_family_count: int, evidence_count: int, weak_points: list[str]) -> str:
    if source_family_count >= 3 and evidence_count >= 3 and not weak_points:
        return "meaningful"
    if source_family_count >= 2 and evidence_count >= 2:
        return "useful_but_verify"
    if evidence_count:
        return "weak"
    return "blocked"


def _agenda_weak_points(
    *,
    top_cards: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    evidence: dict[str, Any],
) -> list[str]:
    weak: list[str] = []
    for card in top_cards:
        weak.extend(card.get("weak_points", []))
        if card.get("readiness") in {"weak", "blocked"}:
            weak.append(f"{card.get('name', 'topic')} 근거 다양성이 약합니다.")
    weak.extend(evidence.get("collection_gaps", []))
    if len(source_rows) < 3:
        weak.append("source family가 3개 미만입니다.")
    if any(row.get("freshness_status") == "sample_cache" for row in source_rows):
        weak.append("일부 근거는 sample cache라 최신 시장 판단으로 바로 쓰면 안 됩니다.")
    return list(dict.fromkeys(weak))[:8]


def _agenda_study_sequence(*, primary: dict[str, Any], weak_points: list[str]) -> list[dict[str, Any]]:
    primary_name = primary.get("name", "오늘 추천 주제")
    return [
        {
            "step": 1,
            "minutes": 4,
            "title": f"{primary_name}를 왜 먼저 보는지 확인",
            "operator_action": primary.get("why_today", "Scout 추천 이유를 읽고 오늘의 질문을 하나 고릅니다."),
            "stop_condition": "왜 이 주제가 오늘 첫 번째인지 한 문장으로 설명할 수 있으면 다음으로 이동합니다.",
        },
        {
            "step": 2,
            "minutes": 6,
            "title": "근거가 서로 다른 출처에서 왔는지 확인",
            "operator_action": "GDELT/공시/가격/Vault 중 어떤 source family가 실제로 영향을 줬는지 봅니다.",
            "stop_condition": "출처가 하나뿐이거나 sample cache뿐이면 결론을 보류합니다.",
        },
        {
            "step": 3,
            "minutes": 6,
            "title": "시나리오를 낙관/base/downside로 나눠 읽기",
            "operator_action": "상승/기본/하락 경로를 비교하고, 어느 근거가 각 경로를 밀어주는지 체크합니다.",
            "stop_condition": "한쪽 시나리오만 강하게 보이면 skeptic task를 먼저 실행합니다.",
        },
        {
            "step": 4,
            "minutes": 4,
            "title": "오늘 남길 메모와 다음 질문 정하기",
            "operator_action": (weak_points[0] if weak_points else primary.get("next_question", "내일 다시 확인할 질문을 하나 남깁니다.")),
            "stop_condition": "매수/매도 결론이 아니라 다음 확인 질문으로 끝냅니다.",
        },
    ]


def _agenda_source_fanout(*, source_rows: list[dict[str, Any]], top_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top_source_names = {
        source.get("source_name", "")
        for card in top_cards
        for source in card.get("source_status", [])
    }
    rows = []
    for row in source_rows:
        source_name = row.get("source_name", "")
        rows.append({
            "source_name": source_name,
            "freshness_status": row.get("freshness_status", ""),
            "relevance_label": row.get("relevance_label", ""),
            "item_count": row.get("item_count", "0"),
            "role": _agenda_source_role(source_name=source_name),
            "influenced_top_topics": source_name in top_source_names,
        })
    return rows


def _agenda_source_role(*, source_name: str) -> str:
    roles = {
        "GDELT": "뉴스/이벤트 서사가 과열인지, 실제 사건인지 확인합니다.",
        "SEC EDGAR": "기업 공시로 서사가 실제 사업/위험 언어에 닿는지 확인합니다.",
        "Stooq": "가격 흐름이 서사와 같은 방향인지 넓은 시장 맥락을 확인합니다.",
    }
    return roles.get(source_name, "오늘 주제의 보조 근거로 사용합니다.")


def _agenda_role_brief(
    *,
    primary: dict[str, Any],
    weak_points: list[str],
    refresh_plan: dict[str, Any],
) -> list[dict[str, Any]]:
    primary_name = primary.get("name", "오늘 주제")
    blocked_refresh = [
        action.get("source_name", "")
        for action in refresh_plan.get("actions", [])
        if action.get("priority") == "high"
    ]
    return [
        {
            "role": "source_scout",
            "task": f"{primary_name}에 필요한 최신 근거 후보를 확인",
            "success_condition": "새 근거가 없으면 sample cache 기반이라는 점을 agenda에 남깁니다.",
        },
        {
            "role": "evidence_curator",
            "task": "근거 출처군, freshness, 중복 가능성을 점검",
            "success_condition": "source family와 weak point가 분리되어 표시됩니다.",
        },
        {
            "role": "market_mapper",
            "task": "주제-엔티티-이벤트가 어떤 market map을 만드는지 읽기 쉽게 정리",
            "success_condition": "초보자가 왜 이 주제가 시장 흐름과 연결되는지 이해합니다.",
        },
        {
            "role": "skeptic",
            "task": weak_points[0] if weak_points else "오늘 근거가 과도하게 한 방향으로 쏠렸는지 확인",
            "success_condition": "약한 근거가 있으면 투자 행동 후보가 아니라 추가 질문으로 남깁니다.",
        },
        {
            "role": "publisher",
            "task": "폰에서 읽을 순서와 다음 질문만 남기기",
            "success_condition": "오늘 output은 실행 지시가 아니라 학습/리서치 루틴으로 끝납니다.",
        },
        {
            "role": "refresh_gate",
            "task": f"필요한 live refresh 후보: {', '.join(blocked_refresh) or '없음'}",
            "success_condition": "live network refresh는 별도 승인 없이는 실행되지 않습니다.",
        },
    ]


def _agenda_questions(*, primary: dict[str, Any], weak_points: list[str]) -> list[str]:
    name = primary.get("name", "오늘 주제")
    question = primary.get("next_question") or f"오늘 {name}에서 초보자가 먼저 이해해야 할 변화는 무엇인가요?"
    questions = [
        question,
        f"{name}의 낙관/base/downside 경로를 가르는 핵심 근거는 무엇인가요?",
        "오늘 근거 중 sample cache 또는 stale 가능성이 있는 것은 무엇인가요?",
    ]
    if weak_points:
        questions.append(f"약한 근거 점검: {weak_points[0]}")
    return questions


def _readiness_artifact_check(
    *,
    root: Path,
    name: str,
    path: Path,
    kind: str,
    required: bool,
    freshness_hours: int,
    now: datetime,
) -> dict[str, Any]:
    full_path = path if path.is_absolute() else root / path
    exists = full_path.exists()
    payload: dict[str, Any] = {}
    age_hours: float | None = None
    if exists:
        if full_path.suffix == ".json":
            try:
                payload = load_json(full_path)
            except json.JSONDecodeError:
                payload = {}
        age_hours = _readiness_age_hours(full_path, payload=payload, now=now)
    freshness_status = "missing"
    if exists and age_hours is not None:
        freshness_status = "fresh" if age_hours <= freshness_hours else "stale"
    display_path = full_path.as_posix()
    try:
        display_path = full_path.relative_to(root).as_posix()
    except ValueError:
        pass
    return {
        "name": name,
        "path": display_path,
        "kind": kind,
        "required": required,
        "exists": exists,
        "freshness_status": freshness_status,
        "age_hours": round(age_hours, 2) if age_hours is not None else None,
        "generated_at": payload.get("generated_at", "") if payload else "",
        "schema_version": payload.get("schema_version", "") if payload else "",
    }


def _readiness_age_hours(path: Path, *, payload: dict[str, Any], now: datetime) -> float:
    generated_at = payload.get("generated_at")
    if isinstance(generated_at, str) and generated_at:
        try:
            generated = datetime.fromisoformat(generated_at)
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=timezone.utc)
            return (now - generated.astimezone(timezone.utc)).total_seconds() / 3600
        except ValueError:
            pass
    modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return (now - modified).total_seconds() / 3600


def _source_refresh_brief_actions(
    *,
    refresh_plan: dict[str, Any],
    refresh_apply: dict[str, Any],
    live_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    plan_by_adapter = {item.get("adapter_id", ""): item for item in refresh_plan.get("actions", [])}
    blocked_by_adapter = {item.get("adapter_id", ""): item for item in live_gate.get("blocked_actions", [])}
    rows = []
    for result in refresh_apply.get("results", []):
        adapter_id = result.get("adapter_id", "")
        plan = plan_by_adapter.get(adapter_id, {})
        blocked = blocked_by_adapter.get(adapter_id, {})
        rows.append({
            "source_name": result.get("source_name", plan.get("source_name", "")),
            "adapter_id": adapter_id,
            "decision": result.get("decision", ""),
            "status": result.get("status", ""),
            "approval_required": result.get("approval_required", "none"),
            "reason": result.get("reason", plan.get("reason", "")),
            "command": result.get("command", plan.get("command", "")),
            "expected_artifact": result.get("expected_artifact", blocked.get("expected_artifact", "")),
            "cadence": plan.get("cadence", ""),
            "priority": plan.get("priority", ""),
        })
    if rows:
        return rows
    return [
        {
            "source_name": item.get("source_name", ""),
            "adapter_id": item.get("adapter_id", ""),
            "decision": "planned",
            "status": "not_applied",
            "approval_required": "operator_review" if item.get("adapter_id") in {"gdelt-live", "stooq-live"} else "none",
            "reason": item.get("reason", ""),
            "command": item.get("command", ""),
            "expected_artifact": item.get("expected_artifact", ""),
            "cadence": item.get("cadence", ""),
            "priority": item.get("priority", ""),
        }
        for item in refresh_plan.get("actions", [])
    ]


def _source_refresh_weak_evidence(*, evidence: dict[str, Any], scout: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for gap in evidence.get("collection_gaps", [])[:4]:
        rows.append({
            "kind": "catalog_gap",
            "title": _gap_label(gap),
            "why_it_matters": "브리프 확신도를 낮추는 evidence catalog gap입니다.",
        })
    for recommendation in scout.get("recommendations", [])[:3]:
        missing = recommendation.get("missing_evidence", []) or []
        for gap in missing[:2]:
            rows.append({
                "kind": recommendation.get("name", "topic"),
                "title": _gap_label(gap),
                "why_it_matters": recommendation.get("why", "오늘 주제 판단 전에 확인해야 할 약한 근거입니다."),
            })
    seen = set()
    deduped = []
    for row in rows:
        key = (row["kind"], row["title"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped[:6]


def _source_refresh_brief_status(
    *,
    actions: list[dict[str, Any]],
    live_gate: dict[str, Any],
    live_run: dict[str, Any],
    preflight: dict[str, Any],
) -> str:
    if live_run.get("execution", {}).get("status") == "executed":
        return "executed"
    if preflight.get("status") == "passed":
        return "ready_to_execute"
    if live_run.get("approval_status") == "approved" and live_run.get("execution", {}).get("status") == "ready_to_execute":
        return "preflight_required"
    if live_gate.get("status") == "approval_required":
        return "approval_required"
    if any(action.get("decision") == "ready" for action in actions):
        return "local_ready"
    if not actions:
        return "no_refresh_needed"
    return "blocked"


def _source_refresh_operator_decision(
    *,
    live_gate: dict[str, Any],
    live_run: dict[str, Any],
    preflight: dict[str, Any],
) -> dict[str, Any]:
    decision = (live_gate.get("decisions") or [{}])[0]
    if live_gate.get("status") != "approval_required":
        return {
            "approval_required": False,
            "title": "live source refresh 승인 없음",
            "why": "현재 live refresh gate가 승인 요구 상태가 아닙니다.",
        }
    return {
        "approval_required": True,
        "id": decision.get("id", "live_network_refresh"),
        "title": "free/no-key live source refresh 승인",
        "why": "GDELT 또는 Stooq 같은 무료 공개 자료 live refresh 후보가 있지만 네트워크 호출이므로 별도 승인 전에는 실행하지 않습니다.",
        "approval_scope": decision.get("approval_scope", "live_network_refresh"),
        "risk_level": decision.get("risk_level", "medium"),
        "copy_ready_response": decision.get("copy_ready_response", "approve live_network_refresh live_network_refresh"),
        "stale_context_guard": decision.get("stale_context_guard", "Regenerate refresh artifacts if scout or source plan changed."),
        "approval_status": live_run.get("approval_status", "missing"),
        "preflight_status": preflight.get("status", "missing"),
    }


def _source_refresh_next_action(
    *,
    status: str,
    live_gate: dict[str, Any],
    live_run: dict[str, Any],
    preflight: dict[str, Any],
) -> str:
    if status == "executed":
        return "live evidence catalog가 생성됐습니다. validator를 통과한 뒤 daily loop를 다시 실행해 브리프에 반영하세요."
    if status == "ready_to_execute":
        return "preflight가 통과했습니다. 실제 live network 실행은 별도 최종 확인 후에만 진행하세요."
    if status == "preflight_required":
        return "승인 응답은 유효합니다. 실행 전 source-refresh-live-preflight를 실행해 source id, output path, confirmation을 확인하세요."
    if status == "approval_required":
        decision = (live_gate.get("decisions") or [{}])[0]
        return f"필요하면 다음 응답을 검토하세요: {decision.get('copy_ready_response', 'approve live_network_refresh live_network_refresh')}"
    if status == "local_ready":
        return "먼저 로컬/샘플/cache 작업을 검증하고, live refresh는 약한 근거가 계속 남을 때만 승인하세요."
    if status == "no_refresh_needed":
        return "오늘은 별도 source refresh가 필요하지 않습니다. agenda와 today brief를 먼저 읽으세요."
    blockers = preflight.get("blockers") or live_run.get("execution", {}).get("blockers", [])
    return "차단 이유를 먼저 해소하세요: " + (", ".join(blockers[:3]) if blockers else "refresh artifacts를 다시 생성하세요.")


def _scheduler_proof_artifact(
    *,
    name: str,
    path: Path,
    expected_schema: str,
    freshness_hours: int,
    now: datetime,
) -> dict[str, Any]:
    exists = path.exists()
    payload: dict[str, Any] = {}
    age_hours: float | None = None
    freshness_status = "missing"
    summary_status = "missing"
    if exists:
        try:
            payload = load_json(path)
            age_hours = _readiness_age_hours(path, payload=payload, now=now)
            freshness_status = "fresh" if age_hours <= freshness_hours else "stale"
            summary_status = str(payload.get("status", payload.get("delivery_status", "present")))
            if payload.get("schema_version") != expected_schema:
                freshness_status = "invalid_schema"
                summary_status = f"unexpected schema {payload.get('schema_version', '')}"
        except json.JSONDecodeError:
            freshness_status = "invalid_schema"
            summary_status = "invalid json"
    return {
        "name": name,
        "path": path.as_posix(),
        "exists": exists,
        "freshness_status": freshness_status,
        "age_hours": round(age_hours, 2) if age_hours is not None else None,
        "schema_version": payload.get("schema_version", ""),
        "summary_status": summary_status,
        "host_write_performed": payload.get("host_write_performed", False),
    }


def _scheduler_operations_status(
    *,
    install_state: dict[str, Any],
    local_run: dict[str, Any],
    activation_preflight: dict[str, Any],
    activation_verify: dict[str, Any],
    runtime: dict[str, Any],
    proof_artifacts: list[dict[str, Any]],
) -> str:
    if any(item.get("freshness_status") == "invalid_schema" for item in proof_artifacts):
        return "blocked"
    if activation_verify.get("status") == "active_verified" and install_state.get("loaded"):
        return "active_verified"
    if activation_preflight.get("status") in {"ready", "already_active"} and local_run.get("status") == "passed":
        return "activation_ready"
    if install_state.get("script_ready") and install_state.get("plist_ready") and runtime.get("doctor_status") == "ready":
        return "manual_ready"
    if not install_state.get("script_ready") or not install_state.get("plist_ready"):
        return "not_ready"
    return "blocked"


def _scheduler_operations_next_action(
    *,
    status: str,
    install_state: dict[str, Any],
    local_run: dict[str, Any],
    activation_preflight: dict[str, Any],
    runtime: dict[str, Any],
) -> str:
    if status == "active_verified":
        return "자동 실행이 확인됐습니다. 내일 archive와 log가 새로 생기는지 점검하세요."
    if status == "activation_ready":
        return "수동 run-once와 preflight가 통과했습니다. host scheduler 활성화는 별도 확인과 승인 후에만 진행하세요."
    if not install_state.get("script_ready") or not install_state.get("plist_ready"):
        return "먼저 appliance init으로 runner script와 LaunchAgent plist를 생성하세요."
    if runtime.get("doctor_status") != "ready":
        return "runtime doctor가 ready가 아닙니다. readiness와 doctor proof를 먼저 새로 생성하세요."
    if local_run.get("status") != "passed":
        return "host-level 활성화 전에 scheduler run-once를 실행해 로컬 runner가 끝까지 도는지 확인하세요."
    if activation_preflight.get("status") != "ready":
        return "dry-run apply, run-once, notification dry-run proof를 만든 뒤 activation-preflight를 다시 실행하세요."
    return "현재 상태를 확인하고 readiness, morning, scheduler 순서로 폰에서 검토하세요."


def _scheduler_operations_commands(*, overall_status: str) -> list[dict[str, Any]]:
    commands = [
        {
            "label": "scheduler assets 생성",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance init --project-root .",
            "why": "runner script와 LaunchAgent plist를 로컬 repo 안에 생성합니다.",
            "requires_separate_approval": False,
            "external_effect_performed": False,
        },
        {
            "label": "수동 run-once proof",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance scheduler run-once",
            "why": "host scheduler 설치 없이 같은 runner를 한 번 실행합니다.",
            "requires_separate_approval": False,
            "external_effect_performed": False,
        },
        {
            "label": "activation preflight",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance scheduler activation-preflight",
            "why": "host write 전에 필요한 proof가 충분한지 다시 검사합니다.",
            "requires_separate_approval": False,
            "external_effect_performed": False,
        },
    ]
    if overall_status == "activation_ready":
        commands.append({
            "label": "별도 승인 후 활성화",
            "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m mybroker appliance scheduler apply --install --load --start-now --confirm-host-write",
            "why": "현재 macOS 사용자 LaunchAgent를 설치/load/start합니다. 별도 승인 없이는 실행하지 않습니다.",
            "requires_separate_approval": True,
            "external_effect_performed": False,
        })
    return commands


def _readiness_scheduler_state(status_path: Path) -> dict[str, Any]:
    if not status_path.exists():
        return {
            "status": "missing",
            "loaded": False,
            "installed": False,
            "path": status_path.as_posix(),
            "message": "Scheduler status artifact is missing.",
        }
    payload = load_json(status_path)
    return {
        "status": payload.get("status", "unknown"),
        "loaded": bool(payload.get("launchd", {}).get("loaded")),
        "installed": bool(payload.get("installed_plist", {}).get("exists")),
        "path": status_path.as_posix(),
        "message": payload.get("next_actions", [""])[0] if payload.get("next_actions") else "",
    }


def _readiness_status(
    *,
    missing_required: list[dict[str, Any]],
    stale_required: list[dict[str, Any]],
) -> str:
    if missing_required:
        return "blocked"
    if stale_required:
        return "stale"
    return "ready"


def _readiness_next_actions(
    *,
    status: str,
    missing_required: list[dict[str, Any]],
    stale_required: list[dict[str, Any]],
    scheduler: dict[str, Any],
) -> list[str]:
    actions: list[str] = []
    if missing_required:
        names = ", ".join(item["name"] for item in missing_required)
        actions.append(f"필수 artifact가 없습니다: {names}. `appliance run --dry-run`을 먼저 실행하세요.")
    if stale_required:
        names = ", ".join(item["name"] for item in stale_required)
        actions.append(f"필수 artifact가 오래됐습니다: {names}. daily run을 다시 생성하세요.")
    if status == "ready":
        actions.append("필수 산출물은 freshness 기준을 통과했습니다. morning, today, agenda 순서로 읽어도 됩니다.")
    if not scheduler.get("loaded"):
        actions.append("자동 실행은 아직 활성 확인이 안 됐습니다. 필요하면 scheduler status와 activation-preflight를 검토하세요.")
    actions.append("외부 효과가 필요한 source refresh, 알림 전송, host scheduler 쓰기는 별도 승인 게이트에서만 실행하세요.")
    return actions


def _readiness_css(status: str) -> str:
    return status if status in {"fresh", "stale", "missing"} else "missing"


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


def _local_date_label(value: str) -> str:
    if not value:
        return datetime.now().astimezone().strftime("%Y-%m-%d local")
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone().strftime("%Y-%m-%d local")
    except ValueError:
        return _short_date(value)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
