"""Four-switch build wrapper for local development profiles.

Supported toggles:
- debug: on/off
- tests: on/off
- docs: on/off
- clean: on/off
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = REPO_ROOT / "build"
BUILD_DOCS_DIR = BUILD_DIR / "docs"
LOCK_PATH = BUILD_DIR / ".build.lock"
BASELINE_ROOT = REPO_ROOT / "docs" / "baseline"
BASELINE_SNAPSHOTS_ROOT = BASELINE_ROOT / "snapshots"
ACTIVE_BASELINE_PATH = BASELINE_ROOT / "active_baseline.json"
CR_ROOT = REPO_ROOT / "docs" / "change-requests"

PROFILE_MAP = {
    "quick": {"debug": "off", "tests": "off", "docs": "off", "clean": "off"},
    "dev": {"debug": "on", "tests": "on", "docs": "off", "clean": "off"},
    "ci": {"debug": "off", "tests": "on", "docs": "on", "clean": "on"},
    # release intentionally aliases ci for now.
    "release": {"debug": "off", "tests": "on", "docs": "on", "clean": "on"},
    "baseline-sync": {"debug": "off", "tests": "off", "docs": "off", "clean": "off"},
    "cr-prepare": {"debug": "off", "tests": "off", "docs": "off", "clean": "off"},
    "cr-impact-check": {"debug": "off", "tests": "off", "docs": "off", "clean": "off"},
}

STRICT_RELEASE_PROFILES = {"ci", "release"}

ON_OFF = {"on", "off"}

GEN_RUNTIME_SUBDIRS = [
    REPO_ROOT / "gen" / "debug",
    REPO_ROOT / "gen" / "llm",
    REPO_ROOT / "gen" / "pipeline-runs",
    REPO_ROOT / "gen" / "reports",
    REPO_ROOT / "gen" / "tmp",
]

CLEAN_PROTECTED_PATHS = [
    REPO_ROOT / "docs",
    BASELINE_ROOT,
    CR_ROOT,
    REPO_ROOT / "gen" / "docs",
    REPO_ROOT / "reports",
]

REPORT_OUTPUTS = [
    REPO_ROOT / "reports" / "TEST_REPORT.md",
    REPO_ROOT / "reports" / "run_summary_latest.csv",
    REPO_ROOT / "reports" / "test_case_results_latest.csv",
    REPO_ROOT / "reports" / "failing_requirements_latest.csv",
    REPO_ROOT / "reports" / "requirement_status_latest.csv",
]

BASELINE_SOURCE_DOCS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "PUSH_CHECKLIST.md",
    REPO_ROOT / "docs" / "AI_INSTRUCTIONS.md",
    REPO_ROOT / "docs" / "DESIGN_DEVELOPMENT_DOCUMENT.md",
    REPO_ROOT / "docs" / "PRODUCT_CURRENT_STATUS.md",
    REPO_ROOT / "docs" / "PRODUCT_ROADMAP.md",
    REPO_ROOT / "docs" / "QUICK_REFERENCE.md",
    REPO_ROOT / "gen" / "docs" / "00_AI_Product_Development_Approach.md",
    REPO_ROOT / "gen" / "docs" / "document_update_protocol.md",
    REPO_ROOT / "gen" / "docs" / "validation_gates.md",
    REPO_ROOT / "gen" / "docs" / "requirement_test_traceability.json",
]

IMPACT_REQUIRED_HEADERS = [
    "## Changed Documents",
    "## Code Impact",
    "## Test Impact",
    "## Risks and Rollback",
    "## Consistency Updates",
]


class BuildError(RuntimeError):
    """Raised for build-stage hard failures."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _bool_from_on_off(value: str) -> bool:
    return value.strip().lower() == "on"


