#!/usr/bin/env bash
set -euo pipefail
DIR="$(mktemp -d)"; trap 'rm -rf "$DIR"' EXIT
printf 'proof' > "$DIR/proof.txt"; printf '{"requirements":[{"id":"one","evidence_paths":["proof.txt"]}]}' > "$DIR/contract.json"
bash "$(dirname "$0")/run.sh" --root "$DIR" --contract contract.json | grep -q '"status": "PASS"'
echo 'contract-checker-selftest=PASS'
