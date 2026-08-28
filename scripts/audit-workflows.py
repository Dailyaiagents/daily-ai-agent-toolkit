#!/usr/bin/env python3
"""Enforce immutable action references and explicit workflow permissions."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"^[0-9a-f]{40}$")


def main() -> int:
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    if not workflows:
        raise SystemExit("workflow-audit FAIL: no workflows")
    failures: list[str] = []
    uses_count = 0
    for workflow in workflows:
        text = workflow.read_text(encoding="utf-8")
        if "permissions:" not in text:
            failures.append(f"{workflow.name}: explicit permissions missing")
        for line_number, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped.startswith("uses:") and not stripped.startswith("- uses:"):
                continue
            uses_count += 1
            value = stripped.split("uses:", 1)[1].strip()
            if value.startswith("./"):
                continue
            if "@" not in value or not SHA.fullmatch(value.rsplit("@", 1)[1].split()[0]):
                failures.append(f"{workflow.name}:{line_number}: action is not SHA-pinned")
    if uses_count == 0:
        failures.append("no action references found")
    if failures:
        raise SystemExit("workflow-audit FAIL:\n" + "\n".join(failures))
    print(f"workflow-audit=PASS workflows={len(workflows)} actions={uses_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