def _is_repo_relative_safe(path: Path) -> bool:
    root = REPO_ROOT.resolve()
    candidate = path.resolve()
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _clean_directory_contents(path: Path) -> None:
    if not _is_repo_relative_safe(path):
        raise BuildError(f"Refusing to clean path outside repository: {path}")

    path.mkdir(parents=True, exist_ok=True)
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def _paths_overlap(path_a: Path, path_b: Path) -> bool:
    a = path_a.resolve()
    b = path_b.resolve()

    try:
        a.relative_to(b)
        return True
    except ValueError:
        pass

    try:
        b.relative_to(a)
        return True
    except ValueError:
        return False


def _validate_clean_targets(targets: list[Path]) -> None:
    for target in targets:
        if not _is_repo_relative_safe(target):
            raise BuildError(f"Refusing to clean path outside repository: {target}")

        for protected in CLEAN_PROTECTED_PATHS:
            if _paths_overlap(target, protected):
                raise BuildError(
                    "Clean policy violation: target overlaps protected governance/canonical path "
                    f"({target} overlaps {protected})"
                )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _default_baseline_id() -> str:
    return datetime.now().strftime("baseline_%Y%m%d_%H%M%S")


def _build_baseline_snapshot(baseline_id: str) -> dict[str, Any]:
    BASELINE_SNAPSHOTS_ROOT.mkdir(parents=True, exist_ok=True)
    snapshot_root = BASELINE_SNAPSHOTS_ROOT / baseline_id
    source_root = snapshot_root / "source"
    source_root.mkdir(parents=True, exist_ok=True)

    sources: list[dict[str, Any]] = []

    for src in BASELINE_SOURCE_DOCS:
        if not src.exists():
            continue
        rel = src.relative_to(REPO_ROOT)
        dst = source_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        sources.append(
            {
                "path": str(rel).replace("\\", "/"),
                "size_bytes": dst.stat().st_size,
                "sha256": _sha256_file(dst),
            }
        )

    manifest = {
        "baseline_id": baseline_id,
        "created_at": utc_now_iso(),
        "source_count": len(sources),
        "source_root": str(source_root.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sources": sources,
    }
    manifest_path = snapshot_root / "manifest.json"
    _write_json(manifest_path, manifest)

    pointer = {
        "active_baseline_id": baseline_id,
        "updated_at": utc_now_iso(),
        "snapshot_path": str(snapshot_root.relative_to(REPO_ROOT)).replace("\\", "/"),
        "manifest_path": str(manifest_path.relative_to(REPO_ROOT)).replace("\\", "/"),
    }
    _write_json(ACTIVE_BASELINE_PATH, pointer)
    return pointer


def _load_active_baseline() -> dict[str, Any]:
    if not ACTIVE_BASELINE_PATH.exists():
        raise BuildError("Active baseline pointer not found. Run --profile baseline-sync first.")
    return json.loads(ACTIVE_BASELINE_PATH.read_text(encoding="utf-8"))


def _prepare_change_request(cr_id: str, title: str | None, owner: str | None) -> dict[str, Any]:
    active = _load_active_baseline()
    baseline_id = active.get("active_baseline_id")
    if not baseline_id:
        raise BuildError("Active baseline pointer missing active_baseline_id")

    snapshot_root = REPO_ROOT / active.get("snapshot_path", "")
    manifest_path = REPO_ROOT / active.get("manifest_path", "")
    if not snapshot_root.exists() or not manifest_path.exists():
        raise BuildError("Active baseline snapshot files are missing")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_root = snapshot_root / "source"
    if not source_root.exists():
        raise BuildError("Active baseline source root is missing")

    cr_root = CR_ROOT / cr_id
    baseline_copy = cr_root / "baseline-copy"
    proposed = cr_root / "proposed"
    supporting = cr_root / "supporting"

    baseline_copy.mkdir(parents=True, exist_ok=True)
    proposed.mkdir(parents=True, exist_ok=True)
    supporting.mkdir(parents=True, exist_ok=True)

    for source in manifest.get("sources", []):
        rel = Path(source["path"])
        src = source_root / rel
        if not src.exists():
            continue

        dst_base = baseline_copy / rel
        dst_prop = proposed / rel
        dst_base.parent.mkdir(parents=True, exist_ok=True)
        dst_prop.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst_base)
        shutil.copy2(src, dst_prop)

    metadata = {
        "cr_id": cr_id,
        "title": title or "Pending Input",
        "owner": owner or "Pending Input",
        "status": "draft",
        "created_at": utc_now_iso(),
        "baseline_id": baseline_id,
        "impact_analysis_status": "required",
        "implementation_approval": "pending",
    }
    _write_json(cr_root / "metadata.json", metadata)

    impact_template = """# Impact Analysis

## Changed Documents
- Pending Input

## Code Impact
- Pending Input

## Test Impact
- Pending Input

## Risks and Rollback
- Pending Input

## Consistency Updates
- Pending Input
"""

    handoff_template = """# AI Handoff Summary

## Objective
- Pending Input

## In Scope
- Pending Input

## Out of Scope
- Pending Input

## Required Validation
- Pending Input

## Rollback Notes
- Pending Input
"""

    notes_template = """# Implementation Notes

- Keep baseline-copy unchanged.
- Apply all edits only under proposed.
- Update metadata status transitions as review progresses.
"""

    (supporting / "IMPACT_ANALYSIS.md").write_text(impact_template, encoding="utf-8")
    (supporting / "AI_HANDOFF.md").write_text(handoff_template, encoding="utf-8")
    (supporting / "IMPLEMENTATION_NOTES.md").write_text(notes_template, encoding="utf-8")

    return {
        "cr_id": cr_id,
        "path": str(cr_root.relative_to(REPO_ROOT)).replace("\\", "/"),
        "baseline_id": baseline_id,
    }


