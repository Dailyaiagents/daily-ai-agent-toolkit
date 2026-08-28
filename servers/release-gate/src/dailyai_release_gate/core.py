from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID = {"PASS", "FAIL", "UNVERIFIED", "NOT_RUN", "BLOCKED"}
RECEIPT_SCHEMAS = {
    "dailyai.evidence-gate-receipt/v1",
    "dailyai.release-gate-receipt/v1",
}
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_ITEMS = 100
MAX_TEXT_CHARS = 4096
MAX_PATH_REFERENCES = 200
MAX_REQUEST_BYTES = 50 * 1024 * 1024


class _ReadBudget:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("root_directory_required")
        self.cache: dict[tuple[str, ...], tuple[str, bytes]] = {}
        self.total_bytes = 0

    def read_parts(self, parts: tuple[str, ...]) -> tuple[str, bytes]:
        if parts in self.cache:
            return self.cache[parts]
        result = _read_parts(self.root, parts)
        if self.total_bytes + len(result[1]) > MAX_REQUEST_BYTES:
            raise ValueError("request_byte_limit_exceeded")
        self.total_bytes += len(result[1])
        self.cache[parts] = result
        return result

    def read(self, candidate: str | Path) -> tuple[str, bytes]:
        return self.read_parts(_parts(self.root, candidate))


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parts(root: Path, candidate: str | Path, *, directory: bool = False) -> tuple[str, ...]:
    raw = Path(candidate).expanduser()
    if directory and raw == Path("."):
        return ()
    if raw.is_absolute():
        try:
            relative = Path(os.path.abspath(raw)).relative_to(root)
        except ValueError as exc:
            raise ValueError("path_outside_root") from exc
    else:
        relative = raw
    parts = relative.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("path_component_invalid")
    return parts


def _verify_directory(root: Path, parts: tuple[str, ...]) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    try:
        descriptors.append(os.open(root, flags))
        for component in parts:
            descriptors.append(os.open(component, flags, dir_fd=descriptors[-1]))
    except OSError as exc:
        raise ValueError("directory_unavailable") from exc
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _read_parts(root: Path, parts: tuple[str, ...]) -> tuple[str, bytes]:
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    try:
        descriptors.append(os.open(root, directory_flags))
        for component in parts[:-1]:
            descriptors.append(os.open(component, directory_flags, dir_fd=descriptors[-1]))
        descriptors.append(os.open(parts[-1], file_flags, dir_fd=descriptors[-1]))
        file_descriptor = descriptors[-1]
        details = os.fstat(file_descriptor)
        if not stat.S_ISREG(details.st_mode):
            raise ValueError("regular_file_required")
        if details.st_size > MAX_FILE_BYTES:
            raise ValueError("file_too_large")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(file_descriptor, min(1024 * 1024, MAX_FILE_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_FILE_BYTES:
                raise ValueError("file_too_large")
        return Path(*parts).as_posix(), b"".join(chunks)
    except OSError as exc:
        raise ValueError("file_unavailable") from exc
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _read_rooted(root: str | Path, candidate: str | Path) -> tuple[str, bytes]:
    base = Path(root).expanduser().resolve(strict=True)
    if not base.is_dir():
        raise ValueError("root_directory_required")
    return _read_parts(base, _parts(base, candidate))


def _receipt(tool: str, status: str, findings: list[dict[str, Any]], limitations: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "dailyai.release-gate-receipt/v1",
        "tool": tool,
        "status": status,
        "findings": findings,
        "limitations": limitations or [],
        "generated_at": _now(),
    }


def _valid_receipt(value: Any) -> bool:
    base_valid = (
        isinstance(value, dict)
        and value.get("schema_version") in RECEIPT_SCHEMAS
        and isinstance(value.get("tool"), str)
        and bool(value.get("tool"))
        and value.get("status") in VALID
        and isinstance(value.get("generated_at"), str)
        and bool(value.get("generated_at"))
        and isinstance(value.get("findings"), list)
        and len(value.get("findings")) <= MAX_ITEMS
        and isinstance(value.get("limitations"), list)
    )
    if not base_valid:
        return False
    try:
        datetime.fromisoformat(value["generated_at"])
    except ValueError:
        return False
    if value["schema_version"] == "dailyai.evidence-gate-receipt/v1":
        if not isinstance(value.get("checked"), int) or not 0 <= value["checked"] <= MAX_ITEMS:
            return False
        if value["tool"] == "verify_artifact" and value["status"] == "PASS":
            artifact = value.get("artifact")
            return (
                isinstance(artifact, dict)
                and isinstance(artifact.get("path"), str)
                and bool(artifact["path"])
                and isinstance(artifact.get("sha256"), str)
                and re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]) is not None
            )
        return value["tool"] in {
            "verify_artifact", "audit_claims", "audit_citations", "summarize_verification"
        }
    required = {
        "check_contract": "requirements",
        "evaluate_completion": "requirements",
        "format_blockers": "findings",
        "build_release_receipt": "artifacts",
    }
    key = required.get(value["tool"])
    if key is None or not isinstance(value.get(key), list):
        return False
    limit = MAX_PATH_REFERENCES if key == "artifacts" else MAX_ITEMS
    return len(value[key]) <= limit


