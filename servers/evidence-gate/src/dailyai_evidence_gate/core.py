from __future__ import annotations

import hashlib
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


STATUSES = {"PASS", "FAIL", "UNVERIFIED", "NOT_RUN", "BLOCKED"}
RECEIPT_SCHEMAS = {
    "dailyai.evidence-gate-receipt/v1",
    "dailyai.release-gate-receipt/v1",
}
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_ITEMS = 100
MAX_TERMS = 100
MAX_TEXT_CHARS = 4096
MAX_PATH_REFERENCES = 200
MAX_REQUEST_BYTES = 50 * 1024 * 1024


class _ReadBudget:
    def __init__(self, root: str | Path) -> None:
        self.root = root
        self.cache: dict[str, tuple[str, bytes]] = {}
        self.total_bytes = 0

    def read(self, candidate: str | Path) -> tuple[str, bytes]:
        key = os.fspath(candidate)
        if key in self.cache:
            return self.cache[key]
        result = _read_rooted(self.root, candidate)
        if self.total_bytes + len(result[1]) > MAX_REQUEST_BYTES:
            raise ValueError("request_byte_limit_exceeded")
        self.total_bytes += len(result[1])
        self.cache[key] = result
        return result


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _relative_parts(root: Path, candidate: str | Path) -> tuple[tuple[str, ...], str]:
    raw = Path(candidate).expanduser()
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
    return parts, Path(*parts).as_posix()


def _read_rooted(root: str | Path, candidate: str | Path) -> tuple[str, bytes]:
    """Read one regular file beneath root without following symlinks.

    Directory-descriptor traversal plus O_NOFOLLOW removes the resolve-then-open
    race present in ordinary Path.resolve()/Path.read_bytes() sequences.
    """

    base = Path(root).expanduser().resolve(strict=True)
    if not base.is_dir():
        raise ValueError("root_directory_required")
    parts, display = _relative_parts(base, candidate)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    try:
        descriptors.append(os.open(base, directory_flags))
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
        return display, b"".join(chunks)
    except OSError as exc:
        raise ValueError("file_unavailable") from exc
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _receipt(tool: str, status: str, checked: int, findings: list[dict[str, Any]], limitations: list[str]) -> dict[str, Any]:
    if status not in STATUSES:
        raise ValueError("unsupported_status")
    return {
        "schema_version": "dailyai.evidence-gate-receipt/v1",
        "tool": tool,
        "status": status,
        "checked": checked,
        "findings": findings,
        "limitations": limitations,
        "generated_at": _now(),
    }


def _bounded_strings(values: Iterable[str] | None, *, limit: int = MAX_TERMS) -> list[str]:
    result = list(values or [])
    if len(result) > limit or any(not isinstance(value, str) or not value or len(value) > MAX_TEXT_CHARS for value in result):
        raise ValueError("input_limit_exceeded")
    return result


