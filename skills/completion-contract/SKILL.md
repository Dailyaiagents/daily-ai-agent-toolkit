---
name: completion-contract
description: Persist ordered completion steps and refuse skipped, repeated, or out-of-order completion claims.
license: Apache-2.0
compatibility: Requires bash and Python 3.11+.
metadata:
  version: 0.1.0
  author: Daily AI Agents LLC
---

# Completion Contract

```bash
bash scripts/run.sh init state.json step-a step-b
bash scripts/run.sh mark state.json step-a receipt-a.json
bash scripts/run.sh status state.json
```

Only the next incomplete step may be marked. A receipt path is required. This does not validate the receipt contents.