def _receipt_artifact_digests(receipt: dict[str, Any]) -> dict[str, str]:
    paths: dict[str, str] = {}
    artifact = receipt.get("artifact")
    if isinstance(artifact, dict) and isinstance(artifact.get("path"), str) and isinstance(artifact.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]):
        paths[artifact["path"]] = artifact["sha256"]
    artifacts = receipt.get("artifacts")
    if isinstance(artifacts, list) and len(artifacts) <= MAX_PATH_REFERENCES:
        for row in artifacts:
            if isinstance(row, dict) and isinstance(row.get("path"), str) and isinstance(row.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
                paths[row["path"]] = row["sha256"]
    return paths


def check_contract(root: str | Path, contract_path: str, workspace_path: str = ".") -> dict[str, Any]:
    limitations = ["This check proves declared evidence-file presence, not the truth of narrative claims."]
    try:
        base = Path(root).expanduser().resolve(strict=True)
        workspace_parts = _parts(base, workspace_path, directory=True)
        _verify_directory(base, workspace_parts)
        reader = _ReadBudget(base)
        _, contract_bytes = reader.read(contract_path)
        contract = json.loads(contract_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        return _receipt("check_contract", "FAIL", [{"code": str(exc)}], limitations)
    if not isinstance(contract, dict):
        return _receipt("check_contract", "FAIL", [{"code": "contract_object_required"}], limitations)
    requirements = contract.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        return _receipt("check_contract", "FAIL", [{"code": "requirements_required"}], limitations)
    if len(requirements) > MAX_ITEMS:
        return _receipt("check_contract", "FAIL", [{"code": "input_limit_exceeded"}], limitations)
    path_references = sum(
        len(requirement.get("evidence_paths", []))
        for requirement in requirements
        if isinstance(requirement, dict) and isinstance(requirement.get("evidence_paths", []), list)
    )
    if path_references > MAX_PATH_REFERENCES:
        return _receipt("check_contract", "FAIL", [{"code": "request_path_limit_exceeded"}], limitations)
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            findings.append({"id": f"requirement-{index}", "status": "FAIL", "code": "requirement_object_required"})
            continue
        rid = str(requirement.get("id", "")).strip()
        if not rid or len(rid) > MAX_TEXT_CHARS:
            findings.append({"id": f"requirement-{index}", "status": "FAIL", "code": "requirement_id_invalid"})
            continue
        if rid in seen:
            findings.append({"id": rid, "status": "FAIL", "code": "requirement_id_duplicate"})
            continue
        seen.add(rid)
        paths = requirement.get("evidence_paths") or []
        if not isinstance(paths, list) or len(paths) > MAX_ITEMS:
            findings.append({"id": rid, "status": "FAIL", "code": "evidence_paths_invalid"})
            continue
        if not paths:
            findings.append({"id": rid, "status": "UNVERIFIED", "code": "evidence_paths_missing"})
            continue
        missing: list[str] = []
        for candidate in paths:
            if not isinstance(candidate, str) or not candidate or len(candidate) > MAX_TEXT_CHARS:
                missing.append(str(candidate))
                continue
            try:
                raw = Path(candidate)
                if raw.is_absolute():
                    candidate_parts = _parts(base, raw)
                    if candidate_parts[: len(workspace_parts)] != workspace_parts:
                        raise ValueError("path_outside_workspace")
                else:
                    if any(part in {"", ".", ".."} for part in raw.parts):
                        raise ValueError("path_component_invalid")
                    candidate_parts = workspace_parts + raw.parts
                _, data = reader.read_parts(candidate_parts)
                if not data:
                    missing.append(candidate)
            except ValueError:
                missing.append(candidate)
        findings.append({"id": rid, "status": "PASS" if not missing else "FAIL", "missing": missing})
    states = {item["status"] for item in findings}
    status = "FAIL" if "FAIL" in states else "UNVERIFIED" if "UNVERIFIED" in states else "PASS"
    return _receipt("check_contract", status, findings, limitations)


def evaluate_completion(
    requirements: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    root: str | Path | None = None,
) -> dict[str, Any]:
    limitations = [
        "Receipt shape does not authenticate who produced the receipt.",
        "A PASS requires every referenced artifact to be reopened and match its receipt digest.",
    ]
    if not isinstance(requirements, list) or not requirements:
        return _receipt("evaluate_completion", "UNVERIFIED", [{"code": "requirements_required"}], limitations)
    if not isinstance(evidence, list) or len(requirements) > MAX_ITEMS or len(evidence) > MAX_ITEMS:
        return _receipt("evaluate_completion", "FAIL", [{"code": "input_limit_exceeded"}], limitations)
    path_references = sum(
        len(item.get("evidence_refs", []))
        for item in evidence
        if isinstance(item, dict) and isinstance(item.get("evidence_refs", []), list)
    )
    if path_references > MAX_PATH_REFERENCES:
        return _receipt("evaluate_completion", "FAIL", [{"code": "request_path_limit_exceeded"}], limitations)
    try:
        reader = _ReadBudget(root) if root is not None else None
    except (OSError, ValueError):
        reader = None
    evidence_by_id: dict[str, dict[str, Any]] = {}
    duplicate_evidence: set[str] = set()
    for item in evidence:
        if not isinstance(item, dict):
            continue
        rid = str(item.get("requirement_id", "")).strip()
        if not rid:
            continue
        if rid in evidence_by_id:
            duplicate_evidence.add(rid)
        evidence_by_id[rid] = item
    findings: list[dict[str, Any]] = []
    seen_requirements: set[str] = set()
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            findings.append({"id": f"requirement-{index}", "status": "FAIL", "code": "requirement_object_required"})
            continue
        rid = str(requirement.get("id", "")).strip()
        if not rid or len(rid) > MAX_TEXT_CHARS:
            findings.append({"id": f"requirement-{index}", "status": "FAIL", "code": "requirement_id_invalid"})
            continue
        if rid in seen_requirements:
            findings.append({"id": rid, "status": "FAIL", "code": "requirement_id_duplicate"})
            continue
        seen_requirements.add(rid)
        if rid in duplicate_evidence:
            findings.append({"id": rid, "status": "FAIL", "code": "evidence_duplicate"})
            continue
        item = evidence_by_id.get(rid)
        if not item:
            findings.append({"id": rid, "status": "NOT_RUN", "code": "evidence_absent"})
            continue
        references = item.get("evidence_refs")
        receipt = item.get("receipt")
        if (
            not isinstance(references, list)
            or not references
            or len(references) > MAX_ITEMS
            or any(not isinstance(ref, str) or not ref or len(ref) > MAX_TEXT_CHARS for ref in references)
            or not _valid_receipt(receipt)
        ):
            findings.append({"id": rid, "status": "UNVERIFIED", "code": "qualifying_receipt_required", "evidence_refs": references or []})
            continue
        state = receipt["status"]
        if item.get("status") not in (None, state):
            state = "UNVERIFIED"
            code = "declared_status_mismatch"
        elif state == "PASS":
            digests = _receipt_artifact_digests(receipt)
            if reader is None:
                state = "UNVERIFIED"
                code = "artifact_reverification_required"
            else:
                try:
                    matches = all(
                        ref in digests
                        and hashlib.sha256(reader.read(ref)[1]).hexdigest() == digests[ref]
                        for ref in references
                    )
                except ValueError:
                    matches = False
                if not matches:
                    state = "UNVERIFIED"
                    code = "receipt_artifact_digest_mismatch"
                else:
                    code = "receipt_artifacts_reverified"
        else:
            code = "receipt_shape_valid"
        findings.append({"id": rid, "status": state, "code": code, "evidence_refs": references})
    states = {item["status"] for item in findings}
    if "FAIL" in states:
        status = "FAIL"
    elif "BLOCKED" in states:
        status = "BLOCKED"
    elif states - {"PASS"}:
        status = "UNVERIFIED"
    else:
        status = "PASS"
    return _receipt("evaluate_completion", status, findings, limitations)


def format_blockers(findings: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(findings, list) or not findings:
        return _receipt("format_blockers", "UNVERIFIED", [{"code": "findings_required"}])
    if len(findings) > MAX_ITEMS:
        return _receipt("format_blockers", "FAIL", [{"code": "input_limit_exceeded"}])
    blockers = []
    for finding in findings:
        if not isinstance(finding, dict):
            blockers.append({"requirement_id": "unknown", "state": "UNVERIFIED", "reason": "finding_object_required", "repair": "Provide a structured finding and rerun."})
            continue
        state = finding.get("status", "UNVERIFIED")
        if state != "PASS":
            blockers.append({
                "requirement_id": finding.get("id") or finding.get("requirement_id") or "unknown",
                "state": state if state in VALID else "UNVERIFIED",
                "reason": finding.get("code") or finding.get("reason") or "acceptance_not_proven",
                "repair": finding.get("repair") or "Provide qualifying evidence and rerun the same check.",
            })
    return _receipt("format_blockers", "PASS" if not blockers else "BLOCKED", blockers)


def build_release_receipt(root: str | Path, checks: list[dict[str, Any]], artifacts: list[str]) -> dict[str, Any]:
    limitations = [
        "A release receipt does not publish, deploy, or approve the release.",
        "Receipt shape validation does not authenticate who produced an input receipt.",
    ]
    if not isinstance(checks, list) or not isinstance(artifacts, list) or len(checks) > MAX_ITEMS or len(artifacts) > MAX_ITEMS:
        return _receipt("build_release_receipt", "FAIL", [{"code": "input_limit_exceeded"}], limitations)
    try:
        reader = _ReadBudget(root)
    except (OSError, ValueError) as exc:
        return _receipt("build_release_receipt", "FAIL", [{"code": str(exc)}], limitations)
    findings: list[dict[str, Any]] = []
    if not checks:
        findings.append({"kind": "check", "status": "UNVERIFIED", "code": "checks_required"})
    for index, check in enumerate(checks):
        if _valid_receipt(check):
            state = check["status"]
            code = "receipt_shape_valid"
            if state == "PASS":
                digests = _receipt_artifact_digests(check)
                try:
                    matches = bool(digests) and all(
                        hashlib.sha256(reader.read(path)[1]).hexdigest() == digest
                        for path, digest in digests.items()
                    )
                except ValueError:
                    matches = False
                if not matches:
                    state = "UNVERIFIED"
                    code = "check_artifact_reverification_failed"
                else:
                    code = "check_artifacts_reverified"
        else:
            state = "UNVERIFIED"
            code = "invalid_check_receipt"
        findings.append({"kind": "check", "index": index, "status": state, "code": code})
    artifact_rows = []
    for artifact in artifacts:
        if not isinstance(artifact, str) or not artifact or len(artifact) > MAX_TEXT_CHARS:
            row = {"path": str(artifact), "status": "FAIL", "code": "artifact_path_invalid"}
        else:
            try:
                display, data = reader.read(artifact)
                row = {"path": display, "status": "PASS" if data else "FAIL", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            except ValueError as exc:
                row = {"path": artifact, "status": "FAIL", "code": str(exc)}
        artifact_rows.append(row)
        findings.append({"kind": "artifact", **row})
    states = {item.get("status") for item in findings}
    status = "PASS" if states <= {"PASS"} and findings else "FAIL" if "FAIL" in states else "UNVERIFIED"
    receipt = _receipt("build_release_receipt", status, findings, limitations)
    receipt["artifacts"] = artifact_rows
    return receipt
