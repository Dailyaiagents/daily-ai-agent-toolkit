from pathlib import Path

from dailyai_evidence_gate import core


def test_artifact_rules_and_path_boundary(tmp_path: Path) -> None:
    artifact = tmp_path / "report.md"
    artifact.write_text("result\n", encoding="utf-8")
    assert core.verify_artifact(tmp_path, "report.md")["status"] == "PASS"
    assert core.verify_artifact(tmp_path, "report.md", forbidden_terms=["result"])["status"] == "FAIL"
    assert core.verify_artifact(tmp_path, "missing.md")["status"] == "FAIL"
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    assert core.verify_artifact(tmp_path, str(outside))["status"] == "FAIL"


def test_symlink_file_and_directory_escapes_are_rejected(tmp_path: Path) -> None:
    outside_directory = tmp_path.parent / "outside-directory"
    outside_directory.mkdir()
    outside_file = outside_directory / "secret.txt"
    outside_file.write_text("secret", encoding="utf-8")
    (tmp_path / "file-link").symlink_to(outside_file)
    (tmp_path / "directory-link").symlink_to(outside_directory, target_is_directory=True)

    assert core.verify_artifact(tmp_path, "file-link")["status"] == "FAIL"
    assert core.verify_artifact(tmp_path, "directory-link/secret.txt")["status"] == "FAIL"


def test_claim_and_citation_states(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("The retained sample contained thirteen entries.", encoding="utf-8")
    claims = core.audit_claims(tmp_path, [{"statement": "A sample exists", "source_paths": ["source.txt"]}])
    assert claims["status"] == "PASS"
    url_only = core.audit_claims(tmp_path, [{"statement": "A current claim", "source_urls": ["https://example.com"]}])
    assert url_only["status"] == "UNVERIFIED"
    citations = core.audit_citations(tmp_path, [{"quote": "thirteen entries", "source_path": "source.txt"}])
    assert citations["status"] == "PASS"


def test_empty_inputs_and_self_asserted_receipts_never_pass(tmp_path: Path) -> None:
    assert core.audit_claims(tmp_path, [])["status"] == "UNVERIFIED"
    assert core.audit_citations(tmp_path, [])["status"] == "UNVERIFIED"
    assert core.summarize_verification([])["status"] == "UNVERIFIED"
    assert core.summarize_verification([{"status": "PASS"}])["status"] == "UNVERIFIED"
    oversized_receipt = {
        "schema_version": "dailyai.release-gate-receipt/v1",
        "tool": "build_release_receipt",
        "status": "PASS",
        "generated_at": "2026-08-27T00:00:00+00:00",
        "findings": [],
        "limitations": [],
        "artifacts": [{"path": f"proof-{index}.txt", "sha256": "0" * 64} for index in range(core.MAX_PATH_REFERENCES + 1)],
    }
    assert core.summarize_verification([oversized_receipt], tmp_path)["status"] == "UNVERIFIED"


def test_summary_preserves_valid_receipt_uncertainty(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("proof", encoding="utf-8")
    passed = core.verify_artifact(tmp_path, "artifact.txt")
    uncertain = core.audit_claims(tmp_path, [{"statement": "External claim", "source_urls": ["https://example.com"]}])
    assert core.summarize_verification([passed])["status"] == "UNVERIFIED"
    assert core.summarize_verification([passed], tmp_path)["status"] == "PASS"
    result = core.summarize_verification([passed, uncertain], tmp_path)
    assert result["status"] == "UNVERIFIED"


def test_file_and_input_limits_fail_closed(tmp_path: Path) -> None:
    large = tmp_path / "large.bin"
    large.write_bytes(b"x" * (core.MAX_FILE_BYTES + 1))
    assert core.verify_artifact(tmp_path, "large.bin")["status"] == "FAIL"
    oversized = [{"statement": "x", "source_urls": ["https://example.com"]}] * (core.MAX_ITEMS + 1)
    assert core.audit_claims(tmp_path, oversized)["status"] == "FAIL"


def test_request_wide_path_and_byte_limits(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "a.txt").write_text("aa", encoding="utf-8")
    (tmp_path / "b.txt").write_text("bb", encoding="utf-8")
    monkeypatch.setattr(core, "MAX_PATH_REFERENCES", 1)
    too_many = core.audit_claims(
        tmp_path,
        [{"statement": "x", "source_paths": ["a.txt", "b.txt"]}],
    )
    assert too_many["status"] == "FAIL"
    monkeypatch.setattr(core, "MAX_PATH_REFERENCES", 200)
    monkeypatch.setattr(core, "MAX_REQUEST_BYTES", 3)
    over_bytes = core.audit_citations(
        tmp_path,
        [
            {"quote": "aa", "source_path": "a.txt"},
            {"quote": "bb", "source_path": "b.txt"},
        ],
    )
    assert over_bytes["status"] == "FAIL"
