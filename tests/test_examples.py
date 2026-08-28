from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run-examples.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_examples", RUNNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_has_twenty_cases_covering_all_tools_and_outcome_classes() -> None:
    catalog = json.loads((ROOT / "examples" / "cases.json").read_text(encoding="utf-8"))
    cases = catalog["cases"]

    assert len(cases) == 20
    assert len({case["id"] for case in cases}) == 20
    assert {case["tool"] for case in cases} == {
        "verify_artifact",
        "audit_claims",
        "audit_citations",
        "summarize_verification",
        "check_contract",
        "evaluate_completion",
        "format_blockers",
        "build_release_receipt",
    }
    assert {case["expected"]["status"] for case in cases} >= {"PASS", "FAIL", "BLOCKED", "UNVERIFIED"}


def test_all_examples_match_their_declared_outcomes() -> None:
    runner = _load_runner()
    result = runner.run_catalog(ROOT / "examples" / "cases.json")

    assert result["case_count"] == 20
    assert result["passed"] == 20
    assert result["failed"] == 0
