#!/usr/bin/env python3
"""Wait for both immutable packages and MCP ownership markers on public PyPI."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


PACKAGES = {
    "dailyaiagents-evidence-gate": "io.github.Dailyaiagents/evidence-gate",
    "dailyaiagents-release-gate": "io.github.Dailyaiagents/release-gate",
}
PACKAGES_BY_SLUG = {
    "evidence-gate": "dailyaiagents-evidence-gate",
    "release-gate": "dailyaiagents-release-gate",
}


def available(
    project: str,
    version: str,
    mcp_name: str,
    expected_files: dict[str, tuple[str, int]],
) -> tuple[bool, str]:
    url = f"https://pypi.org/pypi/{project}/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:  # noqa: S310
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        return False, str(error)
    info = payload.get("info", {})
    if info.get("version") != version:
        return False, f"unexpected version {info.get('version')!r}"
    marker = f"mcp-name: {mcp_name}"
    if marker not in info.get("description", ""):
        return False, "MCP ownership marker is not visible in PyPI description"
    release_files = payload.get("urls", [])
    observed = {item.get("filename"): item for item in release_files}
    if set(observed) != set(expected_files):
        return False, f"published filenames differ: {sorted(observed)}"
    for filename, (expected_sha256, expected_size) in expected_files.items():
        item = observed[filename]
        if item.get("digests", {}).get("sha256") != expected_sha256:
            return False, f"digest mismatch: {filename}"
        if item.get("size") != expected_size:
            return False, f"size mismatch: {filename}"
    package_types = {item.get("packagetype") for item in release_files}
    if package_types != {"bdist_wheel", "sdist"}:
        return False, f"unexpected package types: {sorted(package_types)}"
    return True, "exact wheel and sdist digests, sizes, and ownership marker visible"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--interval", type=int, default=10)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    artifacts = manifest.get("artifacts", [])
    expected: dict[str, dict[str, tuple[str, int]]] = {}
    for slug in ("evidence-gate", "release-gate"):
        rows = [
            item
            for item in artifacts
            if item.get("path", "").startswith(f"{slug}/")
            and (item["path"].endswith(".whl") or item["path"].endswith(".tar.gz"))
        ]
        if len(rows) != 2:
            raise SystemExit(f"manifest FAIL: expected two distributions for {slug}")
        expected[PACKAGES_BY_SLUG[slug]] = {
            Path(item["path"]).name: (item["sha256"], item["size"]) for item in rows
        }
    deadline = time.monotonic() + args.timeout
    pending = dict(PACKAGES)
    last: dict[str, str] = {}
    while pending:
        for project, mcp_name in list(pending.items()):
            passed, detail = available(project, args.version, mcp_name, expected[project])
            last[project] = detail
            if passed:
                print(f"PyPI PASS {project}=={args.version}: {detail}")
                del pending[project]
        if not pending:
            return 0
        if time.monotonic() >= deadline:
            for project in pending:
                print(f"PyPI BLOCKED-EXTERNAL {project}: {last[project]}")
            return 1
        time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
