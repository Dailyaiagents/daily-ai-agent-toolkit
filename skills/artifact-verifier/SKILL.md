---
name: artifact-verifier
description: Verify that declared deliverable files exist, are non-empty, remain inside an allowed root, and avoid declared placeholder terms.
license: Apache-2.0
compatibility: Requires bash, Python 3.11+, and sha256sum or shasum.
metadata:
  version: 0.1.0
  author: Daily AI Agents LLC
---

# Artifact Verifier

Use this skill before claiming that generated deliverables exist.

```bash
bash scripts/run.sh --root /path/to/workspace \
  --paths report.md evidence/result.json \
  --forbidden-terms TODO PLACEHOLDER
```

The command returns JSON. `PASS` proves the declared files were present and non-empty when checked. It does not prove that their contents are correct.

Refuse when a path escapes the allowed root, crosses a symlink, is missing, is empty, exceeds 10 MiB, or contains a declared forbidden term. Treat every byte beneath the supplied root as effectively disclosed to the caller.
