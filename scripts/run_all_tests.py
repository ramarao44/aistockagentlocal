import csv
import ast
import glob
import importlib
import inspect
import io
import json
import os
import runpy
import sys
import time
import traceback
import unittest
from datetime import datetime, timezone


ROOT = r"C:\RAMARAO\Learning\AI\N8N\aistockagentlocal"
REPORTS_DIR = os.path.join(ROOT, "reports")
TRACEABILITY_PATH = os.path.join(ROOT, "gen", "docs", "requirement_test_traceability.json")


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_traceability() -> dict:
    if not os.path.exists(TRACEABILITY_PATH):
        return {
            "requirements": [],
            "test_case_map": {},
            "test_module_map": {},
        }
    with open(TRACEABILITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def map_requirements(test_case_id: str, module_name: str, traceability: dict) -> list[str]:
    case_map = traceability.get("test_case_map", {})
    module_map = traceability.get("test_module_map", {})

    reqs = case_map.get(test_case_id, [])
    if reqs:
        return sorted(set(reqs))

    reqs = module_map.get(module_name, [])
    return sorted(set(reqs))


class CaseCaptureResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self._start_times = {}
        self.rows = []

    def startTest(self, test):
        self._start_times[test.id()] = time.perf_counter()
        super().startTest(test)

    def _duration_ms(self, test) -> int:
        start = self._start_times.pop(test.id(), time.perf_counter())
        return int((time.perf_counter() - start) * 1000)

    def addSuccess(self, test):
        self.rows.append({
            "test_case_id": test.id(),
            "module": test.__class__.__module__,
            "test_file": test.__class__.__module__.replace(".", "/") + ".py",
            "result": "passed",
            "duration_ms": self._duration_ms(test),
            "message": "",
        })
        super().addSuccess(test)

    def addFailure(self, test, err):
        self.rows.append({
            "test_case_id": test.id(),
            "module": test.__class__.__module__,
            "test_file": test.__class__.__module__.replace(".", "/") + ".py",
            "result": "failed",
            "duration_ms": self._duration_ms(test),
            "message": self._exc_info_to_string(err, test).strip(),
        })
        super().addFailure(test, err)

    def addError(self, test, err):
        self.rows.append({
            "test_case_id": test.id(),
            "module": test.__class__.__module__,
            "test_file": test.__class__.__module__.replace(".", "/") + ".py",
            "result": "failed",
            "duration_ms": self._duration_ms(test),
            "message": self._exc_info_to_string(err, test).strip(),
        })
        super().addError(test, err)

    def addSkip(self, test, reason):
        self.rows.append({
            "test_case_id": test.id(),
            "module": test.__class__.__module__,
            "test_file": test.__class__.__module__.replace(".", "/") + ".py",
            "result": "skipped",
            "duration_ms": self._duration_ms(test),
            "message": reason,
        })
        super().addSkip(test, reason)


def run_script_module(module_name: str, file_path: str) -> list[dict]:
    rows = []

    # Prefer explicit test_ callables for granular requirement mapping.
    # Parse source first so smoke scripts are not imported unless needed.
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    test_func_names = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            if len(node.args.args) == 0 and node.args.vararg is None and node.args.kwarg is None:
                test_func_names.append(node.name)

    if test_func_names:
        module = importlib.import_module(module_name)
        for name in sorted(test_func_names):
            fn = getattr(module, name)
            if not inspect.isfunction(fn):
                continue
            start = time.perf_counter()
            try:
                fn()
                rows.append(
                    {
                        "test_case_id": f"{module_name}::{name}",
                        "module": module_name,
                        "test_file": file_path.replace("\\", "/"),
                        "result": "passed",
                        "duration_ms": int((time.perf_counter() - start) * 1000),
                        "message": "",
                    }
                )
            except Exception:
                rows.append(
                    {
                        "test_case_id": f"{module_name}::{name}",
                        "module": module_name,
                        "test_file": file_path.replace("\\", "/"),
                        "result": "failed",
                        "duration_ms": int((time.perf_counter() - start) * 1000),
                        "message": traceback.format_exc().strip(),
                    }
                )
        return rows

    # Fallback for pure smoke scripts with no test_ callables.
    test_case_id = f"{module_name}::module"
    start = time.perf_counter()
    try:
        runpy.run_module(module_name, run_name="__main__")
        rows.append(
            {
                "test_case_id": test_case_id,
                "module": module_name,
                "test_file": file_path.replace("\\", "/"),
                "result": "passed",
                "duration_ms": int((time.perf_counter() - start) * 1000),
                "message": "",
            }
        )
    except Exception:
        rows.append(
            {
                "test_case_id": test_case_id,
                "module": module_name,
                "test_file": file_path.replace("\\", "/"),
                "result": "failed",
                "duration_ms": int((time.perf_counter() - start) * 1000),
                "message": traceback.format_exc().strip(),
            }
        )
    return rows


def run_unittest_module(module_name: str) -> list[dict]:
    loader = unittest.defaultTestLoader
    suite = loader.loadTestsFromName(module_name)
    runner = unittest.TextTestRunner(
        stream=io.StringIO(),
        verbosity=1,
        resultclass=CaseCaptureResult,
    )
    result = runner.run(suite)
    return result.rows


def write_csv(path: str, rows: list[dict], headers: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in headers})


