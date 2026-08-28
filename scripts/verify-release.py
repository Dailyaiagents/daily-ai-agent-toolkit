#!/usr/bin/env python3
"""Validate release metadata and artifacts without publishing them."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
import tomllib


PACKAGES = {
    "evidence-gate": {
        "distribution": "dailyaiagents-evidence-gate",
        "module": "dailyai_evidence_gate",
        "command": "dailyai-evidence-gate",
        "mcp_name": "io.github.dailyaiagents/evidence-gate",
        "repository_id": "1349161176",
    },
    "release-gate": {
        "distribution": "dailyaiagents-release-gate",
        "module": "dailyai_release_gate",
        "command": "dailyai-release-gate",
        "mcp_name": "io.github.dailyaiagents/release-gate",
        "repository_id": "1349161176",
    },
}

REQUIRED_RELEASE_ASSETS = (
    "demo/daily-ai-agent-toolkit-demo-v0.1.0.mp4",
    "demo/daily-ai-agent-toolkit-demo-v0.1.0.srt",
    "docs/DEMO-TRANSCRIPT.md",
    "docs/TECHNICAL-REPORT.md",
    "registry/evidence-gate.server.json",
    "registry/release-gate.server.json",
)

FORBIDDEN_NAME_PARTS = {".env", ".git", "__pycache__", ".DS_Store"}
FORBIDDEN_CONTENT = (
    re.compile(rb"/" + b"Users/" + rb"[^/\s]+/"),
    re.compile(b"AKIA" + rb"[0-9A-Z]{16}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def safe_member(name: str) -> None:
    member = PurePosixPath(name)
    if member.is_absolute() or ".." in member.parts:
        raise ValueError(f"unsafe archive member: {name}")
    if FORBIDDEN_NAME_PARTS.intersection(member.parts):
        raise ValueError(f"forbidden archive member: {name}")


def inspect_archive(path: Path) -> None:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            members = []
            for item in archive.infolist():
                safe_member(item.filename)
                mode = item.external_attr >> 16
                file_type = stat.S_IFMT(mode)
                if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise ValueError(f"unsafe zip member type: {item.filename}")
                if not item.is_dir():
                    members.append((item.filename, archive.read(item)))
    else:
        with tarfile.open(path, "r:gz") as archive:
            members = []
            for item in archive.getmembers():
                safe_member(item.name)
                if item.isdir():
                    continue
                if not item.isfile():
                    raise ValueError(f"unsafe tar member type: {item.name}")
                extracted = archive.extractfile(item)
                members.append((item.name, extracted.read() if extracted else b""))
    for name, content in members:
        safe_member(name)
        for pattern in FORBIDDEN_CONTENT:
            if pattern.search(content):
                raise ValueError(f"sensitive/private content in {path.name}:{name}")


def metadata(repo: Path, package: str) -> tuple[str, str]:
    package_root = repo / "servers" / package
    project = tomllib.loads((package_root / "pyproject.toml").read_text())["project"]
    server = json.loads((package_root / "server.json").read_text())
    expected = PACKAGES[package]
    version = project["version"]
    if project["name"] != expected["distribution"]:
        raise ValueError(f"{package}: unexpected distribution name")
    expected_entry_point = f"{expected['module']}.server:main"
    if project.get("scripts", {}).get(expected["command"]) != expected_entry_point:
        raise ValueError(f"{package}: unexpected or missing CLI entry point")
    if server["name"] != expected["mcp_name"] or server["version"] != version:
        raise ValueError(f"{package}: server name/version is not aligned")
    repository = server.get("repository", {})
    if repository.get("id") != expected["repository_id"]:
        raise ValueError(f"{package}: stable repository ID is missing or unexpected")
    registry_package = server["packages"]
    if len(registry_package) != 1:
        raise ValueError(f"{package}: expected exactly one registry package")
    registry_package = registry_package[0]
    if (
        registry_package["registryType"] != "pypi"
        or registry_package["identifier"] != expected["distribution"]
        or registry_package["version"] != version
    ):
        raise ValueError(f"{package}: PyPI package metadata is not aligned")
    readme = (package_root / "README.md").read_text()
    marker = f"<!-- mcp-name: {expected['mcp_name']} -->"
    if marker not in readme:
        raise ValueError(f"{package}: missing PyPI MCP ownership marker")
    return expected["distribution"].replace("-", "_"), version


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", type=Path)
    parser.add_argument("--tag")
    parser.add_argument("--require-sboms", action="store_true")
    parser.add_argument("--write-checksums", action="store_true")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent
    versions: set[str] = set()
    release_files: list[Path] = []
    for package in PACKAGES:
        normalized_name, version = metadata(repo, package)
        versions.add(version)
        if args.dist is None:
            continue
        package_dist = args.dist / package
        wheel = list(package_dist.glob("*.whl"))
        sdist = list(package_dist.glob("*.tar.gz"))
        if len(wheel) != 1 or len(sdist) != 1:
            raise ValueError(f"{package}: expected exactly one wheel and one sdist")
        expected_prefix = f"{normalized_name}-{version}"
        for artifact in wheel + sdist:
            if not artifact.name.startswith(expected_prefix):
                raise ValueError(f"{package}: unexpected artifact {artifact.name}")
            inspect_archive(artifact)
            release_files.append(artifact)
        sbom = package_dist / f"{package}.sbom.cdx.json"
        if args.require_sboms:
            bom = json.loads(sbom.read_text())
            components = bom.get("components", [])
            expected_name = PACKAGES[package]["distribution"]
            root_component = bom.get("metadata", {}).get("component", {})
            if root_component.get("name") != expected_name and not any(
                item.get("name") == expected_name for item in components
            ):
                raise ValueError(f"{package}: SBOM omits {expected_name}")
            root_ref = root_component.get("bom-ref")
            component_refs = {
                item.get("bom-ref") for item in components if isinstance(item, dict)
            }
            root_dependencies = [
                row for row in bom.get("dependencies", []) if row.get("ref") == root_ref
            ]
            if (
                root_ref != "root-component"
                or len(root_dependencies) != 1
                or set(root_dependencies[0].get("dependsOn", [])) != component_refs
            ):
                raise ValueError(f"{package}: SBOM root dependency graph is incomplete")
            release_files.append(sbom)

    if len(versions) != 1:
        raise ValueError("package versions must match for a toolkit release")
    release_version = next(iter(versions))
    if args.tag is not None and args.tag != f"v{release_version}":
        raise ValueError(
            f"release tag {args.tag!r} does not match package version v{release_version}"
        )

    if args.dist is not None:
        for relative in REQUIRED_RELEASE_ASSETS:
            asset = args.dist / relative
            if not asset.is_file() or asset.is_symlink() or asset.stat().st_size == 0:
                raise ValueError(f"missing or invalid release asset: {relative}")
            release_files.append(asset)

    if args.dist is not None and args.write_checksums:
        for provenance in sorted(args.dist.glob("*.sigstore.json")):
            json.loads(provenance.read_text())
            release_files.append(provenance)
        sums = args.dist / "SHA256SUMS"
        lines = [
            f"{digest(path)}  {path.relative_to(args.dist).as_posix()}"
            for path in sorted(release_files)
        ]
        sums.write_text("\n".join(lines) + "\n")
        manifest = {
            "schema": "daily-ai-agent-toolkit-release/v1",
            "version": release_version,
            "artifacts": [
                {
                    "path": path.relative_to(args.dist).as_posix(),
                    "sha256": digest(path),
                    "size": path.stat().st_size,
                }
                for path in sorted(release_files)
            ],
        }
        (args.dist / "RELEASE-MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        )

    print(f"release metadata PASS: {len(PACKAGES)} packages, version {release_version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"release verification FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
