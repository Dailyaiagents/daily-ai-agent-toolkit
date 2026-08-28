---
name: contract-checker
description: Compare a JSON output contract with retained evidence files under one workspace root.
license: Apache-2.0
compatibility: Requires bash and Python 3.11+.
metadata:
  version: 0.1.0
  author: Daily AI Agents LLC
---

# Contract Checker

The contract contains a non-empty `requirements` array. Each requirement has an `id` and `evidence_paths`.

```bash
bash scripts/run.sh --root /workspace --contract contract.json
```

The gate proves file presence and root containment. A separate review must determine whether the evidence actually satisfies the requirement.
