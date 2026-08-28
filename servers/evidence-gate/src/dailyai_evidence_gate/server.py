from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import core

mcp = FastMCP("Daily AI Evidence Gate", instructions="Local deterministic evidence checks. No network access.")
_ROOT: Path | None = None


def _configured_root() -> Path:
    if _ROOT is None:
        raise RuntimeError("server root is not configured; start with --root")
    return _ROOT


@mcp.tool()
def verify_artifact(artifact_path: str, required_terms: list[str] | None = None, forbidden_terms: list[str] | None = None) -> dict[str, Any]:
    """Check that one rooted artifact exists, is non-empty, and obeys declared text rules."""
    return core.verify_artifact(_configured_root(), artifact_path, required_terms, forbidden_terms)


@mcp.tool()
def audit_claims(claims: list[dict[str, Any]]) -> dict[str, Any]:
    """Check whether claims declare available local evidence; URLs remain unverified."""
    return core.audit_claims(_configured_root(), claims)


@mcp.tool()
def audit_citations(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    """Check whether quoted text is literally contained in a rooted local source."""
    return core.audit_citations(_configured_root(), pairs)


@mcp.tool()
def summarize_verification(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate evidence receipts without upgrading uncertain states."""
    return core.summarize_verification(results, _configured_root())


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
