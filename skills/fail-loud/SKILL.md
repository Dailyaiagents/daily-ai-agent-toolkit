---
name: fail-loud
description: Convert a failed dependency or tool step into an explicit blocker record without substituting a narrative success.
license: Apache-2.0
compatibility: Requires bash and Python 3.11+.
metadata:
  version: 0.1.0
  author: Daily AI Agents LLC
---

# Fail Loud

```bash
bash scripts/run.sh --lane build-1 --what "package build" --where "release" --reason "dependency missing" --repair "install the declared build dependency"
```

The command prints a structured `BLOCKED` record and exits non-zero. It never sends a notification or substitutes another provider.
