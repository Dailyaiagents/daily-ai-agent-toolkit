#!/usr/bin/env bash
set -euo pipefail
DIR="$(mktemp -d)"; trap 'rm -rf "$DIR"' EXIT
printf 'proof\n' > "$DIR/proof.txt"
bash "$(dirname "$0")/run.sh" --root "$DIR" --paths proof.txt | grep -q '"status": "PASS"'
printf 'TODO placeholder\n' > "$DIR/placeholder.txt"
if bash "$(dirname "$0")/run.sh" --root "$DIR" --paths placeholder.txt --forbidden-terms TODO >/dev/null 2>&1; then exit 1; fi
if bash "$(dirname "$0")/run.sh" --root "$DIR" --paths missing.txt >/dev/null 2>&1; then exit 1; fi
echo 'artifact-verifier-selftest=PASS'
