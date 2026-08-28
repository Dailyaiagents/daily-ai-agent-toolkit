#!/usr/bin/env python3
"""Run the public failure -> correction -> receipt demonstration."""

from __future__ import annotations

import json
import argparse
import sys
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "servers" / "evidence-gate" / "src"))
sys.path.insert(0, str(REPOSITORY_ROOT / "servers" / "release-gate" / "src"))

from dailyai_evidence_gate import core as evidence_core  # noqa: E402
from dailyai_release_gate import core as release_core  # noqa: E402


def _stable(receipt: dict[str, object]) -> dict[str, object]:
    """Remove the runtime timestamp so the demonstration output is reproducible."""
    return {key: value for key, value in receipt.items() if key != "generated_at"}


def _show(title: str, receipt: dict[str, object]) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(_stable(receipt), indent=2, sort_keys=True))


def run_demo() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="dailyai-demo-") as temporary:
        root = Path(temporary)
        report = root / "release-report.md"
        report.write_text("", encoding="utf-8")

        first = evidence_core.verify_artifact(
            root,
            "release-report.md",
            required_terms=["Verification: PASS"],
        )
        blockers = release_core.format_blockers(
            [{"id": "release-report", "status": first["status"], "code": "required_artifact_invalid"}]
        )
        report.write_text(
            "# Release report\n\nVerification: PASS\n\nScope: local deterministic demonstration.\n",
            encoding="utf-8",
        )
        second = evidence_core.verify_artifact(
            root,
            "release-report.md",
            required_terms=["Verification: PASS"],
        )
        receipt = release_core.build_release_receipt(
            root,
            checks=[second],
            artifacts=["release-report.md"],
        )
        return {
            "schema_version": "dailyai.demo-sequence/v1",
            "first": _stable(first),
            "blockers": _stable(blockers),
            "second": _stable(second),
            "receipt": _stable(receipt),
            "status": "PASS"
            if first["status"] == "FAIL" and receipt["status"] == "PASS"
            else "FAIL",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_demo()
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        _show("1. Incomplete evidence is rejected", result["first"])
        _show("2. The failed check becomes an explicit blocker", result["blockers"])
        _show("3. Add the evidence and rerun the same check", result["second"])
        _show("4. Retain a scoped release receipt", result["receipt"])
        print("\nThe receipt does not publish, deploy, or approve the release.")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
