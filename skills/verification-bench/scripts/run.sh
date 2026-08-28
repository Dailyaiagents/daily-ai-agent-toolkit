#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "--selftest" ]; then exec bash "$(dirname "$0")/selftest.sh"; fi
if [ "$#" -ne 0 ]; then echo '{"status":"FAIL","reason":"usage"}'; exit 2; fi
python3 - <<'PY'
import json,tempfile
from pathlib import Path

def subject(path):
 try:
  data=path.read_bytes()
 except OSError:
  return False
 return bool(data) and b'TODO' not in data and b'PLACEHOLDER' not in data

definitions=[
 ('missing_file',None,False),
 ('empty_file','',False),
 ('todo_placeholder','TODO',False),
 ('named_placeholder','PLACEHOLDER',False),
 ('valid_receipt','status=PASS',True),
 ('valid_report','verified output',True),
]
rows=[]
with tempfile.TemporaryDirectory(prefix='verification-bench-') as temporary:
 root=Path(temporary)
 for name,content,expected in definitions:
  path=root/f'{name}.txt'
  if content is not None: path.write_text(content,encoding='utf-8')
  observed=subject(path)
  rows.append({'id':name,'expected_accept':expected,'observed_accept':observed,'matched':observed==expected})
failures=[row for row in rows if not row['expected_accept']]; passes=[row for row in rows if row['expected_accept']]
caught=sum(not row['observed_accept'] for row in failures); false_refused=sum(not row['observed_accept'] for row in passes)
status='PASS' if all(row['matched'] for row in rows) else 'FAIL'
print(json.dumps({'schema_version':'dailyai.verification-bench/v1','status':status,'total':len(rows),'failure_cases':len(failures),'caught_failures':caught,'pass_cases':len(passes),'false_refusals':false_refused,'catch_rate':caught/len(failures),'false_refusal_rate':false_refused/len(passes),'results':rows,'limitations':['Synthetic fixtures test this bundled subject only and do not establish production accuracy.']},sort_keys=True))
raise SystemExit(0 if status=='PASS' else 1)
PY
