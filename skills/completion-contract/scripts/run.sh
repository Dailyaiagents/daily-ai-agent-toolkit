#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "--selftest" ]; then exec bash "$(dirname "$0")/selftest.sh"; fi
python3 - "$@" <<'PY'
import json,sys
from pathlib import Path
cmd=sys.argv[1]; path=Path(sys.argv[2])
if cmd=='init':
 steps=sys.argv[3:]
 if not steps or len(set(steps))!=len(steps): raise SystemExit(2)
 data={'schema_version':'dailyai.completion-contract/v1','steps':[{'id':s,'status':'NOT_RUN','evidence':None} for s in steps]}; path.write_text(json.dumps(data,indent=2)+'\n')
elif cmd=='mark':
 step=sys.argv[3]; evidence=sys.argv[4]; data=json.loads(path.read_text()); pending=next((s for s in data['steps'] if s['status']!='PASS'),None)
 if not pending or pending['id']!=step or not Path(evidence).is_file(): print(json.dumps({'status':'FAIL','reason':'out_of_order_or_evidence_missing'})); raise SystemExit(1)
 pending.update(status='PASS',evidence=evidence); path.write_text(json.dumps(data,indent=2)+'\n')
elif cmd=='status': data=json.loads(path.read_text())
else: raise SystemExit(2)
status='PASS' if all(s['status']=='PASS' for s in data['steps']) else 'UNVERIFIED'
print(json.dumps({'status':status,'steps':data['steps']},sort_keys=True))
PY
