# Daily AI Agent Toolkit: Technical Report

Version: `0.1.0` release candidate

Project lead: Cooper Reed, founder and lead engineer, Daily AI Agents

Report date: 2026-08-27

## Abstract

AI-assisted work often fails at the boundary between producing an answer and proving that the answer satisfies a release contract. The Daily AI Agent Toolkit provides two local Model Context Protocol (MCP) servers and six portable Agent Skills for that boundary. Evidence Gate checks retained artifacts, declared claim support, and literal citation containment. Release Gate evaluates completion evidence, makes blockers explicit, and hashes retained artifacts into a release receipt.

The toolkit is intentionally deterministic and local. It does not call a model, retrieve URLs, execute inspected artifacts, approve a release, or establish semantic truth. Its useful output is therefore a bounded receipt: what was checked, against which declared rule, with which result and limitation.

## Problem

An agent can produce plausible prose while omitting the artifact, test, source, or approval needed to support it. A conventional success message can also collapse materially different states—`FAIL`, `BLOCKED`, `NOT_RUN`, and `UNVERIFIED`—into an ambiguous “done.” This creates three recurring risks:

1. a claimed artifact does not exist or differs from the retained bytes;
2. a claim cites evidence that is absent, inaccessible, or only a URL the checker never opened; and
3. a release is represented as complete despite an unmet requirement or missing approval.

The toolkit addresses these mechanical failure modes. It does not attempt to replace domain review, security testing, legal analysis, factual verification, or human authorization.

## Design

### Evidence Gate

Evidence Gate exposes four tools:

- `verify_artifact` confirms that a rooted file exists, is non-empty, records its SHA-256 digest, and applies declared required or forbidden text rules.
- `audit_claims` checks whether each supplied claim declares available local evidence. URL-only evidence remains `UNVERIFIED` because the server does not fetch URLs.
- `audit_citations` tests normalized literal quote containment in a rooted local source. Containment does not establish entailment, source quality, or factual truth.
- `summarize_verification` aggregates receipt states without upgrading uncertainty.

### Release Gate

Release Gate exposes four tools:

- `check_contract` checks the presence and non-empty status of evidence files named by a JSON completion contract.
- `evaluate_completion` preserves explicit completion states and downgrades an unsupported `PASS` to `UNVERIFIED`.
- `format_blockers` converts non-passing findings into explicit blocker records with a suggested repair.
- `build_release_receipt` hashes retained artifacts and summarizes supplied check states. It neither publishes nor approves the release.

### Security boundary

Each server receives an explicit filesystem root. File-descriptor-relative traversal with `O_NOFOLLOW` rejects files outside that root, including symlink swaps and symlinked directory components. Reads and input collections are bounded. Inputs are treated as data rather than shell fragments. The servers make no network calls and perform no publication or deployment action.

Root containment is not a confidentiality boundary. A caller can use repeated content, path, size, and digest queries as a membership oracle, so every byte under the supplied root must be treated as disclosed to that client. Operators should expose a dedicated sanitized root and independently review consequential output.

## State model

The shared result vocabulary prevents missing proof from becoming success:

| State | Meaning |
| --- | --- |
| `PASS` | The declared local check passed within its stated scope. |
| `FAIL` | The declared check found a contradiction or missing required artifact. |
| `BLOCKED` | Progress requires a missing prerequisite, authority, or repair. |
| `NOT_RUN` | No qualifying execution evidence was supplied. |
| `UNVERIFIED` | Available evidence is insufficient for the requested conclusion. |

A local `PASS` is not evidence of hosted availability, production reliability, external-client compatibility, semantic truth, or release approval.

## Verification status

The retained local record in [`LOCAL-VERIFICATION.md`](https://github.com/Dailyaiagents/daily-ai-agent-toolkit/blob/v0.1.0/LOCAL-VERIFICATION.md) reports the following checks from 2026-08-27:

- 19 Python tests passed, including symlink, archive-link, malformed-contract, empty-evidence, self-asserted-status, request-budget, resource-limit, and demo-evidence cases;
- all six skill self-tests passed;
- all 20 declared-outcome examples matched across all eight tools;
- both MCP manifests passed local `mcp-publisher validate` checks;
- public path, secret, and TODO scans passed;
- byte-identical duplicate builds, hash-locked dependencies, a zero-known-vulnerability runtime audit, and package-specific CycloneDX SBOM checks passed; and
- clean local wheel installation and stdio discovery found exactly four tools on each server.

Those results are evidence for that run and those retained bytes only. The following remain `UNVERIFIED` until demonstrated against public release artifacts:

- installation from public PyPI;
- discovery through the public MCP Registry;
- public GitHub release availability;
- compatibility with external MCP clients beyond the documented local matrix;
- CI execution on GitHub-hosted Ubuntu and macOS for Python 3.11–3.13; and
- any resume or portfolio claim that depends on the public release.

## Reproducibility

Run the repository's deterministic local checks from its root:

```bash
bash scripts/test-all.sh
```

The SBOMs inventory the hash-locked `mcp==1.29.1` runtime graph plus each package as the root component. They are dependency snapshots, not vulnerability-free guarantees; the separate `pip-audit` gate checks the same complete runtime lock and must report zero known vulnerabilities at build time.

After publication, clean-environment installation, PyPI attestations, exact public digest/size equality, GitHub provenance, and public registry discovery must be rerun against immutable version `0.1.0`; a successful local build does not substitute for those checks. Release artifacts retain wheels, source distributions, checksums, package-specific software bills of materials, demo evidence, registry manifests, and provenance together so a reviewer can relate public bytes to the reported verification.

## Limitations

- Rules are supplied by the operator. A weak or incomplete rule can pass while material risk remains.
- Literal citation containment is mechanical and can neither assess source credibility nor prove that a quote supports an inference.
- Hashing establishes byte identity, not correctness or safety.
- Evidence-file presence does not prove the narrative attached to that evidence.
- Results are time- and scope-bounded. A later change requires a new run and new receipt.
- Human authorization remains required for publication and other consequential external actions.

## Conclusion

The toolkit makes a narrow promise: preserve proof boundaries and make unsupported completion harder to hide. Its value is not autonomous judgment; it is a small, inspectable layer that keeps local evidence, uncertainty, blockers, and immutable artifact identity visible before a human or controlled process decides to release.
