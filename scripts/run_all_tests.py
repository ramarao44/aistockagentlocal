import csv
import ast
import glob
import importlib
import inspect
import io
import os
import runpy
import sys
import time
import traceback
import unittest
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(ROOT, "reports")


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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

    # Prefer explicit test_ callables to preserve test-level evidence.
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


def build_module_status_rows(rows: list[dict], run_id: str, timestamp: str) -> list[dict]:
    by_module = {}
    for row in rows:
        module = row["module"]
        if module not in by_module:
            by_module[module] = {
                "run_id": run_id,
                "updated_at": timestamp,
                "module": module,
                "total_test_count": 0,
                "passing_test_count": 0,
                "failing_test_count": 0,
                "skipped_test_count": 0,
                "outcome": "Passed",
                "status_impact": "Working",
            }

        by_module[module]["total_test_count"] += 1
        if row["result"] == "passed":
            by_module[module]["passing_test_count"] += 1
        elif row["result"] == "failed":
            by_module[module]["failing_test_count"] += 1
            by_module[module]["outcome"] = "Failed"
            by_module[module]["status_impact"] = "Not Working"
        else:
            by_module[module]["skipped_test_count"] += 1
            if by_module[module]["outcome"] == "Passed":
                by_module[module]["outcome"] = "Partial"

    return sorted(by_module.values(), key=lambda x: x["module"])


def write_markdown_summary(
    timestamp: str,
    executed: list[str],
    rows: list[dict],
    module_rows: list[dict],
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

    outcome_counts = {}
    for row in module_rows:
        outcome = row.get("outcome", "Unknown")
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

    lines.extend(["", "## Module Outcomes"])
    lines.append(f"- Passed: {outcome_counts.get('Passed', 0)}")
    lines.append(f"- Failed: {outcome_counts.get('Failed', 0)}")
    if outcome_counts.get("Partial", 0):
        lines.append(f"- Partial: {outcome_counts.get('Partial', 0)}")

    failed_modules = [r for r in module_rows if r.get("outcome") == "Failed"]
    lines.extend(["", "## Failed Modules"])
    if not failed_modules:
        lines.append("- None")
    else:
        for module in failed_modules:
            lines.append(
                f"- {module['module']} (failing tests: {module['failing_test_count']})"
            )

    out_path = os.path.join(REPORTS_DIR, "TEST_REPORT.md")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    os.chdir(ROOT)
    sys.path.insert(0, ROOT)

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
        rows.extend(script_rows)
        print("RESULT", ", ".join(sorted({r["result"].upper() for r in script_rows})))

    print("FOUND", len(unittest_tests), "UNITTEST MODULES")
    for path in unittest_tests:
        name = os.path.splitext(path.replace("\\", "/"))[0].replace("/", ".")
        executed_commands.append(f"python -m unittest {name}")
        print("===", name, "===")
        rows.extend(run_unittest_module(name))

    failed = sum(1 for r in rows if r["result"] == "failed")
    gate_verdict = "PASS" if failed == 0 else "FAIL"

    module_rows = build_module_status_rows(rows, run_id, timestamp)
    failing_rows = [
        {
            "run_id": run_id,
            "test_case_id": row["test_case_id"],
            "module": row["module"],
            "test_file": row["test_file"],
            "duration_ms": row["duration_ms"],
            "message": row["message"],
        }
        for row in rows
        if row["result"] == "failed"
    ]

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
            "message",
        ],
    )

    write_csv(
        os.path.join(REPORTS_DIR, "failing_test_cases_latest.csv"),
        failing_rows,
        ["run_id", "test_case_id", "module", "test_file", "duration_ms", "message"],
    )

    write_csv(
        os.path.join(REPORTS_DIR, "module_status_latest.csv"),
        module_rows,
        [
            "run_id",
            "updated_at",
            "module",
            "total_test_count",
            "passing_test_count",
            "failing_test_count",
            "skipped_test_count",
            "outcome",
            "status_impact",
        ],
    )

    write_markdown_summary(
        timestamp,
        executed_commands,
        rows,
        module_rows,
        gate_verdict,
    )

    print("RUN_ID", run_id)
    print("TOTAL", len(rows), "FAILED", failed, "GATE", gate_verdict)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