def _valid_receipt(value: Any) -> bool:
    base_valid = (
        isinstance(value, dict)
        and value.get("schema_version") in RECEIPT_SCHEMAS
        and isinstance(value.get("tool"), str)
        and bool(value.get("tool"))
        and value.get("status") in STATUSES
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
    schema = value["schema_version"]
    if schema == "dailyai.evidence-gate-receipt/v1":
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
    result: dict[str, str] = {}
    candidates: list[Any] = [receipt.get("artifact")]
    artifacts = receipt.get("artifacts")
    if isinstance(artifacts, list) and len(artifacts) <= MAX_PATH_REFERENCES:
        candidates.extend(artifacts)
    for artifact in candidates:
        if (
            isinstance(artifact, dict)
            and isinstance(artifact.get("path"), str)
            and isinstance(artifact.get("sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"])
        ):
            result[artifact["path"]] = artifact["sha256"]
    return result


def verify_artifact(
    root: str | Path,
    artifact_path: str,
    required_terms: Iterable[str] | None = None,
    forbidden_terms: Iterable[str] | None = None,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    try:
        required = _bounded_strings(required_terms)
        forbidden = _bounded_strings(forbidden_terms)
        display, data = _read_rooted(root, artifact_path)
    except ValueError as exc:
        return _receipt("verify_artifact", "FAIL", 1, [{"code": str(exc), "path": artifact_path}], [])
    if not data:
        findings.append({"code": "empty_artifact", "path": display})
    text = data.decode("utf-8", errors="replace")
    for term in required:
        if term not in text:
            findings.append({"code": "required_term_missing", "term": term})
    for term in forbidden:
        if term in text:
            findings.append({"code": "forbidden_term_present", "term": term})
    status = "PASS" if not findings else "FAIL"
    receipt = _receipt(
        "verify_artifact",
        status,
        1,
        findings,
        [
            "This check establishes file properties and declared text rules, not factual truth.",
            "The MCP caller can infer queried content, size, and digest information for files inside the supplied root.",
        ],
    )
    receipt["artifact"] = {
        "path": display,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    return receipt


def audit_claims(root: str | Path, claims: list[dict[str, Any]]) -> dict[str, Any]:
    limitations = [
        "Evidence presence is not semantic entailment.",
        "URLs are never fetched by this local server.",
        "The MCP caller can infer whether supplied local paths are readable inside the supplied root.",
    ]
    if not isinstance(claims, list) or not claims:
        return _receipt("audit_claims", "UNVERIFIED", 0, [{"code": "claims_required"}], limitations)
    if len(claims) > MAX_ITEMS:
        return _receipt("audit_claims", "FAIL", 0, [{"code": "input_limit_exceeded"}], limitations)
    path_references = sum(
        len(claim.get("source_paths", []))
        for claim in claims
        if isinstance(claim, dict) and isinstance(claim.get("source_paths", []), list)
    )
    if path_references > MAX_PATH_REFERENCES:
        return _receipt("audit_claims", "FAIL", 0, [{"code": "request_path_limit_exceeded"}], limitations)
    reader = _ReadBudget(root)
    findings: list[dict[str, Any]] = []
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            findings.append({"index": index, "status": "FAIL", "code": "claim_object_required"})
            continue
        statement = str(claim.get("statement", "")).strip()
        local_sources = claim.get("source_paths") or []
        urls = claim.get("source_urls") or []
        if len(statement) > MAX_TEXT_CHARS:
            findings.append({"index": index, "status": "FAIL", "code": "input_limit_exceeded"})
            continue
        if not isinstance(local_sources, list) or not isinstance(urls, list) or len(local_sources) > MAX_ITEMS or len(urls) > MAX_ITEMS:
            findings.append({"index": index, "status": "FAIL", "code": "input_limit_exceeded"})
            continue
        if not statement:
            findings.append({"index": index, "status": "FAIL", "code": "statement_missing"})
            continue
        if not local_sources and not urls:
            findings.append({"index": index, "status": "FAIL", "code": "evidence_missing", "statement": statement})
            continue
        bad_sources: list[str] = []
        for source in local_sources:
            if not isinstance(source, str) or not source or len(source) > MAX_TEXT_CHARS:
                bad_sources.append(str(source))
                continue
            try:
                reader.read(source)
            except ValueError:
                bad_sources.append(source)
        if bad_sources:
            findings.append({"index": index, "status": "FAIL", "code": "local_source_unavailable", "sources": bad_sources})
        elif urls and not local_sources:
            findings.append({"index": index, "status": "UNVERIFIED", "code": "url_not_fetched", "urls": urls})
        else:
            findings.append({"index": index, "status": "PASS", "code": "declared_local_evidence_present"})
    states = {item["status"] for item in findings}
    status = "FAIL" if "FAIL" in states else "UNVERIFIED" if "UNVERIFIED" in states else "PASS"
    return _receipt("audit_claims", status, len(claims), findings, limitations)


def audit_citations(root: str | Path, pairs: list[dict[str, Any]]) -> dict[str, Any]:
    limitations = [
        "Literal containment does not establish that a citation supports an inference.",
        "Quote queries can reveal whether supplied text occurs in files inside the supplied root.",
    ]
    if not isinstance(pairs, list) or not pairs:
        return _receipt("audit_citations", "UNVERIFIED", 0, [{"code": "citation_pairs_required"}], limitations)
    if len(pairs) > MAX_ITEMS:
        return _receipt("audit_citations", "FAIL", 0, [{"code": "input_limit_exceeded"}], limitations)
    reader = _ReadBudget(root)
    findings: list[dict[str, Any]] = []
    for index, pair in enumerate(pairs):
        if not isinstance(pair, dict):
            findings.append({"index": index, "status": "FAIL", "code": "citation_object_required"})
            continue
        quote = str(pair.get("quote", "")).strip()
        source_path = str(pair.get("source_path", "")).strip()
        if not quote or not source_path:
            findings.append({"index": index, "status": "FAIL", "code": "quote_and_source_required"})
            continue
        if len(quote) > MAX_TEXT_CHARS or len(source_path) > MAX_TEXT_CHARS:
            findings.append({"index": index, "status": "FAIL", "code": "input_limit_exceeded"})
            continue
        try:
            _, data = reader.read(source_path)
        except ValueError as exc:
            findings.append({"index": index, "status": "FAIL", "code": str(exc), "source_path": source_path})
            continue
        source = data.decode("utf-8", errors="replace")
        normalize = lambda value: re.sub(r"\s+", " ", value).strip().casefold()
        contained = normalize(quote) in normalize(source)
        findings.append({"index": index, "status": "PASS" if contained else "FAIL", "code": "quote_contained" if contained else "quote_not_contained"})
    status = "PASS" if findings and all(item["status"] == "PASS" for item in findings) else "FAIL"
    return _receipt("audit_citations", status, len(pairs), findings, limitations)


def summarize_verification(
    results: list[dict[str, Any]], root: str | Path | None = None
) -> dict[str, Any]:
    limitations = [
        "The summary inherits the boundaries of its input receipts.",
        "Receipt shape validation does not authenticate who produced a receipt.",
    ]
    if not isinstance(results, list) or not results:
        return _receipt("summarize_verification", "UNVERIFIED", 0, [{"code": "receipts_required"}], limitations)
    if len(results) > MAX_ITEMS:
        return _receipt("summarize_verification", "FAIL", 0, [{"code": "input_limit_exceeded"}], limitations)
    try:
        reader = _ReadBudget(root) if root is not None else None
    except (OSError, ValueError):
        reader = None
    counts = {status: 0 for status in sorted(STATUSES)}
    findings: list[dict[str, Any]] = []
    for index, result in enumerate(results):
        if not _valid_receipt(result):
            status = "UNVERIFIED"
            tool = "unknown"
            code = "invalid_receipt"
        else:
            status = result["status"]
            tool = result["tool"]
            code = "receipt_shape_valid"
            if status == "PASS":
                digests = _receipt_artifact_digests(result)
                if reader is None or not digests:
                    status = "UNVERIFIED"
                    code = "artifact_reverification_required"
                else:
                    try:
                        matches = all(
                            hashlib.sha256(reader.read(path)[1]).hexdigest() == digest
                            for path, digest in digests.items()
                        )
                    except ValueError:
                        matches = False
                    if not matches:
                        status = "UNVERIFIED"
                        code = "receipt_artifact_digest_mismatch"
                    else:
                        code = "receipt_artifacts_reverified"
        counts[status] += 1
        findings.append({"index": index, "tool": tool, "status": status, "code": code})
    if counts["FAIL"]:
        status = "FAIL"
    elif counts["BLOCKED"]:
        status = "BLOCKED"
    elif counts["UNVERIFIED"] or counts["NOT_RUN"]:
        status = "UNVERIFIED"
    else:
        status = "PASS"
    receipt = _receipt("summarize_verification", status, len(results), findings, limitations)
    receipt["counts"] = counts
    return receipt