def build_requirement_rows(
    traceability: dict,
    rows: list[dict],
    run_id: str,
    timestamp: str,
) -> tuple[list[dict], list[dict]]:
    requirements = traceability.get("requirements", [])
    test_case_map = traceability.get("test_case_map", {})
    module_map = traceability.get("test_module_map", {})

    failing_by_req = {}
    by_req = {}
    for req in requirements:
        req_id = req.get("requirement_id")
        by_req[req_id] = {
            "run_id": run_id,
            "updated_at": timestamp,
            "requirement_id": req_id,
            "feature": req.get("feature", ""),
            "requirement_title": req.get("title", ""),
            "status": req.get("status", "Pending Input"),
            "evidence_quality": req.get("evidence_quality", "pending"),
            "owner": req.get("owner", "Pending Input"),
            "mapped_test_count": 0,
            "passing_test_count": 0,
        }

    for row in rows:
        mapped = row.get("requirement_ids", [])
        if not mapped:
            mapped = test_case_map.get(row["test_case_id"], [])
        if not mapped:
            mapped = module_map.get(row["module"], [])

        for req_id in mapped:
            if req_id not in by_req:
                continue
            by_req[req_id]["mapped_test_count"] += 1
            if row["result"] == "passed":
                by_req[req_id]["passing_test_count"] += 1
            if row["result"] == "failed":
                failing_by_req.setdefault(req_id, []).append(row["test_case_id"])

    for req_id, failing_tests in failing_by_req.items():
        by_req[req_id]["status"] = "Not Working"

    failing_rows = []
    for req_id, failing_tests in sorted(failing_by_req.items()):
        failing_rows.append(
            {
                "run_id": run_id,
                "requirement_id": req_id,
                "failing_test_case_ids": ";".join(sorted(set(failing_tests))),
                "status_impact": "Not Working",
            }
        )

    return sorted(by_req.values(), key=lambda x: x["requirement_id"]), failing_rows


