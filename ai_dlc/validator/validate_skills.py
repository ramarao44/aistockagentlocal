#!/usr/bin/env python3
"""AI-DLC Skill Validator - Enterprise Edition.

Validates all skills against governance rules before execution.
Prevents drift, PSC violations, role bypass, and unsafe outputs.
"""

import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "ai_dlc" / "validator" / "skill-validator.yaml"
SKILLS_DIR = REPO_ROOT / "ai_dlc" / "skills"


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_skill(skill_path: Path, validator: dict) -> bool:
    """Validate a single skill file against all governance rules."""
    skill = load_yaml(skill_path).get("skill", {})
    errors = []
    warns = []

    checks = validator.get("validator", {}).get("checks", {})

    # 1. Schema Validation
    required_keys = checks.get("schema-validation", {}).get("required_keys", [])
    for key in required_keys:
        if key not in skill:
            errors.append(f"Missing required key: {key}")

    # Early exit if schema is broken
    if errors:
        print(f"❌ Skill '{skill.get('name', 'unknown')}' FAILED schema validation:")
        for e in errors:
            print(f"   - {e}")
        return False

    skill_name = skill.get("name", "unknown")
    role = skill.get("role", "unknown")
    writes_to = skill.get("writes-to", [])
    constraints = skill.get("constraints", [])

    # 2. Protected Path Validation
    forbidden = checks.get("protected-paths", {}).get("forbidden", [])
    for path in writes_to:
        for forbidden_path in forbidden:
            if path == forbidden_path or path.startswith(forbidden_path.rstrip("/") + "/"):
                errors.append(f"Forbidden write path: {path}")

    # 3. PSC Boundary Validation
    psc_forbidden = checks.get("psc-boundary", {}).get("forbidden_keywords", [])
    for constraint in constraints:
        for keyword in psc_forbidden:
            if keyword.lower() in constraint.lower():
                errors.append(f"PSC violation: '{keyword}' in constraint")

    # 4. Role Boundary Validation
    role_perms = checks.get("role-boundary", {}).get("role_permissions", {})
    allowed_writes = role_perms.get(role, {}).get("allowed_writes", [])
    for path in writes_to:
        allowed = False
        for allowed_prefix in allowed_writes:
            if path == allowed_prefix.rstrip("/") or path.startswith(allowed_prefix.rstrip("/") + "/"):
                allowed = True
                break
        if not allowed and allowed_writes:
            warns.append(f"Role '{role}' typically writes to {allowed_writes}, not '{path}'")

    # 5. Output
    if errors:
        print(f"❌ Skill '{skill_name}' FAILED validation:")
        for e in errors:
            print(f"   - {e}")
        return False
    elif warns:
        print(f"⚠ Skill '{skill_name}' PASSED with warnings:")
        for w in warns:
            print(f"   - {w}")
        return True
    else:
        print(f"✔ Skill '{skill_name}' PASSED validation (role: {role}).")
        return True


def main() -> int:
    """Validate all skills in the skills directory."""
    if not VALIDATOR_PATH.exists():
        print(f"❌ Validator config not found: {VALIDATOR_PATH}")
        return 1

    validator = load_yaml(VALIDATOR_PATH)
    all_passed = True

    if not SKILLS_DIR.exists():
        print(f"❌ Skills directory not found: {SKILLS_DIR}")
        return 1

    for file in sorted(os.listdir(SKILLS_DIR)):
        if file.endswith(".yaml") and file != "skill-validator.yaml":
            skill_path = SKILLS_DIR / file
            if not validate_skill(skill_path, validator):
                all_passed = False

    if all_passed:
        print("\n✅ All skills validated successfully.")
        return 0
    else:
        print("\n❌ One or more skills failed validation.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())