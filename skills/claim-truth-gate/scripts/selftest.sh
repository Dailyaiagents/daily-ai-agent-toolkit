#!/usr/bin/env bash
set -euo pipefail
DIR="$(mktemp -d)"; trap 'rm -rf "$DIR"' EXIT
printf '[{"statement":"Observed locally","status":"PASS","sources":["receipt.json"]},{"statement":"Unknown","status":"UNVERIFIED","sources":[]}]' > "$DIR/pass.json"
printf '[{"statement":"Unsupported","status":"PASS","sources":[]}]' > "$DIR/fail.json"
bash "$(dirname "$0")/run.sh" "$DIR/pass.json" | grep -q '"status": "PASS"'
if bash "$(dirname "$0")/run.sh" "$DIR/fail.json" >/dev/null 2>&1; then exit 1; fi
echo 'claim-truth-gate-selftest=PASS'
