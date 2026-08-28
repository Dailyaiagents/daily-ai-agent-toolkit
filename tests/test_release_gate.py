import json
from pathlib import Path

from dailyai_evidence_gate import core as evidence_core
from dailyai_release_gate import core


def test_contract_completion_and_receipt(tmp_path: Path) -> None:
    (tmp_path / "proof.txt").write_text("proof", encoding="utf-8")
    (tmp_path / "contract.json").write_text(
        json.dumps({"requirements": [{"id": "r1", "evidence_paths": ["proof.txt"]}]}),
        encoding="utf-8",
    )
    assert core.check_contract(tmp_path, "contract.json")["status"] == "PASS"
    proof_receipt = evidence_core.verify_artifact(tmp_path, "proof.txt")
    result = core.evaluate_completion(
        [{"id": "r1"}],
        [{"requirement_id": "r1", "status": "PASS", "evidence_refs": ["proof.txt"], "receipt": proof_receipt}],
        tmp_path,
    )
    assert result["status"] == "PASS"
    release_receipt = core.build_release_receipt(tmp_path, [proof_receipt], ["proof.txt"])
    assert release_receipt["status"] == "PASS"


def test_missing_opaque_and_empty_evidence_never_passes(tmp_path: Path) -> None:
    result = core.evaluate_completion([{"id": "r1"}], [])
    assert result["status"] == "UNVERIFIED"
    opaque = core.evaluate_completion(
        [{"id": "r1"}],
        [{"requirement_id": "r1", "status": "PASS", "evidence_refs": ["proof.txt"]}],
    )
    assert opaque["status"] == "UNVERIFIED"
    assert core.evaluate_completion([], [])["status"] == "UNVERIFIED"
    assert core.format_blockers([])["status"] == "UNVERIFIED"
    assert core.build_release_receipt(tmp_path, [{"status": "PASS"}], [])["status"] == "UNVERIFIED"


def test_fabricated_pass_receipt_is_reverified(tmp_path: Path) -> None:
    fabricated = {
        "schema_version": "dailyai.evidence-gate-receipt/v1",
        "tool": "verify_artifact",
        "status": "PASS",
        "generated_at": "2026-08-27T00:00:00+00:00",
        "checked": 1,
        "findings": [],
        "limitations": [],
        "artifact": {"path": "proof.txt", "sha256": "0" * 64},
    }
    result = core.evaluate_completion(
        [{"id": "r1"}],
        [{"requirement_id": "r1", "status": "PASS", "evidence_refs": ["proof.txt"], "receipt": fabricated}],
        tmp_path,
    )
    assert result["status"] == "UNVERIFIED"
    assert result["findings"][0]["code"] == "receipt_artifact_digest_mismatch"
    oversized_receipt = {
        "schema_version": "dailyai.release-gate-receipt/v1",
        "tool": "build_release_receipt",
        "status": "PASS",
        "generated_at": "2026-08-27T00:00:00+00:00",
        "findings": [],
        "limitations": [],
        "artifacts": [{"path": f"proof-{index}.txt", "sha256": "0" * 64} for index in range(core.MAX_PATH_REFERENCES + 1)],
    }
    oversized = core.evaluate_completion(
        [{"id": "r1"}],
        [{"requirement_id": "r1", "status": "PASS", "evidence_refs": ["proof.txt"], "receipt": oversized_receipt}],
        tmp_path,
    )
    assert oversized["status"] == "UNVERIFIED"


def test_blockers_are_explicit() -> None:
    result = core.evaluate_completion([{"id": "r1"}], [])
    blockers = core.format_blockers(result["findings"])
    assert blockers["status"] == "BLOCKED"
    assert blockers["findings"][0]["requirement_id"] == "r1"


def test_malformed_contract_and_duplicate_ids_fail(tmp_path: Path) -> None:
    (tmp_path / "malformed.json").write_text(json.dumps({"requirements": [1]}), encoding="utf-8")
    assert core.check_contract(tmp_path, "malformed.json")["status"] == "FAIL"
    duplicate = core.evaluate_completion([{"id": "same"}, {"id": "same"}], [])
    assert duplicate["status"] == "FAIL"


def test_contract_symlink_escapes_are_rejected(tmp_path: Path) -> None:
    outside_directory = tmp_path.parent / "release-outside"
    outside_directory.mkdir()
    (outside_directory / "proof.txt").write_text("proof", encoding="utf-8")
    (tmp_path / "outside-link").symlink_to(outside_directory, target_is_directory=True)
    (tmp_path / "contract.json").write_text(
        json.dumps({"requirements": [{"id": "r1", "evidence_paths": ["outside-link/proof.txt"]}]}),
        encoding="utf-8",
    )
    assert core.check_contract(tmp_path, "contract.json")["status"] == "FAIL"


def test_contract_request_wide_path_limit(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "contract.json").write_text(
        json.dumps(
            {
                "requirements": [
                    {"id": "r1", "evidence_paths": ["a.txt", "b.txt"]}
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(core, "MAX_PATH_REFERENCES", 1)
    receipt = core.check_contract(tmp_path, "contract.json")
    assert receipt["status"] == "FAIL"
    assert receipt["findings"][0]["code"] == "request_path_limit_exceeded"
