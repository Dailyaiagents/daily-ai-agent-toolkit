# Demo transcript

Runtime: 2:59

Artifact: `daily-ai-agent-toolkit-demo-v0.1.1.mp4`

## 0:00 — Proof should travel with the work

AI systems can say work is complete before the evidence is retained. I built the Daily AI Agent Toolkit to make that boundary explicit. It provides two local MCP servers, eight deterministic tools, and six portable Agent Skills.

## 0:18 — Incomplete evidence is rejected

Evidence Gate checks a file beneath an operator supplied root. This synthetic report exists, but it is empty and fails the declared required-text rule. The result is fail, with machine-readable findings. This is a bounded local receipt, not a semantic judgment.

## 0:46 — Turn failure into an actionable blocker

Release Gate converts the failed finding into an explicit blocker. The requirement, observed state, reason, and repair remain visible. Missing or invalid evidence does not become an optimistic pass, and the next action is inspectable.

## 1:10 — Repair, then rerun the identical rule

I add the qualifying evidence and rerun the identical check. It now passes and records a byte count and SHA-256 digest for the retained artifact. That proves this file met this declared rule. It does not prove every statement in the report.

## 1:38 — Retain the release receipt

Release Gate then hashes the repaired artifact into a retained release receipt. The check status, relative path, byte count, digest, and limitation travel together. The receipt does not publish, deploy, or approve anything. It gives a reviewer reproducible evidence for the next controlled decision.

## 2:08 — Fixed examples prevent hand-picked proof

A single demonstration can be hand picked, so the repository includes twenty declared-outcome examples across all eight tools. They cover pass, fail, blocked, and unverified states. The same catalog runs in the test suite, alongside thirty-three Python tests and six deterministic skill self-tests.

## 2:34 — Inspect the evidence. Keep the boundary.

The Daily AI Agent Toolkit is open source, local, and deterministic. Its job is narrow: make evidence, blockers, uncertainty, and immutable artifact identity easier to inspect before release. A local pass is never represented as semantic truth, production proof, or publication authority.
