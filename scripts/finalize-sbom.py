#!/usr/bin/env python3
"""Link a CycloneDX root component to the complete locked runtime graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sbom", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.sbom.read_text(encoding="utf-8"))
    root = payload.get("metadata", {}).get("component", {}).get("bom-ref")
    components = payload.get("components")
    dependencies = payload.get("dependencies")
    if root != "root-component" or not isinstance(components, list) or not components:
        raise SystemExit("SBOM root or components missing")
    if not isinstance(dependencies, list):
        raise SystemExit("SBOM dependency graph missing")
    component_refs = sorted(
        component["bom-ref"]
        for component in components
        if isinstance(component, dict) and isinstance(component.get("bom-ref"), str)
    )
    if len(component_refs) != len(components) or len(set(component_refs)) != len(component_refs):
        raise SystemExit("SBOM component references are invalid")
    dependencies = [row for row in dependencies if row.get("ref") != root]
    dependencies.append({"ref": root, "dependsOn": component_refs})
    payload["dependencies"] = sorted(dependencies, key=lambda row: row["ref"])
    args.sbom.write_text(
        json.dumps(payload, indent=2, sort_keys=True, separators=(",", ": ")) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
