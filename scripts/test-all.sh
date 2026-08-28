#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/servers/evidence-gate/src:$ROOT/servers/release-gate/src${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q "$ROOT/tests"
python3 "$ROOT/scripts/run-examples.py" >/dev/null
python3 "$ROOT/scripts/demo-sequence.py" >/dev/null
for skill in "$ROOT"/skills/*; do
  bash "$skill/scripts/selftest.sh"
done
python3 "$ROOT/scripts/scan-public.py"
python3 "$ROOT/scripts/audit-workflows.py"
echo 'toolkit-tests=PASS'
