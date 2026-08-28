---
name: claim-truth-gate
description: Refuse claim records that lack an explicit source or an honest unverified state.
license: Apache-2.0
compatibility: Requires bash and Python 3.11+.
metadata:
  version: 0.1.0
  author: Daily AI Agents LLC
---

# Claim Truth Gate

Prepare a JSON array of claim records. Each record needs `statement`, `status`, and `sources`. A record with no source may pass only when its status is `UNVERIFIED`.

```bash
bash scripts/run.sh claims.json
```

This gate checks disclosure and evidence references. It does not fetch sources or determine semantic truth.
