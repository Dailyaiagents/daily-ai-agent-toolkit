from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import core

mcp = FastMCP("Daily AI Release Gate", instructions="Local completion checks and release receipts. No external effects.")
_ROOT: Path | None = None


def _configured_root() -> Path:
    if _ROOT is None:
        raise RuntimeError("server root is not configured; start with --root")
    return _ROOT


@mcp.tool()
def check_contract(contract_path: str, workspace_path: str = ".") -> dict[str, Any]:
    """Check declared evidence files for a JSON completion contract."""
    return core.check_contract(_configured_root(), contract_path, workspace_path)


@mcp.tool()
def evaluate_completion(requirements: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate requirement states without upgrading missing or uncertain evidence."""
    return core.evaluate_completion(requirements, evidence, _configured_root())


@mcp.tool()
def format_blockers(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Convert non-passing findings into explicit blocker records."""
    return core.format_blockers(findings)


@mcp.tool()
def build_release_receipt(checks: list[dict[str, Any]], artifacts: list[str]) -> dict[str, Any]:
    """Hash retained artifacts and summarize check states without publishing."""
    return core.build_release_receipt(_configured_root(), checks, artifacts)


def main() -> None:
    global _ROOT
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    _ROOT = Path(args.root).expanduser().resolve(strict=True)
    if not _ROOT.is_dir():
        parser.error("--root must be a directory")
    mcp.run()


if __name__ == "__main__":
    main()
