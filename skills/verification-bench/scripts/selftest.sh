#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "$0")/run.sh" | grep -q '"status": "PASS"'
if bash "$(dirname "$0")/run.sh" unexpected >/dev/null 2>&1; then exit 1; fi
echo 'verification-bench-selftest=PASS'
