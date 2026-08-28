#!/usr/bin/env python3
"""Classify one immutable PyPI release before a publish or resume job."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import urllib.parse


PACKAGES = {
    "evidence-gate": {
        "project": "dailyaiagents-evidence-gate",
        "mcp_name": "io.github.Dailyaiagents/evidence-gate",
    },
    "release-gate": {
        "project": "dailyaiagents-release-gate",
        "mcp_name": "io.github.Dailyaiagents/release-gate",
    },
}
MAX_METADATA_BYTES = 4 * 1024 * 1024
MAX_ARTIFACT_BYTES = 50 * 1024 * 1024


def validate_https_url(url: object, hostname: str, *, label: str) -> str:
    if not isinstance(url, str):
        raise ValueError(f"{label} URL is malformed")
    parsed = urllib.parse.urlsplit(url)
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError(f"{label} URL has an invalid port") from error
    if (
        parsed.scheme != "https"
        or parsed.hostname != hostname
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
    ):
        raise ValueError(f"{label} URL is not an approved HTTPS endpoint")
    return url


def read_bounded(response: object, limit: int) -> bytes:
    data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"public response exceeds {limit} bytes")
    return data


def is_absent_http_error(error: urllib.error.HTTPError) -> bool:
    validate_https_url(
        error.geturl(), "pypi.org", label="final PyPI metadata error response"
    )
    return error.code == 404


def expected_files(manifest: dict[str, object], slug: str) -> dict[str, tuple[str, int]]:
    rows = [
        item
        for item in manifest.get("artifacts", [])
        if isinstance(item, dict)
        and item.get("path", "").startswith(f"{slug}/")
        and (item["path"].endswith(".whl") or item["path"].endswith(".tar.gz"))
    ]
    if len(rows) != 2:
        raise ValueError(f"{slug}: manifest must contain exactly one wheel and one sdist")
    if any(not isinstance(item.get("size"), int) for item in rows):
        raise ValueError(f"{slug}: manifest artifact size is malformed")
    if any(item["size"] < 1 or item["size"] > MAX_ARTIFACT_BYTES for item in rows):
        raise ValueError(f"{slug}: manifest artifact size is outside the release bound")
    return {
        Path(item["path"]).name: (item["sha256"], item["size"])
        for item in rows
    }


def validate_payload(
    payload: dict[str, object],
    *,
    version: str,
    mcp_name: str,
    expected: dict[str, tuple[str, int]],
) -> list[dict[str, object]]:
    info = payload.get("info", {})
    if not isinstance(info, dict) or info.get("version") != version:
        raise ValueError("public PyPI version metadata does not match")
    marker = f"<!-- mcp-name: {mcp_name} -->"
    if marker not in str(info.get("description", "")):
        raise ValueError("public PyPI MCP ownership marker does not match")
    rows = payload.get("urls", [])
    if not isinstance(rows, list) or not all(isinstance(item, dict) for item in rows):
        raise ValueError("public PyPI file metadata is malformed")
    observed = {item.get("filename"): item for item in rows}
    if set(observed) != set(expected):
        raise ValueError(
            f"public PyPI filename set differs: {sorted(str(name) for name in observed)}"
        )
    for filename, (sha256, size) in expected.items():
        item = observed[filename]
        if item.get("yanked") is True:
            raise ValueError(f"public PyPI artifact is yanked: {filename}")
        if item.get("digests", {}).get("sha256") != sha256:
            raise ValueError(f"public PyPI digest differs: {filename}")
        if item.get("size") != size:
            raise ValueError(f"public PyPI size differs: {filename}")
        validate_https_url(
            item.get("url"),
            "files.pythonhosted.org",
            label=f"public PyPI download for {filename}",
        )
    if {item.get("packagetype") for item in rows} != {"bdist_wheel", "sdist"}:
        raise ValueError("public PyPI package types differ")
    return rows


def record_publish(value: bool) -> None:
    line = f"publish={'true' if value else 'false'}\n"
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with Path(output).open("a", encoding="utf-8") as handle:
            handle.write(line)
    print(line.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", choices=sorted(PACKAGES), required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()

    package = PACKAGES[args.slug]
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected = expected_files(manifest, args.slug)
    metadata_url = f"https://pypi.org/pypi/{package['project']}/{args.version}/json"
    try:
        request = urllib.request.Request(metadata_url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            validate_https_url(
                response.geturl(), "pypi.org", label="final PyPI metadata response"
            )
            payload = json.loads(read_bounded(response, MAX_METADATA_BYTES))
    except urllib.error.HTTPError as error:
        if is_absent_http_error(error):
            record_publish(True)
            print(f"PyPI ABSENT {package['project']}=={args.version}: publication required")
            return 0
        raise

    rows = validate_payload(
        payload,
        version=args.version,
        mcp_name=package["mcp_name"],
        expected=expected,
    )
    with tempfile.TemporaryDirectory(prefix="dailyai-pypi-preflight-") as temporary:
        root = Path(temporary)
        for item in rows:
            filename = item["filename"]
            destination = root / filename
            sha256, size = expected[filename]
            request = urllib.request.Request(
                item["url"], headers={"Cache-Control": "no-cache"}
            )
            with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
                validate_https_url(
                    response.geturl(),
                    "files.pythonhosted.org",
                    label=f"final public PyPI download for {filename}",
                )
                content = read_bounded(response, size)
            destination.write_bytes(content)
            if destination.stat().st_size != size:
                raise ValueError(f"downloaded public PyPI size differs: {filename}")
            if hashlib.sha256(content).hexdigest() != sha256:
                raise ValueError(f"downloaded public PyPI digest differs: {filename}")
            subprocess.run(
                [
                    "pypi-attestations",
                    "verify",
                    "pypi",
                    str(destination),
                    "--repository",
                    args.repository,
                ],
                check=True,
                timeout=60,
            )
    record_publish(False)
    print(
        f"PyPI EXACT {package['project']}=={args.version}: "
        "upload skipped after exact files and attestations verified"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"PyPI CONFLICT-BLOCKED: {error}", file=sys.stderr)
        raise SystemExit(1)
