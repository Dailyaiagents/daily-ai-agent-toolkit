# Repository controls

Status updated on 2026-08-28 for `Dailyaiagents/daily-ai-agent-toolkit`.

## Confirmed live controls

- The repository publicly serves the one-commit source candidate `73b4ae46e5a1e1482c5613d978fc0581bd93dc64` from `main`.
- GitHub reports its SSH signature as verified and valid; the tree is byte-identical to the independently accepted candidate.
- Hosted CI passed all six Ubuntu/macOS Python 3.11–3.13 jobs plus dependency and workflow-security audits at that exact commit.
- Secret scanning, push protection, validity checks, web commit signoff, and automatic head-branch deletion are enabled.
- An active `Protect release tags` ruleset blocks deletion and non-fast-forward updates for `refs/tags/v*`, with no bypass actors.
- An active no-bypass `Protect main` ruleset requires signed commits, a pull request review, strict success from all eight hosted checks, resolved review threads, and last-push approval; it blocks deletion and non-fast-forward updates.
- Four deployment environments exist: one PyPI and one MCP Registry environment for each package.
- Every deployment environment disallows administrator bypass, requires a reviewer, prevents self-review, and accepts only `v*` tags.

## Fail-closed publication state

`BLOCKED-AUTH`: the organization currently has one member, `dailyaiagents-cpu`. That same account is the only eligible environment reviewer, so `prevent_self_review` deliberately prevents it from approving its own publication jobs. A distinct trusted organization member must be invited and configured as the required reviewer before a tag can publish.

The local public signing key is registered with GitHub. No private key material was uploaded.

PyPI Trusted Publishing and MCP Registry namespace verification remain `UNVERIFIED` until their authenticated provider-side setup is completed. Token or improvised-namespace fallbacks are prohibited.

## Remaining external gates

- Release/tag creation, PyPI publication, MCP Registry publication, and public-release verification remain blocked until the authorization gates above are cleared.

This document is a dated control receipt, not a claim that external publication has occurred.
