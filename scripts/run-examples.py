#!/usr/bin/env python3
"""Run the public deterministic example catalog against the MCP core functions."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Callable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "servers" / "evidence-gate" / "src"))
sys.path.insert(0, str(REPOSITORY_ROOT / "servers" / "release-gate" / "src"))

from dailyai_evidence_gate import core as evidence_core  # noqa: E402
from dailyai_release_gate import core as release_core  # noqa: E402


Tool = Callable[[Path, dict[str, Any]], dict[str, Any]]


def _verify_artifact(root: Path, values: dict[str, Any]) -> dict[str, Any]:
    return evidence_core.verify_artifact(root, **values)


def _audit_claims(root: Path, values: dict[str, Any]) -> dict[str, Any]:
    return evidence_core.audit_claims(root, **values)


def _audit_citations(root: Path, values: dict[str, Any]) -> dict[str, Any]:
    return evidence_core.audit_citations(root, **values)


def _summarize_verification(root: Path, values: dict[str, Any]) -> dict[str, Any]:
    return evidence_core.summarize_verification(root=root, **values)


def _check_contract(root: Path, values: dict[str, Any]) -> dict[str, Any]:
    return release_core.check_contract(root, **values)


def _evaluate_completion(root: Path, values: dict[str, Any]) -> dict[str, Any]:
    return release_core.evaluate_completion(root=root, **values)


def _format_blockers(_root: Path, values: dict[str, Any]) -> dict[str, Any]:
    return release_core.format_blockers(**values)


def _build_release_receipt(root: Path, values: dict[str, Any]) -> dict[str, Any]:
    return release_core.build_release_receipt(root, **values)


TOOLS: dict[str, Tool] = {
    "verify_artifact": _verify_artifact,
    "audit_claims": _audit_claims,
    "audit_citations": _audit_citations,
    "summarize_verification": _summarize_verification,
    "check_contract": _check_contract,
    "evaluate_completion": _evaluate_completion,
    "format_blockers": _format_blockers,
    "build_release_receipt": _build_release_receipt,
}


def _write_fixtures(root: Path, fixtures: dict[str, str]) -> None:
    for relative_path, content in fixtures.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _mismatches(receipt: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []
    for field in ("status", "checked"):
        if field in expected and receipt.get(field) != expected[field]:
            mismatches.append(f"{field}: expected {expected[field]!r}, got {receipt.get(field)!r}")

    findings = receipt.get("findings", [])
    if "finding_count" in expected and len(findings) != expected["finding_count"]:
        mismatches.append(f"finding_count: expected {expected['finding_count']}, got {len(findings)}")
    if "finding_codes" in expected:
        actual_codes = [finding.get("code") for finding in findings if "code" in finding]
        if actual_codes != expected["finding_codes"]:
            mismatches.append(f"finding_codes: expected {expected['finding_codes']!r}, got {actual_codes!r}")
    if "finding_statuses" in expected:
        actual_statuses = [finding.get("status") for finding in findings]
        if actual_statuses != expected["finding_statuses"]:
            mismatches.append(f"finding_statuses: expected {expected['finding_statuses']!r}, got {actual_statuses!r}")
    return mismatches


def run_catalog(catalog_path: Path) -> dict[str, Any]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    for case in catalog["cases"]:
        with tempfile.TemporaryDirectory(prefix="dailyai-example-") as temporary:
            root = Path(temporary)
            _write_fixtures(root, case.get("fixtures", {}))
            receipt = TOOLS[case["tool"]](root, case["input"])
            mismatches = _mismatches(receipt, case["expected"])
        results.append(
            {
                "id": case["id"],
                "tool": case["tool"],
                "expected_status": case["expected"]["status"],
                "actual_status": receipt.get("status"),
                "passed": not mismatches,
                "mismatches": mismatches,
            }
        )

    return {
        "schema_version": catalog["schema_version"],
        "case_count": len(results),
        "passed": sum(result["passed"] for result in results),
        "failed": sum(not result["passed"] for result in results),
        "tools": dict(sorted(Counter(result["tool"] for result in results).items())),
        "declared_statuses": dict(sorted(Counter(result["expected_status"] for result in results).items())),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=REPOSITORY_ROOT / "examples" / "cases.json")
    parser.add_argument("--json", action="store_true", help="emit the stable machine-readable summary")
    args = parser.parse_args()

    summary = run_catalog(args.catalog)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        for result in summary["results"]:
            marker = "PASS" if result["passed"] else "FAIL"
            print(f"{marker} {result['id']} ({result['actual_status']})")
            for mismatch in result["mismatches"]:
                print(f"  {mismatch}")
        print(f"\n{summary['passed']}/{summary['case_count']} examples matched declared outcomes")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
