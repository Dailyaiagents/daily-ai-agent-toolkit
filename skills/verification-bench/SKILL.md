---
name: verification-bench
description: Run a labeled fixture set through the bundled deterministic subject and report catch rate and false-refusal rate without converting synthetic performance into production proof.
license: Apache-2.0
compatibility: Requires bash and Python 3.11+.
metadata:
  version: 0.1.0
  author: Daily AI Agents LLC
---

# Verification Bench

Run the bundled synthetic fixtures:

```bash
bash scripts/run.sh
```

The receipt reports every fixture's expected and observed outcome, the denominator, caught failures, accepted pass cases, catch rate, and false-refusal rate. The bundled subject rejects missing, empty, TODO, and PLACEHOLDER artifacts. Synthetic results do not establish production accuracy or the performance of a different checker.
