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

from mybroker.vault import DEFAULT_VAULT_COMPILE_OUTPUT


TODAY_SURFACE_SCHEMA_VERSION = "today_surface.v1"
NOTIFICATION_SCHEMA_VERSION = "notification_delivery.v1"
ARCHIVE_SCHEMA_VERSION = "daily_archive.v1"
RUNTIME_PLAYBOOK_SCHEMA_VERSION = "personal_analyst_runtime_playbook.v1"
PHONE_ACCESS_SCHEMA_VERSION = "phone_access_plan.v1"
OPERATOR_DECISION_PACKET_SCHEMA_VERSION = "operator_decision_packet.v1"
OPERATOR_DECISION_APPLY_SCHEMA_VERSION = "operator_decision_apply.v1"
MEMORY_INDEX_SCHEMA_VERSION = "personal_memory_index.v1"
MEMORY_QUERY_SCHEMA_VERSION = "personal_memory_query.v1"
RUNTIME_DOCTOR_SCHEMA_VERSION = "local_runtime_doctor.v1"
SCHEDULER_STATUS_SCHEMA_VERSION = "local_scheduler_status.v1"
SCHEDULER_APPLY_SCHEMA_VERSION = "local_scheduler_apply.v1"
SCHEDULER_RUN_ONCE_SCHEMA_VERSION = "local_scheduler_run_once.v1"
SCHEDULER_ACTIVATION_PREFLIGHT_SCHEMA_VERSION = "local_scheduler_activation_preflight.v1"
SCHEDULER_ACTIVATION_VERIFY_SCHEMA_VERSION = "local_scheduler_activation_verify.v1"
LAUNCHD_LABEL = "com.mybroker.daily-analyst"

DEFAULT_TODAY_OUTPUT = Path("reports/product/today.html")
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
DEFAULT_RUNTIME_DOCTOR_OUTPUT = Path("reports/runtime/local-runtime-doctor.json")
DEFAULT_RUNTIME_DOCTOR_ACTIVATION_OUTPUT = Path("reports/runtime/local-runtime-doctor-activation.json")
DEFAULT_SCHEDULER_STATUS_OUTPUT = Path("reports/runtime/scheduler-status.json")
DEFAULT_SCHEDULER_APPLY_OUTPUT = Path("reports/runtime/scheduler-apply.json")
DEFAULT_SCHEDULER_RUN_ONCE_OUTPUT = Path("reports/runtime/scheduler-run-once.json")
DEFAULT_SCHEDULER_ACTIVATION_PREFLIGHT_OUTPUT = Path("reports/runtime/scheduler-activation-preflight.json")
DEFAULT_SCHEDULER_ACTIVATION_VERIFY_OUTPUT = Path("reports/runtime/scheduler-activation-verify.json")
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


def write_today_surface(
    *,
    scenario_path: str | Path,
    verdict_path: str | Path,
    memory_path: str | Path,
    evidence_path: str | Path,
    brief_path: str | Path,
    output_path: str | Path = DEFAULT_TODAY_OUTPUT,
    archive_manifest_path: str | Path | None = None,
    memory_surface_path: str | Path | None = None,
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
            memory_surface_path=Path(memory_surface_path) if memory_surface_path else None,
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
    memory_surface_path: Path | None = None,
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