def _check_cr_impact_gate(cr_id: str) -> dict[str, Any]:
    cr_root = CR_ROOT / cr_id
    metadata_path = cr_root / "metadata.json"
    impact_path = cr_root / "supporting" / "IMPACT_ANALYSIS.md"
    handoff_path = cr_root / "supporting" / "AI_HANDOFF.md"

    if not cr_root.exists():
        raise BuildError(f"CR folder not found: {cr_root}")
    if not metadata_path.exists():
        raise BuildError("CR metadata.json missing")
    if not impact_path.exists():
        raise BuildError("CR supporting/IMPACT_ANALYSIS.md missing")
    if not handoff_path.exists():
        raise BuildError("CR supporting/AI_HANDOFF.md missing")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("status") != "approved":
        raise BuildError("CR status must be 'approved' before implementation")

    impact_text = impact_path.read_text(encoding="utf-8")
    missing_headers = [h for h in IMPACT_REQUIRED_HEADERS if h not in impact_text]
    if missing_headers:
        raise BuildError(f"Impact analysis missing sections: {missing_headers}")

    if "Pending Input" in impact_text:
        raise BuildError("Impact analysis still contains Pending Input placeholders")

    return {
        "cr_id": cr_id,
        "status": "passed",
        "checked_at": utc_now_iso(),
    }


def _acquire_lock() -> bool:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False

    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps({"pid": os.getpid(), "created_at": utc_now_iso()}, indent=2))
    return True


def _release_lock() -> None:
    try:
        if LOCK_PATH.exists():
            LOCK_PATH.unlink()
    except Exception:
        pass


def _run_command(cmd: list[str], timeout_seconds: int, env: dict[str, str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            env=env,
            timeout=timeout_seconds,
            check=False,
        )
        return completed.returncode, "ok"
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout_seconds}s"
    except Exception as exc:
        return 1, str(exc)


def _preflight(toggles: dict[str, str]) -> None:
    if not sys.executable:
        raise BuildError("Python executable not available in current environment")

    if _bool_from_on_off(toggles["tests"]):
        test_runner = REPO_ROOT / "scripts" / "run_all_tests.py"
        if not test_runner.exists():
            raise BuildError(f"Missing test runner: {test_runner}")


