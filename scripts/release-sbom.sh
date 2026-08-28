#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dist_root="${1:-${repo_root}/dist/release}"
command -v cyclonedx-py >/dev/null || {
  echo "cyclonedx-py is required (tested with cyclonedx-bom==7.1.0)" >&2
  exit 2
}

for package in evidence-gate release-gate; do
  wheel_count=0
  wheel=""
  while IFS= read -r candidate; do
    wheel_count=$((wheel_count + 1))
    wheel="${candidate}"
  done < <(find "${dist_root}/${package}" -maxdepth 1 -type f -name '*.whl' -print)
  if [[ "${wheel_count}" -ne 1 ]]; then
    echo "expected exactly one wheel for ${package}, found ${wheel_count}" >&2
    exit 1
  fi

  PYTHONWARNINGS="ignore:The Component this BOM is describing None has no defined dependencies" \
    cyclonedx-py requirements "${repo_root}/requirements/runtime.lock" \
    --pyproject "${repo_root}/servers/${package}/pyproject.toml" \
    --mc-type application \
    --spec-version 1.6 \
    --output-reproducible \
    --output-format JSON \
    --output-file "${dist_root}/${package}/${package}.sbom.cdx.json"
  python "${repo_root}/scripts/finalize-sbom.py" \
    "${dist_root}/${package}/${package}.sbom.cdx.json"
done

python "${repo_root}/scripts/verify-release.py" \
  --dist "${dist_root}" \
  --require-sboms \
  --write-checksums
