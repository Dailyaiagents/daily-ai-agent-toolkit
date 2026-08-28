#!/usr/bin/env bash
set -euo pipefail
DIR="$(mktemp -d)"; trap 'rm -rf "$DIR"' EXIT
printf '{}' > "$DIR/a.json"; printf '{}' > "$DIR/b.json"
bash "$(dirname "$0")/run.sh" init "$DIR/state.json" a b >/dev/null
if bash "$(dirname "$0")/run.sh" mark "$DIR/state.json" b "$DIR/b.json" >/dev/null 2>&1; then exit 1; fi
bash "$(dirname "$0")/run.sh" mark "$DIR/state.json" a "$DIR/a.json" >/dev/null
bash "$(dirname "$0")/run.sh" mark "$DIR/state.json" b "$DIR/b.json" | grep -q '"status": "PASS"'
echo 'completion-contract-selftest=PASS'
