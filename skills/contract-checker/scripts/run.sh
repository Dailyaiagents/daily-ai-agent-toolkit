#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "--selftest" ]; then exec bash "$(dirname "$0")/selftest.sh"; fi
ROOT=""; CONTRACT=""
while [ "$#" -gt 0 ]; do case "$1" in --root) ROOT="$2"; shift 2;; --contract) CONTRACT="$2"; shift 2;; *) exit 2;; esac; done
python3 - "$ROOT" "$CONTRACT" <<'PY'
import json,sys
from pathlib import Path
root=Path(sys.argv[1]).expanduser().resolve(strict=True); contract=(root/sys.argv[2]).resolve(strict=True)
if contract!=root and root not in contract.parents: raise SystemExit(2)
data=json.loads(contract.read_text()); rows=[]
for req in data.get('requirements',[]):
 missing=[]
 for raw in req.get('evidence_paths',[]):
  try:
   p=(root/raw).resolve(strict=True)
   if root not in p.parents or not p.is_file() or p.stat().st_size==0: missing.append(raw)
  except OSError: missing.append(raw)
 rows.append({'id':req.get('id'),'status':'PASS' if req.get('evidence_paths') and not missing else 'FAIL','missing':missing})
status='PASS' if rows and all(r['status']=='PASS' for r in rows) else 'FAIL'
print(json.dumps({'schema_version':'dailyai.contract-checker/v1','status':status,'requirements':rows},sort_keys=True)); raise SystemExit(0 if status=='PASS' else 1)
PY
