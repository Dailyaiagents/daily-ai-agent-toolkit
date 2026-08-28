#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "--selftest" ]; then exec bash "$(dirname "$0")/selftest.sh"; fi
LANE=""; WHAT=""; WHERE=""; REASON=""; REPAIR=""
while [ "$#" -gt 0 ]; do case "$1" in --lane) LANE="$2";; --what) WHAT="$2";; --where) WHERE="$2";; --reason) REASON="$2";; --repair) REPAIR="$2";; *) exit 2;; esac; shift 2; done
python3 - "$LANE" "$WHAT" "$WHERE" "$REASON" "$REPAIR" <<'PY'
import json,sys
keys=['lane','what','where','reason','repair']; values=sys.argv[1:]
if any(not v.strip() for v in values): raise SystemExit(2)
print(json.dumps({'schema_version':'dailyai.fail-loud/v1','status':'BLOCKED',**dict(zip(keys,values))},sort_keys=True))
PY
exit 1
