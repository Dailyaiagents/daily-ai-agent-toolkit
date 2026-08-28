#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "--selftest" ]; then exec bash "$(dirname "$0")/selftest.sh"; fi
python3 - "$1" <<'PY'
import json,sys
from pathlib import Path
try: rows=json.loads(Path(sys.argv[1]).read_text())
except Exception as exc:
 print(json.dumps({'status':'FAIL','reason':f'invalid_input:{type(exc).__name__}'})); raise SystemExit(1)
findings=[]
for i,row in enumerate(rows if isinstance(rows,list) else []):
 statement=str(row.get('statement','')).strip(); state=row.get('status'); sources=row.get('sources') or []
 if not statement: findings.append({'index':i,'status':'FAIL','reason':'statement_missing'})
 elif sources: findings.append({'index':i,'status':'PASS','reason':'source_declared'})
 elif state=='UNVERIFIED': findings.append({'index':i,'status':'PASS','reason':'uncertainty_disclosed'})
 else: findings.append({'index':i,'status':'FAIL','reason':'source_or_unverified_required'})
status='PASS' if findings and all(x['status']=='PASS' for x in findings) else 'FAIL'
print(json.dumps({'schema_version':'dailyai.claim-truth-gate/v1','status':status,'findings':findings},sort_keys=True))
raise SystemExit(0 if status=='PASS' else 1)
PY
