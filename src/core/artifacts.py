"""Helpers for generated runtime artifacts under gen/."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


GEN_ROOT = Path("gen")
GEN_SUBDIRS = {
    "feature-docs": GEN_ROOT / "feature-docs",
    "pipeline-runs": GEN_ROOT / "pipeline-runs",
    "debug": GEN_ROOT / "debug",
    "llm": GEN_ROOT / "llm",
    "reports": GEN_ROOT / "reports",
    "tmp": GEN_ROOT / "tmp",
}


def ensure_gen_dirs() -> None:
    for path in GEN_SUBDIRS.values():
        path.mkdir(parents=True, exist_ok=True)


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def sanitize_name(value: str | None, default: str = "artifact") -> str:
    text = (value or "").strip() or default
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", text)


def write_text_artifact(subdir: str, filename: str, content: str) -> Path:
    ensure_gen_dirs()
    base = GEN_SUBDIRS.get(subdir, GEN_ROOT / subdir)
    base.mkdir(parents=True, exist_ok=True)
    path = base / filename
    path.write_text(content, encoding="utf-8")
    return path


def write_json_artifact(subdir: str, filename: str, payload: Any) -> Path:
    ensure_gen_dirs()
    base = GEN_SUBDIRS.get(subdir, GEN_ROOT / subdir)
    base.mkdir(parents=True, exist_ok=True)
    path = base / filename
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path