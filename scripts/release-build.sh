#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
canonical_output="${repo_root}/dist/release"
requested_output="${1:-${canonical_output}}"
mkdir -p "${repo_root}/dist"
if [[ "${requested_output}" != "${canonical_output}" && "${requested_output}" != "dist/release" ]]; then
  echo "release output must be the repository's dist/release directory" >&2
  exit 2
fi
if [[ -L "${repo_root}/dist" || -L "${canonical_output}" ]]; then
  echo "refusing symlinked release output path" >&2
  exit 2
fi
output_root="${canonical_output}"

work_root="$(mktemp -d "${TMPDIR:-/tmp}/dailyai-toolkit-release.XXXXXX")"
trap 'rm -rf "${work_root}"' EXIT

source_date_epoch="$(git -C "${repo_root}" show -s --format=%ct HEAD)"
export SOURCE_DATE_EPOCH="${source_date_epoch}"
export PYTHONHASHSEED=0
export TZ=UTC
export LC_ALL=C

rm -rf "${output_root}"
mkdir -p "${output_root}"

for package in evidence-gate release-gate; do
  first="${work_root}/${package}/first"
  second="${work_root}/${package}/second"
  destination="${output_root}/${package}"
  mkdir -p "${first}" "${second}" "${destination}"

  python -m build --no-isolation \
    --outdir "${first}" "${repo_root}/servers/${package}"
  python -m build --no-isolation \
    --outdir "${second}" "${repo_root}/servers/${package}"

  FIRST="${first}" SECOND="${second}" python - <<'PY'
import hashlib
import os
from pathlib import Path

first = Path(os.environ["FIRST"])
second = Path(os.environ["SECOND"])
first_files = {path.name: path for path in first.iterdir() if path.is_file()}
second_files = {path.name: path for path in second.iterdir() if path.is_file()}
if first_files.keys() != second_files.keys():
    raise SystemExit("reproducibility failure: build outputs have different names")
for name in sorted(first_files):
    left = hashlib.sha256(first_files[name].read_bytes()).hexdigest()
    right = hashlib.sha256(second_files[name].read_bytes()).hexdigest()
    if left != right:
        raise SystemExit(f"reproducibility failure: {name} differs between builds")
    print(f"reproducible {name}: {left}")
PY

  cp "${first}"/* "${destination}/"
done

mkdir -p "${output_root}/demo" "${output_root}/docs" "${output_root}/registry"
cp "${repo_root}/demo/daily-ai-agent-toolkit-demo-v0.1.1.mp4" "${output_root}/demo/"
cp "${repo_root}/demo/daily-ai-agent-toolkit-demo-v0.1.1.srt" "${output_root}/demo/"
cp "${repo_root}/docs/DEMO-TRANSCRIPT.md" "${output_root}/docs/"
cp "${repo_root}/docs/TECHNICAL-REPORT.md" "${output_root}/docs/"
cp "${repo_root}/servers/evidence-gate/server.json" "${output_root}/registry/evidence-gate.server.json"
cp "${repo_root}/servers/release-gate/server.json" "${output_root}/registry/release-gate.server.json"

python "${repo_root}/scripts/verify-release.py" \
  --dist "${output_root}" \
  --write-checksums
