# Evidence-gated career claims

These drafts are intentionally anonymized. Replace bracketed fields only with public, verified URLs or dates. Do not present a pending claim as completed.

## Public toolkit

Status: `PENDING_PUBLICATION`

Release gate: use the language below only after the public repository, both PyPI `0.1.0` packages, both MCP Registry entries, and retained verification artifacts work without authentication.

### Resume draft

> Founded and led development of an Apache-2.0 toolkit with two local Python MCP servers, eight deterministic verification tools, and six portable Agent Skills for artifact, claim, citation, completion-contract, and release-receipt checks. Published reproducible tests and explicit proof boundaries across GitHub, PyPI, and the MCP Registry. ([repository], [release])

### LinkedIn project draft

> Built and open-sourced the Daily AI Agent Toolkit, a local deterministic verification layer for AI-assisted workflows. Its two MCP servers preserve `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, and `UNVERIFIED` states instead of converting missing evidence into completion. The project includes reproducible examples, retained checksums and provenance, and explicit limits: a local pass does not prove semantic truth or grant release authority. ([repository], [demo])

### Claims not authorized by this release

- “Proves AI outputs are true.”
- “Certifies secure or production-ready agents.”
- “Works with every MCP client.”
- “Prevents hallucinations.”
- Any adoption, download, performance, customer, or production-impact metric without separate evidence.

## AWS Agentic AI Demonstrated

Status: `PENDING_CREDENTIAL`

Credential gate: use completion language only after AWS posts a shareable credential or verification record for Cooper's personally completed assessment.

### Resume draft after verification

> Earned AWS Agentic AI Demonstrated, a hands-on AWS microcredential covering troubleshooting, repair, integration, and enhancement of AI agents built using Amazon Bedrock. ([credential URL], [month year])

### LinkedIn credential draft after verification

> Earned AWS Agentic AI Demonstrated through AWS's hands-on, provisioned-environment assessment. Credential: [verification URL].

### Acceptable language before verification

> Preparing for the AWS Agentic AI Demonstrated hands-on assessment.

Do not claim a score, duration, task set, Bedrock service surface, or assessment result unless the shareable AWS record establishes it.

## Evidence ledger

| Claim | Required public proof | Current state |
| --- | --- | --- |
| Toolkit author and lead | Public repository history and project attribution | `PENDING_PUBLICATION` |
| Two MCP servers, eight tools, six skills | Public source plus reproducible discovery/self-tests | `PENDING_PUBLICATION` |
| PyPI and MCP Registry availability | Exact public package and registry URLs | `PENDING_PUBLICATION` |
| AWS microcredential earned | Shareable AWS credential or verification record | `PENDING_CREDENTIAL` |

Once each gate passes, replace the status with `VERIFIED`, add the exact proof URL, and preserve the verification date. If a surface later disappears or changes materially, mark the affected claim `TODO-VERIFY` rather than silently retaining it.
