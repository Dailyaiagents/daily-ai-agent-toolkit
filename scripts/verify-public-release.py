#!/usr/bin/env python3
"""Clean-install each package and discover its exact public MCP tool surface."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv
import urllib.request


PACKAGES = {
    "evidence-gate": {
        "project": "dailyaiagents-evidence-gate",
        "command": "dailyai-evidence-gate",
        "tools": [
            "audit_citations",
            "audit_claims",
            "summarize_verification",
            "verify_artifact",
        ],
    },
    "release-gate": {
        "project": "dailyaiagents-release-gate",
        "command": "dailyai-release-gate",
        "tools": [
            "build_release_receipt",
            "check_contract",
            "evaluate_completion",
            "format_blockers",
        ],
    },
}

CLIENT = r"""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    parameters = StdioServerParameters(
        command=sys.argv[1], args=["--root", sys.argv[2]]
    )
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.list_tools()
            print(json.dumps(sorted(tool.name for tool in result.tools)))

asyncio.run(main())
"""


def executable(venv_root: Path, name: str) -> Path:
    scripts = "Scripts" if os.name == "nt" else "bin"
    suffix = ".exe" if os.name == "nt" else ""
    return venv_root / scripts / f"{name}{suffix}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--runtime-lock",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "requirements" / "runtime.lock",
    )
    parser.add_argument(
        "--artifacts",
        type=Path,
        help="Use local release artifacts instead of the public PyPI index.",
    )
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected_artifacts = {
        Path(row["path"]).name: row for row in manifest.get("artifacts", [])
    }

    with tempfile.TemporaryDirectory(prefix="dailyai-public-verify-") as temporary:
        temporary_root = Path(temporary)
        for slug, expected in PACKAGES.items():
            venv_root = temporary_root / slug
            venv.EnvBuilder(with_pip=True, clear=True).create(venv_root)
            python = executable(venv_root, "python")
            if args.artifacts:
                candidates = list((args.artifacts / slug).glob("*.whl"))
                if len(candidates) != 1:
                    raise ValueError(f"{slug}: expected exactly one local wheel")
                wheel = candidates[0]
            else:
                url = f"https://pypi.org/pypi/{expected['project']}/{args.version}/json"
                with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310
                    payload = json.load(response)
                release_files = payload.get("urls", [])
                if len(release_files) != 2:
                    raise ValueError(f"{slug}: expected exactly two public files")
                wheel = None
                for item in release_files:
                    filename = item["filename"]
                    declared = expected_artifacts.get(filename)
                    if declared is None:
                        raise ValueError(f"{slug}: {filename} absent from release manifest")
                    target = temporary_root / filename
                    request = urllib.request.Request(
                        item["url"], headers={"Cache-Control": "no-cache"}
                    )
                    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
                        target.write_bytes(response.read())
                    observed = hashlib.sha256(target.read_bytes()).hexdigest()
                    if observed != declared["sha256"] or target.stat().st_size != declared["size"]:
                        raise ValueError(f"{slug}: public artifact mismatch: {filename}")
                    subprocess.run(
                        [
                            "pypi-attestations",
                            "verify",
                            "pypi",
                            str(target),
                            "--repository",
                            "https://github.com/Dailyaiagents/daily-ai-agent-toolkit",
                        ],
                        check=True,
                        timeout=60,
                    )
                    if filename.endswith(".whl"):
                        wheel = target
                if wheel is None:
                    raise ValueError(f"{slug}: public wheel missing")
            subprocess.run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--quiet",
                    "--disable-pip-version-check",
                    "--no-cache-dir",
                    "--require-hashes",
                    "-r",
                    str(args.runtime_lock),
                ],
                check=True,
            )
            subprocess.run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--quiet",
                    "--disable-pip-version-check",
                    "--no-cache-dir",
                    "--no-deps",
                    str(wheel),
                ],
                check=True,
            )
            command = executable(venv_root, expected["command"])
            completed = subprocess.run(
                [str(python), "-c", CLIENT, str(command), str(temporary_root)],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            tools = json.loads(completed.stdout.strip().splitlines()[-1])
            if tools != expected["tools"]:
                raise ValueError(
                    f"{slug}: discovered {tools!r}, expected {expected['tools']!r}"
                )
            print(f"public-install PASS {expected['project']}=={args.version}: 4 tools")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"public-install FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