def write_markdown_summary(
    timestamp: str,
    executed: list[str],
    rows: list[dict],
    failing_requirements: list[dict],
    gate_verdict: str,
) -> None:
    passed = sum(1 for r in rows if r["result"] == "passed")
    failed = sum(1 for r in rows if r["result"] == "failed")
    skipped = sum(1 for r in rows if r["result"] == "skipped")

    lines = [
        f"# Test Report - {timestamp}",
        "",
        "## Run Scope",
        "- Designated run type: pre-push mandatory suite",
        "- Commands:",
    ]
    lines.extend([f"  - `{cmd}`" for cmd in executed])
    lines.extend(
        [
            "",
            "## Results Summary",
            f"- Total test items: {len(rows)}",
            f"- Passed: {passed}",
            f"- Failed: {failed}",
            f"- Skipped: {skipped}",
            f"- Gate verdict: {gate_verdict}",
            "",
            "## Failing Test Cases",
        ]
    )

    failed_rows = [r for r in rows if r["result"] == "failed"]
    if not failed_rows:
        lines.append("- None")
    else:
        for row in failed_rows:
            lines.append(f"- {row['test_case_id']}")

    lines.extend(["", "## Failing Requirements"])
    if not failing_requirements:
        lines.append("- None")
    else:
        for req in failing_requirements:
            lines.append(
                f"- {req['requirement_id']} (tests: {req['failing_test_case_ids']})"
            )

    out_path = os.path.join(REPORTS_DIR, "TEST_REPORT.md")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    os.chdir(ROOT)
    sys.path.insert(0, ROOT)

    traceability = load_traceability()
    timestamp = iso_now()
    run_id = str(int(time.time()))

    script_tests = sorted(glob.glob("scripts/test_*.py"))
    unittest_tests = sorted(glob.glob("tests/test_*.py"))

    executed_commands = []
    rows = []

    print("FOUND", len(script_tests), "SCRIPT TEST MODULES")
    for path in script_tests:
        name = os.path.splitext(os.path.basename(path))[0]
        module = f"scripts.{name}"
        executed_commands.append(f"python -m {module}")
        print("===", module, "===")
        script_rows = run_script_module(module, path)
        for row in script_rows:
            row["requirement_ids"] = map_requirements(row["test_case_id"], row["module"], traceability)
            rows.append(row)
        print("RESULT", ", ".join(sorted({r["result"].upper() for r in script_rows})))

    print("FOUND", len(unittest_tests), "UNITTEST MODULES")
    for path in unittest_tests:
        name = os.path.splitext(path.replace("\\", "/"))[0].replace("/", ".")
        executed_commands.append(f"python -m unittest {name}")
        print("===", name, "===")
        for row in run_unittest_module(name):
            row["requirement_ids"] = map_requirements(row["test_case_id"], row["module"], traceability)
            rows.append(row)

    for row in rows:
        row["requirement_ids"] = sorted(set(row.get("requirement_ids", [])))
        row["requirement_ids_text"] = ";".join(row["requirement_ids"])

    failed = sum(1 for r in rows if r["result"] == "failed")
    gate_verdict = "PASS" if failed == 0 else "FAIL"

    requirement_rows, failing_requirement_rows = build_requirement_rows(traceability, rows, run_id, timestamp)

    write_csv(
        os.path.join(REPORTS_DIR, "run_summary_latest.csv"),
        [
            {
                "run_id": run_id,
                "timestamp": timestamp,
                "total": len(rows),
                "passed": sum(1 for r in rows if r["result"] == "passed"),
                "failed": failed,
                "skipped": sum(1 for r in rows if r["result"] == "skipped"),
                "gate_verdict": gate_verdict,
            }
        ],
        ["run_id", "timestamp", "total", "passed", "failed", "skipped", "gate_verdict"],
    )

    write_csv(
        os.path.join(REPORTS_DIR, "test_case_results_latest.csv"),
        rows,
        [
            "test_case_id",
            "module",
            "test_file",
            "result",
            "duration_ms",
            "requirement_ids_text",
            "message",
        ],
    )

    write_csv(
        os.path.join(REPORTS_DIR, "failing_requirements_latest.csv"),
        failing_requirement_rows,
        ["run_id", "requirement_id", "failing_test_case_ids", "status_impact"],
    )

    write_csv(
        os.path.join(REPORTS_DIR, "requirement_status_latest.csv"),
        requirement_rows,
        [
            "run_id",
            "updated_at",
            "requirement_id",
            "feature",
            "requirement_title",
            "status",
            "evidence_quality",
            "owner",
            "mapped_test_count",
            "passing_test_count",
        ],
    )

    write_markdown_summary(timestamp, executed_commands, rows, failing_requirement_rows, gate_verdict)

    print("RUN_ID", run_id)
    print("TOTAL", len(rows), "FAILED", failed, "GATE", gate_verdict)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
