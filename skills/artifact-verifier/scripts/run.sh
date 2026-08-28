#!/usr/bin/env bash
set -euo pipefail
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "${1:-}" = "--selftest" ]; then exec bash "$SELF_DIR/selftest.sh"; fi
ROOT=""; MODE=""; declare -a PATHS=() TERMS=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --root) ROOT="${2:-}"; shift 2; MODE="" ;;
    --paths) MODE="paths"; shift ;;
    --forbidden-terms) MODE="terms"; shift ;;
    --*) echo '{"status":"FAIL","reason":"usage"}'; exit 2 ;;
    *)
      case "$MODE" in
        paths) PATHS+=("$1") ;;
        terms) TERMS+=("$1") ;;
        *) echo '{"status":"FAIL","reason":"usage"}'; exit 2 ;;
      esac
      shift
      ;;
  esac
done
PATH_COUNT="${#PATHS[@]}"
python3 - "$ROOT" "$PATH_COUNT" ${PATHS[@]+"${PATHS[@]}"} ${TERMS[@]+"${TERMS[@]}"} <<'PY'
import hashlib,json,os,stat,sys
from pathlib import Path

MAX_FILE_BYTES=10*1024*1024
root=Path(sys.argv[1]).expanduser().resolve(strict=True)
path_count=int(sys.argv[2]); raw_paths=sys.argv[3:3+path_count]; forbidden=sys.argv[3+path_count:]
if not root.is_dir() or not raw_paths or len(raw_paths)>100 or len(forbidden)>100 or any(not x or len(x)>4096 for x in [*raw_paths,*forbidden]):
 print(json.dumps({'status':'FAIL','reason':'input_invalid'},sort_keys=True)); raise SystemExit(2)

def read_beneath(raw):
 candidate=Path(raw).expanduser()
 if candidate.is_absolute():
  try: relative=Path(os.path.abspath(candidate)).relative_to(root)
  except ValueError: raise ValueError('path_outside_root')
 else: relative=candidate
 parts=relative.parts
 if not parts or any(x in ('','.','..') for x in parts): raise ValueError('path_component_invalid')
 dflags=os.O_RDONLY|getattr(os,'O_DIRECTORY',0)|getattr(os,'O_NOFOLLOW',0); fflags=os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)
 fds=[]
 try:
  fds.append(os.open(root,dflags))
  for part in parts[:-1]: fds.append(os.open(part,dflags,dir_fd=fds[-1]))
  fds.append(os.open(parts[-1],fflags,dir_fd=fds[-1])); details=os.fstat(fds[-1])
  if not stat.S_ISREG(details.st_mode): raise ValueError('regular_file_required')
  if details.st_size>MAX_FILE_BYTES: raise ValueError('file_too_large')
  data=os.read(fds[-1],MAX_FILE_BYTES+1)
  if len(data)>MAX_FILE_BYTES: raise ValueError('file_too_large')
  return Path(*parts).as_posix(),data
 except OSError as exc: raise ValueError('file_unavailable') from exc
 finally:
  for fd in reversed(fds):
   try: os.close(fd)
   except OSError: pass

rows=[]
for raw in raw_paths:
 try:
  display,data=read_beneath(raw)
  if not data: raise ValueError('empty_artifact')
  text=data.decode('utf-8',errors='replace'); present=[term for term in forbidden if term in text]
  if present: raise ValueError('forbidden_term_present:'+','.join(present))
  rows.append({'path':display,'status':'PASS','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 except ValueError as exc:
  rows.append({'path':raw,'status':'FAIL','reason':str(exc)})
status='PASS' if rows and all(row['status']=='PASS' for row in rows) else 'FAIL'
print(json.dumps({'schema_version':'dailyai.artifact-verifier/v1','status':status,'artifacts':rows,'limitations':['All bytes beneath root are effectively disclosed to the caller.']},sort_keys=True))
raise SystemExit(0 if status=='PASS' else 1)
PY