def _package_docs(run_summary: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "run_id": run_summary["run_id"],
        "created_at": utc_now_iso(),
        "files": [],
        "warnings": [],
    }

    BUILD_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    def copy_file(src: Path, dst: Path) -> None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        manifest["files"].append(
            {
                "source": str(src.relative_to(REPO_ROOT)).replace("\\", "/"),
                "target": str(dst.relative_to(REPO_ROOT)).replace("\\", "/"),
                "size_bytes": dst.stat().st_size,
            }
        )

    for src in REPORT_OUTPUTS:
        if src.exists():
            copy_file(src, BUILD_DOCS_DIR / "reports" / src.name)
        else:
            manifest["warnings"].append(f"missing source: {src.relative_to(REPO_ROOT)}")

    gen_reports_dir = REPO_ROOT / "gen" / "reports"
    if gen_reports_dir.exists():
        html_files = sorted(gen_reports_dir.glob("*.html"))
        if html_files:
            for html_file in html_files:
                copy_file(html_file, BUILD_DOCS_DIR / "gen-reports" / html_file.name)
        else:
            manifest["warnings"].append("no html reports found under gen/reports")
    else:
        manifest["warnings"].append("missing source directory: gen/reports")

    pipeline_dir = REPO_ROOT / "gen" / "pipeline-runs"
    latest_json = None
    if pipeline_dir.exists():
        json_runs = sorted(pipeline_dir.glob("run_*.json"), key=lambda p: p.stat().st_mtime)
        if json_runs:
            latest_json = json_runs[-1]
            copy_file(latest_json, BUILD_DOCS_DIR / "pipeline" / "latest_run.json")
        else:
            manifest["warnings"].append("no run_*.json found under gen/pipeline-runs")
    else:
        manifest["warnings"].append("missing source directory: gen/pipeline-runs")

    if latest_json is not None:
        manifest["latest_pipeline_json"] = str(latest_json.relative_to(REPO_ROOT)).replace("\\", "/")

    manifest_path = BUILD_DOCS_DIR / "index.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _write_run_summary(summary: dict[str, Any]) -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    json_path = BUILD_DIR / "build_summary_latest.json"
    txt_path = BUILD_DIR / "build_summary_latest.txt"

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        f"run_id: {summary['run_id']}",
        f"started_at: {summary['started_at']}",
        f"ended_at: {summary['ended_at']}",
        f"duration_sec: {summary['duration_sec']}",
        f"status: {summary['status']}",
        f"profile: {summary['profile']}",
        "toggles:",
        f"  debug={summary['toggles']['debug']}",
        f"  tests={summary['toggles']['tests']}",
        f"  docs={summary['toggles']['docs']}",
        f"  clean={summary['toggles']['clean']}",
    ]

    if summary.get("warnings"):
        lines.append("warnings:")
        lines.extend([f"  - {w}" for w in summary["warnings"]])

    if summary.get("errors"):
        lines.append("errors:")
        lines.extend([f"  - {e}" for e in summary["errors"]])

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _resolve_toggles(args: argparse.Namespace) -> tuple[str, dict[str, str]]:
    profile = args.profile or "quick"
    toggles = dict(PROFILE_MAP[profile])

    for key in ("debug", "tests", "docs", "clean"):
        value = getattr(args, key)
        if value is not None:
            toggles[key] = value

    for key, value in toggles.items():
        if value not in ON_OFF:
            raise BuildError(f"Invalid value for {key}: {value}")

    return profile, toggles


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run four-switch build wrapper")
    parser.add_argument("--profile", choices=sorted(PROFILE_MAP.keys()), default="quick")
    parser.add_argument("--debug", choices=sorted(ON_OFF))
    parser.add_argument("--tests", choices=sorted(ON_OFF))
    parser.add_argument("--docs", choices=sorted(ON_OFF))
    parser.add_argument("--clean", choices=sorted(ON_OFF))
    parser.add_argument("--baseline-id")
    parser.add_argument("--cr-id")
    parser.add_argument("--cr-title")
    parser.add_argument("--cr-owner")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    run_id = str(int(time.time()))
    started_at = utc_now_iso()
    start_perf = time.perf_counter()

    summary: dict[str, Any] = {
        "run_id": run_id,
        "started_at": started_at,
        "ended_at": started_at,
        "duration_sec": 0,
        "status": "running",
        "profile": "quick",
        "toggles": {},
        "actions": [],
        "warnings": [],
        "errors": [],
    }

    lock_acquired = False
    exit_code = 0

    try:
        lock_acquired = _acquire_lock()
        if not lock_acquired:
            raise BuildError("Another build is already running (lock file present)")

        profile, toggles = _resolve_toggles(args)
        summary["profile"] = profile
        summary["toggles"] = toggles

        if profile == "baseline-sync":
            baseline_id = args.baseline_id or _default_baseline_id()
            pointer = _build_baseline_snapshot(baseline_id)
            summary["actions"].append("baseline-sync")
            summary["artifacts"] = pointer
            summary["status"] = "ok"
            return 0

        if profile == "cr-prepare":
            if not args.cr_id:
                raise BuildError("--cr-id is required for profile cr-prepare")
            cr_info = _prepare_change_request(args.cr_id, args.cr_title, args.cr_owner)
            summary["actions"].append("cr-prepare")
            summary["artifacts"] = cr_info
            summary["status"] = "ok"
            return 0

        if profile == "cr-impact-check":
            if not args.cr_id:
                raise BuildError("--cr-id is required for profile cr-impact-check")
            gate_info = _check_cr_impact_gate(args.cr_id)
            summary["actions"].append("cr-impact-check")
            summary["artifacts"] = gate_info
            summary["status"] = "ok"
            return 0

        if profile in STRICT_RELEASE_PROFILES:
            if not args.cr_id:
                raise BuildError("--cr-id is required for profile ci/release")
            gate_info = _check_cr_impact_gate(args.cr_id)
            summary["actions"].append("cr-impact-check")
            summary["artifacts"] = {"cr_gate": gate_info}

        _preflight(toggles)

        if _bool_from_on_off(toggles["clean"]):
            clean_targets = [*GEN_RUNTIME_SUBDIRS, BUILD_DOCS_DIR]
            _validate_clean_targets(clean_targets)
            for path in GEN_RUNTIME_SUBDIRS:
                _clean_directory_contents(path)
            _clean_directory_contents(BUILD_DOCS_DIR)
            summary["actions"].append("clean")

        env = os.environ.copy()
        env["AISA_DEBUG"] = "1" if _bool_from_on_off(toggles["debug"]) else "0"
        summary["actions"].append(f"debug:{toggles['debug']}")

        tests_rc = 0
        if _bool_from_on_off(toggles["tests"]):
            tests_rc, detail = _run_command(
                [sys.executable, "-m", "scripts.run_all_tests"],
                timeout_seconds=max(1, args.timeout_seconds),
                env=env,
            )
            summary["actions"].append("tests")
            if tests_rc != 0:
                summary["errors"].append(f"tests failed ({detail})")

        if _bool_from_on_off(toggles["docs"]):
            manifest = _package_docs(summary)
            summary["actions"].append("docs")
            if manifest.get("warnings"):
                summary["warnings"].extend(manifest["warnings"])

        if tests_rc != 0:
            exit_code = tests_rc
            summary["status"] = "failed"
        elif summary["warnings"]:
            summary["status"] = "unstable"
        else:
            summary["status"] = "ok"

    except BuildError as exc:
        exit_code = 2
        summary["status"] = "failed"
        summary["errors"].append(str(exc))
    except Exception as exc:
        exit_code = 1
        summary["status"] = "failed"
        summary["errors"].append(f"unexpected error: {exc}")
    finally:
        summary["ended_at"] = utc_now_iso()
        summary["duration_sec"] = round(time.perf_counter() - start_perf, 3)
        _write_run_summary(summary)
        if lock_acquired:
            _release_lock()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
