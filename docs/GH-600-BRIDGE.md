# GH-600 five-day bridge plan

Prepared for Cooper Reed

Updated: 2026-08-27

## Current official exam shape

The GitHub Certified Agentic AI Developer exam is identified as **GH-600**. Microsoft states that the assessment allows 120 minutes, is proctored, and may include interactive components. Microsoft recommends registering with a personal Microsoft account so the record is not lost when leaving an organization. Result timing is `UNVERIFIED` here and must be confirmed on the live scheduling surface. Sources: [certification page](https://learn.microsoft.com/en-us/credentials/certifications/agentic-ai-developer/) and [official GH-600 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-600).

The current domain weights are:

| Domain | Weight |
| --- | ---: |
| Prepare agent architecture and SDLC processes | 15–20% |
| Implement tool use and environment interaction | 20–25% |
| Manage memory, state, and execution | 10–15% |
| Perform evaluation, error analysis, and tuning | 15–20% |
| Orchestrate multi-agent coordination | 15–20% |
| Implement guardrails and accountability | 10–15% |

This plan uses the toolkit as a practice substrate; it does not claim the toolkit covers the entire exam.

## Day 1 — Architecture, SDLC, and control boundaries

Target: 75–90 minutes.

- Read the official objectives for agent/SDLC integration, success criteria, planning-versus-action separation, observability, autonomy, and human intervention.
- Diagram a sample workflow with explicit inputs, outputs, branch scope, success criteria, failure states, human approval, and retained artifacts.
- Use the toolkit's release boundary as a case study: explain why a deterministic local `PASS` is not publication authority.
- Practice identifying anti-patterns: ambiguous success criteria, excessive autonomy, shared mutable workspaces, unreviewed side effects, and missing rollback paths.
- Produce one page from memory, then compare it against the [official study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-600).

Acceptance: explain, without notes, how planning is separated from execution and where a human gate belongs for an irreversible action.

## Day 2 — Tools, MCP, environments, and error handling

Target: 90 minutes.

- Review tool selection, permissions, MCP server configuration, registries, allow lists, repository scope, CI invocation, branches, retries, rollbacks, escalation, and traceability from the official objectives.
- Install both toolkit servers in an isolated environment and discover their tool schemas through an MCP client.
- Trace one call end to end: client configuration, stdio process, rooted filesystem scope, tool input, receipt, and failure handling.
- Explain the difference between tool availability and tool authorization, and between retryable failure and a blocker requiring human intervention.
- Design—but do not execute—a CI workflow that invokes a read-only gate on a branch and uploads its receipt for review.

Acceptance: diagnose three planted configuration errors without broadening permissions or bypassing the declared root.

## Day 3 — Memory, state, evaluation, and tuning

Target: 90 minutes.

- Review short-term, long-term, and external memory; relevance scope; expiration, pruning, reset, durable progress, context drift, stale context, and cross-tool continuity.
- Write a compact durable handoff containing objective, scope, decisions, current state, evidence references, blockers, and next action.
- Use the toolkit's 20 examples as an evaluation set. Group outcomes into reasoning error, tool misuse, context/environment issue, expected blocker, and successful result.
- Define useful signals before changing instructions. Change one variable in a practice workflow, rerun the fixed set, and compare results without hiding regressions.
- Explain why `summarize_verification` must not upgrade an uncertain input receipt.

Acceptance: resume the practice task from the handoff without repeating completed work or changing prior decisions, then identify one stale-context risk.

## Day 4 — Multi-agent orchestration and recovery

Target: 90 minutes.

- Review orchestration patterns, parallel isolation, conflict detection, decision/handoff artifacts, partial and stalled executions, recovery, lifecycle changes, and retirement.
- Split a synthetic release across independent documentation, verification, packaging, and review lanes with explicit ownership and non-overlapping write scopes.
- Introduce one overlapping edit and one stalled lane. Detect each from status and artifacts, preserve completed independent work, and define the safe recovery.
- Produce a post-hoc record that distinguishes complete, partial, blocked, and not-run work.
- Explain when sequential work is safer than parallelism and when a human-in-the-loop transition is required.

Acceptance: recover the synthetic workflow without discarding unrelated valid output or claiming the overall release complete.

## Day 5 — Guardrails, accountability, and timed rehearsal

Target: 105–120 minutes.

- Review risk-based autonomy, least privilege, policy-blocked actions, explicit authorization, controlled paths, and approvals that materially reduce risk.
- Classify actions such as reading files, running tests, publishing packages, changing permissions, deleting artifacts, and deploying production changes by risk and required intervention.
- Rehearse a 120-minute exam block using the official exam sandbox or legitimate Microsoft/GitHub learning material. Do not seek or use recalled exam questions.
- Spend review time in proportion to the published domain weights, with extra practice on tool/environment interaction because it has the largest stated range.
- Record weak objectives by official domain and schedule one bounded follow-up session rather than studying every topic again.

Acceptance: explain the least-privilege and human-approval design for three consequential scenarios, and finish the timed rehearsal with enough time to review flagged items.

## Toolkit-to-objective map

| Toolkit practice | GH-600 relevance | Boundary |
| --- | --- | --- |
| Explicit completion contract | Inputs, outputs, success criteria, inspectable SDLC artifacts | File presence is not narrative truth. |
| Rooted MCP servers | Tool configuration, execution context, repository scope, least privilege | Local stdio does not prove remote MCP configuration. |
| `PASS`/`FAIL`/`BLOCKED`/`NOT_RUN`/`UNVERIFIED` | Evaluation signals, error analysis, escalation, accountability | Vocabulary alone does not implement orchestration or policy. |
| Artifact hashes and receipts | Durable state, continuity, review, audit | A hash proves byte identity, not correctness. |
| Parallel release lanes | Multi-agent isolation, conflicts, handoffs, recovery | A synthetic sprint is not production-grade operating proof. |
| External publication gate | Human intervention and authorization for consequential actions | Approval is organizational context, not an MCP tool result. |

## Scheduling and credential boundary

- Register with a personal Microsoft account as recommended on the official certification page.
- Confirm price, availability, result timing, identity requirements, system check, reschedule policy, and accommodations on the scheduling surface before purchase; these are current-account and region-dependent and are `UNVERIFIED` here.
- The assessment must be completed personally under the proctoring and exam-security rules.
- Do not publish a pass claim until the result is available and a shareable credential or transcript record exists.
- Until then, acceptable language is: `Preparing for GitHub Certified: Agentic AI Developer (GH-600)`.
