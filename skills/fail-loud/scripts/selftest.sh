#!/usr/bin/env bash
set -euo pipefail
OUT="$(mktemp)"; trap 'rm -f "$OUT"' EXIT
if bash "$(dirname "$0")/run.sh" --lane test --what check --where local --reason missing --repair provide > "$OUT"; then exit 1; fi
grep -q '"status": "BLOCKED"' "$OUT"
echo 'fail-loud-selftest=PASS'
