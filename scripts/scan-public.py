#!/usr/bin/env python3
"""Fail closed when tracked public source contains private paths or secrets."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 10 * 1024 * 1024
PATTERNS = {
    "absolute-user-path": re.compile(rb"/" + b"Users/" + rb"[^/\s]+/"),
    "aws-access-key": re.compile(b"AKIA" + rb"[0-9A-Z]{16}"),
    "private-key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "api-key-variable": re.compile(
        b"(?:OPENAI|ANTHROPIC|XAI)" + rb"_API_KEY\s*=\s*[^\s<]+"
    ),
}


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    files = [item for item in result.stdout.split(b"\0") if item]
    if not files:
        raise SystemExit("public scan FAIL: git returned no tracked files")
    failures: list[str] = []
    for raw in files:
        relative = raw.decode("utf-8", errors="strict")
        path = ROOT / relative
        if path.is_symlink():
            failures.append(f"{relative}: tracked symlink is not allowed")
            continue
        data = path.read_bytes()
        if len(data) > MAX_FILE_BYTES and path.suffix != ".mp4":
            failures.append(f"{relative}: file exceeds scan limit")
            continue
        if b"\0" in data[:8192]:
            continue
        for name, pattern in PATTERNS.items():
            if pattern.search(data):
                failures.append(f"{relative}: {name}")
    if failures:
        raise SystemExit("public scan FAIL:\n" + "\n".join(failures))
    print(f"public-scan=PASS tracked_files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
